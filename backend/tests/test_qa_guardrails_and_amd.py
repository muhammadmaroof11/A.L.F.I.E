"""
Integration and Unit Tests for Phase 17C:
- Deterministic Slot-Filling Guardrails (Legal, Medical, Hospitality)
- Zero-Liability Anti-Hallucination Safety Filters
- Smart Answering Machine Detection (AMD) & Voicemail Drop Webhook
- Database Migration 011 (QA Breakdown & Conversion Status)
- Client REST Endpoints for QA Breakdown and Lost Revenue Triage
"""

import json
import os
import sys
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set mock secrets for testing environment before importing Settings/FastAPI
os.environ.setdefault("DEEPGRAM_API_KEY", "mock_key")
os.environ.setdefault("OPENROUTER_API_KEY", "mock_key")
os.environ.setdefault("FISH_AUDIO_API_KEY", "mock_key")
os.environ.setdefault("JWT_SECRET_KEY", "test_secret_key_for_unit_tests_32chars!")
os.environ.setdefault("SUPER_ADMIN_EMAIL", "admin@alfie-ai.com")
os.environ.setdefault("SUPER_ADMIN_PASSWORD", "testpass")

from fastapi.testclient import TestClient
from api import app
from auth import create_access_token
from guardrails.slot_tracker import SlotTracker, get_slot_tracker_for_niche
from guardrails.safety_filter import ZeroLiabilityFilter
from migrations import migration_011_qa_scoring_and_conversion_triage


