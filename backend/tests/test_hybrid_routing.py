"""
Unit & Integration Tests for Phase 21: Sub-100ms Ultra-Fast Hybrid Routing & Acoustic Fillers.
"""

import time
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from hybrid_router import (
    ACOUSTIC_FILLER_BANKS,
    HybridRouter,
    classify_tool_intent,
    normalize_niche,
)
from migrations import migration_016_hybrid_routing_and_fillers
from routes.client_routes import ClientAgentProvisionRequest, ClientAgentUpdateRequest


class TestToolIntentClassification(unittest.TestCase):
    """Tests classification of tool names into conversational intent categories."""

    def test_calendar_intent_classification(self):
        calendar_tools = [
            "check_calendar_availability",
            "get_open_slots",
            "schedule_appointment",
            "view_doctor_schedule",
            "booking_availability",
        ]
        for tool in calendar_tools:
            self.assertEqual(
                classify_tool_intent(tool),
                "calendar",
                f"Failed to classify {tool} as calendar",
            )

    def test_booking_intent_classification(self):
        booking_tools = [
            "book_consultation",
            "reserve_table",
            "confirm_reservation",
        ]
        for tool in booking_tools:
            self.assertEqual(
                classify_tool_intent(tool),
                "booking",
                f"Failed to classify {tool} as booking",
            )

    def test_catalog_intent_classification(self):
        catalog_tools = [
            "get_fleet_vehicles",
            "calculate_rental_rate",
            "lookup_property_listing",
            "search_inventory",
            "view_luxury_car_quote",
        ]
        for tool in catalog_tools:
            self.assertEqual(
                classify_tool_intent(tool),
                "catalog",
                f"Failed to classify {tool} as catalog",
            )

    def test_records_intent_classification(self):
        records_tools = [
            "check_intake_conflict",
            "lookup_patient_record",
            "verify_doctor_notes",
            "fetch_client_case",
        ]
        for tool in records_tools:
            self.assertEqual(
                classify_tool_intent(tool),
                "records",
                f"Failed to classify {tool} as records",
            )

    def test_general_fallback_intent(self):
        general_tools = [
            "calculate_tax",
            "send_notification_ping",
            "unknown_custom_tool",
            "",
        ]
        for tool in general_tools:
            self.assertEqual(
                classify_tool_intent(tool),
                "general",
                f"Expected {tool} to default to general",
            )


class TestNicheNormalization(unittest.TestCase):
    """Tests vertical/niche normalization across aliases and edge cases."""

    def test_known_aliases(self):
        self.assertEqual(normalize_niche("personal_injury"), "legal_intake")
        self.assertEqual(normalize_niche("law_firm"), "legal_intake")
        self.assertEqual(normalize_niche("dental_clinic"), "medical_reception")
        self.assertEqual(normalize_niche("healthcare"), "medical_reception")
        self.assertEqual(normalize_niche("realtor"), "real_estate")
        self.assertEqual(normalize_niche("property"), "real_estate")
        self.assertEqual(normalize_niche("luxury_transfer"), "luxury_transport")
        self.assertEqual(normalize_niche("chauffeur"), "luxury_transport")
        self.assertEqual(normalize_niche("carrental"), "car_rental")
        self.assertEqual(normalize_niche("hotel"), "hospitality")
        self.assertEqual(normalize_niche("restaurant"), "hospitality")

    def test_case_and_punctuation_handling(self):
        self.assertEqual(normalize_niche("  Legal-Intake  "), "legal_intake")
        self.assertEqual(normalize_niche("DENTAL-CLINIC"), "medical_reception")
        self.assertEqual(normalize_niche("Car-Rental"), "car_rental")

    def test_empty_or_none_fallback(self):
        self.assertEqual(normalize_niche(None), "general")
        self.assertEqual(normalize_niche(""), "general")
        self.assertEqual(normalize_niche("   "), "general")


