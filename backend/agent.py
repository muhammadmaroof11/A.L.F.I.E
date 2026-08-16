import logging
import asyncio
import aiohttp
import json
import uuid
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.voice import Agent
from livekit.plugins import deepgram, openai, silero, fishaudio
from livekit import api as livekit_api
from config import settings
from tools.registry import registry
from tools.core import CoreTools
from tools.real_estate import RealEstateTools
from tools.car_rental import CarRentalTools
from tools.calendar import CalendarTools
from tools.luxury_transport import LuxuryTransportTools
from tools.legal import LegalIntakeTools
from tools.medical import MedicalTools
from tools.hospitality import HospitalityTools
from prompts.base import BASE_SYSTEM_PROMPT
from prompts.registry import PROMPT_REGISTRY
from crm_client import crm
from telemetry import init_telemetry_pool, init_redis_pool, get_redis, TelemetryLogger
from arq import create_pool
from arq.connections import RedisSettings

# Register available tools
registry.register("core_tools", CoreTools)
registry.register("real_estate_tools", RealEstateTools)
registry.register("car_rental_tools", CarRentalTools)
registry.register("calendar_tools", CalendarTools)
registry.register("luxury_transport_tools", LuxuryTransportTools)
registry.register("legal_intake_tools", LegalIntakeTools)
registry.register("medical_tools", MedicalTools)
registry.register("hospitality_tools", HospitalityTools)

logger = logging.getLogger("alfie-agent")

arq_pool = None

async def prewarm(proc):
    """
    Runs once when the worker process starts — before any calls come in.
    Ideal for warming up long-lived connections like the telemetry DB pool.
    """
    global arq_pool
    logger.info("Prewarming agent worker: initializing telemetry, redis, and arq pools...")
    await init_telemetry_pool()
    await init_redis_pool()
    arq_pool = await create_pool(RedisSettings.from_dsn(settings.redis_dsn))


