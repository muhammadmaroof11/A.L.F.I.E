import logging
from typing import Dict, Optional

logger = logging.getLogger("alfie-feature-flags")

DEFAULT_FLAGS: Dict[str, str] = {
    "semantic_cache_enabled": "1",
    "caller_memory_enabled": "1",
    "prompt_compression_enabled": "1",
    "demo_timer_enforced": "1",
    "max_call_duration_seconds": "900",
    "greeting_style": "warm_professional",
}


async def get_tenant_flags(redis_client, tenant_id: str) -> Dict[str, str]:
    """
    Fetches all active feature flags for a tenant via Redis hash.
    Falls back to system defaults if not explicitly set.
    """
    flags = dict(DEFAULT_FLAGS)
    if not redis_client or not tenant_id:
        return flags

    try:
        key = f"tenant_flags:{tenant_id}"
        custom_flags = await redis_client.hgetall(key)
        if custom_flags:
            flags.update(custom_flags)
    except Exception as e:
        logger.warning(f"Error reading tenant feature flags from Redis: {e}")

    return flags


async def set_tenant_flag(
    redis_client, tenant_id: str, flag_name: str, flag_value: str
):
    """
    Sets or overrides a specific feature flag for a tenant without database downtime.
    """
    if not redis_client or not tenant_id or not flag_name:
        return

    try:
        key = f"tenant_flags:{tenant_id}"
        await redis_client.hset(key, flag_name, str(flag_value))
        logger.info(
            f"Set tenant flag '{flag_name}' = '{flag_value}' for tenant {tenant_id}"
        )
    except Exception as e:
        logger.warning(f"Error setting tenant flag in Redis: {e}")


async def is_feature_enabled(
    redis_client, tenant_id: str, flag_name: str, default: bool = True
) -> bool:
    """
    Helper to check a single boolean feature flag with zero overhead.
    """
    if not redis_client or not tenant_id:
        return default

    try:
        key = f"tenant_flags:{tenant_id}"
        val = await redis_client.hget(key, flag_name)
        if val is not None:
            return val in ["1", "true", "True", "yes"]
    except Exception as e:
        logger.debug(f"Feature flag lookup failed: {e}")

    return default
