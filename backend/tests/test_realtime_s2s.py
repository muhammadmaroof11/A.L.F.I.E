"""
Unit and integration tests for A.L.F.I.E Phase 4:
Dual-Engine Architecture and OpenAI Realtime Speech-to-Speech (S2S) Multimodal Engine.
"""

import asyncio
import base64
import json
import os
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# Ensure test credentials exist before importing settings
os.environ.setdefault("DEEPGRAM_API_KEY", "mock_key")
os.environ.setdefault("OPENROUTER_API_KEY", "mock_key")
os.environ.setdefault("FISH_AUDIO_API_KEY", "mock_key")
os.environ.setdefault("OPENAI_API_KEY", "mock_openai_realtime_key")
os.environ.setdefault("JWT_SECRET_KEY", "test_secret_key_for_unit_tests_32chars!")
os.environ.setdefault("SUPER_ADMIN_EMAIL", "admin@alfie-ai.com")
os.environ.setdefault("SUPER_ADMIN_PASSWORD", "testpass")

from pipeline.realtime_s2s import EngineMode, OpenAIRealtimeSession
from pipeline.audio_engine import build_audio_pipeline, create_realtime_s2s_session


def mock_sync_tool(service_type: str, date: str) -> dict:
    """Check schedule availability."""
    return {"status": "available", "slots": ["10:00 AM", "2:00 PM"]}


async def mock_async_booking_tool(service_name: str, customer_phone: str) -> dict:
    """Book appointment in CRM."""
    return {"booking_id": "bk-999123", "confirmed": True}