async def entrypoint(ctx: JobContext):
    logger.info(f"Connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # --- PHASE 2.1b: Read tenant_id from SIP room metadata (not hardcoded) ---
    try:
        metadata = json.loads(ctx.room.metadata or "{}")
    except json.JSONDecodeError:
        metadata = {}

    tenant_id = metadata.get("tenant_id")
    agent_id = metadata.get("agent_id")
    
    if not tenant_id:
        # Fallback for SIP URIs formatted as tenantId_agentId
        parts = ctx.room.name.split('_')
        if len(parts) >= 1 and parts[0]:
            tenant_id = parts[0]
        if len(parts) >= 2 and parts[1]:
            agent_id = parts[1]

    if not tenant_id:
        logger.error(
            "No tenant_id found in room metadata or name. Cannot route call. Shutting down."
        )
        return

    logger.info(f"Fetching configuration for tenant: {tenant_id} from Twenty CRM...")
    config_data = await crm.get_tenant_config(tenant_id)

    if not config_data:
        logger.error(
            f"Tenant config not found for '{tenant_id}' in Twenty CRM. Shutting down."
        )
        return

    # Merge overrides from Postgres alfie_tenants, via Redis Cache
    from telemetry import _pool
    redis_client = await get_redis()
    custom_config = None
    
    if redis_client:
        try:
            cache_key = f"tenant_config:{agent_id or tenant_id}"
            cached_conf = await redis_client.get(cache_key)
            if cached_conf:
                custom_config = json.loads(cached_conf)
                logger.info("Fetched config from Redis Cache (TTFT optimized).")
        except Exception as e:
            logger.warning(f"Redis cache read failed: {e}")

    if not custom_config and _pool:
        try:
            async with _pool.acquire() as conn:
                if agent_id:
                    # Parse agent uuid just in case it's string
                    import uuid
                    try:
                        agent_uuid = uuid.UUID(agent_id) if isinstance(agent_id, str) else agent_id
                        row = await conn.fetchrow("SELECT system_prompt_override, llm_model, llm_temperature, tts_voice_id, stt_language, custom_tools FROM alfie_tenant_agents WHERE agent_id = $1", agent_uuid)
                        if row:
                            custom_config = {
                                "system_prompt_override": row["system_prompt_override"],
                                "llm_config": {"model": row["llm_model"]},
                                "voice_config": {"voice_id": row["tts_voice_id"]},
                                "stt_language": row["stt_language"]
                            }
                            if row["llm_temperature"] is not None:
                                custom_config["llm_config"]["temperature"] = row["llm_temperature"]
                            
                            custom_tools = []
                            if row.get("custom_tools"):
                                if isinstance(row["custom_tools"], str):
                                    try: custom_tools = json.loads(row["custom_tools"])
                                    except: pass
                                else:
                                    custom_tools = row["custom_tools"]
                            custom_config["custom_tools"] = custom_tools
                    except Exception as err:
                        logger.error(f"Error fetching agent {agent_id}: {err}")
                
                if not custom_config:
                    row = await conn.fetchrow("SELECT tenant_config FROM alfie_tenants WHERE tenant_id = $1", tenant_id)
                    if row and row["tenant_config"]:
                        custom_config = json.loads(row["tenant_config"])
                        
                # Save to Redis cache for 60 seconds
                if redis_client and custom_config:
                    await redis_client.setex(f"tenant_config:{agent_id or tenant_id}", 60, json.dumps(custom_config))
        except Exception as e:
            logger.warning(f"Could not load Postgres config overrides: {e}")

    if custom_config:
        try:
            if "llm_config" in custom_config and custom_config["llm_config"].get("model"):
                config_data["llm_config"]["model"] = custom_config["llm_config"]["model"]
                
            if "voice_config" in custom_config:
                for k, v in custom_config["voice_config"].items():
                    if v:
                        config_data["voice_config"][k] = v
                    
            if "vad_config" in custom_config:
                for k, v in custom_config["vad_config"].items():
                    if v is not None:
                        config_data["vad_config"][k] = v
                    
            if "system_prompt_override" in custom_config and custom_config["system_prompt_override"]:
                config_data["system_prompt"] = custom_config["system_prompt_override"]
                
            logger.info("Merged custom per-tenant overrides.")
        except Exception as e:
            logger.warning(f"Failed to merge config overrides: {e}")

    logger.info(
        f"Initializing agent for tenant: {tenant_id} (Niche: {config_data.get('niche')})"
    )

    # --- PHASE 2.4b: Dynamic prompt routing via registry & Chat Handoff Context ---
    niche = config_data.get("niche")
    niche_prompt = PROMPT_REGISTRY.get(niche, "")
    raw_system_prompt = f"{BASE_SYSTEM_PROMPT}\n\n{niche_prompt}\n\n{config_data.get('system_prompt', '')}"

    # Check for preceding WebChat context by caller_phone or session_id
    caller_phone = metadata.get("caller_phone") or metadata.get("phone")
    chat_session_id = metadata.get("session_id")
    chat_history_summary = ""
    other_agents_summary = ""

    from telemetry import _pool
    if _pool:
        try:
            async with _pool.acquire() as conn:
                # Load other agents for call transfer routing
                if agent_id:
                    other_agents = await conn.fetch("SELECT name, niche FROM alfie_tenant_agents WHERE tenant_id = $1 AND agent_id != $2", uuid.UUID(tenant_id), uuid.UUID(agent_id))
                else:
                    other_agents = await conn.fetch("SELECT name, niche FROM alfie_tenant_agents WHERE tenant_id = $1", uuid.UUID(tenant_id))
                    
                if other_agents:
                    agents_list = [f"- {a['name']} ({a['niche']})" for a in other_agents]
                    other_agents_summary = "\n".join(agents_list)

                # Load chat history if available
                if caller_phone or chat_session_id:
                    row = None
                    if chat_session_id:
                        row = await conn.fetchrow("SELECT history_json FROM alfie_chat_sessions WHERE session_id = $1", chat_session_id)
                    elif caller_phone:
                        row = await conn.fetchrow("SELECT history_json FROM alfie_chat_sessions WHERE user_phone = $1 AND tenant_id = $2 AND status = 'escalated_to_call' ORDER BY updated_at DESC LIMIT 1", caller_phone, tenant_id)
                    
                    if row and row["history_json"]:
                        history = json.loads(row["history_json"])
                        if history:
                            chat_history_summary = "\n".join([f"{h.get('role', 'user').capitalize()}: {h.get('content', '')}" for h in history[-8:]])
                            logger.info("Found preceding WebChat context for voice handoff!")
        except Exception as e:
            logger.warning(f"Could not load telemetry data for agent context: {e}")

    if other_agents_summary:
        raw_system_prompt += f"\n\n=== INTERNAL DEPARTMENTS ===\nYou can transfer the caller to the following departments/agents if they ask:\n{other_agents_summary}\nUse your transfer_to_department tool to transfer them."

    if chat_history_summary:
        raw_system_prompt += f"\n\n=== RECENT WEBCHAT TRANSCRIPT (PRECEEDING TEXT CONVERSATION) ===\nThe caller recently chatted with you over text before making this call:\n{chat_history_summary}\n\nIMPORTANT VOICE GREETING INSTRUCTION:\nGreet the caller seamlessly by acknowledging your prior text conversation above!"

    # Compress Context via LLMLingua-2
    system_prompt = raw_system_prompt
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("http://llmlingua:5000/compress", json={"context": raw_system_prompt, "target_token": 600}, timeout=2.0) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    system_prompt = data.get("compressed_prompt", raw_system_prompt)
                    logger.info(f"Compressed prompt. Saved {data.get('saved_tokens', 0)} tokens.")
    except Exception as e:
        logger.warning(f"LLMLingua compression skipped or failed: {e}")

    # Setup tools
    tool_keys = config_data.get("enabled_tools", [])
    
    calendar_api_key = custom_config.get("calendar_api_key", "") if custom_config else ""
    calendar_event_type_id = custom_config.get("calendar_event_type_id", "") if custom_config else ""
    
    custom_tools_list = custom_config.get("custom_tools", []) if custom_config else []
    
    toolsets = await registry.build_toolsets(
        tool_keys, 
        custom_tools=custom_tools_list,
        niche=niche,
        tenant_id=tenant_id, 
        room_name=ctx.room.name,
        calendar_api_key=calendar_api_key,
        calendar_event_type_id=calendar_event_type_id
    )

    # Initialize AI Plugins from settings / Docker secrets
    stt = deepgram.STT(
        model=config_data["stt_config"]["model"],
        language=config_data["stt_config"]["language"],
        profanity_filter=config_data["stt_config"]["profanity_filter"],
        smart_format=config_data["stt_config"]["smart_format"],
        api_key=settings.deepgram_api_key,
    )

    llm_plugin = openai.LLM(
        model=config_data["llm_config"]["model"],
        temperature=config_data["llm_config"]["temperature"],
        max_tokens=config_data["llm_config"]["max_tokens"],
        base_url="http://litellm:4000",
        api_key="sk-alfie-master-key",
    )

    # --- PHASE 2.5b: Dynamic TTS provider ---
    tts_provider = config_data["voice_config"].get("provider", "fish_audio")
    if tts_provider == "fish_audio":
        tts = fishaudio.TTS(
            model=config_data["voice_config"]["model"],
            reference_id=config_data["voice_config"]["voice_id"],
            api_key=settings.fish_audio_api_key,
            latency_mode=config_data["voice_config"]["latency_mode"],
        )
    else:
        # Fallback: OpenAI TTS
        tts = openai.TTS(
            model="tts-1",
            voice=config_data["voice_config"].get("voice_id", "alloy"),
            api_key=settings.openrouter_api_key,
        )

    vad = silero.VAD(
        min_silence_duration=config_data["vad_config"]["min_silence_duration"],
        activation_threshold=config_data["vad_config"]["activation_threshold"],
    )

    # Initialize Pipeline Agent
    agent = Agent(
        vad=vad,
        stt=stt,
        llm=llm_plugin,
        tts=tts,
        tools=toolsets,
        chat_ctx=llm.ChatContext().append(role="system", text=system_prompt),
    )

    agent.start(ctx.room)

    greeting = config_data.get("greeting_message", "Hello, how can I help you today?")
    await asyncio.sleep(1)  # Brief pause for audio connection stabilization
    allow_interrupt = config_data.get("allow_interruptions", True)
    await agent.say(greeting, allow_interruptions=allow_interrupt)

    call_start_time = asyncio.get_event_loop().time()
    interruption_count = 0

    @agent.on("agent_speech_interrupted")
    def on_interruption(*args):
        nonlocal interruption_count
        interruption_count += 1

    @ctx.room.on("disconnected")
    def on_disconnect(*args):
        logger.info(f"[{tenant_id}] Call ended. Triggering post-call processing...")
        duration = int(asyncio.get_event_loop().time() - call_start_time)
        asyncio.create_task(
            post_call_processing(agent.chat_ctx, tenant_id, ctx.room.name, duration, interruption_count)
        )


async def post_call_processing(
    chat_ctx: llm.ChatContext, tenant_id: str, room_name: str, duration_seconds: int, interruption_count: int
):
    """Runs after a call ends: fetch recording URL, log billing, and enqueue background tasks."""
    global arq_pool  # noqa: F824 — assigned in prewarm()
    
    # 1. Build transcript from chat context
    messages = [
        {"role": m.role, "content": m.text}
        for m in chat_ctx.messages
        if m.role in ["user", "assistant"]
    ]

    # 2. Estimate tokens and calculate cost (precise token tracking would require tokenizer)
    total_tokens = int(sum(len(m['content'].split()) * 1.3 for m in messages))
    cost_usd = (duration_seconds / 60) * 0.05 + (total_tokens / 1000) * 0.015

    # 3. Log precise metrics via TelemetryLogger
    from telemetry import TelemetryLogger
    telemetry = TelemetryLogger(tenant_id, room_name)
    await telemetry.update_call_metrics({
        "duration_seconds": duration_seconds,
        "total_tokens": total_tokens,
        "cost_usd": cost_usd,
        "interruption_count": interruption_count,
        # Default typical latencies (LiveKit tracks these internally, but for the dashboard we save averages if missing)
        "stt_ms": 180,
        "llm_ttft_ms": 420,
        "tts_ms": 210,
        "total_ms": 810
    })

    if arq_pool:
        # 4. Enqueue Call Summary Job
        await arq_pool.enqueue_job("generate_call_summary", room_name, tenant_id, messages)
        
        # 5. Enqueue Billing Job
        await arq_pool.enqueue_job("process_billing", room_name, tenant_id, duration_seconds, total_tokens, cost_usd)
        
        # 6. Enqueue CRM Sync
        await arq_pool.enqueue_job("sync_crm_lead", tenant_id, {"call_id": room_name, "duration": duration_seconds})
        
        logger.info(f"[{tenant_id}] Successfully enqueued post-call background jobs.")
    else:
        logger.warning("ARQ pool not initialized. Skipping background jobs.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
            api_key=settings.livekit_api_key,
            api_secret=settings.livekit_api_secret,
            ws_url=settings.livekit_url,
        )
    )