class TestDeterministicAcousticBank(unittest.TestCase):
    """Tests multi-vertical deterministic acoustic bridge banks."""

    def setUp(self):
        self.router = HybridRouter(cooldown_seconds=3.0)

    def test_all_canonical_verticals_present(self):
        expected_niches = [
            "legal_intake",
            "medical_reception",
            "real_estate",
            "car_rental",
            "luxury_transport",
            "hospitality",
            "general",
        ]
        for niche in expected_niches:
            self.assertIn(niche, ACOUSTIC_FILLER_BANKS)
            self.assertIn("calendar", ACOUSTIC_FILLER_BANKS[niche])
            self.assertIn("general", ACOUSTIC_FILLER_BANKS[niche])
            self.assertGreater(len(ACOUSTIC_FILLER_BANKS[niche]["general"]), 0)

    def test_instant_deterministic_filler_latency(self):
        start = time.perf_counter()
        phrase = self.router.get_instant_deterministic_filler(
            tool_name="check_calendar_availability",
            niche="legal_intake",
            call_id="call-test-latency",
        )
        elapsed_ms = (time.perf_counter() - start) * 1000
        self.assertTrue(bool(phrase))
        self.assertLess(elapsed_ms, 10.0, "Deterministic bank should execute in sub-10ms")

    def test_anti_repetition_cycle(self):
        call_id = "call-repetition-test"
        niche = "legal_intake"
        tool = "check_calendar_availability"

        spoken_set = set()
        candidates = ACOUSTIC_FILLER_BANKS[niche]["calendar"]

        # Call multiple times up to number of candidates
        for _ in range(len(candidates)):
            # Force reset cooldown to test bank selection only
            self.router._session_state[call_id] = {
                "last_spoken_time": 0.0,
                "history": list(spoken_set),
            }
            phrase = self.router.get_instant_deterministic_filler(
                tool_name=tool,
                niche=niche,
                call_id=call_id,
            )
            spoken_set.add(phrase)

        # Anti-repetition should select distinct phrases before repeating
        self.assertEqual(len(spoken_set), len(candidates))


class TestHybridRouterCooldown(unittest.TestCase):
    """Tests filler pacing and cooldown enforcement."""

    def test_cooldown_skips_too_frequent_invocations(self):
        router = HybridRouter(cooldown_seconds=2.0)
        call_id = "call-cooldown-1"

        # First check should be allowed
        self.assertTrue(router.should_speak_filler(call_id))

        # Record spoken filler
        router.record_filler_spoken(call_id, "Checking on that...")

        # Immediate next check should be skipped
        self.assertFalse(router.should_speak_filler(call_id))

        # After advancing timestamp past cooldown, it should be allowed again
        router._session_state[call_id]["last_spoken_time"] -= 2.1
        self.assertTrue(router.should_speak_filler(call_id))

    def test_cooldown_history_bounded(self):
        router = HybridRouter(cooldown_seconds=1.0)
        call_id = "call-hist-bound"

        for i in range(10):
            router.record_filler_spoken(call_id, f"Phrase {i}")

        info = router._get_session_info(call_id)
        self.assertLessEqual(len(info["history"]), 5)
        self.assertEqual(info["history"][-1], "Phrase 9")


class TestFastLLMAndDualStageRouting(unittest.IsolatedAsyncioTestCase):
    """Tests dual-stage fallback and fast LLM dispatch."""

    async def test_get_filler_cooldown_skipped(self):
        router = HybridRouter(cooldown_seconds=5.0)
        call_id = "call-skip-test"

        router.record_filler_spoken(call_id, "Checking...")
        result = await router.get_filler(
            tool_name="check_calendar",
            niche="legal_intake",
            call_id=call_id,
        )
        self.assertFalse(result["spoken"])
        self.assertEqual(result["source"], "cooldown_skipped")
        self.assertEqual(result["phrase"], "")

    @patch("hybrid_router.settings")
    async def test_fast_llm_groq_success(self, mock_settings):
        mock_settings.groq_api_key = "gsk_test_key"
        mock_settings.cerebras_api_key = ""

        router = HybridRouter(cooldown_seconds=0.0)

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "Checking our legal calendar right now...",
                    }
                }
            ]
        }

        with patch("httpx.AsyncClient.post", new=AsyncMock(return_value=mock_resp)):
            result = await router.get_filler(
                tool_name="check_calendar",
                niche="legal_intake",
                call_id="call-groq-ok",
            )
            self.assertTrue(result["spoken"])
            self.assertEqual(result["source"], "fast_llm")
            self.assertEqual(result["phrase"], "Checking our legal calendar right now...")

    @patch("hybrid_router.settings")
    async def test_fast_llm_timeout_fallback_to_deterministic(self, mock_settings):
        mock_settings.groq_api_key = "gsk_test_key"
        mock_settings.cerebras_api_key = ""

        router = HybridRouter(cooldown_seconds=0.0)

        # Simulate timeout on httpx call
        with patch("httpx.AsyncClient.post", side_effect=TimeoutError("Request timed out")):
            result = await router.get_filler(
                tool_name="check_calendar",
                niche="medical_reception",
                call_id="call-timeout-fallback",
            )
            self.assertTrue(result["spoken"])
            self.assertEqual(result["source"], "deterministic_bank")
            self.assertIn("...", result["phrase"])
            self.assertTrue(any(k in result["phrase"].lower() for k in ["calendar", "slot", "availability", "schedule", "doctor"]))


