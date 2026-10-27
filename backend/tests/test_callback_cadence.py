"""
Unit & Integration Tests for Phase 22: Intelligent Multi-Touch Callback Cadence & Timezone Guardrails.
"""

from datetime import datetime, timezone
import json
import unittest
from unittest.mock import AsyncMock, patch
from zoneinfo import ZoneInfo

from migrations import migration_017_callback_cadence_and_timezone
from timezone_guardrails import (
    calculate_next_cadence_attempt,
    extract_npa_area_code,
    is_within_legal_calling_hours,
    resolve_phone_timezone,
)
from worker import execute_callback_touch, process_callback_cadence_queue


class TestAreaCodeTimezoneMapping(unittest.TestCase):
    """Tests NANPA phone area code extraction and timezone resolution."""

    def test_area_code_extraction(self):
        test_cases = [
            ("+1 (415) 555-1234", "415"),
            ("1-415-555-1234", "415"),
            ("4155551234", "415"),
            ("+14155551234", "415"),
            ("(212) 555-9876", "212"),
            ("312-555-0011", "312"),
            ("invalid", None),
            ("", None),
        ]
        for raw, expected in test_cases:
            self.assertEqual(extract_npa_area_code(raw), expected)

    def test_timezone_resolution_us_regions(self):
        # Eastern: NYC
        nyc = resolve_phone_timezone("+1 (212) 555-0100")
        self.assertTrue(nyc["is_valid"])
        self.assertEqual(nyc["timezone"], "America/New_York")
        self.assertEqual(nyc["state"], "NY")

        # Central: Chicago
        chi = resolve_phone_timezone("+1 (312) 555-0100")
        self.assertTrue(chi["is_valid"])
        self.assertEqual(chi["timezone"], "America/Chicago")
        self.assertEqual(chi["state"], "IL")

        # Mountain: Denver
        den = resolve_phone_timezone("+1 (303) 555-0100")
        self.assertTrue(den["is_valid"])
        self.assertEqual(den["timezone"], "America/Denver")
        self.assertEqual(den["state"], "CO")

        # Arizona (No DST)
        phx = resolve_phone_timezone("+1 (602) 555-0100")
        self.assertTrue(phx["is_valid"])
        self.assertEqual(phx["timezone"], "America/Phoenix")
        self.assertEqual(phx["state"], "AZ")

        # Pacific: San Francisco
        sf = resolve_phone_timezone("+1 (415) 555-0100")
        self.assertTrue(sf["is_valid"])
        self.assertEqual(sf["timezone"], "America/Los_Angeles")
        self.assertEqual(sf["state"], "CA")

        # Alaska
        ak = resolve_phone_timezone("+1 (907) 555-0100")
        self.assertTrue(ak["is_valid"])
        self.assertEqual(ak["timezone"], "America/Anchorage")
        self.assertEqual(ak["state"], "AK")

        # Hawaii
        hi = resolve_phone_timezone("+1 (808) 555-0100")
        self.assertTrue(hi["is_valid"])
        self.assertEqual(hi["timezone"], "Pacific/Honolulu")
        self.assertEqual(hi["state"], "HI")

        # Canada: Toronto
        tor = resolve_phone_timezone("+1 (416) 555-0100")
        self.assertTrue(tor["is_valid"])
        self.assertEqual(tor["timezone"], "America/Toronto")
        self.assertEqual(tor["country"], "CA")


