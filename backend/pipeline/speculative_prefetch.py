import asyncio
import hashlib
import json
import logging
import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("alfie-speculative-prefetch")

# Safe read-only / query tools allowed for speculative background execution
SAFE_READ_ONLY_TOOLS: Set[str] = {
    "check_calendar_availability",
    "check_availability",
    "get_available_slots",
    "lookup_case",
    "get_case_status",
    "search_properties",
    "get_property_details",
    "lookup_car_rental",
    "check_luxury_fleet",
    "get_vehicle_rates",
    "fetch_menu_specials",
    "get_reservation_availability",
    "query_crm_contact",
    "get_contact_info",
    "get_faq_answer",
    "check_inventory",
    "get_service_pricing",
}

# State-mutating / side-effect tools that MUST NEVER be executed speculatively
MUTATING_TOOLS: Set[str] = {
    "book_appointment",
    "schedule_appointment",
    "create_lead",
    "submit_intake",
    "cancel_booking",
    "update_booking",
    "send_sms",
    "send_email",
    "charge_payment",
    "process_deposit",
    "transfer_to_department",
    "transfer_to_squad_agent",
    "hangup_call",
}


@dataclass
class SpeculativeToolCandidate:
    """Represents a predicted tool call extracted from streaming partial STT tokens."""
    tool_name: str
    arguments: Dict[str, Any]
    confidence: float
    intent: str
    matched_phrase: str
    extracted_at: float = field(default_factory=time.time)

    def cache_key(self) -> str:
        """Generates deterministic cache key for (tool_name, normalized_args)."""
        args_str = json.dumps(self.arguments, sort_keys=True)
        h = hashlib.md5(f"{self.tool_name}:{args_str}".encode("utf-8")).hexdigest()
        return f"{self.tool_name}:{h}"


@dataclass
class SpeculativeExecutionResult:
    """Stores the execution result of a speculative background tool call."""
    tool_name: str
    arguments: Dict[str, Any]
    result: Any
    execution_time_ms: float
    cached_at: float = field(default_factory=time.time)
    ttl_seconds: float = 25.0
    hit_count: int = 0

    @property
    def is_expired(self) -> bool:
        return (time.time() - self.cached_at) > self.ttl_seconds


