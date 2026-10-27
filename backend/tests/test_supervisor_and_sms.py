import asyncio
import json
import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import uuid

# Set mock secrets for testing environment
os.environ.setdefault("DEEPGRAM_API_KEY", "mock_key")
os.environ.setdefault("OPENROUTER_API_KEY", "mock_key")
os.environ.setdefault("FISH_AUDIO_API_KEY", "mock_key")
os.environ.setdefault("JWT_SECRET_KEY", "test_secret_key_for_unit_tests_32chars!")
os.environ.setdefault("SUPER_ADMIN_EMAIL", "admin@alfie-ai.com")
os.environ.setdefault("SUPER_ADMIN_PASSWORD", "testpass")

from fastapi.testclient import TestClient

from api import app
from auth import create_access_token
from config import settings
from migrations import MIGRATIONS, migration_010_sms_dispatch_and_templates
from telephony_provider import send_sms
from tools.core import CoreTools


class AsyncContextManagerMock:
    def __init__(self, target):
        self.target = target

    async def __aenter__(self):
        return self.target

    async def __aexit__(self, exc_type, exc, tb):
        pass


class TestSupervisorAndSMS(unittest.TestCase):
    """Integration & unit tests for Phase 17B: Supervisor Console & In-Call Instant SMS."""

    def setUp(self):
        self.client = TestClient(app)
        self.test_tenant_id = str(uuid.uuid4())
        self.client_token = create_access_token(
            {"sub": "client_admin", "role": "client_admin", "tenant_id": self.test_tenant_id}
        )
        self.auth_headers = {"Authorization": f"Bearer {self.client_token}"}
        self.test_call_id = "call_test_supervisor_123"

    def test_migration_010_registration(self):
        """Verify Migration 010 is registered in migration manifest."""
        versions = [m["version"] for m in MIGRATIONS]
        self.assertIn("010", versions)
        m010 = next(m for m in MIGRATIONS if m["version"] == "010")
        self.assertEqual(m010["name"], "sms_dispatch_and_templates")

    def test_ghost_whisper_dispatch(self):
        """Verify POST /api/client/calls/{call_id}/whisper publishes to Redis control channel."""
        mock_redis = AsyncMock()

        with patch("telemetry.get_redis", return_value=mock_redis):
            res = self.client.post(
                f"/api/client/calls/{self.test_call_id}/whisper",
                headers=self.auth_headers,
                json={"message": "Offer 10% discount on first consultation", "supervisor_name": "Sarah"},
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["status"], "delivered")
            self.assertEqual(data["call_id"], self.test_call_id)
            self.assertIn("10% discount", data["message"])
            self.assertEqual(mock_redis.publish.call_count, 2)

    def test_ghost_whisper_rejects_empty_message(self):
        """Verify whisper endpoint rejects empty strings."""
        res = self.client.post(
            f"/api/client/calls/{self.test_call_id}/whisper",
            headers=self.auth_headers,
            json={"message": "   "},
        )
        self.assertEqual(res.status_code, 400)

    def test_supervisor_takeover_token_generation(self):
        """Verify supervisor LiveKit WebRTC token generation with room grants."""
        res = self.client.post(
            f"/api/client/calls/{self.test_call_id}/takeover-token",
            headers=self.auth_headers,
            json={"supervisor_name": "Lead Supervisor"},
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("token", data)
        self.assertEqual(data["room_name"], self.test_call_id)
        self.assertIn("supervisor_", data["identity"])

    def test_takeover_and_release_lifecycle(self):
        """Verify 1-click takeover action updates Redis state and publishes events."""
        mock_redis = AsyncMock()

        with patch("telemetry.get_redis", return_value=mock_redis):
            # 1. Initiate Takeover
            res = self.client.post(
                f"/api/client/calls/{self.test_call_id}/takeover",
                headers=self.auth_headers,
                json={"supervisor_name": "Sarah Connor"},
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["status"], "takeover_initiated")
            mock_redis.hset.assert_called()
            mock_redis.publish.assert_called()

            # 2. Release Takeover
            rel_res = self.client.post(
                f"/api/client/calls/{self.test_call_id}/release-takeover",
                headers=self.auth_headers,
            )
            self.assertEqual(rel_res.status_code, 200)
            rel_data = rel_res.json()
            self.assertEqual(rel_data["status"], "takeover_released")

    def test_send_sms_carrier_and_sandbox_fallback(self):
        """Verify telephony send_sms generates structured result in sandbox mode."""
        async def run_test():
            result = await send_sms(
                to_phone="+1 (415) 555-0199",
                message="Your consultation is confirmed for 3 PM.",
                tenant_id=self.test_tenant_id,
                call_id=self.test_call_id,
            )
            self.assertEqual(result["status"], "sent")
            self.assertEqual(result["to_phone"], "+14155550199")
            self.assertIn("consultation is confirmed", result["message"])

        asyncio.run(run_test())

    def test_core_tools_send_sms_to_caller(self):
        """Verify LLM CoreTools send_sms_to_caller tool function."""
        async def run_test():
            tools = CoreTools(
                tenant_id=self.test_tenant_id,
                room_name=self.test_call_id,
                caller_phone="+15559876543",
            )
            res = await tools.send_sms_to_caller(
                message="We are located at 500 Grand Ave, Suite 400."
            )
            self.assertIn("SMS successfully sent", res)
            self.assertIn("+15559876543", res)

        asyncio.run(run_test())

    def test_sms_templates_crud(self):
        """Verify GET and PUT for tenant SMS templates."""
        # 1. GET default templates
        res = self.client.get(
            "/api/client/sms/templates",
            headers=self.auth_headers,
        )
        self.assertEqual(res.status_code, 200)
        templates = res.json()
        self.assertIsInstance(templates, list)
        self.assertGreaterEqual(len(templates), 3)

        # 2. PUT template update
        update_res = self.client.put(
            "/api/client/sms/templates",
            headers=self.auth_headers,
            json={
                "template_key": "appointment_confirmation",
                "name": "Customized Clinic Confirmation",
                "content": "Your dental appointment is locked in for Thursday at 2 PM.",
                "is_enabled": True,
            },
        )
        self.assertEqual(update_res.status_code, 200)
        up_data = update_res.json()
        self.assertEqual(up_data["status"], "success")
        self.assertEqual(up_data["template"]["template_key"], "appointment_confirmation")

    def test_send_sms_api_endpoint(self):
        """Verify POST /api/client/sms/send endpoint."""
        res = self.client.post(
            "/api/client/sms/send",
            headers=self.auth_headers,
            json={
                "to_phone": "+14155550199",
                "message": "Instant directions link: https://maps.google.com",
                "call_id": self.test_call_id,
            },
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "sent")
        self.assertEqual(data["to_phone"], "+14155550199")


if __name__ == "__main__":
    unittest.main()
