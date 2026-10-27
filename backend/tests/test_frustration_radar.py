"""
Unit & Integration Tests for Phase 19: Real-Time Caller Frustration Radar & Live Supervisor Alert Escalation.
"""

import os
import sys
import unittest
from unittest.mock import AsyncMock

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set mock secrets for testing environment before importing Settings/FastAPI
os.environ.setdefault("DEEPGRAM_API_KEY", "mock_key")
os.environ.setdefault("OPENROUTER_API_KEY", "mock_key")
os.environ.setdefault("FISH_AUDIO_API_KEY", "mock_key")
os.environ.setdefault("JWT_SECRET_KEY", "test_secret_key_for_unit_tests_32chars!")
os.environ.setdefault("SUPER_ADMIN_EMAIL", "admin@alfie-ai.com")
os.environ.setdefault("SUPER_ADMIN_PASSWORD", "testpass")

from frustration_radar import (
    FrustrationSessionTracker,
    FrustrationTurnResult,
    HUMAN_HANDOFF_PHRASES,
    HOSTILITY_PHRASES,
    THREAT_OR_CANCEL_PHRASES,
    FRUSTRATED_INTERJECTIONS,
)
from migrations import migration_014_frustration_tracking


class TestFrustrationLexicalAnalysis(unittest.TestCase):
    """Unit tests for lexical sentiment, keyword matching, and capitalization/punctuation heuristics."""

    def setUp(self):
        self.tracker = FrustrationSessionTracker()

    def test_calm_and_empty_utterances(self):
        empty_res = self.tracker.process_turn(text="", turn_id="turn_0")
        self.assertEqual(empty_res.score, 0.0)
        self.assertFalse(empty_res.is_escalation)
        self.assertEqual(empty_res.level.upper(), "LOW")

        calm_res = self.tracker.process_turn(
            text="Hello, I would like to schedule an appointment for Thursday.",
            turn_id="turn_1",
        )
        self.assertLess(calm_res.score, 0.30)
        self.assertFalse(calm_res.is_escalation)
        self.assertEqual(calm_res.level.upper(), "LOW")

    def test_human_agent_handoff_requests(self):
        samples = [
            "Let me speak to a person right now",
            "Can I talk to a human please?",
            "Representative, give me an agent",
            "Connect me to an operator or manager",
            "I want a live agent immediately",
        ]
        for phrase in samples:
            tracker = FrustrationSessionTracker()
            res = tracker.process_turn(text=phrase, turn_id="turn_h")
            self.assertTrue(res.is_escalation, f"Failed for phrase: {phrase}")
            self.assertGreaterEqual(res.score, 0.45)
            self.assertIn(res.level.upper(), ["ELEVATED", "CRITICAL"])
            self.assertIn("Caller demanded human agent", res.reason)

    def test_hostility_and_insult_phrases(self):
        samples = [
            "This stupid bot cannot understand anything",
            "You are useless and wasting my time",
            "This is ridiculous and incompetent",
            "Stop playing games with me",
        ]
        for phrase in samples:
            tracker = FrustrationSessionTracker()
            res = tracker.process_turn(text=phrase, turn_id="turn_hostile")
            self.assertTrue(res.is_escalation, f"Failed for phrase: {phrase}")
            self.assertGreaterEqual(res.score, 0.40)
            self.assertIn(res.level.upper(), ["ELEVATED", "CRITICAL"])
            self.assertIn("Hostile language detected", res.reason)

    def test_threat_and_cancellation_phrases(self):
        samples = [
            "I want to cancel my account immediately",
            "Give me a full refund right now",
            "I am filing a dispute and reporting this to the BBB",
            "I will have my lawyer call you",
        ]
        for phrase in samples:
            tracker = FrustrationSessionTracker()
            res = tracker.process_turn(text=phrase, turn_id="turn_cancel")
            self.assertTrue(res.is_escalation, f"Failed for phrase: {phrase}")
            self.assertGreaterEqual(res.score, 0.45)
            self.assertIn(res.level.upper(), ["ELEVATED", "CRITICAL"])
            self.assertIn("Threat or cancellation intent", res.reason)

    def test_frustrated_interjections(self):
        samples = [
            "What the hell is going on here?",
            "Are you kidding me right now?",
            "Oh for god's sake answer my question",
            "Give me a break",
        ]
        for phrase in samples:
            tracker = FrustrationSessionTracker()
            res = tracker.process_turn(text=phrase, turn_id="turn_interject")
            self.assertGreaterEqual(res.score, 0.25, f"Failed for: {phrase}")
            self.assertIn("Exasperation interjection", res.reason)

    def test_all_caps_shouting_and_exclamations(self):
        tracker = FrustrationSessionTracker()
        shout_res = tracker.process_turn(text="I AM WAITING AND NOTHING IS HAPPENING!!", turn_id="turn_caps")
        self.assertGreaterEqual(shout_res.score, 0.30)
        self.assertTrue(any("all_caps" in t for t in shout_res.matched_triggers))
        self.assertTrue(any("multiple_exclamations" in t for t in shout_res.matched_triggers))


    def test_interruption_tracking(self):
        tracker = FrustrationSessionTracker()
        tracker.record_interruption(offset_seconds=5.0)
        tracker.record_interruption(offset_seconds=7.5)
        tracker.record_interruption(offset_seconds=10.0)
        
        self.assertEqual(tracker.interruption_count, 3)

        # Process a turn with recent interruption spike (3 within 15 seconds)
        res = tracker.process_turn(text="Listen to me, that's not what I asked.", offset_ms=12000, turn_id="turn_intr")
        self.assertGreaterEqual(res.score, 0.20)
        self.assertTrue(any("interruption_spike" in t for t in res.matched_triggers))


