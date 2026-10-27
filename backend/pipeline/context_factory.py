import asyncio
import json
import logging
from typing import Any, Dict, Optional, Tuple
import uuid

import httpx
try:
    from arq import create_pool
    from arq.connections import RedisSettings
except ImportError:
    create_pool = None
    RedisSettings = None

from cache import (
    build_memory_prompt,
    check_duplicate_call,
    get_cached_prompt,
    get_caller_context,
    get_transfer_context,
    init_bloom_filter,
    init_semantic_cache,
    init_timeseries,
    is_feature_enabled,
    prewarm_niche_faqs,
    record_call_start,
    store_cached_prompt,
)
from config import settings
from crm_client import crm
from guardrails import get_slot_tracker_for_niche
from prompts.base import BASE_SYSTEM_PROMPT
from prompts.registry import PROMPT_REGISTRY
from telemetry import (
    _pool,
    get_redis,
    init_redis_pool,
    init_telemetry_pool,
)

logger = logging.getLogger("alfie-pipeline-context")


def safe_uuid(val: Any) -> Optional[uuid.UUID]:
    """Safely converts a string or UUID to a valid UUID object or returns None."""
    if not val:
        return None
    if isinstance(val, uuid.UUID):
        return val
    if isinstance(val, str) and len(val) == 36:
        try:
            return uuid.UUID(val)
        except (ValueError, TypeError, AttributeError):
            return None
    return None


def get_default_config(niche: str = "general", tenant_id: str = "default") -> Dict[str, Any]:
    """Returns baseline system configuration for any voice agent."""
    return {
        "engine_mode": "cascaded",  # "cascaded" or "native_s2s"
        "niche": niche or "general",
        "agent_name": "A.L.F.I.E Voice Agent",
        "system_prompt": "",
        "greeting_message": "Hello, thank you for calling. Please note this call may be recorded for quality assurance. How can I help you today?",
        "human_agent_sip_uri": None,
        "enabled_tools": ["core_tools"],
        "allow_interruptions": True,
        "backchanneling_enabled": True,
        "conversational_fillers_enabled": True,
        "openai_realtime_config": {
            "model": "gpt-4o-realtime-preview",
            "voice": "alloy",
            "temperature": 0.7,
        },
        "voice_config": {
            "provider": "fish_audio",
            "model": "s2.1-pro",
            "voice_id": "224a2257dd4943209a683d27a5e41439",
            "latency_mode": "balanced",
        },
        "stt_config": {
            "provider": "deepgram",
            "model": "nova-2",
            "language": "multi",
            "profanity_filter": False,
            "smart_format": True,
        },
        "llm_config": {
            "provider": "openrouter",
            "model": "meta-llama/llama-3.1-8b-instruct",
            "temperature": 0.7,
            "max_tokens": 1000,
        },
        "vad_config": {
            "min_silence_duration": 0.55,
            "activation_threshold": 0.3,
            "endpointing_preset": "natural",
            "anti_interruption_enabled": True,
            "extended_silence_duration": 1.25,
            "quick_silence_duration": 0.38,
        },
    }


async def prewarm_pipeline() -> Any:
    """
    Initializes telemetry pool, Redis pool, ARQ queue pool, semantic cache, and bloom filters.
    Runs once at worker startup.
    """
    logger.info("Prewarming pipeline: initializing telemetry, redis, arq, and semantic cache...")
    await init_telemetry_pool()
    await init_redis_pool()
    arq_pool = await create_pool(RedisSettings.from_dsn(settings.redis_dsn))

    asyncio.create_task(init_semantic_cache(settings.redis_dsn))
    asyncio.create_task(prewarm_niche_faqs("demo-tenant", "demo"))
    redis_client = await get_redis()
    if redis_client:
        asyncio.create_task(init_bloom_filter(redis_client))
    return arq_pool


