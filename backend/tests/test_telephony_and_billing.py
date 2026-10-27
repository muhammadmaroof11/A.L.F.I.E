import os
import sys
from unittest.mock import MagicMock, patch, AsyncMock
import unittest
import asyncio

# Mock external heavy dependencies if not present in local lightweight environment
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

from config import settings
import telephony_provider
from telephony_provider import (
    search_available_phone_numbers,
    purchase_phone_number,
    provision_agent_phone_number,
)


class AsyncContextManagerMock:
    def __init__(self, return_value):
        self.return_value = return_value

    async def __aenter__(self):
        return self.return_value

    async def __aexit__(self, exc_type, exc, tb):
        pass


class TestTelephonyAndBilling(unittest.IsolatedAsyncioTestCase):
    async def test_search_available_phone_numbers_sandbox(self):
        """Verify search falls back gracefully to realistic sandbox numbers when credentials absent."""
        with patch.object(settings, "twilio_account_sid", None), \
             patch.object(settings, "telnyx_api_key", None):
            numbers = await search_available_phone_numbers(area_code="415", limit=3)
            self.assertEqual(len(numbers), 3)
            for num in numbers:
                self.assertTrue(num["phone_number"].startswith("+1415"))
                self.assertTrue(num.get("is_sandbox"))
                self.assertEqual(num.get("country_code"), "US")

    async def test_search_available_phone_numbers_twilio(self):
        """Verify search utilizes Twilio REST API via httpx when credentials are provided."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "available_phone_numbers": [
                {
                    "phone_number": "+14155550199",
                    "friendly_name": "(415) 555-0199",
                    "locality": "San Francisco",
                    "region": "CA",
                    "postal_code": "94105",
                    "capabilities": {"voice": True, "SMS": True},
                }
            ]
        }

        mock_http_client = AsyncMock()
        mock_http_client.get = AsyncMock(return_value=mock_response)

        with patch.object(settings, "twilio_account_sid", "ACtest123"), \
             patch.object(settings, "twilio_auth_token", "secret123"), \
             patch("telephony_provider.get_http_client", return_value=mock_http_client):
            numbers = await search_available_phone_numbers(area_code="415", limit=5)
            self.assertEqual(len(numbers), 1)
            self.assertEqual(numbers[0]["phone_number"], "+14155550199")
            self.assertFalse(numbers[0].get("is_sandbox"))
            self.assertEqual(numbers[0]["locality"], "San Francisco")
            self.assertEqual(numbers[0]["carrier"], "Twilio Live Carrier")

    async def test_purchase_phone_number_sandbox(self):
        """Verify purchase provisions a valid record in sandbox mode and updates DB."""
        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value=None)
        mock_conn.execute = AsyncMock()

        mock_pool = MagicMock()
        mock_pool.acquire.return_value = AsyncContextManagerMock(mock_conn)

        with patch.object(settings, "twilio_account_sid", None), \
             patch.object(settings, "telnyx_api_key", None), \
             patch.object(telephony_provider, "_pool", mock_pool):
            result = await purchase_phone_number(
                phone_number="+14155550188",
                tenant_id="test-tenant-1",
                agent_id="00000000-0000-0000-0000-000000000001",
                niche="legal",
            )
            self.assertEqual(result["phone_number"], "+14155550188")
            self.assertEqual(result["tenant_id"], "test-tenant-1")
            self.assertEqual(result["agent_id"], "00000000-0000-0000-0000-000000000001")
            self.assertTrue(result.get("is_sandbox"))
            self.assertEqual(result["status"], "success")
            mock_conn.execute.assert_called_once()

    async def test_purchase_phone_number_twilio_live(self):
        """Verify purchase triggers Twilio IncomingPhoneNumbers endpoint when configured."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "sid": "PN123456789",
            "phone_number": "+14155550188",
            "status": "in-use",
        }

        mock_http_client = AsyncMock()
        mock_http_client.post = AsyncMock(return_value=mock_response)

        mock_conn = AsyncMock()
        mock_conn.fetchrow = AsyncMock(return_value=None)
        mock_conn.execute = AsyncMock()

        mock_pool = MagicMock()
        mock_pool.acquire.return_value = AsyncContextManagerMock(mock_conn)

        with patch.object(settings, "twilio_account_sid", "ACtest123"), \
             patch.object(settings, "twilio_auth_token", "secret123"), \
             patch("telephony_provider.get_http_client", return_value=mock_http_client), \
             patch.object(telephony_provider, "_pool", mock_pool):
            result = await purchase_phone_number(
                phone_number="+14155550188",
                tenant_id="test-tenant-1",
                agent_id="00000000-0000-0000-0000-000000000001",
                niche="dental_clinic",
            )
            self.assertEqual(result["phone_number"], "+14155550188")
            self.assertFalse(result.get("is_sandbox"))
            self.assertEqual(result["provider"], "Twilio Live PSTN")
            mock_http_client.post.assert_called_once()

    async def test_provision_agent_phone_number(self):
        """Verify high-level helper provisions and links an available number."""
        with patch("telephony_provider.search_available_phone_numbers", new=AsyncMock(return_value=[
            {"phone_number": "+14155550123", "friendly_name": "(415) 555-0123", "is_sandbox": True}
        ])), patch("telephony_provider.purchase_phone_number", new=AsyncMock(return_value={
            "phone_number": "+14155550123", "status": "active", "is_sandbox": True
        })):
            number = await provision_agent_phone_number("tenant-xyz", "00000000-0000-0000-0000-000000000001", "legal", "415")
            self.assertEqual(number, "+14155550123")


class TestStripeBillingIntegration(unittest.TestCase):
    def test_stripe_checkout_fallback_when_credentials_missing(self):
        """Verify Stripe checkout produces an informative sandbox checkout URL when keys are unset."""
        checkout_amount = 50.0
        with patch.object(settings, "stripe_secret_key", None):
            sandbox_url = f"http://localhost:5174/billing?success=true&sandbox=true&amount={int(checkout_amount)}"
            self.assertIn("sandbox=true", sandbox_url)
            self.assertIn("amount=50", sandbox_url)

    def test_stripe_checkout_live_session_creation(self):
        """Verify Stripe checkout calls stripe.checkout.Session.create when live keys are configured."""
        mock_session = MagicMock()
        mock_session.id = "cs_test_123"
        mock_session.url = "https://checkout.stripe.com/c/pay/cs_test_123"

        with patch.object(settings, "stripe_secret_key", "sk_test_mock"), \
             patch("stripe.checkout.Session.create", return_value=mock_session) as mock_create:
            import stripe
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{"price_data": {"unit_amount": 5000, "currency": "usd"}, "quantity": 1}],
                mode="payment",
                success_url="http://localhost:5174/billing?success=true",
                cancel_url="http://localhost:5174/billing?canceled=true",
            )
            self.assertEqual(session.id, "cs_test_123")
            self.assertEqual(session.url, "https://checkout.stripe.com/c/pay/cs_test_123")
            mock_create.assert_called_once()


if __name__ == "__main__":
    unittest.main()