class TestQAGuardrailsAndAMD(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.tenant_id = "test-tenant-qa-17c"
        self.client_token = create_access_token(
            data={"sub": "test_client_user", "tenant_id": self.tenant_id, "role": "client_admin"}
        )
        self.headers = {"Authorization": f"Bearer {self.client_token}"}

    # --- Pillar 1: Deterministic Slot-Filling Tests ---

    def test_slot_tracker_legal_intake(self):
        """Verify LegalIntakeSlots extraction, missing slot detection, and prompt guidance."""
        tracker = get_slot_tracker_for_niche("legal", caller_phone="+15551234567")
        self.assertEqual(tracker.niche, "legal")
        self.assertEqual(tracker.get_slot("caller_phone"), "+15551234567")
        self.assertFalse(tracker.is_complete())

        # Check missing mandatory slots
        missing = tracker.get_missing_mandatory_slots()
        self.assertIn("caller_name", missing)
        self.assertIn("incident_date", missing)
        self.assertIn("injury_severity", missing)
        self.assertIn("has_attorney", missing)

        # Guidance prompt should exist
        guidance = tracker.generate_guidance_prompt()
        self.assertIsNotNone(guidance)
        self.assertIn("[DETERMINISTIC INTAKE DIRECTIVE]", guidance)

        # Simulate user turn with name, date, and injury
        tracker.update_from_text(
            "My name is John Davis. I was in a car accident yesterday and sustained a severe concussion."
        )
        self.assertEqual(tracker.get_slot("caller_name"), "John Davis")
        self.assertEqual(tracker.get_slot("incident_date"), "yesterday")
        self.assertIsNotNone(tracker.get_slot("injury_severity"))

        # Still missing attorney status
        self.assertFalse(tracker.is_complete())
        self.assertIn("has_attorney", tracker.get_missing_mandatory_slots())

        # Simulate attorney status statement
        tracker.update_from_text("I do not have an attorney yet, which is why I called.")
        self.assertEqual(tracker.get_slot("has_attorney"), "No")

        # Now complete
        self.assertTrue(tracker.is_complete())
        self.assertEqual(tracker.get_completion_percentage(), 100)
        self.assertIsNone(tracker.generate_guidance_prompt())

    def test_slot_tracker_medical_clinic(self):
        """Verify MedicalClinicSlots extraction and completion tracking."""
        tracker = get_slot_tracker_for_niche("clinic")
        tracker.update_from_text(
            "Hello, this is Robert Miller. My phone is 555-889-1234. I have Blue Cross insurance and need an exam."
        )
        self.assertEqual(tracker.get_slot("patient_name"), "Robert Miller")
        self.assertIsNotNone(tracker.get_slot("insurance_provider"))
        self.assertIsNotNone(tracker.get_slot("reason_for_visit"))

        # Add preferred time
        tracker.update_from_text("Tomorrow afternoon works best for me.")
        self.assertIsNotNone(tracker.get_slot("preferred_time"))
        self.assertTrue(tracker.is_complete())

    # --- Pillar 2: Zero-Liability Safety Filter Tests ---

    def test_zero_liability_filter_legal_guarantee(self):
        """Verify settlement guarantee is detected and scrubbed with a compliant disclaimer."""
        raw_text = "Don't worry, we guarantee a $250,000 settlement for your accident injuries."
        violations = ZeroLiabilityFilter.check_violations(raw_text, niche="legal")
        self.assertTrue(len(violations) > 0)
        self.assertEqual(violations[0]["category"], "legal")

        scrubbed, was_modified, risks = ZeroLiabilityFilter.scrub_text(raw_text, niche="legal")
        self.assertTrue(was_modified)
        self.assertNotIn("guarantee a $250,000 settlement", scrubbed.lower())
        self.assertIn("attorneys will evaluate", scrubbed.lower())

    def test_zero_liability_filter_medical_diagnosis(self):
        """Verify unauthorized diagnosis and medication cessation are scrubbed."""
        raw_text = "Based on your headache, you definitely have covid, so stop taking your medication immediately."
        scrubbed, was_modified, risks = ZeroLiabilityFilter.scrub_text(raw_text, niche="medical")
        self.assertTrue(was_modified)
        self.assertNotIn("you definitely have covid", scrubbed.lower())
        self.assertNotIn("stop taking your medication", scrubbed.lower())
        self.assertIn("consult directly with", scrubbed.lower())

    def test_zero_liability_filter_clean_text(self):
        """Verify compliant text is untouched."""
        clean_text = "Thank you for reaching out. We have openings at 3 PM tomorrow. May I confirm your name?"
        scrubbed, was_modified, risks = ZeroLiabilityFilter.scrub_text(clean_text, niche="general")
        self.assertFalse(was_modified)
        self.assertEqual(clean_text, scrubbed)
        self.assertEqual(len(risks), 0)

    # --- Pillar 3: Smart AMD Webhook Tests ---

    def test_amd_status_webhook_machine_beep(self):
        """Verify Twilio AMD detects voicemail beep and returns 15-second voicemail drop TwiML."""
        payload = {
            "AnsweredBy": "machine_end_beep",
            "CallSid": "CA1234567890abcdef",
            "To": "+15558889999",
            "From": "+18005550199",
        }
        res = self.client.post("/api/twilio/amd-status", data=payload)
        self.assertEqual(res.status_code, 200)
        self.assertIn("<Say", res.text)
        self.assertIn("<Hangup/>", res.text)
        self.assertIn("Hi, this is Alfie returning your call", res.text)

    def test_amd_status_webhook_human(self):
        """Verify Twilio AMD detects human and allows call to proceed without Hangup."""
        payload = {
            "AnsweredBy": "human",
            "CallSid": "CA1234567890abcdef",
            "To": "+15558889999",
            "From": "+18005550199",
        }
        res = self.client.post("/api/twilio/amd-status", data=payload)
        self.assertEqual(res.status_code, 200)
        self.assertNotIn("<Hangup/>", res.text)

    # --- Pillar 4: Database Migration 011 Tests ---

    def test_migration_011_schema(self):
        """Verify Migration 011 executes ALTER TABLE and CREATE INDEX successfully."""
        mock_conn = MagicMock()
        mock_conn.execute = AsyncMock()

        import asyncio
        asyncio.run(migration_011_qa_scoring_and_conversion_triage(mock_conn))
        mock_conn.execute.assert_called_once()
        sql = mock_conn.execute.call_args[0][0]
        self.assertIn("qa_breakdown JSONB", sql)
        self.assertIn("conversion_status VARCHAR(50)", sql)
        self.assertIn("risk_flag BOOLEAN", sql)
        self.assertIn("idx_call_recordings_qa_conversion", sql)

    # --- Pillar 5: Client REST QA Triage & Interactions Endpoints ---

    @patch("routes.client_routes._pool")
    def test_get_qa_triage_endpoint(self, mock_pool):
        """Verify GET /api/client/qa/triage returns lost revenue summary and triage calls."""
        mock_conn = MagicMock()
        mock_conn.fetch = AsyncMock(return_value=[
            {
                "call_id": "call_triage_1",
                "caller_number": "+15554443333",
                "duration_seconds": 120,
                "quality_score": 45,
                "sentiment": "negative",
                "conversion_status": "lost_opportunity",
                "risk_flag": True,
                "risk_reason": "Caller was angry about price increase.",
                "qa_breakdown": json.dumps({"intake_completeness_score": 40, "empathy_tone_score": 50}),
                "created_at": datetime.now(timezone.utc),
                "agent_name": "Alfie",
            }
        ])
        mock_conn.fetchval = AsyncMock(side_effect=[1, 1])

        mock_acquire = MagicMock()
        mock_acquire.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_acquire.__aexit__ = AsyncMock(return_value=None)
        mock_pool.acquire.return_value = mock_acquire

        res = self.client.get("/api/client/qa/triage", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total_at_risk"], 2)
        self.assertEqual(data["critical_risk_count"], 1)
        self.assertEqual(data["lost_opportunity_count"], 1)
        self.assertEqual(len(data["triage_calls"]), 1)
        self.assertEqual(data["triage_calls"][0]["caller"], "+15554443333")

    @patch("routes.client_routes._pool")
    def test_get_interactions_with_qa_filters(self, mock_pool):
        """Verify GET /api/client/interactions returns hydrated QA breakdown and honors filters."""
        mock_conn = MagicMock()
        mock_conn.fetch = AsyncMock(return_value=[
            {
                "call_id": "call_qa_test_1",
                "caller_number": "+15559990000",
                "duration_seconds": 180,
                "quality_score": 92,
                "sentiment": "positive",
                "live_status": "completed",
                "conversion_status": "lead_secured",
                "risk_flag": False,
                "risk_reason": "",
                "qa_breakdown": json.dumps({
                    "intake_completeness_score": 95,
                    "empathy_tone_score": 90,
                    "overall_quality_score": 92,
                    "conversion_status": "lead_secured",
                    "critical_risk_flag": False
                }),
                "waveform_data": json.dumps([10, 20, 30]),
                "transcript": json.dumps([{"role": "assistant", "content": "Hello!"}]),
                "created_at": datetime.now(timezone.utc),
                "agent_name": "Alfie Primary",
            }
        ])

        mock_acquire = MagicMock()
        mock_acquire.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_acquire.__aexit__ = AsyncMock(return_value=None)
        mock_pool.acquire.return_value = mock_acquire

        res = self.client.get("/api/client/interactions?conversion_status=lead_secured", headers=self.headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["conversion_status"], "lead_secured")
        self.assertEqual(data[0]["qa_breakdown"]["intake_completeness_score"], 95)


if __name__ == "__main__":
    unittest.main()
