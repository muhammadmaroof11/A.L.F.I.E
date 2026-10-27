"""
Sub-100ms Ultra-Fast Hybrid Routing & Acoustic Fillers Engine.

Provides dual-stage ultra-low-latency verbal bridge generation during tool execution
to eliminate dead air (800ms - 2000ms latency gap) in live voice telephony calls.
"""

import logging
import random
import time
from typing import Any, Dict, List, Optional

import httpx

from config import settings

logger = logging.getLogger("alfie-hybrid-router")

# Normalization mapping for vertical aliases
NICHE_ALIASES: Dict[str, str] = {
    "personal_injury": "legal_intake",
    "law_firm": "legal_intake",
    "law_firms": "legal_intake",
    "lawyer": "legal_intake",
    "legal": "legal_intake",
    "dental": "medical_reception",
    "dental_clinic": "medical_reception",
    "clinic": "medical_reception",
    "clinics": "medical_reception",
    "healthcare": "medical_reception",
    "doctor": "medical_reception",
    "medical": "medical_reception",
    "realtor": "real_estate",
    "realty": "real_estate",
    "properties": "real_estate",
    "property": "real_estate",
    "luxury_transfer": "luxury_transport",
    "fleet": "luxury_transport",
    "chauffeur": "luxury_transport",
    "carrental": "car_rental",
    "car_rental": "car_rental",
    "restaurant": "hospitality",
    "hotel": "hospitality",
    "dining": "hospitality",
}

# Curated, multi-variety acoustic bridge banks for deterministic instant fallback (<1ms)
ACOUSTIC_FILLER_BANKS: Dict[str, Dict[str, List[str]]] = {
    "legal_intake": {
        "calendar": [
            "Checking our attorney availability for you right now...",
            "One moment while I pull up our consultation schedule...",
            "Let me see what open slots we have with our legal team...",
            "Checking our case consultation calendar...",
        ],
        "records": [
            "Looking into that for your case right now...",
            "Let me review our intake guidelines real quick...",
            "Checking our practice details on that for you...",
        ],
        "booking": [
            "Reserving that consultation slot with the attorney now...",
            "Securing your appointment details right now...",
        ],
        "general": [
            "Let me check that in our legal system for you...",
            "One moment while I look into those case details...",
            "Pulling that up for you right now...",
        ],
    },
    "medical_reception": {
        "calendar": [
            "One moment while I check the doctor's appointment calendar...",
            "Checking available clinic slots for you right now...",
            "Let me see when our providers have open availability...",
            "Checking our doctor's schedule right now...",
        ],
        "records": [
            "Looking up our department directory for you...",
            "Checking our clinic intake notes real quick...",
            "Let me pull up that medical specialty information...",
        ],
        "booking": [
            "Scheduling your clinic visit right now...",
            "Reserving that appointment time on our calendar...",
        ],
        "general": [
            "Let me check that in our clinic system for you...",
            "One moment while I pull up those details...",
            "Checking on that for you right now...",
        ],
    },
    "real_estate": {
        "calendar": [
            "Checking viewing availability for that property right now...",
            "One moment while I check the agent's showing schedule...",
            "Let me see what viewing slots are open this week...",
        ],
        "catalog": [
            "Let me pull up our property listings database...",
            "Checking current inventory and pricing for that property...",
            "Pulling up the property specifications right now...",
        ],
        "booking": [
            "Locking in your viewing request with the listing agent...",
            "Scheduling your property tour right now...",
        ],
        "general": [
            "Let me verify those property details for you...",
            "Checking our real estate registry right now...",
            "One second while I pull that listing up...",
        ],
    },
    "car_rental": {
        "calendar": [
            "Checking vehicle pickup availability for those dates...",
            "One moment while I look at our reservation calendar...",
        ],
        "catalog": [
            "Checking our fleet inventory for those dates right now...",
            "Let me see what vehicle classes are currently available...",
            "Pulling up our current fleet rates and models...",
        ],
        "booking": [
            "Reserving that vehicle category for you right now...",
            "Putting a hold on that car rental slot...",
        ],
        "general": [
            "Let me check that in our fleet management system...",
            "One moment while I verify vehicle availability...",
            "Looking up those rental details right now...",
        ],
    },
    "luxury_transport": {
        "calendar": [
            "Checking chauffeur availability for your requested pickup time...",
            "Let me verify our executive vehicle schedule...",
        ],
        "catalog": [
            "Calculating your route and vehicle tier options right now...",
            "Checking our luxury fleet availability for you...",
        ],
        "booking": [
            "Reserving your chauffeur dispatch right now...",
            "Confirming vehicle availability with dispatch...",
        ],
        "general": [
            "Checking with our dispatch coordinator right now...",
            "One moment while I look into those transfer details...",
        ],
    },
    "hospitality": {
        "calendar": [
            "Checking table availability for your party size right now...",
            "One moment while I look at our dining reservation book...",
            "Let me check our seating chart for that time...",
        ],
        "catalog": [
            "Checking our seating arrangements and table capacity...",
            "Pulling up our dining options for you right now...",
        ],
        "booking": [
            "Reserving your table right now...",
            "Securing that dining reservation for you...",
        ],
        "general": [
            "Let me check our reservation system for you...",
            "One moment while I look into our table arrangements...",
        ],
    },
    "general": {
        "calendar": [
            "Checking our appointment schedule for you right now...",
            "One moment while I look at our available times...",
            "Let me check calendar availability right now...",
        ],
        "booking": [
            "Reserving that appointment time for you right now...",
            "Securing those details on our calendar...",
        ],
        "catalog": [
            "Pulling up that information for you right now...",
            "Checking our available options right now...",
        ],
        "records": [
            "Looking up those details in our system right now...",
            "One moment while I check our database...",
        ],
        "general": [
            "Let me look into that for you right now...",
            "One moment while I check on that...",
            "Pulling up those details for you...",
            "Just a second while I check that...",
            "Let me check our system right quick...",
        ],
    },
}