class TestOpenAIRealtimeSession(unittest.IsolatedAsyncioTestCase):
    """Verifies the OpenAI Realtime S2S Multimodal Session Adapter."""

    def setUp(self):
        self.session = OpenAIRealtimeSession(
            instructions="You are a warm, conversational AI receptionist for a luxury salon.",
            voice="alloy",
            model="gpt-4o-realtime-preview",
            tools=[mock_sync_tool, mock_async_booking_tool],
            temperature=0.7,
            api_key="mock_key",
        )

    def test_session_update_payload_construction(self):
        payload = self.session.build_session_update()

        self.assertEqual(payload["type"], "session.update")
        sess = payload["session"]
        self.assertEqual(sess["voice"], "alloy")
        self.assertEqual(sess["input_audio_format"], "pcm16")
        self.assertEqual(sess["output_audio_format"], "pcm16")
        self.assertIn("text", sess["modalities"])
        self.assertIn("audio", sess["modalities"])
        self.assertEqual(sess["turn_detection"]["type"], "server_vad")

        # Verify serialized tools
        tools = sess["tools"]
        self.assertEqual(len(tools), 2)
        tool_names = [t["name"] for t in tools]
        self.assertIn("mock_sync_tool", tool_names)
        self.assertIn("mock_async_booking_tool", tool_names)

    def test_audio_framing_and_base64_conversion(self):
        raw_pcm = b"\x00\x10\x00\x20\x00\x30"
        b64 = self.session.encode_pcm_chunk(raw_pcm)
        decoded = self.session.decode_pcm_chunk(b64)
        self.assertEqual(decoded, raw_pcm)

        append_event = self.session.create_audio_append_event(raw_pcm)
        self.assertEqual(append_event["type"], "input_audio_buffer.append")
        self.assertEqual(append_event["audio"], b64)

    async def test_inbound_audio_and_transcript_events(self):
        # 1. Audio delta event
        raw_audio = b"RIFF_PCM_DATA_CHUNK"
        b64_audio = base64.b64encode(raw_audio).decode("utf-8")

        events = await self.session.handle_server_event({
            "type": "response.audio.delta",
            "delta": b64_audio,
        })
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["action"], "audio_delta")
        self.assertEqual(events[0]["audio_bytes"], raw_audio)

        # 2. Agent transcript delta
        t_events = await self.session.handle_server_event({
            "type": "response.audio_transcript.delta",
            "delta": "Certainly, let me check ",
        })
        self.assertEqual(len(t_events), 1)
        self.assertEqual(t_events[0]["action"], "transcript_delta")
        self.assertEqual(t_events[0]["text"], "Certainly, let me check ")
        self.assertEqual(t_events[0]["speaker"], "agent")

    async def test_barge_in_and_muting_shim(self):
        # 1. Barge-in detection
        barge_events = await self.session.handle_server_event({
            "type": "input_audio_buffer.speech_started",
        })
        self.assertEqual(len(barge_events), 1)
        self.assertEqual(barge_events[0]["action"], "barge_in")

        # 2. Muting during 1-Click Takeover
        self.session.set_muted(True)
        self.assertTrue(self.session.is_muted)

        muted_audio_events = await self.session.handle_server_event({
            "type": "response.audio.delta",
            "delta": base64.b64encode(b"SILENCED_AGENT_AUDIO").decode("utf-8"),
        })
        self.assertEqual(len(muted_audio_events), 0)

    async def test_tool_execution_dispatch(self):
        # Trigger async tool call from OpenAI Realtime
        fn_event = {
            "type": "response.function_call_arguments.done",
            "call_id": "call_fn_12345",
            "name": "mock_async_booking_tool",
            "arguments": json.dumps({"service_name": "VIP Haircut", "customer_phone": "+1555123456"}),
        }

        outcomes = await self.session.handle_server_event(fn_event)
        self.assertEqual(len(outcomes), 2)

        # First outcome is conversation.item.create with function output
        self.assertEqual(outcomes[0]["action"], "send_to_server")
        item_payload = outcomes[0]["payload"]
        self.assertEqual(item_payload["type"], "conversation.item.create")
        self.assertEqual(item_payload["item"]["type"], "function_call_output")
        self.assertEqual(item_payload["item"]["call_id"], "call_fn_12345")

        output_data = json.loads(item_payload["item"]["output"])
        self.assertEqual(output_data["booking_id"], "bk-999123")
        self.assertTrue(output_data["confirmed"])

        # Second outcome is response.create to continue generation
        self.assertEqual(outcomes[1]["action"], "send_to_server")
        self.assertEqual(outcomes[1]["payload"]["type"], "response.create")

    def test_supervisor_and_dtmf_shims(self):
        # 1. Ghost Whisper
        whisper = self.session.inject_supervisor_whisper("Offer 10% discount on first booking")
        self.assertEqual(whisper["type"], "conversation.item.create")
        self.assertIn("10% discount", whisper["item"]["content"][0]["text"])

        # 2. DTMF Tone
        dtmf = self.session.handle_dtmf_digit("1")
        self.assertEqual(dtmf["type"], "conversation.item.create")
        self.assertIn("DIGIT: 1", dtmf["item"]["content"][0]["text"])


class TestDualEngineDispatcher(unittest.IsolatedAsyncioTestCase):
    """Verifies that the pipeline dynamically instantiates the correct engine mode."""

    async def test_native_s2s_pipeline_dispatch(self):
        config_data = {
            "engine_mode": "native_s2s",
            "openai_realtime_config": {
                "voice": "shimmer",
                "model": "gpt-4o-realtime-preview",
            },
        }

        agent, session, endpoint_analyzer, vad, anti_interruption = await build_audio_pipeline(
            config_data=config_data,
            assembled_prompt="System Prompt Test",
            toolsets=[mock_sync_tool],
            cache_enabled=True,
            tenant_id="tenant-s2s-101",
        )

        self.assertIsInstance(agent, OpenAIRealtimeSession)
        self.assertEqual(agent.voice, "shimmer")
        self.assertEqual(agent.model, "gpt-4o-realtime-preview")

    async def test_cascaded_pipeline_dispatch(self):
        config_data = {
            "engine_mode": "cascaded",
            "voice_config": {"provider": "cartesia"},
        }

        agent, session, endpoint_analyzer, vad, anti_interruption = await build_audio_pipeline(
            config_data=config_data,
            assembled_prompt="System Prompt Test",
            toolsets=[],
            cache_enabled=True,
            tenant_id="tenant-cascaded-202",
        )

        # Agent should be LiveKit Agent or cascaded pipeline instance
        self.assertNotIsInstance(agent, OpenAIRealtimeSession)


if __name__ == "__main__":
    unittest.main()
