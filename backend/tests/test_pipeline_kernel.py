import asyncio
import json
import os
import sys
import unittest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

# Mock heavy external modules if not installed in lightweight testing env
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
]:
    try:
        __import__(mod)
    except (ImportError, Exception):
        sys.modules[mod] = MagicMock()

import livekit.plugins.silero as silero_mod
silero_mod.VAD = MagicMock()
silero_mod.VAD.load = MagicMock()

# Setup test secrets
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

from pipeline import (
    CallMetrics,
    CallTelemetrySink,
    DialogueSessionManager,
    assemble_system_prompt,
    build_audio_pipeline,
    create_stt_plugin,
    create_tts_plugin,
    create_vad_and_endpointing,
    get_default_config,
    resolve_call_config,
    safe_uuid,
)
from agent import get_default_config as agent_get_default_config, CallMetrics as AgentCallMetrics


class TestPipelineKernel(unittest.IsolatedAsyncioTestCase):
    def test_default_config_contract(self):
        """Verify get_default_config provides all required keys."""
        conf = get_default_config(niche="dental_clinic", tenant_id="t-123")
        self.assertEqual(conf["niche"], "dental_clinic")
        self.assertIn("voice_config", conf)
        self.assertIn("stt_config", conf)
        self.assertIn("llm_config", conf)
        self.assertIn("vad_config", conf)
        self.assertTrue(conf.get("backchanneling_enabled"))
        self.assertTrue(conf.get("conversational_fillers_enabled"))

    def test_agent_backwards_compatibility(self):
        """Verify agent.py exports get_default_config and CallMetrics for existing callers."""
        conf = agent_get_default_config(niche="legal_intake")
        self.assertEqual(conf["niche"], "legal_intake")
        metrics = AgentCallMetrics()
        self.assertEqual(metrics.avg([100, 200]), 150)

    def test_safe_uuid(self):
        """Verify safe_uuid handles strings, invalid tokens, and None safely."""
        valid_str = "12345678-1234-5678-1234-567812345678"
        u = safe_uuid(valid_str)
        self.assertEqual(str(u), valid_str)
        self.assertIsNone(safe_uuid("invalid-uuid"))
        self.assertIsNone(safe_uuid(None))

    async def test_resolve_call_config_from_redis_cache(self):
        """Verify resolve_call_config immediately returns cached config if available."""
        fake_redis = AsyncMock()
        mock_conf = {"niche": "luxury_transport", "agent_name": "VIP Chauffeur"}
        fake_redis.get.return_value = json.dumps(mock_conf)

        resolved = await resolve_call_config(
            tenant_id="tenant-123",
            agent_id="agent-456",
            metadata={},
            redis_client=fake_redis,
        )
        self.assertEqual(resolved["niche"], "luxury_transport")
        self.assertEqual(resolved["agent_name"], "VIP Chauffeur")
        fake_redis.get.assert_called_once_with("tenant_config:agent-456")

    async def test_assemble_system_prompt_zero_latency(self):
        """Verify assemble_system_prompt builds complete prompt without blocking."""
        fake_redis = AsyncMock()
        fake_redis.get.return_value = None
        fake_redis.exists.return_value = False
        fake_redis.hget.return_value = "1"
        fake_redis.hgetall.return_value = {}

        with patch("pipeline.context_factory.get_caller_context", new_callable=AsyncMock) as mock_caller_ctx:
            mock_caller_ctx.return_value = {"caller_name": "Sarah", "notes": "VIP client"}
            conf = get_default_config(niche="car_rental", tenant_id="t-rent-1")
            prompt, slot_tracker, cache_enabled = await assemble_system_prompt(
                tenant_id="t-rent-1",
                agent_id=None,
                config_data=conf,
                metadata={"caller_phone": "+14155552671"},
                room_name="room_rent_01",
                redis_client=fake_redis,
            )
            self.assertTrue(len(prompt) > 50)
            self.assertIsNotNone(slot_tracker)
            self.assertTrue(cache_enabled)

    def test_audio_engine_creators(self):
        """Verify STT, TTS, and VAD plugin initializers."""
        stt = create_stt_plugin({"model": "nova-2", "language": "en"}, "dummy-key")
        self.assertIsNotNone(stt)

        tts = create_tts_plugin({"provider": "fish_audio", "model": "s2.1-pro"})
        self.assertIsNotNone(tts)

        vad, analyzer, anti_interrupt = create_vad_and_endpointing(
            {"min_silence_duration": 0.55, "endpointing_preset": "natural"}
        )
        self.assertIsNotNone(vad)
        self.assertIsNotNone(analyzer)
        self.assertTrue(anti_interrupt)

    async def test_telemetry_sink_lifecycle(self):
        """Verify CallTelemetrySink initializes, sends deltas, and finalizes cleanly."""
        fake_redis = AsyncMock()
        fake_arq = AsyncMock()

        sink = CallTelemetrySink(
            tenant_id="tenant-audit-1",
            call_id="call-room-99",
            agent_id="agent-01",
            agent_name="Alfie Test Agent",
            niche="general",
            caller_phone="+1234567890",
            redis_client=fake_redis,
            arq_pool=fake_arq,
        )

        with patch("pipeline.telemetry_sink.init_call_record", new_callable=AsyncMock) as mock_init:
            with patch("pipeline.telemetry_sink.complete_call_record", new_callable=AsyncMock) as mock_complete:
                with patch("pipeline.telemetry_sink.update_caller_memory", new_callable=AsyncMock):
                    await sink.initialize()
                    sink.publish_transcript_delta(
                        turn_id="turn_1", role="user", text="Hello there", offset_ms=100
                    )
                    sink.update_live_state(state="speaking", speaker="caller")

                    await sink.finalize(
                        turns_count=2,
                        interruption_count=0,
                        dtmf_events=[],
                        frustration_tracker=None,
                        slot_tracker=None,
                    )
                    mock_complete.assert_called_once()
                    self.assertEqual(fake_arq.enqueue_job.call_count, 2)
                    fake_arq.enqueue_job.assert_any_call(
                        "process_call_qa",
                        call_id="call-room-99",
                        tenant_id="tenant-audit-1",
                    )
                    fake_arq.enqueue_job.assert_any_call(
                        "process_call_recording_job",
                        call_id="call-room-99",
                        tenant_id="tenant-audit-1",
                    )


if __name__ == "__main__":
    unittest.main()
