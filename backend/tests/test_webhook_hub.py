"""
Unit and Integration Tests for Phase 20: Outbound Webhook Automation Hub.
Tests HMAC-SHA256 signing, multi-tenant fanout, event type filtering,
exponential backoff retries, test ping delivery, and REST CRUD endpoints.
"""

import hashlib
import hmac
import json
import os
import sys
import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DEEPGRAM_API_KEY", "mock_key")
os.environ.setdefault("OPENROUTER_API_KEY", "mock_key")
os.environ.setdefault("FISH_AUDIO_API_KEY", "mock_key")
os.environ.setdefault("JWT_SECRET_KEY", "test_secret_key_for_unit_tests_32chars!")
os.environ.setdefault("SUPER_ADMIN_EMAIL", "admin@alfie-ai.com")
os.environ.setdefault("SUPER_ADMIN_PASSWORD", "testpass")

from auth import create_access_token
from fastapi.testclient import TestClient
from api import app
from webhook_dispatcher import (
    compute_hmac_signature,
    generate_signing_secret,
    dispatch_webhook,
    retry_webhook_delivery,
    send_test_ping,
    RETRY_DELAYS,
    MAX_RETRY_ATTEMPTS,
)


class TestWebhookCryptographicSignatures(unittest.TestCase):
    """Test 1 & 5: Cryptographic HMAC-SHA256 signature generation and backoff schedules."""

    def test_hmac_sha256_computation_exactness(self):
        """Verify HMAC-SHA256 signature conforms to standard RFC 2104 hex digest."""
        secret = "whsec_test_secret_1234567890abcdef"
        payload = json.dumps({"event": "call.completed", "call_id": "test_123"}).encode("utf-8")

        expected = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
        computed = compute_hmac_signature(payload, secret)

        self.assertEqual(computed, expected)
        self.assertEqual(len(computed), 64)

    def test_generate_signing_secret_format(self):
        """Verify generated secrets have whsec_ prefix and high entropy."""
        secret1 = generate_signing_secret()
        secret2 = generate_signing_secret()

        self.assertTrue(secret1.startswith("whsec_"))
        self.assertTrue(secret2.startswith("whsec_"))
        self.assertNotEqual(secret1, secret2)
        self.assertGreaterEqual(len(secret1), 32)

    def test_exponential_backoff_schedule_timing(self):
        """Verify delay sequence strictly follows 30s -> 2m -> 10m -> 1h -> 6h."""
        self.assertEqual(RETRY_DELAYS, [30, 120, 600, 3600, 21600])
        self.assertEqual(MAX_RETRY_ATTEMPTS, 5)


