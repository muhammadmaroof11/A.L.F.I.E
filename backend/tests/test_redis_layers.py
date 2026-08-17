import unittest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from cache.caller_memory import (
    build_memory_prompt,
    update_caller_memory,
    get_caller_context,
)
from cache.demo_limiter import check_demo_rate_limit
from cache.feature_flags import get_tenant_flags, set_tenant_flag, is_feature_enabled
from cache.faq_prewarmer import NICHE_FAQS
from cache.transfer_buffer import store_transfer_context, get_transfer_context


class TestRedisLayers(unittest.IsolatedAsyncioTestCase):
    def test_build_memory_prompt(self):
        caller_data = {
            "name": "Sarah Connor",
            "call_count": "3",
            "last_intent": "Luxury Villa Viewing",
            "notes": "Prefers beachfront properties in Miami",
            "last_call": "2026-08-16T12:00:00Z",
        }
        prompt = build_memory_prompt(caller_data)
        self.assertIn("RETURNING CALLER PROFILE & MEMORY", prompt)
        self.assertIn("Sarah Connor", prompt)
        self.assertIn("3 time(s)", prompt)
        self.assertIn("Luxury Villa Viewing", prompt)
        self.assertIn("Prefers beachfront properties in Miami", prompt)

    def test_build_memory_prompt_empty(self):
        self.assertEqual(build_memory_prompt(None), "")
        self.assertEqual(build_memory_prompt({}), "")

    def test_niche_faqs_structure(self):
        expected_niches = [
            "legal_intake",
            "real_estate",
            "car_rental",
            "medical_reception",
            "hospitality",
            "demo",
        ]
        for niche in expected_niches:
            self.assertIn(niche, NICHE_FAQS)
            self.assertGreaterEqual(len(NICHE_FAQS[niche]), 3)
            for q, a in NICHE_FAQS[niche]:
                self.assertGreater(len(q), 5)
                self.assertGreater(len(a), 10)

    async def test_demo_rate_limiter(self):
        mock_redis = AsyncMock()
        mock_redis.get.return_value = "2"
        mock_pipe = MagicMock()
        mock_pipe.incr = MagicMock()
        mock_pipe.expire = MagicMock()
        mock_pipe.execute = AsyncMock()
        mock_redis.pipeline = MagicMock(return_value=mock_pipe)

        allowed = await check_demo_rate_limit(mock_redis, "192.168.1.50", limit=5)
        self.assertTrue(allowed)

        mock_redis.get.return_value = "5"
        blocked = await check_demo_rate_limit(mock_redis, "192.168.1.50", limit=5)
        self.assertFalse(blocked)

        # Localhost should always pass
        localhost_allowed = await check_demo_rate_limit(
            mock_redis, "127.0.0.1", limit=1
        )
        self.assertTrue(localhost_allowed)

    async def test_feature_flags(self):
        mock_redis = AsyncMock()
        mock_redis.hgetall.return_value = {
            "semantic_cache_enabled": "1",
            "max_call_duration_seconds": "600",
        }

        flags = await get_tenant_flags(mock_redis, "tenant-123")
        self.assertEqual(flags["semantic_cache_enabled"], "1")
        self.assertEqual(flags["max_call_duration_seconds"], "600")

        mock_redis.hget.return_value = "1"
        enabled = await is_feature_enabled(
            mock_redis, "tenant-123", "semantic_cache_enabled"
        )
        self.assertTrue(enabled)

        mock_redis.hget.return_value = "0"
        disabled = await is_feature_enabled(
            mock_redis, "tenant-123", "semantic_cache_enabled"
        )
        self.assertFalse(disabled)

    async def test_transfer_buffer(self):
        mock_redis = AsyncMock()
        mock_redis.get.return_value = '{"tenant_id": "t1", "caller_phone": "+1234567890", "transcript_summary": "Inquiring about legal retainer"}'

        context = await get_transfer_context(mock_redis, "room-abc")
        self.assertIsNotNone(context)
        self.assertEqual(context["caller_phone"], "+1234567890")
        self.assertIn("legal retainer", context["transcript_summary"])


if __name__ == "__main__":
    unittest.main()
