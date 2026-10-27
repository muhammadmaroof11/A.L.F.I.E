import os
import sys
from unittest.mock import MagicMock
import unittest

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

# Ensure dummy environment keys for testing
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


class TestAgentDecoupling(unittest.TestCase):
    def test_settings_initializes_without_twenty_api_key(self):
        """Verify that Settings does not crash if twenty_api_key is empty."""
        self.assertIsNotNone(settings)
        self.assertFalse(hasattr(settings, "STARTUP_FAILED"))

    def test_get_default_config_structure(self):
        """Verify that get_default_config returns all essential keys required by the pipeline."""
        conf = get_default_config(niche="legal_intake", tenant_id="test-tenant-123")
        self.assertEqual(conf["niche"], "legal_intake")
        self.assertIn("voice_config", conf)
        self.assertIn("stt_config", conf)
        self.assertIn("llm_config", conf)
        self.assertIn("vad_config", conf)
        self.assertIn("enabled_tools", conf)
        self.assertEqual(conf["voice_config"]["provider"], "fish_audio")
        self.assertEqual(conf["stt_config"]["provider"], "deepgram")
        self.assertEqual(conf["llm_config"]["provider"], "openrouter")

    def test_get_default_config_fallback(self):
        """Verify that get_default_config defaults to 'general' when niche is empty."""
        conf = get_default_config(niche="")
        self.assertEqual(conf["niche"], "general")


if __name__ == "__main__":
    unittest.main()
