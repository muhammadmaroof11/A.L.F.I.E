import logging
from typing import Optional

logger = logging.getLogger("alfie-demo-limiter")

DEFAULT_DAILY_DEMO_LIMIT = 5
DEMO_TTL_SECONDS = 86400  # 24 hours


async def check_demo_rate_limit(
    redis_client, client_ip: str, limit: int = DEFAULT_DAILY_DEMO_LIMIT
) -> bool:
    """
    Checks if a visitor IP has exceeded their daily limit of live demo calls.
    Returns True if allowed, False if rate limited.
    Fails open (returns True) if Redis is unavailable.
    """
    if not redis_client or not client_ip:
        return True

    try:
        clean_ip = client_ip.strip()
        # Whitelist localhost/internal IPs
        if clean_ip in ["127.0.0.1", "::1", "localhost", "testclient"]:
            return True

        key = f"demo_rate_limit:{clean_ip}"
        current = await redis_client.get(key)

        if current and int(current) >= limit:
            logger.warning(
                f"[DEMO RATE LIMIT HIT] IP {clean_ip} has exhausted daily demo allowance ({current}/{limit})."
            )
            return False

        pipe = redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, DEMO_TTL_SECONDS)
        await pipe.execute()
        return True
    except Exception as e:
        logger.warning(f"Demo rate limit check encountered error: {e}")
        return True
