"""
Prompt Template Cache — Avoids redundant LLMLingua compression calls.

Key pattern: prompt_compressed:{sha256_hex[:16]}
Value: The compressed prompt string
TTL: 300 seconds (5 minutes) — matches config cache lifetime

Flow:
  1. Hash the raw system prompt (before compression)
  2. Check Redis for existing compressed version
  3. HIT  -> Use cached compressed prompt (0ms vs 200-2000ms)
  4. MISS -> Call LLMLingua, cache the result
"""

import hashlib
import logging
from typing import Optional

logger = logging.getLogger("alfie-prompt-cache")

PROMPT_CACHE_TTL = 300  # 5 minutes


async def get_cached_prompt(redis_client, raw_prompt: str) -> Optional[str]:
    """
    Check if a compressed version of this exact prompt already exists.
    Uses first 16 chars of SHA-256 as the cache key.
    """
    if not redis_client or not raw_prompt:
        return None

    try:
        prompt_hash = hashlib.sha256(raw_prompt.encode()).hexdigest()[:16]
        key = f"prompt_compressed:{prompt_hash}"
        cached = await redis_client.get(key)
        if cached:
            logger.info(
                "[PROMPT CACHE HIT] Skipping LLMLingua compression (saved ~500ms)"
            )
            return cached
    except Exception as e:
        logger.debug(f"Prompt cache lookup failed: {e}")
    return None


async def store_cached_prompt(redis_client, raw_prompt: str, compressed_prompt: str):
    """
    Cache a compressed prompt for future calls with the same content.
    """
    if not redis_client or not raw_prompt or not compressed_prompt:
        return

    try:
        prompt_hash = hashlib.sha256(raw_prompt.encode()).hexdigest()[:16]
        key = f"prompt_compressed:{prompt_hash}"
        await redis_client.setex(key, PROMPT_CACHE_TTL, compressed_prompt)
        logger.debug(f"[PROMPT CACHE STORED] Hash: {prompt_hash}")
    except Exception as e:
        logger.debug(f"Prompt cache store failed: {e}")
