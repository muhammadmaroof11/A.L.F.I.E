"""
Unit and integration tests for A.L.F.I.E Phase 3:
Multi-Provider Streaming Mesh, Cartesia Sonic 3.0, and Resilient Circuit Breakers.
"""

import asyncio
import os
import time
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Ensure test credentials exist before importing settings
os.environ.setdefault("DEEPGRAM_API_KEY", "mock_key")
os.environ.setdefault("OPENROUTER_API_KEY", "mock_key")
os.environ.setdefault("FISH_AUDIO_API_KEY", "mock_key")
os.environ.setdefault("CARTESIA_API_KEY", "mock_cartesia_key")
os.environ.setdefault("ELEVENLABS_API_KEY", "mock_eleven_key")
os.environ.setdefault("GROQ_API_KEY", "mock_groq_key")
os.environ.setdefault("JWT_SECRET_KEY", "test_secret_key_for_unit_tests_32chars!")
os.environ.setdefault("SUPER_ADMIN_EMAIL", "admin@alfie-ai.com")
os.environ.setdefault("SUPER_ADMIN_PASSWORD", "testpass")

from pipeline.audio_mesh import (
    BaseSTTAdapter,
    BaseTTSAdapter,
    CartesiaTTS,
    CircuitBreaker,
    CircuitState,
    DeepgramAuraTTS,
    DeepgramSTT,
    ElevenLabsTTS,
    FishAudioTTS,
    GroqWhisperSTT,
    OpenAITTS,
    ProviderHealth,
    ResilientSTTMesh,
    ResilientTTSMesh,
    build_default_stt_mesh,
    build_default_tts_mesh,
)


class TestCircuitBreaker(unittest.TestCase):
    """Verifies circuit breaker state machine transitions."""

    def test_circuit_state_transitions(self):
        cb = CircuitBreaker(provider_name="cartesia", failure_threshold=2, recovery_timeout_sec=0.1)

        # 1. Initially CLOSED
        self.assertEqual(cb.circuit_state, CircuitState.CLOSED)
        self.assertTrue(cb.can_execute())

        # 2. First failure (threshold = 2) -> still CLOSED
        cb.record_failure(RuntimeError("HTTP 500 Internal Error"))
        self.assertEqual(cb.consecutive_failures, 1)
        self.assertEqual(cb.circuit_state, CircuitState.CLOSED)
        self.assertTrue(cb.can_execute())

        # 3. Second failure -> trips to OPEN
        cb.record_failure(RuntimeError("HTTP 503 Service Unavailable"))
        self.assertEqual(cb.consecutive_failures, 2)
        self.assertEqual(cb.circuit_state, CircuitState.OPEN)
        self.assertFalse(cb.can_execute())

        # 4. Wait for recovery timeout -> transitions to HALF_OPEN
        time.sleep(0.12)
        self.assertTrue(cb.can_execute())
        self.assertEqual(cb.circuit_state, CircuitState.HALF_OPEN)

        # 5. Success while HALF_OPEN resets to CLOSED
        cb.record_success()
        self.assertEqual(cb.circuit_state, CircuitState.CLOSED)
        self.assertEqual(cb.consecutive_failures, 0)
        self.assertEqual(cb.total_successes, 1)


class TestTTSAdapters(unittest.IsolatedAsyncioTestCase):
    """Verifies TTS provider adapters."""

    async def test_cartesia_tts_synthesis(self):
        cartesia = CartesiaTTS(
            voice_id="a0e99841-438c-4a64-b679-ae501e7d6091",
            model="sonic-english",
            api_key="mock_cartesia_test_key",
        )
        self.assertEqual(cartesia.provider_name, "cartesia")
        self.assertEqual(cartesia.model, "sonic-english")

        # Mock httpx response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"RIFF" + b"\x00" * 50 + b"WAVECARTESIA"

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
            audio = await cartesia.synthesize("Hello from Cartesia Sonic 3.0")
            self.assertTrue(audio.startswith(b"RIFF"))

    async def test_elevenlabs_tts_synthesis(self):
        eleven = ElevenLabsTTS(
            voice_id="21m00Tcm4TlvDq8ikWAM",
            model="eleven_flash_v2_5",
            api_key="mock_eleven_key",
        )
        self.assertEqual(eleven.provider_name, "elevenlabs")
        self.assertEqual(eleven.model, "eleven_flash_v2_5")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"RIFF" + b"\x00" * 50 + b"WAVEELEVEN"

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock, return_value=mock_response):
            audio = await eleven.synthesize("Hello from ElevenLabs Flash")
            self.assertTrue(audio.startswith(b"RIFF"))


