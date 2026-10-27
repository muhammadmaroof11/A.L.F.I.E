"""
A.L.F.I.E — RFC 4733 DTMF Telephony Utilities & Keypad Buffer
Provides standards-compliant tone code mappings, sequence validation,
timed tone dispatching for LiveKit SIP, and debounced keypad accumulation.
"""

import asyncio
import logging
import re
from typing import Dict, List, Optional, Tuple, Callable, Any

logger = logging.getLogger("alfie.dtmf")

# RFC 4733 standard DTMF event codes (0-15)
# 0-9: 0-9, *: 10, #: 11, A: 12, B: 13, C: 14, D: 15
DTMF_CHAR_TO_CODE: Dict[str, int] = {
    "0": 0, "1": 1, "2": 2, "3": 3, "4": 4,
    "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
    "*": 10,
    "#": 11,
    "A": 12, "B": 13, "C": 14, "D": 15,
    "a": 12, "b": 13, "c": 14, "d": 15,
}

DTMF_CODE_TO_CHAR: Dict[int, str] = {
    0: "0", 1: "1", 2: "2", 3: "3", 4: "4",
    5: "5", 6: "6", 7: "7", 8: "8", 9: "9",
    10: "*",
    11: "#",
    12: "A", 13: "B", 14: "C", 15: "D",
}

# Standard dual frequencies (Hz) for DTMF audio synthesis (Row x Column)
DTMF_FREQUENCIES: Dict[str, Tuple[int, int]] = {
    "1": (697, 1209), "2": (697, 1336), "3": (697, 1477), "A": (697, 1633),
    "4": (770, 1209), "5": (770, 1336), "6": (770, 1477), "B": (770, 1633),
    "7": (852, 1209), "8": (852, 1336), "9": (852, 1477), "C": (852, 1633),
    "*": (941, 1209), "0": (941, 1336), "#": (941, 1477), "D": (941, 1633),
}

# Validation pattern: allows 0-9, *, #, A-D, and commas ',' for pauses
DTMF_SEQUENCE_REGEX = re.compile(r"^[0-9*#A-Da-d,]+$")


def validate_dtmf_sequence(sequence: str) -> bool:
    """Validate if a string contains only valid DTMF characters or pause commas."""
    if not sequence or not isinstance(sequence, str):
        return False
    return bool(DTMF_SEQUENCE_REGEX.match(sequence.strip()))


def get_dtmf_code(digit: str) -> Optional[int]:
    """Return the RFC 4733 integer code for a DTMF digit character."""
    return DTMF_CHAR_TO_CODE.get(digit)


def get_dtmf_digit(code: int) -> Optional[str]:
    """Return the character representation of an RFC 4733 code."""
    return DTMF_CODE_TO_CHAR.get(code)


async def dispatch_dtmf_sequence(
    room: Any,
    sequence: str,
    inter_digit_delay_ms: int = 250,
    pause_comma_delay_ms: int = 500,
    on_digit_sent: Optional[Callable[[str, int], None]] = None,
) -> int:
    """
    Transmit a sequence of DTMF digits through a LiveKit Room's local_participant.
    Supports comma ',' for pauses (default 500ms).

    Returns:
        Number of tones successfully transmitted.
    """
    if not validate_dtmf_sequence(sequence):
        raise ValueError(f"Invalid DTMF sequence: '{sequence}'")

    local_participant = getattr(room, "local_participant", None)
    tones_sent = 0

    for char in sequence.strip():
        if char == ",":
            await asyncio.sleep(pause_comma_delay_ms / 1000.0)
            continue

        normalized_char = char.upper()
        code = DTMF_CHAR_TO_CODE.get(normalized_char)
        if code is None:
            continue

        if local_participant and hasattr(local_participant, "publish_dtmf"):
            try:
                await local_participant.publish_dtmf(code=code, digit=normalized_char)
            except Exception as err:
                logger.warning(f"publish_dtmf error on tone '{normalized_char}': {err}")

        tones_sent += 1
        if on_digit_sent:
            try:
                res = on_digit_sent(normalized_char, code)
                if asyncio.iscoroutine(res):
                    await res
            except Exception as e:
                logger.warning(f"on_digit_sent callback error: {e}")

        # Inter-digit spacing so receiving PBX/IVR registers discrete digits
        await asyncio.sleep(inter_digit_delay_ms / 1000.0)

    return tones_sent


class DTMFKeypadBuffer:
    """
    Debounced accumulator for inbound caller DTMF keypad entries.
    Gathers sequences (e.g. entering account numbers, PINs, or menu options)
    and invokes a callback once typing pauses (debounce) or '#' (submit) is pressed.
    """

    def __init__(
        self,
        on_sequence_completed: Callable[[str], Any],
        debounce_seconds: float = 1.2,
        max_digits: int = 16,
    ):
        self.on_sequence_completed = on_sequence_completed
        self.debounce_seconds = debounce_seconds
        self.max_digits = max_digits
        self._buffer: List[str] = []
        self._timer_task: Optional[asyncio.Task] = None

    def add_digit(self, digit: str) -> Optional[asyncio.Task]:
        """Add an incoming DTMF digit to the buffer and restart the debounce timer."""
        norm = digit.strip().upper()
        if norm not in DTMF_CHAR_TO_CODE:
            return None

        # Cancel existing debounce timer
        if self._timer_task and not self._timer_task.done():
            self._timer_task.cancel()

        self._buffer.append(norm)

        # If '#' (pound) is pressed, submit immediately as it's the standard telephony submit key
        if norm == "#" or len(self._buffer) >= self.max_digits:
            self._flush()
            return None

        # Schedule debounce timer
        self._timer_task = asyncio.create_task(self._wait_and_flush())
        return self._timer_task

    async def _wait_and_flush(self):
        try:
            await asyncio.sleep(self.debounce_seconds)
            self._flush()
        except asyncio.CancelledError:
            pass

    def _flush(self):
        if not self._buffer:
            return
        sequence = "".join(self._buffer)
        self._buffer.clear()
        if self._timer_task and not self._timer_task.done():
            self._timer_task.cancel()
        self._timer_task = None

        try:
            res = self.on_sequence_completed(sequence)
            if asyncio.iscoroutine(res):
                asyncio.create_task(res)
        except Exception as e:
            logger.warning(f"Error executing DTMF sequence completion callback: {e}")

    def clear(self):
        self._buffer.clear()
        if self._timer_task and not self._timer_task.done():
            self._timer_task.cancel()
        self._timer_task = None

    @property
    def current_sequence(self) -> str:
        return "".join(self._buffer)