def normalize_niche(niche: Optional[str]) -> str:
    """Normalizes any vertical alias into its canonical key."""
    if not niche or not niche.strip():
        return "general"
    clean = niche.strip().lower().replace("-", "_")
    return NICHE_ALIASES.get(clean, clean)


def classify_tool_intent(tool_name: str) -> str:
    """Classifies tool name into high-level intent category."""
    name = (tool_name or "").lower()
    if any(k in name for k in ("calendar", "availability", "slot", "schedule", "appointment")):
        return "calendar"
    if any(k in name for k in ("book", "reserve", "confirm")):
        return "booking"
    if any(k in name for k in ("fleet", "car", "rental", "vehicle", "quote", "rate", "listing", "property", "table", "inventory")):
        return "catalog"
    if any(k in name for k in ("conflict", "record", "doctor", "lawyer", "intake", "client", "case")):
        return "records"
    return "general"


class HybridRouter:
    """
    Dual-Stage Ultra-Fast Router & Acoustic Filler Engine.
    Coordinates sub-100ms LLM filler generation with an instant deterministic bank.
    """

    def __init__(self, cooldown_seconds: float = 3.5):
        self.cooldown_seconds = cooldown_seconds
        # Session state: call_id -> dict with last_filler_time and recent_fillers
        self._session_state: Dict[str, Dict[str, Any]] = {}

    def _get_session_info(self, call_id: str) -> Dict[str, Any]:
        if call_id not in self._session_state:
            self._session_state[call_id] = {
                "last_spoken_time": 0.0,
                "history": [],
            }
        return self._session_state[call_id]

    def should_speak_filler(self, call_id: str) -> bool:
        """Determines if enough time has elapsed since the last filler."""
        if not call_id:
            return True
        info = self._get_session_info(call_id)
        now = time.monotonic()
        elapsed = now - info["last_spoken_time"]
        return elapsed >= self.cooldown_seconds

    def record_filler_spoken(self, call_id: str, filler_text: str):
        """Records a filler as spoken to prevent duplicate repetition."""
        if not call_id:
            return
        info = self._get_session_info(call_id)
        info["last_spoken_time"] = time.monotonic()
        info["history"].append(filler_text)
        # Keep last 5
        if len(info["history"]) > 5:
            info["history"] = info["history"][-5:]

    def get_instant_deterministic_filler(
        self,
        tool_name: str,
        niche: Optional[str] = None,
        call_id: Optional[str] = None,
    ) -> str:
        """
        Instant (<1ms) fallback filler selected from the curated bank,
        avoiding recently spoken phrases in the active call.
        """
        norm_n = normalize_niche(niche)
        intent = classify_tool_intent(tool_name)

        niche_bank = ACOUSTIC_FILLER_BANKS.get(norm_n, ACOUSTIC_FILLER_BANKS["general"])
        candidates = niche_bank.get(intent) or niche_bank.get("general") or ACOUSTIC_FILLER_BANKS["general"]["general"]

        # Filter out recent phrases from this session if possible
        recent = self._get_session_info(call_id)["history"] if call_id else []
        fresh_candidates = [c for c in candidates if c not in recent]
        selected = random.choice(fresh_candidates if fresh_candidates else candidates)

        if call_id:
            self.record_filler_spoken(call_id, selected)
        return selected

    async def generate_fast_llm_filler(
        self,
        tool_name: str,
        niche: Optional[str] = None,
        caller_input: Optional[str] = None,
        timeout_seconds: float = 0.12,
    ) -> Optional[str]:
        """
        Queries Groq, Cerebras, or OpenRouter for an ultra-fast dynamic filler.
        Enforces a strict timeout (default 120ms). Returns None if timeout or error.
        """
        # 1. Groq ultra-low latency gateway
        if settings.groq_api_key:
            try:
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {settings.groq_api_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "You are an ultra-fast voice receptionist. Output ONE natural acoustic filler phrase "
                                "(maximum 6-8 words) acknowledging you are checking the requested tool right now. "
                                "Never say hello, never ask questions, never output quotes. End with an ellipsis."
                            ),
                        },
                        {
                            "role": "user",
                            "content": f"Action: {tool_name} | Vertical: {niche or 'general'} | Context: {caller_input or 'caller inquiry'}",
                        },
                    ],
                    "temperature": 0.3,
                    "max_tokens": 15,
                }
                async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                    resp = await client.post(url, headers=headers, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        content = data["choices"][0]["message"]["content"].strip().strip('"\'')
                        if content and len(content) < 90:
                            return content
            except Exception as e:
                logger.debug(f"Groq fast filler skipped/timed out: {e}")

        # 2. Cerebras ultra-fast gateway
        if settings.cerebras_api_key:
            try:
                url = "https://api.cerebras.ai/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {settings.cerebras_api_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": "llama3.1-8b",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Output ONE verbal filler bridge (under 8 words) acknowledging tool lookup. End with '...'",
                        },
                        {
                            "role": "user",
                            "content": f"Tool: {tool_name}, Niche: {niche or 'general'}",
                        },
                    ],
                    "temperature": 0.2,
                    "max_tokens": 15,
                }
                async with httpx.AsyncClient(timeout=timeout_seconds) as client:
                    resp = await client.post(url, headers=headers, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        content = data["choices"][0]["message"]["content"].strip().strip('"\'')
                        if content and len(content) < 90:
                            return content
            except Exception as e:
                logger.debug(f"Cerebras fast filler skipped/timed out: {e}")

        return None

    async def get_filler(
        self,
        tool_name: str,
        niche: Optional[str] = None,
        call_id: Optional[str] = None,
        caller_input: Optional[str] = None,
        timeout_seconds: float = 0.12,
    ) -> Dict[str, Any]:
        """
        Coordinates dual-stage routing: attempts fast LLM generator (<120ms budget),
        falling back seamlessly to instant deterministic bank (<1ms).
        Returns dictionary containing phrase, source, and latency.
        """
        start_t = time.perf_counter()

        # Cooldown guard: if called too frequently, return empty phrase
        if call_id and not self.should_speak_filler(call_id):
            return {
                "phrase": "",
                "source": "cooldown_skipped",
                "latency_ms": 0,
                "spoken": False,
            }

        # Stage 1: Attempt ultra-fast LLM if keys configured
        if settings.groq_api_key or settings.cerebras_api_key:
            try:
                fast_phrase = await self.generate_fast_llm_filler(
                    tool_name=tool_name,
                    niche=niche,
                    caller_input=caller_input,
                    timeout_seconds=timeout_seconds,
                )
                if fast_phrase:
                    latency = round((time.perf_counter() - start_t) * 1000, 1)
                    if call_id:
                        self.record_filler_spoken(call_id, fast_phrase)
                    return {
                        "phrase": fast_phrase,
                        "source": "fast_llm",
                        "latency_ms": latency,
                        "spoken": True,
                    }
            except Exception as e:
                logger.debug(f"Stage 1 fast LLM error: {e}")

        # Stage 2: Instant deterministic fallback (<1ms)
        fallback_phrase = self.get_instant_deterministic_filler(
            tool_name=tool_name,
            niche=niche,
            call_id=call_id,
        )
        latency = round((time.perf_counter() - start_t) * 1000, 1)
        return {
            "phrase": fallback_phrase,
            "source": "deterministic_bank",
            "latency_ms": latency,
            "spoken": True,
        }
