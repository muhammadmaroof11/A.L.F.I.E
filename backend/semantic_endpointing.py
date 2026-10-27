"""
Semantic Turn Endpointing & Anti-Interruption Intelligence Engine.

Dynamically inspects caller speech transcripts to determine whether a pause is a mid-sentence
hesitation (stretching VAD silence duration to prevent interruptions) or a conclusive statement
(shortening VAD silence duration for snappy responses).
"""

from dataclasses import dataclass
import re
from typing import Dict, List, Optional, Set


@dataclass
class EndpointDecision:
    """Represents an endpointing decision for a speech segment."""
    is_incomplete: bool
    is_conclusive: bool
    silence_threshold_seconds: float
    reason: str
    matched_token: Optional[str] = None
    confidence: float = 1.0


# Configurable Pacing Presets
PACING_PRESETS: Dict[str, Dict[str, float]] = {
    "natural": {
        "base_silence": 0.55,
        "extended_silence": 1.25,
        "quick_silence": 0.38,
    },
    "patient": {
        "base_silence": 0.75,
        "extended_silence": 1.75,
        "quick_silence": 0.48,
    },
    "fast": {
        "base_silence": 0.38,
        "extended_silence": 0.85,
        "quick_silence": 0.28,
    },
}

# Hesitation & filler vocabulary
HESITATION_WORDS: Set[str] = {
    "um", "uh", "er", "ah", "hmm", "hm", "like", "well", "eh", "erm",
    "wait", "hold", "yeah", "okay",
}

HESITATION_PHRASES: List[str] = [
    "you know", "let me see", "hold on", "one second", "give me a second",
    "what is it", "i mean", "how do you say", "let's see", "wait a minute",
]

# Trailing conjunctions indicating continuation
TRAILING_CONJUNCTIONS: Set[str] = {
    "and", "or", "but", "so", "because", "although", "though", "if", "when",
    "while", "since", "unless", "whereas", "plus", "nor", "either",
}

# Trailing relative pronouns & subordinators
TRAILING_SUBORDINATORS: Set[str] = {
    "which", "that", "who", "whom", "whose", "where", "why", "how", "whether",
    "what",
}

# Trailing prepositions requiring an object
TRAILING_PREPOSITIONS: Set[str] = {
    "to", "with", "for", "about", "at", "in", "on", "of", "from", "by",
    "into", "onto", "under", "over", "between", "through", "as", "after",
    "before", "during", "without",
}

# Conclusive short phrases
CONCLUSIVE_PHRASES: Set[str] = {
    "yes", "yeah", "yep", "yup", "sure", "no", "nope", "nah", "correct",
    "right", "exactly", "that's it", "that is all", "that's all", "thank you",
    "thanks", "perfect", "goodbye", "bye", "all set", "nothing else",
    "sounds good", "done", "got it", "understood", "okay bye", "have a good day",
}

# Regex for trailing number / digits
TRAILING_DIGIT_PATTERN = re.compile(
    r"\b(zero|one|two|three|four|five|six|seven|eight|nine|ten|first|second|third|\d+)\s*$",
    re.IGNORECASE,
)


