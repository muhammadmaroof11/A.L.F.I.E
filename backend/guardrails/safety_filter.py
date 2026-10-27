"""
Anti-Hallucination & Zero-Liability Safety Filter.
Intercepts and scrubs unauthorized guarantees, definitive medical diagnoses,
illegal drug recommendations, or financial ROI guarantees before TTS synthesis.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("alfie.guardrails.safety")


class ZeroLiabilityFilter:
    """
    Scans assistant-generated response text for dangerous legal, medical,
    and financial commitments that carry enterprise regulatory liability.
    Replaces violations with compliant, professional disclaimers.
    """

    # Disallowed patterns across regulated vertical categories
    PATTERNS: Dict[str, List[Dict[str, Any]]] = {
        "legal": [
            {
                "pattern": r"\b(?:we\s+guarantee|i\s+guarantee|guaranteed)\s+(?:a\s+)?(?:[\$\d,kKmM\w]+\s+)?(?:settlement|payout|compensation|outcome|victory|win)\b",
                "risk": "Unauthorized legal outcome or settlement guarantee",
                "replacement": "our attorneys will evaluate the merits and compensation potential of your case during your consultation",
            },
            {
                "pattern": r"\b(?:promise|guarantee)\s+(?:(?:that\s+)?(?:we|you|our\s+firm|our\s+team|i)\s+will)\s+(?:win|get\s+[\$\d,kKmM\w]+|secure\s+[\$\d,kKmM\w]+|receive\s+money)\b",
                "risk": "Case victory guarantee",
                "replacement": "our legal team will vigorously represent your interests to seek maximum recovery",
            },
            {
                "pattern": r"\b(?:you\s+(?:definitely|certainly)\s+have\s+a\s+case|you\s+will\s+definitely\s+win)\b",
                "risk": "Conclusive liability determination without attorney review",
                "replacement": "our licensed attorneys will review the specific facts to determine case viability",
            },
        ],
        "medical": [
            {
                "pattern": r"\b(?:i\s+diagnose\s+you\s+with|you\s+(?:definitely|certainly)\s+have\s+(?:cancer|covid|strep|pneumonia|diabetes|a\s+fracture))\b",
                "risk": "Unauthorized medical diagnosis",
                "replacement": "please consult directly with our licensed clinician for an accurate medical diagnosis",
            },
            {
                "pattern": r"\b(?:stop\s+taking\s+(?:your\s+)?(?:medication|prescriptions?|pills?|insulin))\b",
                "risk": "Dangerous medication cessation instruction",
                "replacement": "please consult directly with your prescribing physician before modifying any medications",
            },
            {
                "pattern": r"\b(?:take|prescribe)\s+\d+\s*(?:mg|milligrams|tablets|pills)\s+(?:of\s+)?\w+\b",
                "risk": "Unauthorized drug dosage recommendation",
                "replacement": "our physician will prescribe appropriate treatment options during your visit",
            },
            {
                "pattern": r"\b(?:guaranteed\s+(?:cure|healing|recovery)|we\s+guarantee\s+a\s+100%\s+cure)\b",
                "risk": "Medical cure guarantee",
                "replacement": "our clinical staff will discuss proven treatment protocols and expected outcomes with you",
            },
        ],
        "realestate": [
            {
                "pattern": r"\b(?:guaranteed\s+(?:return|profit|appreciation|roi)|risk-free\s+investment)\b",
                "risk": "Unauthorized investment or real estate return guarantee",
                "replacement": "market appreciation varies, and our advisors will provide comprehensive neighborhood historical data",
            },
            {
                "pattern": r"\b(?:you\s+are\s+guaranteed\s+to\s+(?:double|make\s+money))\b",
                "risk": "Financial profit promise",
                "replacement": "our brokers will help you evaluate potential property valuation trends",
            },
            {
                "pattern": r"\b(?:we\s+only\s+(?:rent|sell)\s+to\s+(?:certain|specific|families|couples))\b",
                "risk": "Potential Fair Housing Act steering violation",
                "replacement": "we provide equal housing opportunities for all qualified clients",
            },
        ],
        "general": [
            {
                "pattern": r"\b(?:i\s+guarantee\s+100%|we\s+guarantee\s+100%)\b",
                "risk": "Absolute blanket guarantee",
                "replacement": "we will make every reasonable effort to assist you",
            }
        ],
    }

    def __init__(self, tenant_id: Optional[str] = None):
        self.tenant_id = tenant_id or "default"

    @classmethod
    def check_violations(cls, text: str, niche: str = "general") -> List[Dict[str, Any]]:
        """
        Scans text and returns list of violation records if found.
        """
        if not text:
            return []

        clean_niche = (niche or "general").lower()
        active_categories = ["general"]
        for cat in cls.PATTERNS.keys():
            if cat in clean_niche and cat != "general":
                active_categories.append(cat)

        violations = []
        for cat in active_categories:
            for rule in cls.PATTERNS.get(cat, []):
                match = re.search(rule["pattern"], text, re.IGNORECASE)
                if match:
                    violations.append({
                        "category": cat,
                        "matched_text": match.group(0),
                        "risk": rule["risk"],
                        "suggested_replacement": rule["replacement"],
                    })

        return violations

    @classmethod
    def scrub_text(cls, text: str, niche: str = "general") -> Tuple[str, bool, List[str]]:
        """
        Detects violations and replaces them with compliant disclaimer phrasing.
        Returns: (scrubbed_text, was_modified, list_of_risks)
        """
        if not text:
            return text, False, []

        clean_niche = (niche or "general").lower()
        active_categories = ["general"]
        for cat in cls.PATTERNS.keys():
            if cat in clean_niche and cat != "general":
                active_categories.append(cat)

        scrubbed = text
        risks_found = []
        modified = False

        for cat in active_categories:
            for rule in cls.PATTERNS.get(cat, []):
                pattern = re.compile(rule["pattern"], re.IGNORECASE)
                if pattern.search(scrubbed):
                    modified = True
                    risks_found.append(rule["risk"])
                    scrubbed = pattern.sub(rule["replacement"], scrubbed)
                    logger.warning(
                        f"[SAFETY FILTER INTERCEPT] Category: {cat} | Risk: {rule['risk']} | Scrubbed hazardous text."
                    )

        return scrubbed, modified, risks_found