class TestFrustrationDecayAndRollingScore(unittest.TestCase):
    """Unit tests for rolling score accumulation, decay, and peak preservation."""

    def test_rolling_accumulation_and_decay(self):
        tracker = FrustrationSessionTracker(decay_factor=0.60)

        # Turn 1: Frustrated statement
        r1 = tracker.process_turn(text="Let me speak to a manager right now!", turn_id="t1")
        self.assertGreaterEqual(r1.score, 0.45)
        peak_after_t1 = tracker.peak_score

        # Turn 2: Calm resolution
        r2 = tracker.process_turn(text="Okay, thank you for clarifying that.", turn_id="t2")
        self.assertLess(r2.score, r1.score)
        # Peak score remains the highest level reached
        self.assertEqual(tracker.peak_score, peak_after_t1)

        # Turn 3: Continued calm speech decays further
        r3 = tracker.process_turn(text="That sounds perfect, have a wonderful day.", turn_id="t3")
        self.assertLess(r3.score, r2.score)
        self.assertEqual(tracker.peak_score, peak_after_t1)

    def test_escalation_events_ledger(self):
        tracker = FrustrationSessionTracker()
        tracker.process_turn(text="Hello there", turn_id="t1")
        tracker.process_turn(text="I demand to speak to your manager right now!", turn_id="t2")
        tracker.process_turn(text="Okay fine, let's continue.", turn_id="t3")
        tracker.process_turn(text="You are useless and wasting my time!", turn_id="t4")

        events = tracker.get_escalation_events()
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["turn_id"], "t2")
        self.assertIn("Caller demanded human agent", events[0]["reason"])
        self.assertEqual(events[1]["turn_id"], "t4")
        self.assertIn("Hostile language detected", events[1]["reason"])


class TestMigration014(unittest.IsolatedAsyncioTestCase):
    """Verify Database Migration 014 schema execution."""

    async def test_migration_014_frustration_tracking(self):
        mock_conn = AsyncMock()
        await migration_014_frustration_tracking(mock_conn)

        self.assertEqual(mock_conn.execute.call_count, 1)
        executed_sql = mock_conn.execute.call_args[0][0]

        self.assertIn("peak_frustration_score", executed_sql)
        self.assertIn("frustration_events", executed_sql)
        self.assertIn("idx_call_recordings_frustration", executed_sql)


from datetime import datetime, timezone
import json
from unittest.mock import MagicMock, patch


