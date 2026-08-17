"""
Redis TimeSeries metrics for cache observability.

Tracks:
  - ts:cache_hit:{tenant_id}   — Incremented on each semantic cache hit
  - ts:cache_miss:{tenant_id}  — Incremented on each semantic cache miss
  - ts:calls:{tenant_id}       — Incremented on each call start
  - ts:cost_saved:{tenant_id}  — Estimated USD saved per cache hit

Queryable via TS.RANGE for the admin dashboard.
24-hour retention with 1-minute aggregation buckets.
"""

import logging

logger = logging.getLogger("alfie-metrics")

RETENTION_MS = 86_400_000  # 24 hours
DEFAULT_COST_PER_LLM_CALL = 0.02  # Estimated cost per LLM call in USD


async def init_timeseries(redis_client, tenant_id: str):
    """Create TimeSeries keys for a tenant (idempotent)."""
    if not redis_client or not tenant_id:
        return

    for metric in ["cache_hit", "cache_miss", "calls"]:
        try:
            await redis_client.execute_command(
                "TS.CREATE",
                f"ts:{metric}:{tenant_id}",
                "RETENTION",
                RETENTION_MS,
                "LABELS",
                "tenant",
                tenant_id,
                "metric",
                metric,
                "DUPLICATE_POLICY",
                "SUM",
            )
        except Exception:
            pass  # Already exists or TS module not available


async def record_cache_hit(redis_client, tenant_id: str):
    """Record a semantic cache hit."""
    if not redis_client or not tenant_id:
        return
    try:
        await redis_client.execute_command(
            "TS.INCRBY",
            f"ts:cache_hit:{tenant_id}",
            1,
            "RETENTION",
            RETENTION_MS,
            "LABELS",
            "tenant",
            tenant_id,
            "metric",
            "cache_hit",
        )
    except Exception as e:
        logger.debug(f"TimeSeries record hit failed: {e}")


async def record_cache_miss(redis_client, tenant_id: str):
    """Record a semantic cache miss."""
    if not redis_client or not tenant_id:
        return
    try:
        await redis_client.execute_command(
            "TS.INCRBY",
            f"ts:cache_miss:{tenant_id}",
            1,
            "RETENTION",
            RETENTION_MS,
            "LABELS",
            "tenant",
            tenant_id,
            "metric",
            "cache_miss",
        )
    except Exception as e:
        logger.debug(f"TimeSeries record miss failed: {e}")


async def record_call_start(redis_client, tenant_id: str):
    """Record a call start event."""
    if not redis_client or not tenant_id:
        return
    try:
        await redis_client.execute_command(
            "TS.INCRBY",
            f"ts:calls:{tenant_id}",
            1,
            "RETENTION",
            RETENTION_MS,
            "LABELS",
            "tenant",
            tenant_id,
            "metric",
            "calls",
        )
    except Exception as e:
        logger.debug(f"TimeSeries record call start failed: {e}")


async def get_cache_hit_rate(
    redis_client, tenant_id: str, window_ms: int = 3_600_000
) -> dict:
    """
    Query cache hit rate for the last `window_ms` milliseconds.
    Returns dict with hits, misses, rate, and estimated savings.
    """
    if not redis_client or not tenant_id:
        return {"hits": 0, "misses": 0, "rate": 0.0, "savings_usd": 0.0}

    try:
        hits_data = await redis_client.execute_command(
            "TS.RANGE",
            f"ts:cache_hit:{tenant_id}",
            "-",
            "+",
            "AGGREGATION",
            "sum",
            str(window_ms),
        )
        misses_data = await redis_client.execute_command(
            "TS.RANGE",
            f"ts:cache_miss:{tenant_id}",
            "-",
            "+",
            "AGGREGATION",
            "sum",
            str(window_ms),
        )

        hits = int(float(hits_data[-1][1])) if hits_data else 0
        misses = int(float(misses_data[-1][1])) if misses_data else 0
        total = hits + misses
        rate = (hits / total * 100) if total > 0 else 0.0
        savings = hits * DEFAULT_COST_PER_LLM_CALL

        return {
            "hits": hits,
            "misses": misses,
            "rate": round(rate, 1),
            "savings_usd": round(savings, 4),
        }
    except Exception as e:
        logger.debug(f"TimeSeries query failed: {e}")
        return {"hits": 0, "misses": 0, "rate": 0.0, "savings_usd": 0.0}
