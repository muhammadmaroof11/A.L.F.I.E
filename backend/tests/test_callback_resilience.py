import os
import unittest
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio

# Set dummy environment variables for tests before importing config
for secret_key in [
    "LIVEKIT_API_KEY",
    "LIVEKIT_API_SECRET",
    "DEEPGRAM_API_KEY",
    "OPENROUTER_API_KEY",
    "FISH_AUDIO_API_KEY",
    "TWENTY_API_KEY",
    "JWT_SECRET_KEY",
    "SUPER_ADMIN_EMAIL",
    "SUPER_ADMIN_PASSWORD",
]:
    if secret_key not in os.environ:
        os.environ[secret_key] = "test-dummy-key"

from tools.core import CoreTools


class TestCallbackResilience(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.tenant_id = "test-tenant-123"
        self.room_name = "test-room-room1"
        self.tools = CoreTools(tenant_id=self.tenant_id, room_name=self.room_name)

    @patch("tools.core.save_callback_record", new_callable=AsyncMock)
    @patch("tools.core.crm.create_lead", new_callable=AsyncMock)
    @patch("tools.core.update_caller_memory", new_callable=AsyncMock)
    @patch("tools.core.send_webhook", new_callable=AsyncMock)
    @patch("tools.core.get_redis", new_callable=AsyncMock)
    async def test_schedule_callback_tool_success(
        self,
        mock_get_redis,
        mock_send_webhook,
        mock_update_memory,
        mock_create_lead,
        mock_save_callback,
    ):
        mock_save_callback.return_value = 42
        mock_redis = MagicMock()
        mock_get_redis.return_value = mock_redis

        result = await self.tools.schedule_callback(
            caller_name="Sarah Connor",
            caller_phone="+15559876543",
            preferred_time="today at 4:30 PM",
            reason="Commercial Lease Contract Review",
            target_department="Legal Specialist",
            notes="Requires review of indemnity clause before Friday",
        )

        # Verify DB save was invoked with right params
        mock_save_callback.assert_awaited_once_with(
            tenant_id=self.tenant_id,
            caller_name="Sarah Connor",
            caller_phone="+15559876543",
            preferred_time="today at 4:30 PM",
            reason="Commercial Lease Contract Review",
            target_department="Legal Specialist",
            notes="Requires review of indemnity clause before Friday",
            call_id=self.room_name,
            priority="high",
            notification_sent=True,
        )

        # Verify CRM lead was updated
        mock_create_lead.assert_awaited_once()

        # Verify caller memory in Redis was updated
        mock_update_memory.assert_awaited_once()

        # Verify instant notification webhook was dispatched
        await asyncio.sleep(0.01)
        mock_send_webhook.assert_called()

        # Check returned text to LLM
        self.assertIn("Callback successfully confirmed", result)
        self.assertIn("4:30 PM", result)
        self.assertIn("Legal Specialist", result)

    @patch("tools.core.send_webhook", new_callable=AsyncMock)
    async def test_transfer_to_department_busy_fallback(self, mock_send_webhook):
        # Simulate when pool has no agent configured or DB offline
        with patch("telemetry._pool", None):
            result = await self.tools.transfer_to_department("Sales")
            self.assertIn("TRANSFER_BUSY", result)
            self.assertIn("schedule a callback", result.lower())

    @patch("tools.core.send_webhook", new_callable=AsyncMock)
    @patch("tools.core.crm.get_tenant_config", new_callable=AsyncMock)
    async def test_transfer_to_human_busy_fallback(
        self, mock_get_config, mock_send_webhook
    ):
        # No human agent SIP configured -> graceful busy message
        mock_get_config.return_value = {"human_agent_sip_uri": None}

        result = await self.tools.transfer_to_human(
            reason="Complex billing question",
            caller_name="John Doe",
            caller_phone="+15551234567",
        )

        self.assertIn("TRANSFER_BUSY", result)
        self.assertIn("callback", result.lower())

    async def test_client_fish_audio_voices_endpoint(self):
        from routes.client_routes import list_client_fish_audio_voices

        user = {"user_id": "test", "tenant_id": self.tenant_id, "role": "client_admin"}
        voices = await list_client_fish_audio_voices(current_user=user)
        self.assertIn("items", voices)
        self.assertGreater(len(voices["items"]), 0)
        self.assertIn("id", voices["items"][0])


if __name__ == "__main__":
    unittest.main()