class TestClientRoutesFrustrationIntegration(unittest.IsolatedAsyncioTestCase):
    """Integration test for /api/client/interactions and /api/client/qa/triage frustration filtering."""

    @patch("routes.client_routes._pool")
    async def test_client_interactions_hydration_and_filtering(self, mock_pool):
        import routes.client_routes as cr

        mock_conn = MagicMock()
        mock_conn.fetch = AsyncMock(return_value=[
            {
                "call_id": "call_frust_1",
                "caller_number": "+15551239999",
                "duration_seconds": 120,
                "quality_score": 65,
                "sentiment": "negative",
                "live_status": "completed",
                "conversion_status": "lost_opportunity",
                "risk_flag": True,
                "risk_reason": "High frustration: human handoff request",
                "peak_frustration_score": 0.85,
                "frustration_events": json.dumps([
                    {
                        "turn_id": "turn_3",
                        "score": 0.85,
                        "level": "CRITICAL",
                        "reason": "human_agent_request",
                        "snippet": "Let me talk to a human right now!"
                    }
                ]),
                "waveform_data": json.dumps([15, 25, 35]),
                "transcript": json.dumps([
                    {"role": "assistant", "content": "Hello!"},
                    {"role": "user", "content": "Let me talk to a human right now!"}
                ]),
                "created_at": datetime.now(timezone.utc),
                "agent_name": "Alfie Support",
            }
        ])

        mock_acquire = MagicMock()
        mock_acquire.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_acquire.__aexit__ = AsyncMock(return_value=None)
        mock_pool.acquire.return_value = mock_acquire

        res = await cr.get_client_interactions(
            tenant_id="00000000-0000-0000-0000-000000000001",
            frustration_level="critical",
            current_user={"sub": "test_user", "tenant_id": "00000000-0000-0000-0000-000000000001"},
        )
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["id"], "call_frust_1")
        self.assertEqual(res[0]["peak_frustration_score"], 0.85)
        self.assertEqual(len(res[0]["frustration_events"]), 1)
        self.assertEqual(res[0]["frustration_events"][0]["level"], "CRITICAL")

        # Verify SQL query had condition for peak_frustration_score >= 0.70
        sql_called = mock_conn.fetch.call_args[0][0]
        self.assertIn("c.peak_frustration_score >= 0.70", sql_called)

    @patch("routes.client_routes._pool")
    async def test_qa_triage_frustration_summary(self, mock_pool):
        import routes.client_routes as cr

        mock_conn = MagicMock()
        mock_conn.fetch = AsyncMock(return_value=[
            {
                "call_id": "call_triage_frust",
                "caller_number": "+15553334444",
                "duration_seconds": 90,
                "quality_score": 60,
                "sentiment": "negative",
                "conversion_status": "lost_opportunity",
                "risk_flag": True,
                "risk_reason": "High Frustration",
                "qa_breakdown": json.dumps({"intake_completeness_score": 50}),
                "peak_frustration_score": 0.88,
                "frustration_events": json.dumps([{"score": 0.88, "reason": "hostility_detected"}]),
                "created_at": datetime.now(timezone.utc),
                "agent_name": "Alfie",
            }
        ])
        mock_conn.fetchval = AsyncMock(side_effect=[1, 1, 1])  # total_risk, total_lost, total_frustrated

        mock_acquire = MagicMock()
        mock_acquire.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_acquire.__aexit__ = AsyncMock(return_value=None)
        mock_pool.acquire.return_value = mock_acquire

        triage = await cr.get_qa_triage(
            tenant_id="00000000-0000-0000-0000-000000000001",
            current_user={"sub": "test_user", "tenant_id": "00000000-0000-0000-0000-000000000001"},
        )
        self.assertEqual(triage["total_at_risk"], 3)
        self.assertEqual(triage["critical_frustration_count"], 1)
        self.assertEqual(len(triage["triage_calls"]), 1)
        self.assertEqual(triage["triage_calls"][0]["peak_frustration_score"], 0.88)


if __name__ == "__main__":
    unittest.main()
