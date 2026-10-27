import asyncio
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
from migrations import MIGRATIONS
from telemetry import (
    deregister_active_call,
    generate_waveform_peaks_synthetic,
    get_active_calls_for_tenant,
    publish_live_transcript_delta,
    register_active_call,
    update_call_live_state,
)


class AsyncContextManagerMock:
    def __init__(self, target):
        self.target = target

    async def __aenter__(self):
        return self.target

    async def __aexit__(self, exc_type, exc, tb):
        pass


class TestLiveCallingPipeline(unittest.TestCase):
    """Integration & unit test suite for Phase 17A: Live Calling Console & Audio Recording."""

    def setUp(self):
        self.client = TestClient(app)
        self.test_tenant_id = str(uuid.uuid4())
        self.client_token = create_access_token(
            {"sub": "client_admin", "role": "client_admin", "tenant_id": self.test_tenant_id}
        )
        self.super_token = create_access_token(
            {"sub": "super_admin", "role": "super_admin"}
        )
        self.auth_headers = {"Authorization": f"Bearer {self.client_token}"}

    def test_migration_009_registration(self):
        """Verify Migration 009 is registered in migration manifest."""
        versions = [m["version"] for m in MIGRATIONS]
        self.assertIn("009", versions)
        m009 = next(m for m in MIGRATIONS if m["version"] == "009")
        self.assertEqual(m009["name"], "call_recordings_and_live_status")

    def test_waveform_peak_generation(self):
        """Verify 100-point normalized waveform envelope generator."""
        peaks = generate_waveform_peaks_synthetic(duration_seconds=120, points=100)
        self.assertEqual(len(peaks), 100)
        for p in peaks:
            self.assertGreaterEqual(p, 0.0)
            self.assertLessEqual(p, 1.0)
        # Verify it has amplitude variation
        self.assertGreater(max(peaks), 0.5)

    def test_redis_active_call_lifecycle(self):
        """Verify Redis live call registration, updates, deltas, and cleanup."""
        async def run_test():
            mock_redis = AsyncMock()
            mock_redis.hgetall.return_value = {
                "call_id": "call_123",
                "tenant_id": self.test_tenant_id,
                "caller_number": "+14155552671",
                "agent_name": "Alfie",
                "state": "speaking",
                "speaker": "caller"
            }
            mock_redis.smembers.return_value = {"call_123"}

            # 1. Register active call
            await register_active_call(
                mock_redis,
                tenant_id=self.test_tenant_id,
                call_id="call_123",
                caller_number="+14155552671",
                agent_name="Alfie",
                niche="medical",
            )
            mock_redis.hset.assert_called()
            mock_redis.sadd.assert_called()
            mock_redis.publish.assert_called()

            # 2. Update state to thinking
            await update_call_live_state(
                mock_redis,
                tenant_id=self.test_tenant_id,
                call_id="call_123",
                state="thinking",
                speaker="agent",
            )
            mock_redis.publish.assert_called()

            # 3. Stream transcript delta
            await publish_live_transcript_delta(
                mock_redis,
                tenant_id=self.test_tenant_id,
                call_id="call_123",
                turn_id="turn_1",
                role="assistant",
                delta="Hello, how can I help?",
                is_final=True,
                offset_ms=1200,
            )
            mock_redis.publish.assert_called()

            # 4. Query active calls
            calls = await get_active_calls_for_tenant(mock_redis, self.test_tenant_id)
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["call_id"], "call_123")

            # 5. Deregister call
            await deregister_active_call(
                mock_redis,
                tenant_id=self.test_tenant_id,
                call_id="call_123",
                duration_seconds=45,
                audio_url="/api/client/recordings/call_123/audio",
            )
            mock_redis.srem.assert_called()
            mock_redis.delete.assert_called()

        asyncio.run(run_test())

    def test_audio_recording_stream_endpoint_fallback(self):
        """Verify audio streaming endpoint generates valid WAV stream with Range support."""
        res = self.client.get(
            "/api/client/recordings/call_mock_test/audio",
            headers=self.auth_headers,
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get("Accept-Ranges"), "bytes")
        self.assertIn("audio/", res.headers.get("Content-Type", ""))
        self.assertGreater(len(res.content), 100)

        # Test HTTP 206 Partial Content
        range_res = self.client.get(
            "/api/client/recordings/call_mock_test/audio",
            headers={**self.auth_headers, "Range": "bytes=0-99"},
        )
        self.assertEqual(range_res.status_code, 206)
        self.assertEqual(len(range_res.content), 100)
        self.assertIn("bytes 0-99/", range_res.headers.get("Content-Range", ""))

    def test_audio_recording_unauthorized_without_token(self):
        """Verify audio endpoint rejects unauthenticated requests."""
        res = self.client.get("/api/client/recordings/call_mock_test/audio")
        self.assertEqual(res.status_code, 401)

    def test_client_interactions_contains_waveform_and_audio_url(self):
        """Verify list_client_interactions returns waveform_data, audio_url, and live_status."""
        mock_conn = AsyncMock()
        mock_conn.fetch.return_value = []
        mock_pool = MagicMock()
        mock_pool.acquire.return_value = AsyncContextManagerMock(mock_conn)

        with patch("routes.client_routes._pool", mock_pool), patch("routes.client_routes.settings.sandbox_mode", True):
            res = self.client.get(
                "/api/client/interactions",
                headers=self.auth_headers,
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertIsInstance(data, list)
            self.assertGreater(len(data), 0)
            first_item = data[0]
            self.assertIn("waveform_data", first_item)
            self.assertIn("audio_url", first_item)
            self.assertIn("live_status", first_item)
            self.assertIsInstance(first_item["waveform_data"], list)
            self.assertEqual(len(first_item["waveform_data"]), 100)

    def test_live_calls_websocket_authentication(self):
        """Verify WebSocket rejects connections without token or with invalid role."""
        # 1. No token -> 1008
        with self.assertRaises(Exception):
            with self.client.websocket_connect("/api/client/live-calls/ws"):
                pass

        # 2. Invalid role token -> 1008
        bad_token = create_access_token({"sub": "anonymous", "role": "unauthorized"})
        with self.assertRaises(Exception):
            with self.client.websocket_connect(f"/api/client/live-calls/ws?token={bad_token}"):
                pass


if __name__ == "__main__":
    unittest.main()
