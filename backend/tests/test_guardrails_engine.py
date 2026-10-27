"""
Unit & Integration Tests for Anti-Hallucination & Enterprise Guardrails Engine.
Verifies Phantom Action Interception, Unauthorized Financial Commitments,
PII Digit Verification, Zero-Liability Scrubbing, and REST Guardrail APIs.
"""

import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from guardrails.anti_hallucination import AntiHallucinationEngine, GuardrailViolation
from guardrails.safety_filter import ZeroLiabilityFilter


def asyncio_run(coro):
    return asyncio.run(coro)


class TestAntiHallucinationEngine(unittest.TestCase):
    """Verifies core anti-hallucination detection and sanitization rules."""

    def setUp(self):
        self.engine = AntiHallucinationEngine(tenant_id="test-tenant")

    def test_phantom_booking_interception_without_tool(self):
        """Assistant claims booking is confirmed, but no tool was executed."""
        text = "I've booked your appointment for tomorrow at 3 PM! See you then."
        violations = self.engine.check_phantom_actions(
            text=text,
            tool_executed=None,
            tool_result=None,
        )
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].violation_type, "phantom_action_confirmation")
        self.assertEqual(violations[0].risk_level, "critical")

        # Verify sanitize_turn rewrites the false confirmation
        sanitized, intercepted, all_violations = self.engine.sanitize_turn(
            assistant_text=text,
            tool_executed=None,
            tool_result=None,
        )
        self.assertTrue(intercepted)
        self.assertNotIn("I've booked your appointment", sanitized)
        self.assertIn("noting your request", sanitized)

    def test_phantom_booking_interception_with_failed_tool(self):
        """Assistant claims booking is confirmed, but tool returned failure."""
        text = "Your reservation is confirmed for a party of 4 at 7:30 PM."
        tool_result = {"status": "failed", "error": "Table not available"}
        violations = self.engine.check_phantom_actions(
            text=text,
            tool_executed="reserve_table",
            tool_result=tool_result,
        )
        self.assertEqual(len(violations), 1)

        sanitized, intercepted, all_violations = self.engine.sanitize_turn(
            assistant_text=text,
            tool_executed="reserve_table",
            tool_result=tool_result,
        )
        self.assertTrue(intercepted)
        self.assertNotIn("is confirmed", sanitized)
        self.assertIn("confirm the final booking details", sanitized)

    def test_legitimate_booking_allowed_when_tool_succeeds(self):
        """Assistant claims booking is confirmed, and tool indeed succeeded."""
        text = "Your booking is confirmed! Your confirmation number is BK-12345."
        tool_result = {"status": "success", "booking_id": "BK-12345"}
        violations = self.engine.check_phantom_actions(
            text=text,
            tool_executed="book_ride",
            tool_result=tool_result,
        )
        self.assertEqual(len(violations), 0)

        sanitized, intercepted, all_violations = self.engine.sanitize_turn(
            assistant_text=text,
            tool_executed="book_ride",
            tool_result=tool_result,
        )
        self.assertFalse(intercepted)
        self.assertEqual(sanitized, text)

    def test_unauthorized_discount_and_price_slashing_intercepted(self):
        """Assistant promises unauthorized discount or free service."""
        text1 = "If you sign up right now, I'll give you 50% off your first month."
        text2 = "We can do it for free as a special courtesy for you."

        v1 = self.engine.check_unauthorized_financials(text1)
        self.assertEqual(len(v1), 1)
        self.assertEqual(v1[0].violation_type, "unauthorized_financial_commitment")

        sanitized1, intercepted1, _ = self.engine.sanitize_turn(text1)
        self.assertTrue(intercepted1)
        self.assertNotIn("50% off", sanitized1)
        self.assertIn("standard pricing applies", sanitized1)

        v2 = self.engine.check_unauthorized_financials(text2)
        self.assertEqual(len(v2), 1)
        sanitized2, intercepted2, _ = self.engine.sanitize_turn(text2)
        self.assertTrue(intercepted2)
        self.assertNotIn("for free", sanitized2)

    def test_pii_digit_mutation_interception(self):
        """Assistant hallucinates incorrect phone number digits differing from caller memory."""
        text = "I have your contact number down as (555) 999-8888, is that correct?"
        active_slots = {"caller_phone": "(555) 123-4567"}

        violations = self.engine.verify_pii_consistency(text, active_slots=active_slots)
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0].violation_type, "pii_digit_mutation")

        sanitized, intercepted, _ = self.engine.sanitize_turn(
            assistant_text=text,
            active_slots=active_slots,
        )
        self.assertTrue(intercepted)
        self.assertIn("(555) 123-4567", sanitized)
        self.assertNotIn("999-8888", sanitized)