class TestTCPAComplianceHours(unittest.TestCase):
    """Tests Federal and State TCPA legal calling hours evaluation."""

    def test_daytime_call_permitted(self):
        # 2:30 PM EDT (14:30 EDT = 18:30 UTC in Summer)
        dt_day = datetime(2026, 6, 15, 18, 30, tzinfo=timezone.utc)
        permitted, reason, _ = is_within_legal_calling_hours("+1 (212) 555-0100", as_of=dt_day)
        self.assertTrue(permitted)
        self.assertIn("Legal calling hours active", reason)

    def test_late_night_call_quiet_hours_postponed(self):
        # 11:30 PM EDT (23:30 EDT = 03:30 UTC next day in Summer)
        dt_night = datetime(2026, 6, 16, 3, 30, tzinfo=timezone.utc)
        permitted, reason, next_utc = is_within_legal_calling_hours("+1 (212) 555-0100", as_of=dt_night)
        self.assertFalse(permitted)
        self.assertIn("Quiet hours: too late", reason)

        # Confirm next_utc is 8:05 AM EDT (12:05 UTC)
        next_local = next_utc.astimezone(ZoneInfo("America/New_York"))
        self.assertEqual(next_local.hour, 8)
        self.assertEqual(next_local.minute, 5)

    def test_early_morning_call_quiet_hours_postponed(self):
        # 6:15 AM PDT (06:15 PDT = 13:15 UTC in Summer)
        dt_early = datetime(2026, 6, 15, 13, 15, tzinfo=timezone.utc)
        permitted, reason, next_utc = is_within_legal_calling_hours("+1 (415) 555-0100", as_of=dt_early)
        self.assertFalse(permitted)
        self.assertIn("Quiet hours: too early", reason)

        # Confirm next_utc is 8:05 AM PDT (15:05 UTC)
        next_local = next_utc.astimezone(ZoneInfo("America/Los_Angeles"))
        self.assertEqual(next_local.hour, 8)
        self.assertEqual(next_local.minute, 5)

    def test_florida_strict_tcpa_8pm_limit(self):
        # 8:15 PM local (20:15) is permitted federally (before 9 PM),
        # but in Florida (FL), it is prohibited past 8:00 PM (20:00).
        # In Summer: 20:15 EDT = 00:15 UTC next day
        dt_test = datetime(2026, 6, 16, 0, 15, tzinfo=timezone.utc)

        # Florida number (Miami: 305)
        fl_permitted, fl_reason, _ = is_within_legal_calling_hours(
            "+1 (305) 555-0100", as_of=dt_test, strict_state_rules=True
        )
        self.assertFalse(fl_permitted)
        self.assertIn("Quiet hours: too late", fl_reason)

        # New York number (212) at same moment: permitted federally
        ny_permitted, ny_reason, _ = is_within_legal_calling_hours(
            "+1 (212) 555-0100", as_of=dt_test, strict_state_rules=True
        )
        self.assertTrue(ny_permitted)


class TestCadenceIntervalCalculation(unittest.TestCase):
    """Tests 3-touch retry interval computation."""

    def test_touch_1_immediate_when_permitted(self):
        dt_noon = datetime(2026, 6, 15, 16, 0, tzinfo=timezone.utc)
        target, status = calculate_next_cadence_attempt("+1 (212) 555-0100", attempt=1, base_time=dt_noon)
        self.assertEqual(status, "immediate")
        self.assertEqual(target, dt_noon)

    def test_touch_2_plus_2_hours(self):
        dt_noon = datetime(2026, 6, 15, 16, 0, tzinfo=timezone.utc)
        target, status = calculate_next_cadence_attempt("+1 (212) 555-0100", attempt=2, base_time=dt_noon)
        self.assertEqual(status, "scheduled_touch_2")
        self.assertEqual(target, datetime(2026, 6, 15, 18, 0, tzinfo=timezone.utc))

    def test_touch_3_next_day_10am_local(self):
        dt_noon = datetime(2026, 6, 15, 16, 0, tzinfo=timezone.utc)
        target_utc, status = calculate_next_cadence_attempt("+1 (415) 555-0100", attempt=3, base_time=dt_noon)
        self.assertEqual(status, "scheduled_touch_3")

        # Recipient is Pacific (Los Angeles): 10:00 AM PDT on June 16 = 17:00 UTC
        target_local = target_utc.astimezone(ZoneInfo("America/Los_Angeles"))
        self.assertEqual(target_local.day, 16)
        self.assertEqual(target_local.hour, 10)
        self.assertEqual(target_local.minute, 0)


