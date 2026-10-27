"""
Unit and Integration Test Suite for Phase 23: Production Hardening Sprint.
Validates:
  1. Transaction atomicity and row-locking in process_billing.
  2. Retry infrastructure (TransientJobError) and Dead Letter Queue recording.
  3. WorkerSettings operational configuration (max_tries, timeout, backoff).
  4. Input validation and strict enum rejection on callback and lead PATCH endpoints.
  5. Response-shape pagination on GET /callbacks, GET /leads, and offset support.
  6. Sandbox-mode gating for mock calls and metrics.
  7. Runtime dependency health check endpoint (/api/health/dependencies).
  8. Sweeper job isolation via ARQ enqueueing.
  9. Database Migration 018 schema and index creation.
"""
import unittest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from api import app
from auth import create_access_token
from config import settings
from dead_letter import record_dead_letter
from migrations import migration_018_production_hardening
from worker import (
    TransientJobError,
    WorkerSettings,
    process_billing,
    process_callback_cadence_queue,
)


class AsyncContextManagerMock:
    def __init__(self, target):
        self.target = target

    async def __aenter__(self):
        return self.target

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


class TestProductionHardeningP23(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.token = create_access_token(
            data={"sub": "user-test-admin", "tenant_id": "00000000-0000-0000-0000-000000000001", "role": "client_admin"}
        )
        self.headers = {"Authorization": f"Bearer {self.token}"}

    # =========================================================================
    # Work Item 1 & 2: Database Transactions, Row Locking, and DLQ
    # =========================================================================

    @patch("worker._pool")
    async def test_billing_row_lock_and_atomic_deduction(self, mock_pool):
        """Verify process_billing uses FOR UPDATE lock and atomic RETURNING deduction."""
        mock_conn = AsyncMock()
        mock_conn.fetchrow.return_value = {
            "subscription_tier": "pro",
            "included_minutes_balance": 100,
            "custom_per_minute_rate": 0.09,
        }
        mock_conn.fetchval.return_value = 85  # Remaining after 15 min call
        mock_pool.acquire.return_value = AsyncContextManagerMock(mock_conn)

        ctx = {"job_try": 1}
        success = await process_billing(ctx, "call_test_101", "tenant_1", duration=900, total_tokens=1500, base_cost_usd=0.0)
        self.assertTrue(success)

        # Assert FOR UPDATE was queried
        select_query = mock_conn.fetchrow.call_args[0][0]
        self.assertIn("FOR UPDATE", select_query)

        # Assert atomic GREATEST deduction
        update_query = mock_conn.fetchval.call_args[0][0]
        self.assertIn("GREATEST(0, included_minutes_balance - $1)", update_query)
        self.assertIn("RETURNING included_minutes_balance", update_query)

    @patch("worker._pool")
    async def test_billing_overage_charge_when_balance_exhausted(self, mock_pool):
        """Verify overage is recorded into credit transactions when included minutes are 0."""
        mock_conn = AsyncMock()
        mock_conn.fetchrow.return_value = {
            "subscription_tier": "plus",
            "included_minutes_balance": 0,
            "custom_per_minute_rate": 0.12,
        }
        mock_pool.acquire.return_value = AsyncContextManagerMock(mock_conn)

        ctx = {"job_try": 1}
        success = await process_billing(ctx, "call_test_102", "tenant_1", duration=300, total_tokens=500, base_cost_usd=0.0)
        self.assertTrue(success)

        # 5 minutes at $0.12/min = $0.60
        self.assertTrue(mock_conn.execute.called)
        executed_sqls = [call[0][0] for call in mock_conn.execute.call_args_list]
        self.assertTrue(any("alfie_credit_transactions" in sql for sql in executed_sqls))
        self.assertTrue(any("alfie_call_recordings" in sql for sql in executed_sqls))

    @patch("worker._pool")
    async def test_transient_error_raises_for_retry(self, mock_pool):
        """Verify TransientJobError is re-raised on database error when attempts remain."""
        mock_conn = AsyncMock()
        mock_conn.fetchrow.side_effect = Exception("Connection timed out")
        mock_pool.acquire.return_value = AsyncContextManagerMock(mock_conn)

        ctx = {"job_try": 1}  # Attempt 1 of 3
        with patch("worker.DB_ERRORS", (Exception,)):
            with self.assertRaises(TransientJobError):
                await process_billing(ctx, "call_fail_1", "tenant_1", duration=60, total_tokens=100, base_cost_usd=0.0)

    @patch("worker.record_dead_letter", new_callable=AsyncMock)
    @patch("worker._pool")
    async def test_dead_letter_called_when_max_tries_exhausted(self, mock_pool, mock_record_dlq):
        """Verify job failure is recorded in DLQ on final attempt (job_try >= 3)."""
        mock_conn = AsyncMock()
        mock_conn.fetchrow.side_effect = Exception("Unrecoverable DB crash")
        mock_pool.acquire.return_value = AsyncContextManagerMock(mock_conn)

        ctx = {"job_try": 3}  # Final attempt
        with patch("worker.DB_ERRORS", (Exception,)):
            result = await process_billing(ctx, "call_exhaust_1", "tenant_1", duration=60, total_tokens=100, base_cost_usd=0.0)
            self.assertFalse(result)
            mock_record_dlq.assert_called_once()
            args = mock_record_dlq.call_args[0]
            self.assertEqual(args[1], "process_billing")
            self.assertEqual(mock_record_dlq.call_args.kwargs.get("attempts"), 3)

    async def test_record_dead_letter_helper(self):
        """Verify record_dead_letter persists failed job metadata to DB."""
        mock_conn = AsyncMock()
        mock_conn.fetchval.return_value = 42

        dlq_id = await record_dead_letter(
            mock_conn,
            job_name="sync_crm_lead",
            job_args={"tenant_id": "tenant-1", "lead_id": "lead-99"},
            error="HTTP 500 External API Unreachable",
            attempts=3,
        )
        self.assertEqual(dlq_id, 42)
        mock_conn.fetchval.assert_called_once()
        sql = mock_conn.fetchval.call_args[0][0]
        self.assertIn("alfie_dead_letter_queue", sql)

    def test_worker_settings_has_retry_config(self):
        """Verify WorkerSettings declares production retry backoff and timeout parameters."""
        self.assertEqual(WorkerSettings.max_tries, 3)
        self.assertEqual(WorkerSettings.retry_delay, 30)
        self.assertEqual(WorkerSettings.job_timeout, 120)
        self.assertEqual(WorkerSettings.max_jobs, 10)

    # =========================================================================
    # Work Item 3: Input Validation & Status Enums
    # =========================================================================

    @patch("routes.client_routes._pool")
    def test_callback_status_validation_accepts_valid(self, mock_pool):
        """Verify PATCH /api/client/callbacks/{id} accepts valid enum status."""
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManagerMock(mock_conn)

        resp = self.client.patch(
            "/api/client/callbacks/101",
            json={"status": "completed"},
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "updated")
        self.assertEqual(data["new_status"], "completed")

    @patch("routes.client_routes._pool")
    def test_callback_status_validation_rejects_invalid(self, mock_pool):
        """Verify PATCH /api/client/callbacks/{id} returns 422 on invalid status enum."""
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManagerMock(mock_conn)

        resp = self.client.patch(
            "/api/client/callbacks/101",
            json={"status": "bogus_status_attempt"},
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 422)

    @patch("routes.client_routes._pool")
    def test_callback_id_validation_rejects_garbage_id(self, mock_pool):
        """Verify non-integer and non-UUID ID string returns 400."""
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManagerMock(mock_conn)

        resp = self.client.patch(
            "/api/client/callbacks/invalid;drop_table;",
            json={"status": "completed"},
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 400)

    @patch("routes.client_routes._pool")
    def test_lead_status_validation_accepts_valid(self, mock_pool):
        """Verify PATCH /api/client/leads/{id}/status accepts valid enum."""
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManagerMock(mock_conn)

        resp = self.client.patch(
            "/api/client/leads/202/status",
            json={"status": "qualified"},
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["new_status"], "qualified")

    @patch("routes.client_routes._pool")
    def test_lead_status_validation_rejects_invalid(self, mock_pool):
        """Verify PATCH /api/client/leads/{id}/status returns 422 on invalid status."""
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value = AsyncContextManagerMock(mock_conn)

        resp = self.client.patch(
            "/api/client/leads/202/status",
            json={"status": "invalid_lead_stage"},
            headers=self.headers,
        )
        self.assertEqual(resp.status_code, 422)

    # =========================================================================
    # Work Item 4: Pagination on List Endpoints
    # =========================================================================

    @patch("routes.client_routes._pool")
    def test_callbacks_list_pagination(self, mock_pool):
        """Verify GET /api/client/callbacks returns {items, total, page, page_size}."""
        mock_conn = AsyncMock()
        mock_conn.fetchval.return_value = 1
        mock_conn.fetch.return_value = [
            {
                "id": 1,
                "caller_phone": "+14155550199",
                "caller_name": "Test Caller",
                "recipient_timezone": "America/Los_Angeles",
                "recipient_state": "CA",
                "status": "scheduled",
                "cadence_status": "pending",
                "attempt_count": 0,
                "max_attempts": 3,
                "created_at": datetime(2026, 6, 16, 12, 0, tzinfo=timezone.utc),
                "attempt_history": "[]",
            }
        ]
        mock_pool.acquire.return_value = AsyncContextManagerMock(mock_conn)

        resp = self.client.get("/api/client/callbacks?page=1&page_size=25", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("items", data)
        self.assertIn("total", data)
        self.assertEqual(data["page"], 1)
        self.assertEqual(data["page_size"], 25)
        self.assertEqual(len(data["items"]), 1)

    @patch("routes.client_routes._pool")
    def test_leads_list_pagination(self, mock_pool):
        """Verify GET /api/client/leads returns {items, total, page, page_size}."""
        mock_conn = AsyncMock()
        mock_conn.fetchval.return_value = 2
        mock_conn.fetch.return_value = [
            {
                "id": 1,
                "name": "Jane Doe",
                "phone": "+12125550188",
                "lead_score": 9,
                "notes": "Hot prospect",
                "status": "new",
                "created_at": datetime(2026, 6, 16, 12, 0, tzinfo=timezone.utc),
            }
        ]
        mock_pool.acquire.return_value = AsyncContextManagerMock(mock_conn)

        resp = self.client.get("/api/client/leads?page=1&page_size=10", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("items", data)
        self.assertIn("total", data)
        self.assertEqual(data["page"], 1)
        self.assertEqual(data["page_size"], 10)

    # =========================================================================
    # Work Item 5: Sweeper Job Isolation
    # =========================================================================

    @patch("worker.execute_callback_touch", new_callable=AsyncMock)
    @patch("worker._pool")
    async def test_sweeper_enqueues_jobs(self, mock_pool, mock_execute_touch):
        """Verify sweeper enqueues each touch as an independent ARQ background job."""
        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = [
            {"id": 101, "callback_id": "cb-uuid-1", "caller_phone": "+14155551234"},
            {"id": 102, "callback_id": "cb-uuid-2", "caller_phone": "+12125559876"},
        ]
        mock_pool.acquire.return_value = AsyncContextManagerMock(mock_conn)

        mock_redis = AsyncMock()
        ctx = {"redis": mock_redis}

        processed = await process_callback_cadence_queue(ctx)
        self.assertEqual(processed, 2)
        # Verify redis.enqueue_job was called twice rather than synchronous execution
        self.assertEqual(mock_redis.enqueue_job.call_count, 2)
        self.assertEqual(mock_execute_touch.call_count, 0)

    # =========================================================================
    # Work Item 6: Sandbox-Gated Mock Data
    # =========================================================================

    @patch("routes.client_routes._pool")
    def test_interactions_mock_data_hidden_in_production(self, mock_pool):
        """When settings.sandbox_mode is False, empty DB results return empty list (no fake mock logs)."""
        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = []
        mock_conn.fetchval.return_value = 0
        mock_pool.acquire.return_value = AsyncContextManagerMock(mock_conn)

        with patch.object(settings, "sandbox_mode", False):
            resp = self.client.get("/api/client/interactions", headers=self.headers)
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertEqual(data, [])

    @patch("routes.client_routes._pool")
    def test_interactions_mock_data_visible_in_sandbox(self, mock_pool):
        """When settings.sandbox_mode is True, empty DB results provide synthetic mock calls."""
        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = []
        mock_conn.fetchval.return_value = 0
        mock_pool.acquire.return_value = AsyncContextManagerMock(mock_conn)

        with patch.object(settings, "sandbox_mode", True):
            resp = self.client.get("/api/client/interactions", headers=self.headers)
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertGreater(len(data), 0)
            self.assertIn("call_mock_1", [c["id"] for c in data])

    # =========================================================================
    # Work Item 7: Dependency Health Endpoint
    # =========================================================================

    @patch("api.get_redis")
    @patch("telemetry._pool")
    def test_dependency_health_endpoint(self, mock_pool, mock_get_redis):
        """Verify /api/health/dependencies queries external services and reports status booleans."""
        mock_conn = AsyncMock()
        mock_conn.fetchval.return_value = 1
        mock_pool.acquire.return_value = AsyncContextManagerMock(mock_conn)

        mock_redis = AsyncMock()
        mock_redis.ping.return_value = True
        mock_redis.exists.return_value = 0
        mock_redis.get.return_value = None
        mock_pipeline = MagicMock()
        mock_pipeline.execute = AsyncMock(return_value=[1, True])
        mock_redis.pipeline = MagicMock(return_value=mock_pipeline)
        mock_get_redis.return_value = mock_redis

        resp = self.client.get("/api/health/dependencies")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("status", data)
        self.assertIn("checks", data)
        checks = data["checks"]
        self.assertTrue(checks["postgresql"])
        self.assertTrue(checks["redis"])
        self.assertIn("twilio_configured", checks)
        self.assertIn("openrouter_configured", checks)
        self.assertIn("livekit_configured", checks)

    # =========================================================================
    # Migration 018: Production Hardening DDL
    # =========================================================================

    async def test_migration_018_dead_letter_ddl(self):
        """Verify migration_018 executes table and index creation for DLQ."""
        mock_conn = AsyncMock()
        await migration_018_production_hardening(mock_conn)
        mock_conn.execute.assert_called_once()
        ddl_sql = mock_conn.execute.call_args[0][0]
        self.assertIn("alfie_dead_letter_queue", ddl_sql)
        self.assertIn("idx_dead_letter_unresolved", ddl_sql)
        self.assertIn("idx_dead_letter_created", ddl_sql)


if __name__ == "__main__":
    unittest.main()