class MockFailingTTS(BaseTTSAdapter):
    def __init__(self, provider_name: str = "failing_primary"):
        super().__init__(provider_name=provider_name, voice_id="test")

    async def synthesize(self, text: str) -> bytes:
        raise RuntimeError("Upstream provider 500 Outage")


class MockWorkingTTS(BaseTTSAdapter):
    def __init__(self, provider_name: str = "working_secondary"):
        super().__init__(provider_name=provider_name, voice_id="test")

    async def synthesize(self, text: str) -> bytes:
        return b"RIFF_AUDIO_OK"


class MockFailingSTT(BaseSTTAdapter):
    def __init__(self, provider_name: str = "failing_stt"):
        super().__init__(provider_name=provider_name)

    async def transcribe(self, audio_bytes: bytes) -> str:
        raise RuntimeError("STT WebSocket Timeout")


class MockWorkingSTT(BaseSTTAdapter):
    def __init__(self, provider_name: str = "working_stt"):
        super().__init__(provider_name=provider_name)

    async def transcribe(self, audio_bytes: bytes) -> str:
        return "I would like to book a haircut consultation."


class TestResilientMeshes(unittest.IsolatedAsyncioTestCase):
    """Verifies sub-200ms automatic mid-call failovers across TTS and STT meshes."""

    async def test_tts_mesh_automatic_failover(self):
        mesh = ResilientTTSMesh()
        failing_p = MockFailingTTS(provider_name="cartesia_primary")
        working_p = MockWorkingTTS(provider_name="fish_secondary")

        mesh.add_provider(failing_p)
        mesh.add_provider(working_p)

        # Primary will fail, should seamlessly fall over to secondary
        audio_bytes, active_provider = await mesh.synthesize("Testing voice synthesis failover")

        self.assertEqual(active_provider, "fish_secondary")
        self.assertEqual(audio_bytes, b"RIFF_AUDIO_OK")

        # Verify failing provider recorded a failure in circuit breaker
        health = mesh.get_health_status()
        self.assertEqual(health["cartesia_primary"]["consecutive_failures"], 1)
        self.assertEqual(health["fish_secondary"]["success_rate"], 1.0)

    async def test_stt_mesh_automatic_failover(self):
        mesh = ResilientSTTMesh()
        failing_stt = MockFailingSTT(provider_name="deepgram_primary")
        working_stt = MockWorkingSTT(provider_name="groq_whisper_secondary")

        mesh.add_provider(failing_stt)
        mesh.add_provider(working_stt)

        transcript, active_provider = await mesh.transcribe(b"DUMMY_AUDIO_FRAMES")

        self.assertEqual(active_provider, "groq_whisper_secondary")
        self.assertEqual(transcript, "I would like to book a haircut consultation.")

        health = mesh.get_health_status()
        self.assertEqual(health["deepgram_primary"]["consecutive_failures"], 1)
        self.assertEqual(health["groq_whisper_secondary"]["success_rate"], 1.0)

    async def test_build_default_meshes(self):
        tts_mesh = build_default_tts_mesh({"provider": "cartesia"})
        self.assertGreaterEqual(len(tts_mesh.providers), 2)
        provider_names = [p.provider_name for p in tts_mesh.providers]
        self.assertIn("cartesia", provider_names)
        self.assertIn("deepgram", provider_names)

        stt_mesh = build_default_stt_mesh({"model": "nova-3"})
        self.assertGreaterEqual(len(stt_mesh.providers), 1)
        stt_names = [p.provider_name for p in stt_mesh.providers]
        self.assertIn("deepgram", stt_names)


if __name__ == "__main__":
    unittest.main()