class SemanticEndpointAnalyzer:
    """Analyzes real-time transcript deltas to dynamically adjust VAD silence thresholds."""

    def __init__(self, preset: str = "natural", custom_pacing: Optional[Dict[str, float]] = None):
        preset_clean = (preset or "natural").lower().strip()
        if preset_clean not in PACING_PRESETS:
            preset_clean = "natural"
        
        self.preset_name = preset_clean
        base_pacing = PACING_PRESETS[preset_clean].copy()
        if custom_pacing:
            base_pacing.update(custom_pacing)
        
        self.base_silence = float(base_pacing.get("base_silence", 0.55))
        self.extended_silence = float(base_pacing.get("extended_silence", 1.25))
        self.quick_silence = float(base_pacing.get("quick_silence", 0.38))

    def analyze_text(self, text: str) -> EndpointDecision:
        """Evaluates speech text and determines adaptive silence duration."""
        if not text or not text.strip():
            return EndpointDecision(
                is_incomplete=False,
                is_conclusive=False,
                silence_threshold_seconds=self.base_silence,
                reason="empty_input",
                confidence=0.5,
            )

        raw = text.strip()
        clean = raw.lower()

        # 1. Check for Question Mark Terminal Turn
        if raw.endswith("?"):
            return EndpointDecision(
                is_incomplete=False,
                is_conclusive=True,
                silence_threshold_seconds=self.quick_silence,
                reason="terminal_question",
                matched_token="?",
                confidence=0.95,
            )

        # 2. Check for Explicit Conclusive Short Answers
        stripped_clean = re.sub(r"[^\w\s']", "", clean).strip()
        if stripped_clean in CONCLUSIVE_PHRASES:
            return EndpointDecision(
                is_incomplete=False,
                is_conclusive=True,
                silence_threshold_seconds=self.quick_silence,
                reason="conclusive_short_answer",
                matched_token=stripped_clean,
                confidence=0.98,
            )

        # 3. Check for Hesitation Phrases at End of Utterance
        for phrase in HESITATION_PHRASES:
            if clean.endswith(phrase) or stripped_clean.endswith(phrase):
                return EndpointDecision(
                    is_incomplete=True,
                    is_conclusive=False,
                    silence_threshold_seconds=self.extended_silence,
                    reason="hesitation_phrase",
                    matched_token=phrase,
                    confidence=0.92,
                )

        # Tokenize words for trailing word analysis
        words = re.findall(r"[\w']+", clean)
        if not words:
            return EndpointDecision(
                is_incomplete=False,
                is_conclusive=False,
                silence_threshold_seconds=self.base_silence,
                reason="no_tokens",
                confidence=0.5,
            )

        last_word = words[-1]

        # 4. Check for Hesitation Words
        if last_word in HESITATION_WORDS:
            return EndpointDecision(
                is_incomplete=True,
                is_conclusive=False,
                silence_threshold_seconds=self.extended_silence,
                reason="hesitation_word",
                matched_token=last_word,
                confidence=0.90,
            )

        # 5. Check for Trailing Conjunctions
        if last_word in TRAILING_CONJUNCTIONS:
            return EndpointDecision(
                is_incomplete=True,
                is_conclusive=False,
                silence_threshold_seconds=self.extended_silence,
                reason="trailing_conjunction",
                matched_token=last_word,
                confidence=0.95,
            )

        # 6. Check for Trailing Subordinators / Relative Pronouns
        if last_word in TRAILING_SUBORDINATORS:
            return EndpointDecision(
                is_incomplete=True,
                is_conclusive=False,
                silence_threshold_seconds=self.extended_silence,
                reason="trailing_subordinator",
                matched_token=last_word,
                confidence=0.90,
            )

        # 7. Check for Trailing Prepositions
        if last_word in TRAILING_PREPOSITIONS:
            return EndpointDecision(
                is_incomplete=True,
                is_conclusive=False,
                silence_threshold_seconds=self.extended_silence,
                reason="trailing_preposition",
                matched_token=last_word,
                confidence=0.88,
            )

        # 8. Check for Trailing Incomplete Digit / Number Strings
        if TRAILING_DIGIT_PATTERN.search(clean) and not (raw.endswith(".") or raw.endswith("!")):
            return EndpointDecision(
                is_incomplete=True,
                is_conclusive=False,
                silence_threshold_seconds=self.extended_silence,
                reason="trailing_number_sequence",
                matched_token=last_word,
                confidence=0.85,
            )

        # 9. Terminal Punctuation (. or !) with complete thought
        if raw.endswith(".") or raw.endswith("!"):
            return EndpointDecision(
                is_incomplete=False,
                is_conclusive=True,
                silence_threshold_seconds=self.quick_silence,
                reason="terminal_punctuation",
                matched_token=raw[-1],
                confidence=0.85,
            )

        # 10. Default Natural Cadence
        return EndpointDecision(
            is_incomplete=False,
            is_conclusive=False,
            silence_threshold_seconds=self.base_silence,
            reason="standard_clause",
            confidence=0.70,
        )