class FastEntityExtractor:
    """
    Ultra-fast (<1ms) heuristic regex & entity extractor for streaming speech tokens.
    Extracts dates, times, vehicle classes, case IDs, and property queries before turn completion.
    """

    # Date and relative time expressions
    DATE_PATTERNS = [
        re.compile(r"\b(tomorrow|today|tonight|yesterday)\b", re.IGNORECASE),
        re.compile(r"\b(next\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|week|month))\b", re.IGNORECASE),
        re.compile(r"\b((?:on\s+)?(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday))\b", re.IGNORECASE),
        re.compile(r"\b((?:jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\s+\d{1,2}(?:st|nd|rd|th)?)\b", re.IGNORECASE),
        re.compile(r"\b(\d{4}-\d{2}-\d{2})\b"),
    ]

    TIME_PATTERNS = [
        re.compile(r"\b(\d{1,2}(?::\d{2})?\s*(?:am|pm))\b", re.IGNORECASE),
        re.compile(r"\b(in the (?:morning|afternoon|evening))\b", re.IGNORECASE),
        re.compile(r"\b(at\s+\d{1,2}\s*(?:o'?clock)?)\b", re.IGNORECASE),
    ]

    # Identifiers (Case numbers, reference codes, policy numbers)
    CASE_PATTERNS = [
        re.compile(r"\b(?:case|claim|ticket|file|reference|ref|policy)(?:\s*(?:number|no|#))?\s*[:#-]?\s*([A-Za-z0-9\-]{3,16})\b", re.IGNORECASE),
    ]

    # Vehicle / Fleet / Rental keywords
    VEHICLE_PATTERNS = [
        re.compile(r"\b(escalade|suburban|sedan|suv|sprinter|limo|limousine|mercedes|bmw|cadillac|rolls\s*royce|phantom|maybach|van)\b", re.IGNORECASE),
    ]

    # Real Estate keywords
    PROPERTY_PATTERNS = [
        re.compile(r"\b(\d+)\s*(?:bed|bedroom|bath|bathroom)\b", re.IGNORECASE),
        re.compile(r"\b(?:in|around|near)\s+([A-Za-z\s]{3,20})\s*(?:downtown|area|district|suburb)?\b", re.IGNORECASE),
    ]

    @classmethod
    def extract_entities(cls, text: str) -> Dict[str, Any]:
        """Extracts parsed entities from partial transcript."""
        entities: Dict[str, Any] = {}
        text_clean = text.strip()

        # 1. Date extraction
        for pattern in cls.DATE_PATTERNS:
            m = pattern.search(text_clean)
            if m:
                entities["date_expression"] = m.group(1).strip()
                break

        # 2. Time extraction
        for pattern in cls.TIME_PATTERNS:
            m = pattern.search(text_clean)
            if m:
                entities["time_expression"] = m.group(1).strip()
                break

        # 3. Case / Identifier extraction
        for pattern in cls.CASE_PATTERNS:
            m = pattern.search(text_clean)
            if m:
                entities["case_id"] = m.group(1).strip()
                break

        # 4. Vehicle category
        for pattern in cls.VEHICLE_PATTERNS:
            m = pattern.search(text_clean)
            if m:
                entities["vehicle_type"] = m.group(1).strip().lower()
                break

        # 5. Property features
        for pattern in cls.PROPERTY_PATTERNS:
            m = pattern.search(text_clean)
            if m:
                entities["property_query"] = m.group(0).strip()
                break

        return entities


class SpeculativeToolPrefetcher:
    """
    Monitors streaming partial STT tokens during caller turns and determines candidate
    read-only tools to prefetch in the background.
    """

    def __init__(self, tenant_id: str, niche: str = "general"):
        self.tenant_id = tenant_id
        self.niche = (niche or "general").strip().lower().replace("-", "_")
        self.last_analyzed_text: str = ""
        self.last_analyzed_time: float = 0.0
        self.min_token_length: int = 8

    def is_safe_tool(self, tool_name: str) -> bool:
        """Returns True if the tool is safe for non-blocking speculative execution."""
        if tool_name in MUTATING_TOOLS:
            return False
        if tool_name in SAFE_READ_ONLY_TOOLS:
            return True
        # Check standard read-only prefixes
        name_lower = tool_name.lower()
        if any(name_lower.startswith(p) for p in ("get_", "check_", "lookup_", "search_", "fetch_", "query_", "list_")):
            return True
        return False

    def on_partial_transcript(
        self,
        partial_text: str,
        enabled_tools: Optional[List[str]] = None,
    ) -> List[SpeculativeToolCandidate]:
        """
        Analyzes partial STT stream and returns candidate tools to pre-fetch.
        """
        if not partial_text or len(partial_text.strip()) < self.min_token_length:
            return []

        clean_text = partial_text.strip()
        # Skip if identical to last analyzed snippet
        if clean_text == self.last_analyzed_text:
            return []

        self.last_analyzed_text = clean_text
        self.last_analyzed_time = time.time()
        candidates: List[SpeculativeToolCandidate] = []

        entities = FastEntityExtractor.extract_entities(clean_text)
        lower_text = clean_text.lower()

        # 1. Calendar / Scheduling Availability Intent
        if "date_expression" in entities or any(w in lower_text for w in ("available", "availability", "schedule", "appointment", "free time", "book")):
            date_val = entities.get("date_expression", "tomorrow")
            time_val = entities.get("time_expression", "afternoon")
            candidate = SpeculativeToolCandidate(
                tool_name="check_calendar_availability",
                arguments={"date": date_val, "preferred_time": time_val},
                confidence=0.88,
                intent="check_availability",
                matched_phrase=clean_text,
            )
            if self.is_safe_tool(candidate.tool_name):
                candidates.append(candidate)

        # 2. Case / Claims / Legal Inquiry
        if "case_id" in entities or any(w in lower_text for w in ("claim status", "case status", "ticket status", "my file")):
            case_id = entities.get("case_id", "active_caller")
            candidate = SpeculativeToolCandidate(
                tool_name="lookup_case",
                arguments={"case_id": case_id},
                confidence=0.92,
                intent="case_inquiry",
                matched_phrase=clean_text,
            )
            if self.is_safe_tool(candidate.tool_name):
                candidates.append(candidate)

        # 3. Fleet / Car Rental / Luxury Transport
        if "vehicle_type" in entities or any(w in lower_text for w in ("luxury", "sedan", "suv", "chauffeur", "car rental", "fleet", "rates")):
            vehicle_type = entities.get("vehicle_type", "luxury_sedan")
            candidate = SpeculativeToolCandidate(
                tool_name="lookup_car_rental",
                arguments={"vehicle_type": vehicle_type, "date": entities.get("date_expression", "today")},
                confidence=0.85,
                intent="vehicle_availability",
                matched_phrase=clean_text,
            )
            if self.is_safe_tool(candidate.tool_name):
                candidates.append(candidate)

        # 4. Real Estate Property Search
        if "property_query" in entities or any(w in lower_text for w in ("property", "listing", "bedroom", "apartment", "house", "rent")):
            candidate = SpeculativeToolCandidate(
                tool_name="search_properties",
                arguments={"query": entities.get("property_query", clean_text), "location": entities.get("property_query", "all")},
                confidence=0.82,
                intent="property_search",
                matched_phrase=clean_text,
            )
            if self.is_safe_tool(candidate.tool_name):
                candidates.append(candidate)

        return candidates