async def resolve_call_config(
    tenant_id: str,
    agent_id: Optional[str],
    metadata: Dict[str, Any],
    redis_client: Any,
) -> Dict[str, Any]:
    """
    Resolves tenant and agent configuration using a tiered cache strategy:
    1. Redis Fast Cache (sub-1ms)
    2. PostgreSQL Authoritative Database
    3. Twenty CRM Integration (optional fallback)
    4. Default Baseline Config
    """
    config_data = None
    cache_key = f"tenant_config:{agent_id or tenant_id}"

    # 1. High-speed Redis Cache lookup
    if redis_client:
        try:
            cached_conf = await redis_client.get(cache_key)
            if cached_conf:
                config_data = json.loads(cached_conf)
                logger.info(f"Loaded config for {tenant_id} from Redis Cache (TTFT optimized).")
                return config_data
        except Exception as e:
            logger.warning(f"Redis config cache read error: {e}")

    # 2. PostgreSQL Authoritative Store
    if _pool:
        try:
            async with _pool.acquire() as conn:
                inferred_niche = metadata.get("niche") or "general"
                base_conf = get_default_config(niche=inferred_niche, tenant_id=tenant_id)
                db_found = False

                agent_uuid = safe_uuid(agent_id)
                if agent_uuid:
                    try:
                        agent_row = await conn.fetchrow(
                            "SELECT name, niche, system_prompt_override, llm_model, "
                            "llm_temperature, tts_voice_id, stt_language, custom_tools, "
                            "endpointing_preset, anti_interruption_enabled, "
                            "conversational_fillers_enabled, filler_pacing_mode, filler_cooldown_seconds "
                            "FROM alfie_tenant_agents WHERE agent_id = $1",
                            agent_uuid,
                        )
                        if agent_row:
                            db_found = True
                            base_conf["agent_name"] = agent_row["name"] or base_conf["agent_name"]
                            base_conf["niche"] = agent_row["niche"] or base_conf["niche"]
                            base_conf["system_prompt"] = agent_row["system_prompt_override"] or ""
                            if agent_row["llm_model"]:
                                base_conf["llm_config"]["model"] = agent_row["llm_model"]
                            if agent_row["llm_temperature"] is not None:
                                base_conf["llm_config"]["temperature"] = float(agent_row["llm_temperature"])
                            if agent_row["tts_voice_id"]:
                                base_conf["voice_config"]["voice_id"] = agent_row["tts_voice_id"]
                            if agent_row["stt_language"]:
                                base_conf["stt_config"]["language"] = agent_row["stt_language"]
                            if agent_row["custom_tools"]:
                                base_conf["custom_tools"] = (
                                    json.loads(agent_row["custom_tools"])
                                    if isinstance(agent_row["custom_tools"], str)
                                    else agent_row["custom_tools"]
                                )
                            if agent_row.get("endpointing_preset"):
                                base_conf["vad_config"]["endpointing_preset"] = agent_row["endpointing_preset"]
                            if agent_row.get("anti_interruption_enabled") is not None:
                                base_conf["vad_config"]["anti_interruption_enabled"] = bool(agent_row["anti_interruption_enabled"])
                            if agent_row.get("conversational_fillers_enabled") is not None:
                                base_conf["conversational_fillers_enabled"] = bool(agent_row["conversational_fillers_enabled"])
                            if agent_row.get("filler_pacing_mode"):
                                base_conf["filler_pacing_mode"] = agent_row["filler_pacing_mode"]
                            if agent_row.get("filler_cooldown_seconds") is not None:
                                base_conf["filler_cooldown_seconds"] = float(agent_row["filler_cooldown_seconds"])
                    except Exception as err:
                        logger.error(f"Error querying agent {agent_id}: {err}")

                tenant_uuid = safe_uuid(tenant_id)
                if tenant_uuid:
                    try:
                        tenant_row = await conn.fetchrow(
                            "SELECT name, niche, tenant_config FROM alfie_tenants WHERE tenant_id = $1",
                            tenant_uuid,
                        )
                        if tenant_row:
                            db_found = True
                            t_niche = tenant_row["niche"] or base_conf["niche"]
                            base_conf["niche"] = t_niche
                            if tenant_row["tenant_config"]:
                                t_conf = (
                                    json.loads(tenant_row["tenant_config"])
                                    if isinstance(tenant_row["tenant_config"], str)
                                    else tenant_row["tenant_config"]
                                )
                                if "system_prompt_override" in t_conf:
                                    base_conf["system_prompt"] = t_conf["system_prompt_override"]
                                elif "system_prompt" in t_conf:
                                    base_conf["system_prompt"] = t_conf["system_prompt"]
                                if "llm_config" in t_conf:
                                    base_conf["llm_config"].update(t_conf["llm_config"])
                                if "voice_config" in t_conf:
                                    base_conf["voice_config"].update(t_conf["voice_config"])
                                if "stt_config" in t_conf:
                                    base_conf["stt_config"].update(t_conf["stt_config"])
                                if "custom_tools" in t_conf:
                                    base_conf["custom_tools"] = t_conf["custom_tools"]
                                if "vad_config" in t_conf and isinstance(t_conf["vad_config"], dict):
                                    base_conf["vad_config"].update(t_conf["vad_config"])
                    except Exception as err:
                        logger.warning(f"Error querying tenant {tenant_id}: {err}")

                if db_found:
                    config_data = base_conf
        except Exception as e:
            logger.warning(f"PostgreSQL config read error: {e}")

    # 3. Twenty CRM Fallback
    if not config_data:
        try:
            config_data = await crm.get_tenant_config(tenant_id)
        except Exception as e:
            logger.debug(f"Twenty CRM lookup skipped/unavailable: {e}")

    # 4. Default Baseline Config
    if not config_data:
        inferred_niche = metadata.get("niche") or "demo"
        config_data = get_default_config(niche=inferred_niche, tenant_id=tenant_id)

    # Cache resolved config in Redis (300s TTL)
    if redis_client and config_data:
        try:
            await redis_client.setex(cache_key, 300, json.dumps(config_data))
        except Exception as e:
            logger.warning(f"Failed to cache resolved config in Redis: {e}")

    return config_data


