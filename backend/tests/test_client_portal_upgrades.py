import os
import sys
import json
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import timedelta

# Mock external heavy dependencies if not present in local environment
for mod in [
    "livekit",
    "livekit.agents",
    "livekit.agents.voice",
    "livekit.plugins",
    "livekit.plugins.deepgram",
    "livekit.plugins.openai",
    "livekit.plugins.silero",
    "livekit.plugins.fishaudio",
    "livekit.api",
    "arq",
    "arq.connections",
    "redisvl",
    "sentence_transformers",
    "stripe",
]:
    try:
        __import__(mod)
    except (ImportError, Exception):
        sys.modules[mod] = MagicMock()

# Ensure test environment variables
for secret_key in [
    "LIVEKIT_API_KEY",
    "LIVEKIT_API_SECRET",
    "DEEPGRAM_API_KEY",
    "OPENROUTER_API_KEY",
    "FISH_AUDIO_API_KEY",
    "JWT_SECRET_KEY",
    "SUPER_ADMIN_EMAIL",
    "SUPER_ADMIN_PASSWORD",
]:
    if secret_key not in os.environ:
        os.environ[secret_key] = "test-dummy-key"

from fastapi.testclient import TestClient
from api import app
from auth import create_access_token
import routes.client_routes as client_routes
from routes.client_routes import resolve_tenant_id


class AsyncContextManagerMock:
    def __init__(self, return_value):
        self.return_value = return_value

    async def __aenter__(self):
        return self.return_value

    async def __aexit__(self, exc_type, exc, tb):
        pass


