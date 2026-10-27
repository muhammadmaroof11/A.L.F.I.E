"""Unit and integration tests for Phase 17D: DTMF Keypad Tone Navigation & Phone Tree Handling."""

import asyncio
import json
import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

# Mock environment variables before importing settings/api
os.environ.setdefault("DEEPGRAM_API_KEY", "mock_key")
os.environ.setdefault("OPENROUTER_API_KEY", "mock_key")
os.environ.setdefault("FISH_AUDIO_API_KEY", "mock_key")
os.environ.setdefault("JWT_SECRET_KEY", "test_secret_key_for_unit_tests_32chars!")
os.environ.setdefault("SUPER_ADMIN_EMAIL", "admin@alfie-ai.com")
os.environ.setdefault("SUPER_ADMIN_PASSWORD", "testpass")

from fastapi.testclient import TestClient

from api import app
from auth import create_access_token
from dtmf_utils import (
    DTMF_CHAR_TO_CODE,
    DTMF_CODE_TO_CHAR,
    DTMFKeypadBuffer,
    dispatch_dtmf_sequence,
    validate_dtmf_sequence,
)
from migrations import MIGRATIONS, migration_012_dtmf_telephony_support
from telemetry import complete_call_record
from tools.core import CoreTools


class AsyncContextManagerMock:
    def __init__(self, target):
        self.target = target

    async def __aenter__(self):
        return self.target

    async def __aexit__(self, exc_type, exc, tb):
        pass