class TestMigration017(unittest.IsolatedAsyncioTestCase):
    """Tests Migration 017 database schema updates."""

    async def test_migration_017_executes_alter_and_indexes(self):
        mock_conn = AsyncMock()
        await migration_017_callback_cadence_and_timezone(mock_conn)

        self.assertTrue(mock_conn.execute.called)
        executed_sqls = [call[0][0] for call in mock_conn.execute.call_args_list]
        combined_sql = " ".join(executed_sqls)

        self.assertIn("attempt_count", combined_sql)
        self.assertIn("max_attempts", combined_sql)
        self.assertIn("next_attempt_at", combined_sql)
        self.assertIn("recipient_timezone", combined_sql)
        self.assertIn("cadence_status", combined_sql)
        self.assertIn("attempt_history", combined_sql)
        self.assertIn("idx_callbacks_cadence_poll", combined_sql)


class TestCallbackCadenceWorker(unittest.IsolatedAsyncioTestCase):
    """Tests worker background tasks: execute_callback_touch and process_callback_cadence_queue."""

    @patch("worker._pool")
    async def test_execute_touch_quiet_hours_postponed(self, mock_pool):
        # Simulate late night call to California (11:00 PM PDT = 06:00 UTC next day)
        late_night_utc = datetime(2026, 6, 16, 6, 0, tzinfo=timezone.utc)

        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        mock_conn.fetchrow.return_value = {
            "id": 101,
            "callback_id": "cb-uuid-1",
            "caller_phone": "+14155551234",
            "caller_name": "John Doe",
            "reason": "Consultation",
            "tenant_id": "tenant-test",
            "attempt_count": 0,
            "max_attempts": 3,
            "sms_notice_sent": False,
            "attempt_history": "[]",
        }

        result = await execute_callback_touch(None, "101", force=False, as_of=late_night_utc)
        self.assertEqual(result["status"], "postponed")
        self.assertIn("Quiet hours", result["reason"])

        # Verify DB update was called to postpone
        self.assertTrue(mock_conn.execute.called)

    @patch("telephony_provider.send_sms", new_callable=AsyncMock)
    @patch("worker._pool")
    async def test_execute_touch_3_sends_sms_and_exhausts(self, mock_pool, mock_send_sms):
        # Permitted daytime hour (2:00 PM EDT = 18:00 UTC)
        daytime_utc = datetime(2026, 6, 16, 18, 0, tzinfo=timezone.utc)

        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        # Callback already has 2 attempts; this is Touch 3
        mock_conn.fetchrow.return_value = {
            "id": 102,
            "callback_id": "cb-uuid-2",
            "caller_phone": "+12125551234",
            "caller_name": "Alice Smith",
            "reason": "Property Viewing",
            "tenant_id": "tenant-test",
            "attempt_count": 2,
            "max_attempts": 3,
            "sms_notice_sent": False,
            "attempt_history": json.dumps([
                {"touch": 1, "action": "call_dispatched"},
                {"touch": 2, "action": "call_dispatched"},
            ]),
        }

        mock_send_sms.return_value = {"status": "sent", "provider": "Twilio Live SMS"}

        result = await execute_callback_touch(None, "102", force=False, as_of=daytime_utc)
        self.assertEqual(result["status"], "dispatched")
        self.assertEqual(result["touch"], 3)
        self.assertEqual(result["cadence_status"], "exhausted")
        self.assertTrue(result["sms_notice_sent"])

        # Verify automated SMS was sent
        mock_send_sms.assert_called_once()
        call_kwargs = mock_send_sms.call_args[1]
        self.assertEqual(call_kwargs["to_phone"], "+12125551234")
        self.assertIn("Alice Smith", call_kwargs["message"])

    @patch("worker.execute_callback_touch", new_callable=AsyncMock)
    @patch("worker._pool")
    async def test_process_callback_cadence_queue_processes_due(self, mock_pool, mock_execute_touch):
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        mock_conn.fetch.return_value = [
            {"id": 1, "callback_id": "uuid-1", "caller_phone": "+12125550001"},
            {"id": 2, "callback_id": "uuid-2", "caller_phone": "+14155550002"},
        ]

        processed_count = await process_callback_cadence_queue(None)
        self.assertEqual(processed_count, 2)
        self.assertEqual(mock_execute_touch.call_count, 2)