class TestClientPortalUpgrades(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.test_tenant_id = "00000000-0000-0000-0000-0000000000aa"
        
        # Client admin token with tenant_id claim
        self.client_token = create_access_token({
            "sub": "client_user_1",
            "role": "client_admin",
            "tenant_id": self.test_tenant_id,
        })
        self.client_headers = {"Authorization": f"Bearer {self.client_token}"}

        # Super admin token
        self.admin_token = create_access_token({
            "sub": "super_admin_1",
            "role": "super_admin",
        })
        self.admin_headers = {"Authorization": f"Bearer {self.admin_token}"}

    def test_resolve_tenant_id_unit_logic(self):
        """Test tenant_id resolution rules across client_admin and super_admin."""
        # 1. Client admin with no query param resolves from JWT tenant_id
        current_user = {"sub": "user_1", "role": "client_admin", "tenant_id": "tenant-uuid-1"}
        self.assertEqual(resolve_tenant_id(None, current_user), "tenant-uuid-1")

        # 2. Client admin with sub fallback
        current_user_sub = {"sub": "tenant-uuid-2", "role": "client_admin"}
        self.assertEqual(resolve_tenant_id(None, current_user_sub), "tenant-uuid-2")

        # 3. Super admin can explicitly query any tenant_id
        super_user = {"sub": "admin", "role": "super_admin"}
        self.assertEqual(resolve_tenant_id("tenant-target-9", super_user), "tenant-target-9")

    @patch("routes.client_routes._pool")
    def test_client_phone_numbers_endpoint_jwt_resolution(self, mock_pool):
        """GET /api/client/phone-numbers automatically resolves tenant from JWT and returns active lines."""
        mock_conn = AsyncMock()
        mock_conn.fetch = AsyncMock(return_value=[
            {
                "id": "1",
                "phone_number": "+14155550199",
                "locality": "San Francisco",
                "region": "CA",
                "capabilities": '{"voice": true, "sms": true}',
                "status": "active",
                "created_at": None,
                "niche": "real_estate",
                "provider": "twilio",
                "agent_id": "00000000-0000-0000-0000-000000000001",
                "agent_name": "Alfie Commercial",
            }
        ])
        mock_pool.acquire.return_value = AsyncContextManagerMock(mock_conn)

        response = self.client.get("/api/client/phone-numbers", headers=self.client_headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["phone_number"], "+14155550199")
        self.assertEqual(data[0]["agent_name"], "Alfie Commercial")

    @patch("livekit.api.AccessToken")
    def test_client_livekit_simulator_token_generation(self, mock_access_token):
        """POST /api/client/livekit/token returns signed LiveKit token for in-browser voice simulation."""
        mock_builder = MagicMock()
        mock_builder.with_identity.return_value = mock_builder
        mock_builder.with_name.return_value = mock_builder
        mock_builder.with_grants.return_value = mock_builder
        mock_builder.with_metadata.return_value = mock_builder
        mock_builder.to_jwt.return_value = "mocked.client.livekit.token.jwt"
        mock_access_token.return_value = mock_builder

        response = self.client.post(
            "/api/client/livekit/token",
            headers=self.client_headers,
            json={"niche": "medical_clinic", "agent_name": "Dr. Alfie Intake"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["token"], "mocked.client.livekit.token.jwt")
        self.assertTrue(data["room_name"].startswith("sim-"))
        self.assertIn("url", data)

    @patch("routes.client_routes._pool")
    def test_client_knowledge_base_get_and_put(self, mock_pool):
        """GET & PUT /api/client/knowledge-base reads and writes business rules and FAQs."""
        mock_conn = AsyncMock()
        
        sample_config = {
            "knowledge_base": {
                "business_hours": "Mon-Fri 8am-6pm",
                "address_directions": "100 Pine St, Suite 500. Free garage validation.",
                "emergency_phone": "+1 555-911-0000",
                "business_rules": "Always verify patient DOB before booking.",
                "faqs": [
                    {"question": "What are your hours?", "answer": "Mon-Fri 8am-6pm"}
                ]
            }
        }
        
        # Mock GET config fetchrow
        mock_conn.fetchrow = AsyncMock(return_value={
            "tenant_config": json.dumps(sample_config)
        })
        mock_conn.execute = AsyncMock(return_value="UPDATE 1")
        mock_pool.acquire.return_value = AsyncContextManagerMock(mock_conn)

        # 1. Test GET
        get_res = self.client.get("/api/client/knowledge-base", headers=self.client_headers)
        self.assertEqual(get_res.status_code, 200)
        kb_data = get_res.json()
        self.assertEqual(kb_data["business_hours"], "Mon-Fri 8am-6pm")
        self.assertEqual(len(kb_data["faqs"]), 1)
        self.assertEqual(kb_data["emergency_phone"], "+1 555-911-0000")

        # 2. Test PUT with updated FAQs
        with patch("telemetry.get_redis", AsyncMock(return_value=None)):
            put_res = self.client.put(
                "/api/client/knowledge-base",
                headers=self.client_headers,
                json={
                    "business_hours": "Mon-Sat 8am-8pm",
                    "address_directions": "200 Market St, valet available.",
                    "emergency_phone": "+1 555-999-8888",
                    "business_rules": "Strict intake rules.",
                    "faqs": [
                        {"question": "Do you take insurance?", "answer": "Yes, BlueCross and Aetna."}
                    ]
                }
            )
            self.assertEqual(put_res.status_code, 200)
            self.assertEqual(put_res.json()["status"], "success")

    @patch("routes.client_routes._pool")
    def test_client_integrations_get_and_put(self, mock_pool):
        """GET & PUT /api/client/integrations manages CRM webhooks and instant lead alerts."""
        mock_conn = AsyncMock()
        sample_config = {
            "integrations": {
                "webhook_url": "https://hooks.zapier.com/hooks/catch/12345/abc",
                "notification_email": "alerts@clientclinic.com",
                "notification_sms": "+15551239999",
                "auto_notify_hot_leads": True,
                "auto_notify_callbacks": True,
            }
        }
        mock_conn.fetchrow = AsyncMock(return_value={
            "tenant_config": json.dumps(sample_config)
        })
        mock_conn.execute = AsyncMock(return_value="UPDATE 1")
        mock_pool.acquire.return_value = AsyncContextManagerMock(mock_conn)

        # 1. Test GET
        get_res = self.client.get("/api/client/integrations", headers=self.client_headers)
        self.assertEqual(get_res.status_code, 200)
        integ = get_res.json()
        self.assertEqual(integ["notification_email"], "alerts@clientclinic.com")
        self.assertTrue(integ["auto_notify_hot_leads"])

        # 2. Test PUT
        with patch("telemetry.get_redis", AsyncMock(return_value=None)):
            put_res = self.client.put(
                "/api/client/integrations",
                headers=self.client_headers,
                json={
                    "webhook_url": "https://api.twenty.com/v1/webhooks/incoming",
                    "notification_email": "newlead@clientclinic.com",
                    "notification_sms": "+15559870000",
                    "auto_notify_hot_leads": True,
                    "auto_notify_callbacks": False
                }
            )
            self.assertEqual(put_res.status_code, 200)
            self.assertEqual(put_res.json()["status"], "success")


if __name__ == "__main__":
    unittest.main()