class TestWebhookDispatchAndFanout(unittest.IsolatedAsyncioTestCase):
    """Tests 2, 3, 4, 6, 7, 10: Dispatching, filtering, retries, and test ping."""

    def setUp(self):
        self.tenant_id = str(uuid.uuid4())
        self.webhook_id = uuid.uuid4()
        self.signing_secret = "whsec_mock_secret_key_12345"

    @patch("webhook_dispatcher._pool")
    @patch("webhook_dispatcher.get_http_client")
    async def test_dispatch_webhook_matching_active_endpoints(self, mock_get_client, mock_pool):
        """Test 2: Outbound event fans out to active endpoints subscribed to event_type."""
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        mock_conn.fetch.return_value = [
            {
                "webhook_id": self.webhook_id,
                "name": "Zapier CRM Sync",
                "target_url": "https://hooks.zapier.com/test",
                "signing_secret": self.signing_secret,
                "event_types": ["call.completed", "lead.qualified"],
                "is_active": True,
            }
        ]

        mock_client = AsyncMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '{"status":"ok"}'
        mock_client.post.return_value = mock_resp
        mock_get_client.return_value = mock_client

        results = await dispatch_webhook(
            tenant_id=self.tenant_id,
            event_type="call.completed",
            payload={"call_id": "call-1", "duration": 120},
            reference_id="call-1",
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["status"], "succeeded")
        self.assertEqual(results[0]["http_status_code"], 200)
        mock_client.post.assert_called_once()
        headers = mock_client.post.call_args[1]["headers"]
        self.assertIn("X-ALFIE-Signature", headers)
        self.assertEqual(headers["X-ALFIE-Event"], "call.completed")

    @patch("webhook_dispatcher._pool")
    @patch("webhook_dispatcher.get_http_client")
    async def test_non_matching_event_types_are_skipped(self, mock_get_client, mock_pool):
        """Test 3: Endpoints subscribed only to call.completed do NOT receive lead.qualified."""
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        mock_conn.fetch.return_value = [
            {
                "webhook_id": self.webhook_id,
                "name": "Call Completed Only",
                "target_url": "https://example.com/calls",
                "signing_secret": self.signing_secret,
                "event_types": ["call.completed"],
                "is_active": True,
            }
        ]

        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        results = await dispatch_webhook(
            tenant_id=self.tenant_id,
            event_type="lead.qualified",
            payload={"name": "Alice"},
        )

        self.assertEqual(results, [])
        mock_client.post.assert_not_called()

    @patch("webhook_dispatcher._pool")
    @patch("webhook_dispatcher.get_http_client")
    @patch("webhook_dispatcher._enqueue_retry_job")
    async def test_failed_delivery_creates_retry_job(self, mock_enqueue, mock_get_client, mock_pool):
        """Test 4: HTTP 500 error marks delivery retrying and enqueues ARQ retry job."""
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        mock_conn.fetch.return_value = [
            {
                "webhook_id": self.webhook_id,
                "name": "Failing Webhook",
                "target_url": "https://example.com/failing",
                "signing_secret": self.signing_secret,
                "event_types": ["call.completed"],
                "is_active": True,
            }
        ]

        mock_client = AsyncMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"
        mock_client.post.return_value = mock_resp
        mock_get_client.return_value = mock_client

        results = await dispatch_webhook(
            tenant_id=self.tenant_id,
            event_type="call.completed",
            payload={"call_id": "call-500"},
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["status"], "retrying")
        mock_enqueue.assert_called_once()
        self.assertEqual(mock_enqueue.call_args[0][1], 30)  # First delay is 30s

    @patch("webhook_dispatcher._pool")
    @patch("webhook_dispatcher.get_http_client")
    @patch("webhook_dispatcher._enqueue_retry_job")
    async def test_max_retry_cap_stops_enqueuing(self, mock_enqueue, mock_get_client, mock_pool):
        """Test 6: When attempt reaches max_attempts (5), status marks failed and retries halt."""
        delivery_id = uuid.uuid4()
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        mock_conn.fetchrow.return_value = {
            "delivery_id": delivery_id,
            "webhook_id": self.webhook_id,
            "tenant_id": self.tenant_id,
            "event_type": "call.completed",
            "payload": {"call_id": "c1"},
            "reference_id": "c1",
            "status": "retrying",
            "attempt_number": 4,  # Next attempt is 5
            "max_attempts": 5,
            "target_url": "https://example.com/failing",
            "signing_secret": self.signing_secret,
            "is_active": True,
            "name": "Webhook",
        }

        mock_client = AsyncMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 503
        mock_resp.text = "Service Unavailable"
        mock_client.post.return_value = mock_resp
        mock_get_client.return_value = mock_client

        result = await retry_webhook_delivery(None, str(delivery_id))

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["attempt"], 5)
        # Should not enqueue any more retries
        mock_enqueue.assert_not_called()

    @patch("webhook_dispatcher._pool")
    @patch("webhook_dispatcher.get_http_client")
    async def test_send_test_ping_returns_status(self, mock_get_client, mock_pool):
        """Test 7: send_test_ping returns HTTP status code and response diagnostic."""
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        mock_conn.fetchrow.return_value = {
            "webhook_id": self.webhook_id,
            "tenant_id": self.tenant_id,
            "name": "Endpoint Under Test",
            "target_url": "https://webhook.site/abc",
            "signing_secret": self.signing_secret,
            "is_active": True,
        }

        mock_client = AsyncMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.text = '{"ping":"received"}'
        mock_client.post.return_value = mock_resp
        mock_get_client.return_value = mock_client

        ping_result = await send_test_ping(str(self.webhook_id), tenant_id=self.tenant_id)

        self.assertTrue(ping_result["success"])
        self.assertEqual(ping_result["status_code"], 200)
        self.assertIn("ping", ping_result["response_body"])

    @patch("webhook_dispatcher._pool")
    @patch("webhook_dispatcher.get_http_client")
    async def test_inactive_webhooks_are_skipped(self, mock_get_client, mock_pool):
        """Test 10: Inactive webhooks (is_active = false) are skipped from dispatch."""
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        # DB query filters WHERE is_active = TRUE so returns empty
        mock_conn.fetch.return_value = []

        mock_client = AsyncMock()
        mock_get_client.return_value = mock_client

        results = await dispatch_webhook(
            tenant_id=self.tenant_id,
            event_type="call.completed",
            payload={"call_id": "c1"},
        )

        self.assertEqual(results, [])
        mock_client.post.assert_not_called()