class SpeculativeExecutionPool:
    """
    Asynchronous promise pool and cache for speculative tool results.
    Eliminates tool latency by fulfilling LLM tool calls immediately from memory.
    """

    def __init__(self, ttl_seconds: float = 25.0, max_cached_items: int = 50):
        self.ttl_seconds = ttl_seconds
        self.max_cached_items = max_cached_items
        self._cache: Dict[str, SpeculativeExecutionResult] = {}
        self._in_flight: Dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()

        # Telemetry metrics
        self.total_dispatched: int = 0
        self.cache_hits: int = 0
        self.cache_misses: int = 0
        self.total_latency_saved_ms: float = 0.0

    def get_cache_key(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Generates canonical cache key."""
        args_str = json.dumps(arguments or {}, sort_keys=True)
        h = hashlib.md5(f"{tool_name}:{args_str}".encode("utf-8")).hexdigest()
        return f"{tool_name}:{h}"

    async def prefetch_candidate(
        self,
        candidate: SpeculativeToolCandidate,
        executor_fn: Callable[..., Any],
    ) -> Optional[str]:
        """
        Dispatches speculative execution in the background if not already cached or running.
        """
        if candidate.tool_name in MUTATING_TOOLS:
            logger.warning(f"Refusing speculative execution of mutating tool: {candidate.tool_name}")
            return None

        key = candidate.cache_key()

        async with self._lock:
            # Check existing valid cache
            cached = self._cache.get(key)
            if cached and not cached.is_expired:
                return key

            # Check existing in-flight task
            if key in self._in_flight and not self._in_flight[key].done():
                return key

            # Launch background execution task
            self.total_dispatched += 1
            task = asyncio.create_task(
                self._execute_and_cache(key, candidate.tool_name, candidate.arguments, executor_fn)
            )
            self._in_flight[key] = task
            return key

    async def _execute_and_cache(
        self,
        key: str,
        tool_name: str,
        arguments: Dict[str, Any],
        executor_fn: Callable[..., Any],
    ):
        """Executes tool in background and caches result with elapsed execution time."""
        t0 = time.time()
        try:
            if asyncio.iscoroutinefunction(executor_fn):
                result = await executor_fn(tool_name, arguments)
            else:
                result = executor_fn(tool_name, arguments)

            elapsed_ms = (time.time() - t0) * 1000

            entry = SpeculativeExecutionResult(
                tool_name=tool_name,
                arguments=arguments,
                result=result,
                execution_time_ms=elapsed_ms,
                ttl_seconds=self.ttl_seconds,
            )

            async with self._lock:
                # Evict expired or overflow items if pool exceeds max
                self._prune_cache_under_lock()
                self._cache[key] = entry
                if key in self._in_flight:
                    del self._in_flight[key]

            logger.info(f"Speculative tool prefetch completed: {tool_name} in {elapsed_ms:.1f}ms (key={key})")
        except Exception as e:
            logger.warning(f"Speculative prefetch error for {tool_name}: {e}")
            async with self._lock:
                if key in self._in_flight:
                    del self._in_flight[key]

    async def get_or_execute(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        default_executor: Callable[..., Any],
    ) -> Tuple[Any, bool, float]:
        """
        Retrieves pre-fetched speculative result if available, or executes synchronously.
        Returns (result, is_cache_hit, latency_saved_ms).
        """
        key = self.get_cache_key(tool_name, arguments)
        t0 = time.time()

        # 1. Check completed cache entry
        async with self._lock:
            cached = self._cache.get(key)
            if cached and not cached.is_expired:
                cached.hit_count += 1
                self.cache_hits += 1
                saved_ms = cached.execution_time_ms
                self.total_latency_saved_ms += saved_ms
                logger.info(f"⚡ Speculative Tool CACHE HIT: {tool_name} (saved ~{saved_ms:.1f}ms latency)")
                return cached.result, True, saved_ms

            # 2. Check in-flight task
            in_flight_task = self._in_flight.get(key)

        if in_flight_task and not in_flight_task.done():
            try:
                await in_flight_task
                async with self._lock:
                    cached = self._cache.get(key)
                    if cached and not cached.is_expired:
                        cached.hit_count += 1
                        self.cache_hits += 1
                        saved_ms = cached.execution_time_ms
                        self.total_latency_saved_ms += saved_ms
                        logger.info(f"⚡ Speculative Tool IN-FLIGHT HIT: {tool_name} (saved ~{saved_ms:.1f}ms)")
                        return cached.result, True, saved_ms
            except Exception as e:
                logger.debug(f"Awaited in-flight speculative task exception: {e}")

        # 3. Cache miss: execute directly
        self.cache_misses += 1
        if asyncio.iscoroutinefunction(default_executor):
            res = await default_executor(tool_name, arguments)
        else:
            res = default_executor(tool_name, arguments)

        elapsed_ms = (time.time() - t0) * 1000
        return res, False, 0.0

    def _prune_cache_under_lock(self):
        """Cleans expired items and enforces maximum capacity."""
        now = time.time()
        expired_keys = [k for k, v in self._cache.items() if (now - v.cached_at) > v.ttl_seconds]
        for k in expired_keys:
            del self._cache[k]

        if len(self._cache) > self.max_cached_items:
            # Drop oldest items
            sorted_keys = sorted(self._cache.keys(), key=lambda k: self._cache[k].cached_at)
            for k in sorted_keys[: len(self._cache) - self.max_cached_items]:
                del self._cache[k]

    def get_metrics(self) -> Dict[str, Any]:
        """Returns comprehensive real-time speculative execution metrics."""
        return {
            "total_dispatched": self.total_dispatched,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_ratio": (self.cache_hits / max(1, self.cache_hits + self.cache_misses)),
            "total_latency_saved_ms": round(self.total_latency_saved_ms, 2),
            "cached_items_count": len(self._cache),
            "in_flight_tasks_count": len(self._in_flight),
        }
