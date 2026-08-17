import unittest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from cache.caller_memory import (
    build_memory_prompt,
    update_caller_memory,
    get_caller_context,
)
from cache.demo_limiter import check_demo_rate_limit
from cache.feature_flags import get_tenant_flags, set_tenant_flag, is_feature_enabled
from cache.faq_prewarmer import NICHE_FAQS, prewarm_tenant_specific
from cache.transfer_buffer import store_transfer_context, get_transfer_context
from cache.prompt_cache import get_cached_prompt, store_cached_prompt
from cache.config_invalidation import invalidate_tenant_config
from cache.call_dedup import init_bloom_filter, check_duplicate_call
from cache.metrics import (
    init_timeseries,
    record_cache_hit,
    record_cache_miss,
    record_call_start,
    get_cache_hit_rate,
)


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

    async def test_prompt_cache(self):
        mock_redis = AsyncMock()
        mock_redis.get.return_value = "Compressed System Prompt"

        res = await get_cached_prompt(mock_redis, "Raw System Prompt Context")
        self.assertEqual(res, "Compressed System Prompt")

        mock_redis.get.return_value = None
        miss = await get_cached_prompt(mock_redis, "Unseen Prompt")
        self.assertIsNone(miss)

        await store_cached_prompt(
            mock_redis, "Raw System Prompt Context", "Compressed System Prompt"
        )
        mock_redis.setex.assert_awaited_once()

    async def test_caller_memory_pipeline_batching(self):
        mock_redis = AsyncMock()
        mock_pipe = MagicMock()
        mock_pipe.hincrby = MagicMock()
        mock_pipe.hset = MagicMock()
        mock_pipe.expire = MagicMock()
        mock_pipe.execute = AsyncMock()
        mock_redis.pipeline = MagicMock(return_value=mock_pipe)

        await update_caller_memory(
            mock_redis,
            tenant_id="tenant-99",
            phone="+1234567890",
            name="John Connor",
            notes="Followup call",
            intent="booking_inquiry",
            intent_score=9,
        )

        mock_pipe.hincrby.assert_called_once_with(
            "caller:tenant-99:+1234567890", "call_count", 1
        )
        mock_pipe.hset.assert_called_once()
        mock_pipe.expire.assert_called_once()
        mock_pipe.execute.assert_awaited_once()

    async def test_call_dedup_cooldown_and_bloom(self):
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None
        mock_redis.execute_command = AsyncMock()

        # First call allowed
        allowed, reason = await check_duplicate_call(
            mock_redis, "+15551234567", "tenant-1"
        )
        self.assertTrue(allowed)
        self.assertEqual(reason, "ok")
        mock_redis.setex.assert_awaited_once()

        # Second call in cooldown rejected
        mock_redis.get.return_value = "1"
        blocked, reason = await check_duplicate_call(
            mock_redis, "+15551234567", "tenant-1"
        )
        self.assertFalse(blocked)
        self.assertEqual(reason, "cooldown")

        # Whitelist allowed
        white_allowed, _ = await check_duplicate_call(
            mock_redis, "127.0.0.1", "tenant-1"
        )
        self.assertTrue(white_allowed)

    async def test_config_invalidation(self):
        mock_redis = AsyncMock()
        mock_redis.scan = AsyncMock(
            return_value=(0, ["prompt_compressed:abc1234567890123"])
        )
        mock_redis.delete = AsyncMock()

        await invalidate_tenant_config(
            mock_redis, tenant_id="tenant-1", agent_id="agent-2"
        )
        self.assertEqual(mock_redis.delete.await_count, 2)

    async def test_metrics_timeseries(self):
        mock_redis = AsyncMock()
        mock_redis.execute_command = AsyncMock(
            side_effect=[
                None,  # TS.INCRBY hit
                None,  # TS.INCRBY miss
                None,  # TS.INCRBY call
                [[1000, 15]],  # TS.RANGE hits
                [[1000, 5]],  # TS.RANGE misses
            ]
        )

        await record_cache_hit(mock_redis, "tenant-1")
        await record_cache_miss(mock_redis, "tenant-1")
        await record_call_start(mock_redis, "tenant-1")

        rate_data = await get_cache_hit_rate(mock_redis, "tenant-1")
        self.assertEqual(rate_data["hits"], 15)
        self.assertEqual(rate_data["misses"], 5)
        self.assertEqual(rate_data["rate"], 75.0)
        self.assertAlmostEqual(rate_data["savings_usd"], 15 * 0.02)

    async def test_tenant_specific_prewarm(self):
        with patch(
            "cache.faq_prewarmer.store_semantic_cache", new_callable=AsyncMock
        ) as mock_store:
            config = {
                "business_name": "Apex Legal Group",
                "office_hours": "Mon-Fri 9am-5pm",
                "address": "100 Brickell Ave, Miami, FL",
                "phone": "+1-800-555-APEX",
                "services": "Corporate Litigation and M&A",
            }
            await prewarm_tenant_specific("tenant-100", "legal_intake", config)
            self.assertGreaterEqual(mock_store.await_count, 5)


if __name__ == "__main__":
    unittest.main()
