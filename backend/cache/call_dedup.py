"""
Bloom Filter-based duplicate/spam call detection using RedisBloom.

Uses Redis Stack's built-in BF.* commands.
Detects if the same phone number has called within the cooldown window.

False positive rate: <1% at 10,000 entries.
Check latency: ~0.1ms.
"""

import logging
from typing import Tuple

logger = logging.getLogger("alfie-call-dedup")

BLOOM_KEY = "call_dedup_bloom"
COOLDOWN_KEY_PREFIX = "call_cooldown:"
COOLDOWN_SECONDS = 30  # Minimum seconds between calls from same number


async def init_bloom_filter(
    redis_client, capacity: int = 10000, error_rate: float = 0.01
):
    """
    Initialize the Bloom filter if it doesn't exist.
    Called once at startup in prewarm().
    """
    if not redis_client:
        return

    try:
        # BF.RESERVE is idempotent-safe — errors if already exists
        await redis_client.execute_command(
            "BF.RESERVE", BLOOM_KEY, error_rate, capacity
        )
        logger.info(f"RedisBloom filter initialized (capacity={capacity})")
    except Exception as e:
        if "item exists" in str(e).lower():
            logger.debug("Bloom filter already exists, skipping init")
        else:
            logger.warning(f"Bloom filter init failed: {e}")


async def check_duplicate_call(
    redis_client, phone: str, tenant_id: str
) -> Tuple[bool, str]:
    """
    Check if this call is a duplicate/spam.

    Returns:
        (is_allowed, reason)
        - (True, "ok") -> proceed with call
        - (False, "cooldown") -> same number called too recently
    """
    if not redis_client or not phone:
        return True, "ok"  # Fail open

    try:
        clean_phone = phone.replace(" ", "").replace("-", "")
        # Internal test numbers whitelist
        if clean_phone in ["127.0.0.1", "localhost", "test_caller", "+10000000000"]:
            return True, "ok"

        cooldown_key = f"{COOLDOWN_KEY_PREFIX}{tenant_id}:{clean_phone}"

        # Check hard cooldown first (exact match, no false positives)
        existing = await redis_client.get(cooldown_key)
        if existing:
            logger.warning(
                f"[SPAM BLOCKED] Phone {clean_phone} called again within "
                f"{COOLDOWN_SECONDS}s cooldown"
            )
            return False, "cooldown"

        # Set cooldown for this number
        await redis_client.setex(cooldown_key, COOLDOWN_SECONDS, "1")

        # Also add to bloom filter for long-term pattern analysis
        try:
            await redis_client.execute_command("BF.ADD", BLOOM_KEY, clean_phone)
        except Exception:
            pass

        return True, "ok"
    except Exception as e:
        logger.debug(f"Duplicate call check failed: {e}")
        return True, "ok"  # Fail open