async def assemble_system_prompt(
    tenant_id: str,
    agent_id: Optional[str],
    config_data: Dict[str, Any],
    metadata: Dict[str, Any],
    room_name: str,
    redis_client: Any,
) -> Tuple[str, Any, bool]:
    """
    Assembles system prompt, slot tracker, caller memory, warm transfers, and WebChat context.
    Eliminates synchronous HTTP compression lag during room connect by using cached prompts with async compression.
    """
    niche = config_data.get("niche")
    norm_niche = (niche or "").strip().lower().replace("-", "_")
    niche_prompt = PROMPT_REGISTRY.get(norm_niche, "")
    user_system_prompt = config_data.get("system_prompt") or ""
    raw_system_prompt = f"{BASE_SYSTEM_PROMPT}\n\n{niche_prompt}\n\n{user_system_prompt}".strip()

    caller_phone = metadata.get("caller_phone") or metadata.get("phone") or metadata.get("caller_number")
    slot_tracker = get_slot_tracker_for_niche(niche=niche or "general", caller_phone=caller_phone)
    initial_slot_guidance = slot_tracker.generate_guidance_prompt()
    if initial_slot_guidance:
        raw_system_prompt += f"\n\n{initial_slot_guidance}"

    chat_session_id = metadata.get("session_id")
    cache_enabled = True

    if redis_client:
        try:
            asyncio.create_task(init_timeseries(redis_client, tenant_id))
            asyncio.create_task(record_call_start(redis_client, tenant_id))

            if caller_phone:
                is_allowed, reason = await check_duplicate_call(redis_client, caller_phone, tenant_id)
                if not is_allowed:
                    logger.warning(f"[{tenant_id}] Rejected duplicate call from {caller_phone}: {reason}")
                    return "", None, False

            cache_enabled = await is_feature_enabled(
                redis_client, tenant_id, "semantic_cache_enabled", default=True
            )

            if caller_phone:
                caller_data = await get_caller_context(redis_client, tenant_id, caller_phone)
                if caller_data:
                    memory_prompt = build_memory_prompt(caller_data)
                    raw_system_prompt += f"\n\n{memory_prompt}"

            transfer_data = await get_transfer_context(redis_client, room_name)
            if transfer_data:
                raw_system_prompt += (
                    f"\n\n=== WARM CALL TRANSFER CONTEXT ===\n"
                    f"The caller was just transferred to you. Prior summary:\n"
                    f"{transfer_data.get('transcript_summary', '')}\n"
                    f"Acknowledge the handoff smoothly and address their need immediately."
                )
        except Exception as e:
            logger.warning(f"Error reading Redis context in prompt assembly: {e}")

    # Append Department Roster & Preceding WebChat History from DB
    if _pool:
        try:
            async with _pool.acquire() as conn:
                tenant_uuid = safe_uuid(tenant_id)
                agent_uuid = safe_uuid(agent_id)
                if tenant_uuid:
                    if agent_uuid:
                        other_agents = await conn.fetch(
                            "SELECT name, niche FROM alfie_tenant_agents WHERE tenant_id = $1 AND agent_id != $2",
                            tenant_uuid,
                            agent_uuid,
                        )
                    else:
                        other_agents = await conn.fetch(
                            "SELECT name, niche FROM alfie_tenant_agents WHERE tenant_id = $1",
                            tenant_uuid,
                        )
                    if other_agents:
                        agents_list = [f"- {a['name']} ({a['niche']})" for a in other_agents]
                        raw_system_prompt += (
                            f"\n\n=== INTERNAL DEPARTMENTS ===\n"
                            f"You can transfer the caller to the following departments/agents if they ask:\n"
                            f"{chr(10).join(agents_list)}\n"
                            f"Use your transfer_to_department tool to transfer them."
                        )

                # WebChat History
                if caller_phone or chat_session_id:
                    row = None
                    if chat_session_id:
                        row = await conn.fetchrow(
                            "SELECT history_json FROM alfie_chat_sessions WHERE session_id = $1",
                            chat_session_id,
                        )
                    elif caller_phone:
                        row = await conn.fetchrow(
                            "SELECT history_json FROM alfie_chat_sessions "
                            "WHERE user_phone = $1 AND tenant_id = $2 AND status = 'escalated_to_call' "
                            "ORDER BY updated_at DESC LIMIT 1",
                            caller_phone,
                            tenant_id,
                        )
                    if row and row["history_json"]:
                        history = json.loads(row["history_json"])
                        if history:
                            chat_summary = "\n".join(
                                [f"{h.get('role', 'user').capitalize()}: {h.get('content', '')}" for h in history[-8:]]
                            )
                            raw_system_prompt += (
                                f"\n\n=== RECENT WEBCHAT TRANSCRIPT (PRECEEDING TEXT CONVERSATION) ===\n"
                                f"The caller recently chatted with you over text before making this call:\n"
                                f"{chat_summary}\n\n"
                                f"IMPORTANT VOICE GREETING INSTRUCTION:\n"
                                f"Greet the caller seamlessly by acknowledging your prior text conversation above!"
                            )
        except Exception as e:
            logger.warning(f"Error appending DB context in prompt assembly: {e}")

    # Zero-Latency Prompt Compression Optimization:
    # 1. Check Redis cache for pre-compressed prompt
    # 2. If missed, immediately use raw_system_prompt (0ms delay!) and trigger async background compression
    final_prompt = raw_system_prompt
    cached_compressed = await get_cached_prompt(redis_client, raw_system_prompt)
    if cached_compressed:
        final_prompt = cached_compressed
    else:
        async def _async_compress_and_cache():
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    resp = await client.post(
                        "http://llmlingua:5000/compress",
                        json={"context": raw_system_prompt, "target_token": 600},
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        comp = data.get("compressed_prompt", raw_system_prompt)
                        if redis_client:
                            await store_cached_prompt(redis_client, raw_system_prompt, comp)
            except Exception:
                pass

        asyncio.create_task(_async_compress_and_cache())

    return final_prompt, slot_tracker, cache_enabled
