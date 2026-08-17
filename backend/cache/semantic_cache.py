import asyncio
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger("alfie-semantic-cache")

_cache_instance = None
_vectorizer_instance = None
_init_lock = asyncio.Lock()


async def init_semantic_cache(redis_url: str):
    """
    Initializes the RedisVL Semantic Cache with all-MiniLM-L6-v2 vector embeddings.
    Runs asynchronously and non-blocking.
    """
    global _cache_instance, _vectorizer_instance
    async with _init_lock:
        if _cache_instance is not None:
            return

        try:
            from redisvl.extensions.cache.llm import SemanticCache
            from redisvl.utils.vectorize import HFTextVectorizer

            def _setup():
                vectorizer = HFTextVectorizer(
                    model="sentence-transformers/all-MiniLM-L6-v2"
                )
                cache = SemanticCache(
                    name="alfie_llm_cache",
                    redis_url=redis_url,
                    distance_threshold=0.18,  # Optimized balance of precision & hit rate
                    vectorizer=vectorizer,
                    ttl=7200,  # 2-hour TTL
                )
                return vectorizer, cache

            # Offload model loading to threadpool to avoid blocking event loop
            _vectorizer_instance, _cache_instance = await asyncio.to_thread(_setup)
            logger.info("RedisVL Semantic LLM Cache initialized successfully.")
        except ImportError as ie:
            logger.warning(
                f"redisvl or sentence-transformers not installed, semantic cache running in degraded mode: {ie}"
            )
        except Exception as e:
            logger.warning(f"Failed to initialize RedisVL Semantic Cache: {e}")


async def check_semantic_cache(
    prompt: str, tenant_id: str = "default", niche: str = "general"
) -> Optional[str]:
    """
    Checks if a semantically similar prompt has been answered before.
    Returns the cached response text, or None if a cache miss.
    """
    global _cache_instance
    if not _cache_instance or not prompt:
        return None

    try:
        clean_prompt = prompt.strip()
        if len(clean_prompt) < 4:
            return None

        def _do_check():
            # Query Redis vector index for matching prompt embeddings
            results = _cache_instance.check(
                prompt=clean_prompt,
                filter_expression=f"@tenant_id:{{{tenant_id}}} @niche:{{{niche}}}",
            )
            if results and len(results) > 0:
                return results[0].get("response")
            return None

        cached_response = await asyncio.to_thread(_do_check)
        if cached_response:
            logger.info(
                f"[SEMANTIC CACHE HIT] Tenant: {tenant_id} | Prompt: '{clean_prompt[:40]}...' (Saved 100% LLM tokens)"
            )
            return cached_response
    except Exception as e:
        logger.debug(f"Semantic cache check skipped: {e}")

    return None


async def store_semantic_cache(
    prompt: str, response: str, tenant_id: str = "default", niche: str = "general"
):
    """
    Stores prompt and LLM response embedding in RedisVL Semantic Cache.
    """
    global _cache_instance
    if not _cache_instance or not prompt or not response:
        return

    try:
        clean_prompt = prompt.strip()
        clean_response = response.strip()

        # Do not cache extremely short or generic acknowledgements
        if len(clean_prompt) < 6 or len(clean_response) < 6:
            return

        def _do_store():
            _cache_instance.store(
                prompt=clean_prompt,
                response=clean_response,
                metadata={
                    "tenant_id": tenant_id,
                    "niche": niche,
                },
            )

        await asyncio.to_thread(_do_store)
        logger.debug(
            f"[SEMANTIC CACHE STORED] Tenant: {tenant_id} | '{clean_prompt[:30]}...'"
        )
    except Exception as e:
        logger.debug(f"Semantic cache store failed: {e}")
