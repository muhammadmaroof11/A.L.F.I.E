import os
import sys

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set mock secrets for testing environment before importing Settings/FastAPI
os.environ.setdefault("DEEPGRAM_API_KEY", "mock_key")
os.environ.setdefault("OPENROUTER_API_KEY", "mock_key")
os.environ.setdefault("FISH_AUDIO_API_KEY", "mock_key")
os.environ.setdefault("JWT_SECRET_KEY", "test_secret_key_for_unit_tests_32chars!")
os.environ.setdefault("SUPER_ADMIN_EMAIL", "admin@alfie-ai.com")
os.environ.setdefault("SUPER_ADMIN_PASSWORD", "testpass")
