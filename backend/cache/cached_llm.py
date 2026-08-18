import asyncio
import logging
from typing import Optional

try:
    from livekit.agents import llm
    from livekit.plugins import openai

    _HAS_LIVEKIT = True
except ImportError:
    llm = None
    openai = None
    _HAS_LIVEKIT = False

from cache.semantic_cache import check_semantic_cache, store_semantic_cache

logger = logging.getLogger("alfie-cached-llm")

if _HAS_LIVEKIT and llm:

    class CachedLLMStream(llm.LLMStream):
        def __init__(
            self,
            parent_llm: "CachedOpenAILLM",
            chat_ctx: llm.ChatContext,
            fnc_ctx: Optional[object] = None,
            **kwargs,
        ):
            super().__init__(parent_llm, chat_ctx=chat_ctx, fnc_ctx=fnc_ctx)
            self.parent_llm = parent_llm
            self.kwargs = kwargs
            self._underlying_stream: Optional[llm.LLMStream] = None

        async def _run(self) -> None:
            last_user_msg = ""
            for msg in reversed(self.chat_ctx.messages):
                if msg.role == "user" and msg.text:
                    last_user_msg = msg.text.strip()
                    break

            # Check semantic cache if enabled
            if self.parent_llm.cache_enabled and last_user_msg:
                try:
                    cached_answer = await check_semantic_cache(
                        last_user_msg,
                        tenant_id=self.parent_llm.tenant_id,
                        niche=self.parent_llm.niche,
                    )
                    if cached_answer:
                        logger.info(
                            f"[SEMANTIC CACHE HIT -> STREAMING CACHED TO TTS] Prompt: '{last_user_msg[:35]}...'"
                        )
                        # Record cache hit metric
                        from telemetry import get_redis
                        from cache.metrics import record_cache_hit

                        redis_client = await get_redis()
                        if redis_client:
                            asyncio.create_task(
                                record_cache_hit(
                                    redis_client, self.parent_llm.tenant_id
                                )
                            )

                        chunk = llm.ChatChunk(
                            choices=[
                                llm.Choice(
                                    delta=llm.ChoiceDelta(
                                        role="assistant", content=cached_answer
                                    ),
                                    index=0,
                                )
                            ]
                        )
                        self._event_ch.send_nowait(chunk)
                        return
                except Exception as e:
                    logger.debug(f"Semantic cache lookup error: {e}")

            # Cache Miss: Delegate to real OpenAI / LiteLLM stream
            try:
                from telemetry import get_redis
                from cache.metrics import record_cache_miss

                redis_client = await get_redis()
                if redis_client:
                    asyncio.create_task(
                        record_cache_miss(redis_client, self.parent_llm.tenant_id)
                    )

                self._underlying_stream = super(CachedOpenAILLM, self.parent_llm).chat(
                    chat_ctx=self.chat_ctx, fnc_ctx=self.fnc_ctx, **self.kwargs
                )

                accumulated_response = []
                async for chunk in self._underlying_stream:
                    self._event_ch.send_nowait(chunk)
                    for choice in chunk.choices:
                        if choice.delta and choice.delta.content:
                            accumulated_response.append(choice.delta.content)

                full_text = "".join(accumulated_response).strip()
                if full_text and last_user_msg and self.parent_llm.cache_enabled:
                    asyncio.create_task(
                        store_semantic_cache(
                            last_user_msg,
                            full_text,
                            tenant_id=self.parent_llm.tenant_id,
                            niche=self.parent_llm.niche,
                        )
                    )
            except Exception as e:
                logger.error(f"Error executing underlying LLM stream: {e}")
                raise

    class CachedOpenAILLM(openai.LLM):
        """
        Subclass of OpenAI LLM that transparently intercepts queries with RedisVL Semantic Cache.
        Reduces latency to <50ms and saves 100% of LLM token costs for cached answers.
        """

        def __init__(
            self,
            tenant_id: str = "default",
            niche: str = "general",
            cache_enabled: bool = True,
            *args,
            **kwargs,
        ):
            super().__init__(*args, **kwargs)
            self.tenant_id = tenant_id
            self.niche = niche
            self.cache_enabled = cache_enabled

        def chat(
            self,
            *,
            chat_ctx: llm.ChatContext,
            fnc_ctx: Optional[object] = None,
            temperature: Optional[float] = None,
            n: Optional[int] = None,
            parallel_tool_calls: Optional[bool] = None,
        ) -> llm.LLMStream:
            return CachedLLMStream(
                parent_llm=self,
                chat_ctx=chat_ctx,
                fnc_ctx=fnc_ctx,
                temperature=temperature,
                n=n,
                parallel_tool_calls=parallel_tool_calls,
            )

else:

    class CachedLLMStream:
        pass

    class CachedOpenAILLM:
        pass