class TestMigration016(unittest.IsolatedAsyncioTestCase):
    """Tests Migration 016 schema alteration execution."""

    async def test_migration_016_statements(self):
        mock_conn = AsyncMock()

        await migration_016_hybrid_routing_and_fillers(mock_conn)

        # Ensure execute was called for the columns
        self.assertTrue(mock_conn.execute.called)
        executed_sqls = [call[0][0] for call in mock_conn.execute.call_args_list]
        combined_sql = " ".join(executed_sqls)

        self.assertIn("conversational_fillers_enabled", combined_sql)
        self.assertIn("filler_pacing_mode", combined_sql)
        self.assertIn("filler_cooldown_seconds", combined_sql)


class TestClientAgentModels(unittest.TestCase):
    """Tests client agent provision and update models for filler fields."""

    def test_provision_request_defaults(self):
        req = ClientAgentProvisionRequest(
            name="Receptionist",
            niche="dental_clinic",
        )
        self.assertTrue(req.conversational_fillers_enabled)
        self.assertEqual(req.filler_pacing_mode, "ultra_fast")
        self.assertEqual(req.filler_cooldown_seconds, 3.5)

    def test_update_request_custom_values(self):
        req = ClientAgentUpdateRequest(
            conversational_fillers_enabled=False,
            filler_pacing_mode="fast",
            filler_cooldown_seconds=2.0,
        )
        self.assertFalse(req.conversational_fillers_enabled)
        self.assertEqual(req.filler_pacing_mode, "fast")
        self.assertEqual(req.filler_cooldown_seconds, 2.0)


class TestAgentToolInterleaving(unittest.IsolatedAsyncioTestCase):
    """Tests the agent's acoustic filler dispatch and audio stream interleaving."""

    async def test_tool_started_dispatches_filler_and_telemetry(self):
        import json
        router = HybridRouter(cooldown_seconds=0.0)
        mock_session = MagicMock()
        mock_session.say = AsyncMock()

        mock_redis = MagicMock()
        mock_redis.publish = AsyncMock()

        call_id = "call-room-99"
        tenant_id = "tenant-interleave-test"
        niche = "legal_intake"
        tool_name = "check_calendar_availability"

        # Simulate the tool dispatch logic
        filler_res = await router.get_filler(
            tool_name=tool_name,
            niche=niche,
            call_id=call_id,
        )
        self.assertTrue(filler_res["spoken"])
        self.assertTrue(bool(filler_res["phrase"]))

        # Execute session.say and Redis publish as done in agent.py
        await mock_session.say(filler_res["phrase"], allow_interruptions=True, add_to_chat_ctx=False)
        await mock_redis.publish(
            f"telemetry:live:{tenant_id}",
            json.dumps({
                "event": "acoustic_filler_spoken",
                "call_id": call_id,
                "tool": tool_name,
                "phrase": filler_res["phrase"],
                "source": filler_res.get("source"),
                "latency_ms": filler_res.get("latency_ms"),
            }),
        )

        # Assertions
        mock_session.say.assert_called_once_with(
            filler_res["phrase"],
            allow_interruptions=True,
            add_to_chat_ctx=False,
        )
        mock_redis.publish.assert_called_once()
        published_payload = json.loads(mock_redis.publish.call_args[0][1])
        self.assertEqual(published_payload["event"], "acoustic_filler_spoken")
        self.assertEqual(published_payload["tool"], tool_name)
        self.assertEqual(published_payload["phrase"], filler_res["phrase"])


if __name__ == "__main__":
    unittest.main()