class TestDTMFTelephony(unittest.TestCase):
    """Test suite for RFC 4733 DTMF mappings, keypad buffer, tools, and endpoints."""

    def setUp(self):
        self.client = TestClient(app)
        self.test_tenant_id = str(uuid.uuid4())
        self.client_token = create_access_token(
            {"sub": "client_admin", "role": "client_admin", "tenant_id": self.test_tenant_id}
        )
        self.auth_headers = {"Authorization": f"Bearer {self.client_token}"}

    # -------------------------------------------------------------------------
    # 1. DTMF Codes and Sequence Validation
    # -------------------------------------------------------------------------
    def test_rfc4733_code_mappings(self):
        """Verify RFC 4733 telephone-event standard code mappings."""
        for i in range(10):
            self.assertEqual(DTMF_CHAR_TO_CODE[str(i)], i)
            self.assertEqual(DTMF_CODE_TO_CHAR[i], str(i))
        self.assertEqual(DTMF_CHAR_TO_CODE["*"], 10)
        self.assertEqual(DTMF_CODE_TO_CHAR[10], "*")
        self.assertEqual(DTMF_CHAR_TO_CODE["#"], 11)
        self.assertEqual(DTMF_CODE_TO_CHAR[11], "#")
        self.assertEqual(DTMF_CHAR_TO_CODE["A"], 12)
        self.assertEqual(DTMF_CHAR_TO_CODE["B"], 13)
        self.assertEqual(DTMF_CHAR_TO_CODE["C"], 14)
        self.assertEqual(DTMF_CHAR_TO_CODE["D"], 15)

    def test_validate_dtmf_sequence_valid(self):
        """Verify sequence validation with digits, symbols, and pause commas."""
        self.assertTrue(validate_dtmf_sequence("1,2,3#*A,4"))
        self.assertTrue(validate_dtmf_sequence("1a2b"))
        self.assertTrue(validate_dtmf_sequence("402#"))

    def test_validate_dtmf_sequence_invalid(self):
        """Verify invalid DTMF characters return False."""
        self.assertFalse(validate_dtmf_sequence(""))
        self.assertFalse(validate_dtmf_sequence("   "))
        self.assertFalse(validate_dtmf_sequence("123X45"))
        self.assertFalse(validate_dtmf_sequence("123@#"))

    # -------------------------------------------------------------------------
    # 2. Async Dispatch Sequence with Tone & Pause Timing
    # -------------------------------------------------------------------------
    def test_dispatch_dtmf_sequence(self):
        """Verify publish_dtmf is invoked sequentially with proper codes."""
        async def run_dispatch():
            mock_room = MagicMock()
            mock_participant = MagicMock()
            mock_participant.publish_dtmf = AsyncMock()
            mock_room.local_participant = mock_participant

            # Sequence with digits and a pause comma
            digits = "1,#"
            tones_sent = await dispatch_dtmf_sequence(
                mock_room,
                digits,
                inter_digit_delay_ms=10,
                pause_comma_delay_ms=20,
            )
            self.assertEqual(tones_sent, 2)
            self.assertEqual(mock_participant.publish_dtmf.call_count, 2)
            # Call 1: '1' -> code 1
            mock_participant.publish_dtmf.assert_any_call(code=1, digit="1")
            # Call 2: '#' -> code 11
            mock_participant.publish_dtmf.assert_any_call(code=11, digit="#")

        asyncio.run(run_dispatch())

    # -------------------------------------------------------------------------
    # 3. DTMFKeypadBuffer Inbound Accumulator
    # -------------------------------------------------------------------------
    def test_dtmf_keypad_buffer_debounce(self):
        """Verify DTMFKeypadBuffer debounces keystrokes and flushes sequence."""
        async def run_buffer_test():
            flushed_sequences = []

            async def on_seq(seq):
                flushed_sequences.append(seq)

            buffer = DTMFKeypadBuffer(on_sequence_completed=on_seq, debounce_seconds=0.05)

            # Rapidly add 4 digits: "1", "2", "3", "4"
            buffer.add_digit("1")
            buffer.add_digit("2")
            buffer.add_digit("3")
            buffer.add_digit("4")

            # Sequence should not be flushed immediately
            self.assertEqual(len(flushed_sequences), 0)

            # Wait for debounce duration
            await asyncio.sleep(0.08)

            # Now it should be flushed as one consolidated string
            self.assertEqual(len(flushed_sequences), 1)
            self.assertEqual(flushed_sequences[0], "1234")

        asyncio.run(run_buffer_test())

    def test_dtmf_keypad_buffer_pound_terminator(self):
        """Verify '#' immediately flushes buffered sequence without waiting for debounce."""
        async def run_pound_test():
            flushed_sequences = []

            async def on_seq(seq):
                flushed_sequences.append(seq)

            buffer = DTMFKeypadBuffer(on_sequence_completed=on_seq, debounce_seconds=1.0)

            buffer.add_digit("9")
            buffer.add_digit("8")
            # Pound key entered - triggers immediate flush
            buffer.add_digit("#")

            # Let the event loop run a tick for the callback task
            await asyncio.sleep(0.01)

            # Immediately flushed
            self.assertEqual(len(flushed_sequences), 1)
            self.assertEqual(flushed_sequences[0], "98#")

        asyncio.run(run_pound_test())

    # -------------------------------------------------------------------------
    # 4. LLM Function Tool: CoreTools.send_dtmf_tones()
    # -------------------------------------------------------------------------
    def test_core_tools_send_dtmf_tones(self):
        """Verify send_dtmf_tones publishes tones, logs event, and updates state."""
        async def run_tool_test():
            mock_room = MagicMock()
            mock_room.local_participant = MagicMock()
            mock_room.local_participant.publish_dtmf = AsyncMock()

            call_state = {"tenant_id": self.test_tenant_id, "call_id": "call-123"}
            tools = CoreTools(
                tenant_id=self.test_tenant_id,
                room_name="call-123",
                call_state=call_state,
                room=mock_room,
            )

            with patch("telemetry.get_redis") as mock_get_redis:
                mock_redis = AsyncMock()
                mock_redis.publish = AsyncMock()
                mock_get_redis.return_value = mock_redis

                result = await tools.send_dtmf_tones(
                    digits="1,4#",
                    reason="Navigating to billing department",
                )

                self.assertIn("Successfully transmitted DTMF tones '1,4#'", result)
                self.assertEqual(mock_room.local_participant.publish_dtmf.call_count, 3)
                self.assertIn("dtmf_events", call_state)
                self.assertEqual(len(call_state["dtmf_events"]), 1)
                event = call_state["dtmf_events"][0]
                self.assertEqual(event["direction"], "outbound")
                self.assertEqual(event["digits"], "1,4#")
                self.assertEqual(event["reason"], "Navigating to billing department")

        asyncio.run(run_tool_test())

    # -------------------------------------------------------------------------
    # 5. REST API: POST /api/client/calls/{call_id}/dtmf
    # -------------------------------------------------------------------------
    @patch("telemetry.get_redis")
    def test_send_client_dtmf_endpoint(self, mock_get_redis):
        """Verify supervisor can inject DTMF tones via REST endpoint."""
        mock_redis = AsyncMock()
        mock_redis.publish = AsyncMock()
        mock_get_redis.return_value = mock_redis

        payload = {"digits": "2,0#", "reason": "Supervisor IVR selection"}
        response = self.client.post(
            "/api/client/calls/call-abc-123/dtmf",
            json=payload,
            headers=self.auth_headers,
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "transmitted")
        self.assertEqual(data["call_id"], "call-abc-123")
        self.assertEqual(data["digits"], "2,0#")

        # Check call_control channel publication
        mock_redis.publish.assert_any_call(
            "call_control:call-abc-123",
            json.dumps({"action": "send_dtmf", "digits": "2,0#", "inter_delay_ms": 250, "supervisor_name": "Supervisor"}),
        )

    def test_send_client_dtmf_invalid_chars(self):
        """Verify invalid DTMF digits return 400 Bad Request."""
        payload = {"digits": "99Z#", "reason": "Invalid tone"}
        response = self.client.post(
            "/api/client/calls/call-abc-123/dtmf",
            json=payload,
            headers=self.auth_headers,
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid DTMF sequence", response.json()["detail"])

    # -------------------------------------------------------------------------
    # 6. Database Migration 012 & Telemetry dtmf_events Persistence
    # -------------------------------------------------------------------------
    def test_migration_012_structure(self):
        """Verify migration 012 is registered in MIGRATIONS list."""
        migration_names = [m["name"] for m in MIGRATIONS]
        self.assertIn("dtmf_telephony_support", migration_names)

    def test_migration_012_execution(self):
        """Verify migration 012 executes SQL safely."""
        async def run_mig():
            mock_conn = MagicMock()
            mock_conn.execute = AsyncMock()
            await migration_012_dtmf_telephony_support(mock_conn)
            self.assertEqual(mock_conn.execute.call_count, 1)

        asyncio.run(run_mig())

    @patch("telemetry._pool")
    def test_complete_call_record_persists_dtmf_events(self, mock_pool):
        """Verify complete_call_record persists dtmf_events into database."""
        async def run_complete():
            mock_conn = MagicMock()
            mock_conn.execute = AsyncMock()
            mock_pool.acquire.return_value = AsyncContextManagerMock(mock_conn)

            dtmf_history = [
                {"direction": "inbound", "digits": "1234#", "timestamp": "2026-09-09T01:00:00Z"},
                {"direction": "outbound", "digits": "1", "reason": "Menu select", "timestamp": "2026-09-09T01:00:05Z"},
            ]

            success = await complete_call_record(
                call_id="call-dtmf-test",
                tenant_id=self.test_tenant_id,
                duration_seconds=120,
                dtmf_events=dtmf_history,
            )
            self.assertTrue(success)

            # Inspect SQL execute call arguments
            mock_conn.execute.assert_called_once()
            args = mock_conn.execute.call_args[0]
            sql = args[0]
            self.assertIn("dtmf_events = COALESCE($9::jsonb, dtmf_events)", sql)
            dtmf_param = args[9]
            self.assertEqual(json.loads(dtmf_param), dtmf_history)

        asyncio.run(run_complete())


if __name__ == "__main__":
    unittest.main()