class TestZeroLiabilityComplianceScrubbing(unittest.TestCase):
    """Verifies regulatory and enterprise liability pattern scrubbing."""

    def test_medical_diagnosis_and_drug_dosage_scrubbing(self):
        text = "Based on what you said, I diagnose you with strep throat. Take 500mg amoxicillin twice daily."
        scrubbed, modified, risks = ZeroLiabilityFilter.scrub_text(text, niche="medical")

        self.assertTrue(modified)
        self.assertGreaterEqual(len(risks), 2)
        self.assertNotIn("I diagnose you with", scrubbed)
        self.assertNotIn("Take 500mg", scrubbed)
        self.assertIn("consult directly with our licensed clinician", scrubbed)

    def test_legal_payout_guarantee_scrubbing(self):
        text = "We guarantee a $500,000 settlement payout for your car accident injury."
        scrubbed, modified, risks = ZeroLiabilityFilter.scrub_text(text, niche="legal")

        self.assertTrue(modified)
        self.assertIn("Unauthorized legal outcome or settlement guarantee", risks)
        self.assertNotIn("guarantee a $500,000", scrubbed)
        self.assertIn("our attorneys will evaluate the merits", scrubbed)

    def test_real_estate_roi_and_fair_housing_scrubbing(self):
        text = "This property is a guaranteed return investment. We only rent to specific families."
        scrubbed, modified, risks = ZeroLiabilityFilter.scrub_text(text, niche="realestate")

        self.assertTrue(modified)
        self.assertNotIn("guaranteed return", scrubbed)
        self.assertNotIn("only rent to specific families", scrubbed)
        self.assertIn("equal housing opportunities", scrubbed)


class TestGuardrailsRESTAPI(unittest.TestCase):
    """Verifies Guardrail configuration and testing REST API endpoints."""

    def test_guardrail_settings_endpoint(self):
        from routes.client_routes import get_guardrails_settings
        res = asyncio_run(get_guardrails_settings(tenant_id="tenant-123", current_user={"role": "client_admin", "sub": "tenant-123"}))
        self.assertEqual(res["tenant_id"], "tenant-123")
        self.assertTrue(res["strict_mode"])
        self.assertTrue(res["phantom_action_interceptor"])
        self.assertTrue(res["unauthorized_financial_guard"])

    def test_guardrail_test_evaluation_endpoint(self):
        from routes.client_routes import test_guardrails_evaluation, GuardrailsTestRequest

        req_violating = GuardrailsTestRequest(
            text="I've booked your luxury vehicle and I can give you 30% off.",
            niche="transport",
            tool_executed=None,
            tool_result=None,
        )
        res1 = asyncio_run(test_guardrails_evaluation(req_violating, current_user={"role": "client_admin", "sub": "t1"}))
        self.assertFalse(res1["is_compliant"])
        self.assertGreater(len(res1["violations"]), 0)
        self.assertNotIn("30% off", res1["sanitized_text"])

        req_clean = GuardrailsTestRequest(
            text="Thank you for providing your pickup location. Where are you heading today?",
            niche="transport",
        )
        res2 = asyncio_run(test_guardrails_evaluation(req_clean, current_user={"role": "client_admin", "sub": "t1"}))
        self.assertTrue(res2["is_compliant"])
        self.assertEqual(res2["violations"], [])
        self.assertEqual(res2["sanitized_text"], req_clean.text)


if __name__ == "__main__":
    unittest.main()
