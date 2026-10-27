import os
import unittest
from unittest.mock import patch, AsyncMock, MagicMock

# Set required environment variables before any app imports
os.environ.update(
    {
        "LIVEKIT_API_KEY": "test_livekit_key",
        "LIVEKIT_API_SECRET": "test_livekit_secret_at_least_32_bytes_long_12345",
        "DEEPGRAM_API_KEY": "test_deepgram_key",
        "OPENROUTER_API_KEY": "test_openrouter_key",
        "FISH_AUDIO_API_KEY": "test_fish_audio_key",
        "JWT_SECRET_KEY": "test_jwt_secret_key_at_least_32_bytes_long_12345",
        "SUPER_ADMIN_EMAIL": "admin@alfie.ai",
        "SUPER_ADMIN_PASSWORD": "super_secret_password_123",
        "LIVEKIT_SIP_DOMAIN": "sip.alfie-ai.com",
    }
)

from fastapi.testclient import TestClient
from api import app
from routes.auth_routes import SUPER_ADMIN_EMAIL, SUPER_ADMIN_PASSWORD


class TestAPIRoutesIntegration(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_metrics_endpoint_returns_prometheus_metrics(self):
        """GET /metrics should return 200 and Prometheus formatted text."""
        response = self.client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        self.assertIn("python_gc_objects_collected_total", response.text)

    def test_security_headers_middleware_is_applied(self):
        """Verify SecurityHeadersMiddleware injects required defensive HTTP headers."""
        response = self.client.get("/metrics")
        self.assertEqual(response.headers.get("x-content-type-options"), "nosniff")
        self.assertEqual(response.headers.get("x-frame-options"), "DENY")
        self.assertEqual(response.headers.get("x-xss-protection"), "1; mode=block")
        self.assertEqual(
            response.headers.get("referrer-policy"), "strict-origin-when-cross-origin"
        )

    def test_super_admin_login_success(self):
        """POST /api/auth/login with valid super admin credentials returns JWT access token."""
        response = self.client.post(
            "/api/auth/login",
            json={
                "email": SUPER_ADMIN_EMAIL,
                "password": SUPER_ADMIN_PASSWORD,
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["role"], "super_admin")
        self.assertEqual(data["token_type"], "bearer")

    def test_super_admin_login_invalid_password_returns_401(self):
        """POST /api/auth/login with incorrect password should return 401 Unauthorized."""
        response = self.client.post(
            "/api/auth/login",
            json={
                "email": SUPER_ADMIN_EMAIL,
                "password": "wrong_password_attempt_99999",
            },
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["detail"], "Invalid credentials")

    def test_public_demo_personas_endpoint(self):
        """GET /api/public/demo/personas should return available demo niches."""
        response = self.client.get("/api/public/demo/personas")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        first = data[0]
        self.assertIn("id", first)
        self.assertIn("name", first)

    @patch("livekit.api.AccessToken")
    def test_public_demo_token_generation(self, mock_access_token):
        """POST /api/public/demo/token should return LiveKit room connection parameters."""
        mock_builder = MagicMock()
        mock_builder.with_identity.return_value = mock_builder
        mock_builder.with_name.return_value = mock_builder
        mock_builder.with_grants.return_value = mock_builder
        mock_builder.with_metadata.return_value = mock_builder
        mock_builder.to_jwt.return_value = "mocked.livekit.token.jwt"
        mock_access_token.return_value = mock_builder

        response = self.client.post(
            "/api/public/demo/token",
            json={
                "niche": "real_estate",
                "visitor_name": "Integration Test Visitor",
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["token"], "mocked.livekit.token.jwt")
        self.assertIn("room_name", data)
        self.assertTrue(data["room_name"].startswith("demo-call-"))

    @patch("routes.twilio_routes._pool", MagicMock())
    @patch("routes.twilio_routes.get_tenant_and_agent_by_phone")
    def test_twilio_incoming_call_unknown_number_returns_error_twiml(
        self, mock_get_tenant
    ):
        """POST /api/twilio/incoming with unassigned phone number returns polite error TwiML."""
        mock_get_tenant.return_value = (None, None)

        response = self.client.post(
            "/api/twilio/incoming",
            data={
                "To": "+19999999999",
                "From": "+18888888888",
                "CallSid": "CA1234567890",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("<Response>", response.text)
        self.assertIn("<Say", response.text)
        self.assertIn("This number is not assigned to an active tenant", response.text)

    @patch("routes.twilio_routes._pool", MagicMock())
    @patch("routes.twilio_routes.get_tenant_and_agent_by_phone")
    def test_twilio_incoming_call_routes_to_livekit_sip(self, mock_get_tenant):
        """POST /api/twilio/incoming with active tenant returns SIP Dial TwiML (BUG-3 fix regression test)."""
        mock_get_tenant.return_value = ("tenant_alpha_123", "agent_beta_456")

        response = self.client.post(
            "/api/twilio/incoming",
            data={
                "To": "+15551234567",
                "From": "+15559876543",
                "CallSid": "CA0987654321",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("<Response>", response.text)
        self.assertIn("<Dial>", response.text)
        self.assertIn("<Sip>", response.text)
        self.assertIn("sip:tenant_alpha_123_agent_beta_456@sip.alfie-ai.com", response.text)


if __name__ == "__main__":
    unittest.main()
