"""
Real-Time Caller Frustration Radar & Sentiment Drift Engine.

Analyzes caller speech turns in real-time to detect rising frustration, hostility,
demands for human supervisors, and rapid interruption spikes, allowing supervisors
to intervene before a high-value client drops off.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Any, Dict, List, Set


# Keyword catalogs for frustration detection
HUMAN_HANDOFF_PHRASES: Set[str] = {
    "talk to a human", "speak to a human", "talk to a person", "speak to a person",
    "real person", "real human", "actual person", "representative", "operator",
    "supervisor", "manager", "get me a person", "let me speak with someone",
    "let me speak to someone", "let me speak to a person", "let me speak to a human",
    "transfer me to someone", "transfer me to a person", "give me a human", "give me an agent",
    "let me speak to your boss", "human agent", "live agent", "someone in charge",
    "human being", "talk to someone", "speak with someone", "person please",
}

HOSTILITY_PHRASES: Set[str] = {
    "this is ridiculous", "ridiculous", "waste of time", "wasting my time",
    "terrible", "horrible", "useless", "stop repeating", "stop talking",
    "shut up", "stupid bot", "stupid machine", "listen to me", "let me finish",
    "stop interrupting", "i'm furious", "im furious", "unacceptable",
    "you're not helping", "you are not helping", "are you deaf", "i already told you",
    "you don't understand", "you dont understand", "this is frustrating",
    "stop playing games", "incompetent", "garbage", "pathetic",
}

THREAT_OR_CANCEL_PHRASES: Set[str] = {
    "lawsuit", "lawyer", "attorney", "sue you", "report you", "better business bureau",
    "bbb", "cancel my appointment", "cancel my account", "cancel my service",
    "cancel my subscription", "cancel everything", "cancel my order", "refund",
    "full refund", "chargeback", "dispute", "calling the police", "press charges",
}

FRUSTRATED_INTERJECTIONS: Set[str] = {
    "ugh", "argh", "jesus", "goddammit", "dammit", "hell no", "what the hell",
    "oh my god", "seriously", "come on", "c'mon", "unbelievable",
    "are you kidding me", "for god's sake", "for christ's sake", "give me a break",
    "what the heck",
}


@dataclass
class FrustrationTurnResult:
    """Evaluation result for a single caller turn."""
    score: float
    level: str  # "LOW", "ELEVATED", "CRITICAL"
    is_escalation: bool
    reason: str
    matched_triggers: List[str]
    consecutive_negative_turns: int
    rolling_score: float


class FrustrationSessionTracker:
    """Tracks caller frustration progression across an active phone conversation."""

    def __init__(
        self,
        critical_threshold: float = 0.70,
        elevated_threshold: float = 0.40,
        decay_factor: float = 0.70,
    ):
        self.critical_threshold = critical_threshold
        self.elevated_threshold = elevated_threshold
        self.decay_factor = decay_factor
        self.rolling_score = 0.0
        self.peak_score = 0.0
        self.consecutive_negative_turns = 0
        self.interruption_timestamps: List[float] = []
        self.events: List[Dict[str, Any]] = []
        self.turn_history: List[Dict[str, Any]] = []

    @property
    def interruption_count(self) -> int:
        return len(self.interruption_timestamps)

    def record_interruption(self, offset_seconds: float = 0.0):
        """Records an overlapping speech / barge-in timestamp."""
        self.interruption_timestamps.append(offset_seconds)

    def _recent_interruption_count(self, current_offset: float, window_seconds: float = 15.0) -> int:
        """Counts how many interruptions occurred within the recent time window."""
        cutoff = max(0.0, current_offset - window_seconds)
        return sum(1 for t in self.interruption_timestamps if t >= cutoff)

    def process_turn(
        self,
        text: str,
        offset_ms: int = 0,
        turn_id: str = "turn_1",
    ) -> FrustrationTurnResult:
        """
        Evaluates a caller speech turn and updates session frustration dynamics.
        """
        raw = (text or "").strip()
        clean = raw.lower()
        matched: List[str] = []
        primary_reason = "Normal conversation"
        turn_boost = 0.0

        if not raw:
            return FrustrationTurnResult(
                score=0.0,
                level="LOW",
                is_escalation=False,
                reason="Empty speech turn",
                matched_triggers=[],
                consecutive_negative_turns=self.consecutive_negative_turns,
                rolling_score=self.rolling_score,
            )

        # 1. Human Handoff Demands
        for phrase in HUMAN_HANDOFF_PHRASES:
            if phrase in clean:
                matched.append(f"handoff:{phrase}")
                turn_boost = max(turn_boost, 0.45)
                primary_reason = f"Caller demanded human agent: '{phrase}'"

        # 2. Hostility & Verbal Frustration
        for phrase in HOSTILITY_PHRASES:
            if phrase in clean:
                matched.append(f"hostility:{phrase}")
                turn_boost = max(turn_boost, 0.40)
                if "human agent" not in primary_reason:
                    primary_reason = f"Hostile language detected: '{phrase}'"

        # 3. Legal / Cancellation Threats
        for phrase in THREAT_OR_CANCEL_PHRASES:
            if phrase in clean:
                matched.append(f"threat:{phrase}")
                turn_boost = max(turn_boost, 0.45)
                if "human agent" not in primary_reason:
                    primary_reason = f"Threat or cancellation intent: '{phrase}'"

        # 4. Frustrated Interjections
        words = set(re.findall(r"[\w']+", clean))
        for interj in FRUSTRATED_INTERJECTIONS:
            if interj in words or interj in clean:
                matched.append(f"interjection:{interj}")
                turn_boost = max(turn_boost, 0.25)
                if "human agent" not in primary_reason and "Hostile" not in primary_reason:
                    primary_reason = f"Exasperation interjection: '{interj}'"

        # 5. ALL CAPS detection (indicates yelling in transcript)
        alpha_tokens = [w for w in raw.split() if w.isalpha() and len(w) > 2]
        all_caps_count = sum(1 for w in alpha_tokens if w.isupper())
        if alpha_tokens and (all_caps_count / len(alpha_tokens)) > 0.4:
            matched.append("formatting:all_caps")
            turn_boost += 0.20
            if "human agent" not in primary_reason:
                primary_reason = "Raised voice / shouting detected"

        # 6. Exclamation mark clusters
        if "!!" in raw or "!?" in raw or "?!" in raw:
            matched.append("formatting:multiple_exclamations")
            turn_boost += 0.15

        # 7. Interruption frequency spike (> 2 interruptions within 15s)
        current_offset_sec = offset_ms / 1000.0
        recent_interruptions = self._recent_interruption_count(current_offset_sec, window_seconds=15.0)
        if recent_interruptions >= 2:
            matched.append(f"telephony:interruption_spike({recent_interruptions})")
            turn_boost += 0.20

        # Calculate state progression
        if matched:
            self.consecutive_negative_turns += 1
            escalation_penalty = min(0.30, (self.consecutive_negative_turns - 1) * 0.15)
            self.rolling_score = min(1.0, self.rolling_score + turn_boost + escalation_penalty)
        else:
            # Natural satisfaction decay when caller speaks normally
            self.consecutive_negative_turns = 0
            self.rolling_score = max(0.0, round(self.rolling_score * self.decay_factor - 0.05, 2))

        self.peak_score = max(self.peak_score, self.rolling_score)

        # Categorize Level
        if self.rolling_score >= self.critical_threshold:
            level = "CRITICAL"
        elif self.rolling_score >= self.elevated_threshold:
            level = "ELEVATED"
        else:
            level = "LOW"

        is_escalation = level == "CRITICAL" or bool(turn_boost >= 0.40)

        # If escalation event, record in audit trail
        if is_escalation:
            event_record = {
                "event_id": f"frust_{len(self.events) + 1}",
                "turn_id": turn_id,
                "offset_ms": offset_ms,
                "score": round(self.rolling_score, 2),
                "level": level,
                "reason": primary_reason,
                "matched_triggers": matched,
                "snippet": raw[:140],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            self.events.append(event_record)

        self.turn_history.append({
            "turn_id": turn_id,
            "score": round(self.rolling_score, 2),
            "level": level,
            "reason": primary_reason,
        })

        return FrustrationTurnResult(
            score=round(self.rolling_score, 2),
            level=level,
            is_escalation=is_escalation,
            reason=primary_reason,
            matched_triggers=matched,
            consecutive_negative_turns=self.consecutive_negative_turns,
            rolling_score=round(self.rolling_score, 2),
        )

    def get_escalation_events(self) -> List[Dict[str, Any]]:
        """Returns the chronological audit trail of frustration escalation events."""
        return list(self.events)