class TestCallbackClientAPIs(unittest.TestCase):
    """Tests client REST API endpoints for callback queue, summary, retry, and cancellation."""

    def setUp(self):
        from fastapi.testclient import TestClient
        from api import app
        from auth import create_access_token
        self.client = TestClient(app)
        self.tenant_id = "00000000-0000-0000-0000-000000000001"
        self.token = create_access_token({
            "sub": self.tenant_id,
            "role": "client_admin",
            "tenant_id": self.tenant_id,
        })
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @patch("routes.client_routes._pool")
    def test_get_callbacks_hydrates_timezone(self, mock_pool):
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.fetch.return_value = [
            {
                "id": 101,
                "callback_id": "cb-uuid-1",
                "tenant_id": self.tenant_id,
                "caller_name": "Jane Doe",
                "caller_phone": "+1 (415) 555-1234",
                "target_department": "Support",
                "preferred_time": "Immediate",
                "reason": "General question",
                "notes": "",
                "status": "scheduled",
                "cadence_status": "pending",
                "attempt_count": 1,
                "max_attempts": 3,
                "next_attempt_at": datetime(2026, 6, 16, 18, 0, tzinfo=timezone.utc),
                "last_attempt_at": datetime(2026, 6, 16, 16, 0, tzinfo=timezone.utc),
                "recipient_timezone": "America/Los_Angeles",
                "recipient_state": "CA",
                "sms_notice_sent": False,
                "attempt_history": json.dumps([{"touch": 1, "action": "call_dispatched"}]),
                "created_at": datetime(2026, 6, 16, 15, 0, tzinfo=timezone.utc),
            }
        ]

        resp = self.client.get("/api/client/callbacks", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        items = data["items"] if isinstance(data, dict) and "items" in data else data
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item["recipient_timezone"], "America/Los_Angeles")
        self.assertEqual(item["recipient_state"], "CA")
        self.assertIn("is_legal_now", item)
        self.assertIn("recipient_local_time", item)

    @patch("routes.client_routes._pool")
    def test_get_callbacks_summary(self, mock_pool):
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        mock_conn.fetch.return_value = [
            {
                "status": "scheduled",
                "cadence_status": "pending",
                "caller_phone": "+1 (212) 555-0100",
            },
            {
                "status": "completed",
                "cadence_status": "completed",
                "caller_phone": "+1 (415) 555-0200",
            },
            {
                "status": "scheduled",
                "cadence_status": "exhausted",
                "caller_phone": "+1 (312) 555-0300",
            },
        ]

        resp = self.client.get("/api/client/callbacks/summary", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        summary = resp.json()
        self.assertEqual(summary["total_callbacks"], 3)
        self.assertEqual(summary["completed"], 1)
        self.assertEqual(summary["exhausted"], 1)
        self.assertEqual(summary["in_cadence"], 1)

    @patch("worker.execute_callback_touch", new_callable=AsyncMock)
    def test_post_callback_retry(self, mock_touch):
        mock_touch.return_value = {"status": "dispatched", "touch": 2}
        resp = self.client.post("/api/client/callbacks/101/retry?force=true", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "dispatched")
        mock_touch.assert_called_once_with(None, "101", force=True)

    @patch("routes.client_routes._pool")
    def test_post_callback_cancel(self, mock_pool):
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn
        resp = self.client.post("/api/client/callbacks/101/cancel", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "cancelled")
        self.assertTrue(mock_conn.execute.called)


if __name__ == "__main__":
    unittest.main()
