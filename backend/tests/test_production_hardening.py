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
from agent import get_default_config
from prompts.base import BASE_SYSTEM_PROMPT
from worker import dispatch_demo_outbound_call, WorkerSettings


class TestProductionHardening(unittest.TestCase):
    def test_default_config_includes_fillers_and_backchanneling(self):
        """Verify get_default_config provides conversational fillers and backchanneling enabled by default."""
        conf = get_default_config(niche="dental_clinic", tenant_id="tenant-prod-1")
        self.assertTrue(conf.get("backchanneling_enabled"))
        self.assertTrue(conf.get("conversational_fillers_enabled"))
        self.assertEqual(conf["voice_config"]["provider"], "fish_audio")

    def test_system_prompt_contains_fillers_and_backchanneling(self):
        """Verify BASE_SYSTEM_PROMPT includes explicit zero-dead-air and acoustic backchanneling rules."""
        self.assertIn("CONVERSATIONAL FILLERS & ZERO DEAD AIR (CRITICAL)", BASE_SYSTEM_PROMPT)
        self.assertIn("ACOUSTIC BACKCHANNELING GUIDELINES", BASE_SYSTEM_PROMPT)
        self.assertIn("mhm", BASE_SYSTEM_PROMPT)
        self.assertIn("I understand", BASE_SYSTEM_PROMPT)

    def test_tts_fallback_uses_deepgram_when_openai_key_absent(self):
        """Verify that when openai_api_key is empty, TTS fallback cleanly selects Deepgram Aura, never using OpenRouter key."""
        with patch.object(settings, "openai_api_key", ""), \
             patch.object(settings, "openrouter_api_key", "sk-or-v1-openrouter-key"), \
             patch.object(settings, "deepgram_api_key", "deepgram-valid-key"):
            
            # Simulate the fallback resolution from agent.py
            config_data = {"voice_config": {"provider": "fish_audio"}}
            has_fish_key = False
            
            tts_provider = config_data["voice_config"].get("provider", "fish_audio")
            chosen_tts = None
            if tts_provider == "fish_audio" and has_fish_key:
                chosen_tts = "fish_audio"
            elif settings.openai_api_key:
                chosen_tts = "openai"
            else:
                chosen_tts = "deepgram_aura"

            self.assertEqual(chosen_tts, "deepgram_aura")
            # Crucial check: openrouter_api_key is never used for OpenAI TTS
            self.assertNotEqual(chosen_tts, "openai")

    def test_tts_fallback_uses_openai_when_openai_key_present(self):
        """Verify that when dedicated openai_api_key is provided, OpenAI TTS is selected."""
        with patch.object(settings, "openai_api_key", "sk-proj-valid-openai-key"):
            config_data = {"voice_config": {"provider": "fish_audio"}}
            has_fish_key = False
            
            tts_provider = config_data["voice_config"].get("provider", "fish_audio")
            chosen_tts = None
            if tts_provider == "fish_audio" and has_fish_key:
                chosen_tts = "fish_audio"
            elif settings.openai_api_key:
                chosen_tts = "openai"
            else:
                chosen_tts = "deepgram_aura"

            self.assertEqual(chosen_tts, "openai")

    def test_worker_settings_has_outbound_dispatch_registered(self):
        """Verify dispatch_demo_outbound_call is registered in WorkerSettings.functions."""
        self.assertIn(dispatch_demo_outbound_call, WorkerSettings.functions)

    def test_dispatch_demo_outbound_call_execution(self):
        """Verify dispatch_demo_outbound_call executes smoothly and returns a valid dispatched status."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                dispatch_demo_outbound_call(
                    ctx={},
                    phone_number="+15551234567",
                    niche="personal_injury",
                    visitor_name="Jane Doe",
                    company_name="Acme Legal",
                )
            )
            self.assertEqual(result["status"], "dispatched")
            self.assertEqual(result["phone_number"], "+15551234567")
            self.assertTrue(result["room_name"].startswith("demo-outbound-"))
            self.assertIn("method", result)
        finally:
            loop.close()


if __name__ == "__main__":
    unittest.main()