class TestWebhookRESTEndpoints(unittest.TestCase):
    """Tests 8 & 9: REST CRUD endpoints and paginated delivery inspector."""

    def setUp(self):
        self.client = TestClient(app)
        self.tenant_id = str(uuid.uuid4())
        self.token = create_access_token(
            data={"sub": self.tenant_id, "tenant_id": self.tenant_id, "role": "client_admin"}
        )
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @patch("routes.client_routes._pool")
    def test_webhook_crud_lifecycle(self, mock_pool):
        """Test 8: Register, list, update, and delete outbound webhook endpoint."""
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        wh_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        # 1. POST /api/client/webhooks
        mock_conn.fetchrow.return_value = {
            "webhook_id": wh_id,
            "tenant_id": uuid.UUID(self.tenant_id),
            "name": "Production HubSpot Relay",
            "target_url": "https://api.hubspot.com/v1/webhook",
            "signing_secret": "whsec_test_abc123",
            "event_types": ["call.completed", "lead.qualified"],
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }

        create_res = self.client.post(
            "/api/client/webhooks",
            headers=self.headers,
            json={
                "name": "Production HubSpot Relay",
                "target_url": "https://api.hubspot.com/v1/webhook",
                "event_types": ["call.completed", "lead.qualified"],
            },
        )
        self.assertEqual(create_res.status_code, 200)
        data = create_res.json()
        self.assertEqual(data["name"], "Production HubSpot Relay")
        self.assertEqual(data["target_url"], "https://api.hubspot.com/v1/webhook")

        # 2. GET /api/client/webhooks
        mock_conn.fetch.return_value = [
            {
                "webhook_id": wh_id,
                "tenant_id": uuid.UUID(self.tenant_id),
                "name": "Production HubSpot Relay",
                "target_url": "https://api.hubspot.com/v1/webhook",
                "signing_secret": "whsec_test_abc123",
                "event_types": ["call.completed", "lead.qualified"],
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            }
        ]

        list_res = self.client.get("/api/client/webhooks", headers=self.headers)
        self.assertEqual(list_res.status_code, 200)
        items = list_res.json()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["webhook_id"], str(wh_id))

        # 3. PATCH /api/client/webhooks/{webhook_id}
        mock_conn.fetchrow.side_effect = [
            # existing record lookup
            {
                "webhook_id": wh_id,
                "tenant_id": uuid.UUID(self.tenant_id),
                "name": "Production HubSpot Relay",
                "target_url": "https://api.hubspot.com/v1/webhook",
                "signing_secret": "whsec_test_abc123",
                "event_types": ["call.completed"],
                "is_active": True,
            },
            # updated record RETURNING
            {
                "webhook_id": wh_id,
                "tenant_id": uuid.UUID(self.tenant_id),
                "name": "Renamed Webhook",
                "target_url": "https://api.hubspot.com/v1/webhook",
                "signing_secret": "whsec_test_abc123",
                "event_types": ["call.completed", "call.risk_flagged"],
                "is_active": False,
                "created_at": now,
                "updated_at": now,
            },
        ]

        patch_res = self.client.patch(
            f"/api/client/webhooks/{wh_id}",
            headers=self.headers,
            json={"name": "Renamed Webhook", "is_active": False},
        )
        self.assertEqual(patch_res.status_code, 200)
        updated = patch_res.json()
        self.assertEqual(updated["name"], "Renamed Webhook")
        self.assertFalse(updated["is_active"])

        # 4. DELETE /api/client/webhooks/{webhook_id}
        mock_conn.execute.return_value = "DELETE 1"
        del_res = self.client.delete(f"/api/client/webhooks/{wh_id}", headers=self.headers)
        self.assertEqual(del_res.status_code, 200)
        self.assertEqual(del_res.json()["status"], "deleted")

    @patch("routes.client_routes._pool")
    def test_delivery_log_pagination(self, mock_pool):
        """Test 9: Paginated delivery history endpoint returns correct counts and slices."""
        mock_conn = AsyncMock()
        mock_pool.acquire.return_value.__aenter__.return_value = mock_conn

        wh_id = uuid.uuid4()
        now = datetime.now(timezone.utc)

        mock_conn.fetchval.return_value = 25  # Total deliveries count
        mock_conn.fetch.return_value = [
            {
                "delivery_id": uuid.uuid4(),
                "webhook_id": wh_id,
                "tenant_id": uuid.UUID(self.tenant_id),
                "event_type": "call.completed",
                "payload": {"call_id": f"call_{i}"},
                "reference_id": f"call_{i}",
                "status": "succeeded",
                "http_status_code": 200,
                "response_body": '{"ok":true}',
                "attempt_number": 1,
                "max_attempts": 5,
                "next_retry_at": None,
                "created_at": now,
                "completed_at": now,
            }
            for i in range(5)
        ]

        res = self.client.get(
            f"/api/client/webhooks/{wh_id}/deliveries?limit=5&offset=10",
            headers=self.headers,
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total"], 25)
        self.assertEqual(data["limit"], 5)
        self.assertEqual(data["offset"], 10)
        self.assertEqual(len(data["items"]), 5)
        self.assertEqual(data["items"][0]["status"], "succeeded")


if __name__ == "__main__":
    unittest.main()
