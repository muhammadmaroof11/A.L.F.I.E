"""
A.L.F.I.E Enterprise Anti-Hallucination & Grounding Guardrails Engine.
Enforces deterministic factual bounds, intercepts phantom tool confirmations,
prevents unauthorized discount/pricing commitments, and verifies PII consistency
across both Cascaded and Native S2S pipelines.
"""

from dataclasses import dataclass, field
import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from .safety_filter import ZeroLiabilityFilter

logger = logging.getLogger("alfie.guardrails.hallucination")


@dataclass
class GuardrailViolation:
    violation_type: str
    risk_level: str  # "low", "medium", "high", "critical"
    matched_phrase: str
    explanation: str
    remedy_action: str


class AntiHallucinationEngine:
    """
    Multi-layer pre-TTS and pre-response guardrail filter.
    Intercepts:
    1. Phantom Action Confirmations (claiming an appointment is booked without valid tool outcome)
    2. Unauthorized Financial Commitments (discount fabrication, free service promises, payout guarantees)
    3. Regulatory & Liability Violations (via ZeroLiabilityFilter)
    4. Distorted PII & Phone Number Hallucinations
    """

    # Phrases indicating the agent claims an action was finalized
    PHANTOM_ACTION_PATTERNS = [
        re.compile(r"\b(?:i(?:'ve| have|ve)\s+(?:officially\s+|already\s+|successfully\s+|just\s+)?(?:booked|confirmed|scheduled|reserved|dispatched|processed|sent)\s+(?:your|the)\b)", re.IGNORECASE),
        re.compile(r"\b(?:your\s+(?:booking|appointment|reservation|ride|order|payment|showing)\s+(?:is|has been)\s+(?:confirmed|booked|scheduled|completed|dispatched|locked in))\b", re.IGNORECASE),
        re.compile(r"\b(?:you(?:'re| are)\s+(?:all\s+)?(?:set|booked|confirmed|scheduled)\s+for\b)", re.IGNORECASE),
        re.compile(r"\b(?:i\s+(?:went ahead and\s+|just\s+)?(?:booked|reserved|scheduled)\s+(?:that|it|you)\b)", re.IGNORECASE),
    ]

    # Phrases indicating unauthorized discounts or price slashing
    UNAUTHORIZED_FINANCIAL_PATTERNS = [
        re.compile(r"\b(?:i(?:'ll| will| can)?\s+give you\s+(?:\d+%\s+off|a\s+discount|it\s+(?:for\s+)?free|a\s+special\s+deal))\b", re.IGNORECASE),
        re.compile(r"\b(?:we\s+can\s+do\s+(?:it\s+)?(?:for\s+)?free|no\s+charge\s+at\s+all\s+for\s+you|zero\s+dollars)\b", re.IGNORECASE),
        re.compile(r"\b(?:i\s+can\s+cut\s+the\s+price|i\s+can\s+lower\s+the\s+(?:rate|fee|price)\s+to)\b", re.IGNORECASE),
        re.compile(r"\b(?:promise|guarantee)\s+(?:you\s+a\s+)?(?:settlement|payout)\s+of\s+[\$\d,kKmM]+\b", re.IGNORECASE),
    ]

    # Standard graceful deflections for ungrounded knowledge queries
    UNGROUNDED_DEFLECTION = (
        "I don't have that specific detail in our verified records, "
        "but I have made a note for our team to confirm that with you directly."
    )

    def __init__(self, tenant_id: Optional[str] = None, strict_mode: bool = True):
        self.tenant_id = tenant_id or "default"
        self.strict_mode = strict_mode
        self.safety_filter = ZeroLiabilityFilter()

    def check_phantom_actions(
        self,
        text: str,
        tool_executed: Optional[str] = None,
        tool_result: Optional[Dict[str, Any]] = None,
    ) -> List[GuardrailViolation]:
        """
        Detects if the assistant claims an action was finalized when either:
        1. No tool was executed during this step/turn.
        2. The executed tool returned an error or non-success status.
        """
        if not text:
            return []

        has_valid_tool_success = False
        if tool_result is not None:
            status = str(tool_result.get("status", "")).lower()
            error = tool_result.get("error")
            has_valid_tool_success = (status in ("success", "confirmed", "ok") or bool(tool_result.get("booking_id") or tool_result.get("id"))) and not error

        violations = []
        for pattern in self.PHANTOM_ACTION_PATTERNS:
            match = pattern.search(text)
            if match and not has_valid_tool_success:
                violations.append(
                    GuardrailViolation(
                        violation_type="phantom_action_confirmation",
                        risk_level="critical",
                        matched_phrase=match.group(0),
                        explanation=(
                            f"Assistant claimed action completion ('{match.group(0)}') "
                            f"without a verified tool success result (tool_executed={tool_executed}, tool_result={tool_result})."
                        ),
                        remedy_action="rewrite_to_pending_verification",
                    )
                )
        return violations

    def check_unauthorized_financials(self, text: str, niche: str = "general") -> List[GuardrailViolation]:
        """
        Detects unauthorized discounts, fabricated pricing, or illegal settlement promises.
        """
        if not text:
            return []

        violations = []
        for pattern in self.UNAUTHORIZED_FINANCIAL_PATTERNS:
            match = pattern.search(text)
            if match:
                violations.append(
                    GuardrailViolation(
                        violation_type="unauthorized_financial_commitment",
                        risk_level="high",
                        matched_phrase=match.group(0),
                        explanation=f"Assistant offered unauthorized discount or monetary guarantee: '{match.group(0)}'.",
                        remedy_action="scrub_financial_promise",
                    )
                )
        return violations

    def verify_pii_consistency(
        self,
        text: str,
        active_slots: Optional[Dict[str, Any]] = None,
    ) -> List[GuardrailViolation]:
        """
        Checks if the assistant hallucinated random phone digits that do not match
        what the caller actually provided in the slot memory.
        """
        if not text or not active_slots:
            return []

        stored_phone = active_slots.get("caller_phone") or active_slots.get("phone")
        if not stored_phone:
            return []

        # Extract digits from stored phone
        stored_digits = re.sub(r"\D", "", str(stored_phone))
        if len(stored_digits) < 7:
            return []

        # Find phone numbers spoken in assistant text (e.g. 555-123-4567 or (555) 123-4567)
        spoken_phone_matches = re.findall(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
        violations = []
        for spoken_phone in spoken_phone_matches:
            spoken_digits = re.sub(r"\D", "", spoken_phone)
            # If spoken phone has 10 digits and doesn't match stored phone digits
            if len(spoken_digits) >= 10 and spoken_digits[-10:] != stored_digits[-10:]:
                violations.append(
                    GuardrailViolation(
                        violation_type="pii_digit_mutation",
                        risk_level="high",
                        matched_phrase=spoken_phone,
                        explanation=f"Assistant hallucinated incorrect phone digits '{spoken_phone}' differing from verified caller phone '{stored_phone}'.",
                        remedy_action="substitute_verified_phone",
                    )
                )
        return violations

    def sanitize_turn(
        self,
        assistant_text: str,
        tool_executed: Optional[str] = None,
        tool_result: Optional[Dict[str, Any]] = None,
        niche: str = "general",
        knowledge_context: str = "",
        active_slots: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, bool, List[str]]:
        """
        Master sanitization pipeline executing across all safety layers in sub-5ms.
        Returns: (sanitized_text, was_intercepted, list_of_violation_summaries)
        """
        if not assistant_text:
            return "", False, []

        sanitized = assistant_text
        intercepted = False
        all_violations: List[str] = []

        # Layer 1: Zero-Liability & Regulatory Compliance Filter (Scrubbing legal/medical liability)
        sanitized, mod_safety, safety_risks = self.safety_filter.scrub_text(sanitized, niche=niche)
        if mod_safety:
            intercepted = True
            all_violations.extend([f"regulatory_liability: {r}" for r in safety_risks])

        # Layer 2: Phantom Action Interception
        phantom_violations = self.check_phantom_actions(
            text=sanitized,
            tool_executed=tool_executed,
            tool_result=tool_result,
        )
        if phantom_violations:
            intercepted = True
            for v in phantom_violations:
                all_violations.append(f"{v.violation_type}: {v.matched_phrase}")
                # Remedy: Replace false confirmation with transparent status
                if tool_result and (tool_result.get("error") or str(tool_result.get("status")).lower() == "failed"):
                    sanitized = re.sub(
                        v.matched_phrase,
                        "I am noting your request and our team will confirm the final booking details with you shortly",
                        sanitized,
                        flags=re.IGNORECASE,
                    )
                else:
                    sanitized = re.sub(
                        v.matched_phrase,
                        "I am noting your request for our team to confirm",
                        sanitized,
                        flags=re.IGNORECASE,
                    )

        # Layer 3: Unauthorized Financial & Discount Guard
        financial_violations = self.check_unauthorized_financials(sanitized, niche=niche)
        if financial_violations:
            intercepted = True
            for v in financial_violations:
                all_violations.append(f"{v.violation_type}: {v.matched_phrase}")
                sanitized = re.sub(
                    v.matched_phrase,
                    "our standard pricing applies and our coordinator can discuss available options with you",
                    sanitized,
                    flags=re.IGNORECASE,
                )

        # Layer 4: PII Consistency & Phone Number Hallucination Guard
        pii_violations = self.verify_pii_consistency(sanitized, active_slots=active_slots)
        if pii_violations:
            intercepted = True
            stored_phone = (active_slots or {}).get("caller_phone") or (active_slots or {}).get("phone", "")
            for v in pii_violations:
                all_violations.append(f"{v.violation_type}: {v.matched_phrase}")
                if stored_phone:
                    sanitized = sanitized.replace(v.matched_phrase, str(stored_phone))

        if intercepted:
            logger.warning(
                f"[ANTI-HALLUCINATION INTERCEPT] Tenant: {self.tenant_id} | Violations: {all_violations}"
            )

        return sanitized, intercepted, all_violations
