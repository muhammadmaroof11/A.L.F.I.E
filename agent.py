import logging
import asyncio
import json
from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli, llm
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import deepgram, openai, silero, fishaudio
from livekit import api as livekit_api
from config import settings
from tools.registry import registry
from tools.core import CoreTools
from tools.real_estate import RealEstateTools
from tools.car_rental import CarRentalTools
from prompts.base import BASE_SYSTEM_PROMPT
from prompts.registry import PROMPT_REGISTRY
from crm_client import crm
from telemetry import init_telemetry_pool

# Register available tools
registry.register("core_tools", CoreTools)
registry.register("real_estate_tools", RealEstateTools)
registry.register("car_rental_tools", CarRentalTools)

logger = logging.getLogger("alfie-agent")


async def prewarm(proc):
    """
    Runs once when the worker process starts — before any calls come in.
    Ideal for warming up long-lived connections like the telemetry DB pool.
    """
    logger.info("Prewarming agent worker: initializing telemetry pool...")
    await init_telemetry_pool()


async def entrypoint(ctx: JobContext):
    logger.info(f"Connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # --- PHASE 2.1b: Read tenant_id from SIP room metadata (not hardcoded) ---
    try:
        metadata = json.loads(ctx.room.metadata or "{}")
    except json.JSONDecodeError:
        metadata = {}

    tenant_id = metadata.get("tenant_id")
    if not tenant_id:
        logger.error("No tenant_id found in room metadata. Cannot route call. Shutting down.")
        return

    logger.info(f"Fetching configuration for tenant: {tenant_id} from Twenty CRM...")
    config_data = await crm.get_tenant_config(tenant_id)

    if not config_data:
        logger.error(f"Tenant config not found for '{tenant_id}' in Twenty CRM. Shutting down.")
        return

    logger.info(f"Initializing agent for tenant: {tenant_id} (Niche: {config_data.get('niche')})")

    # --- PHASE 2.4b: Dynamic prompt routing via registry ---
    niche = config_data.get("niche")
    niche_prompt = PROMPT_REGISTRY.get(niche, "")
    system_prompt = f"{BASE_SYSTEM_PROMPT}\n\n{niche_prompt}\n\n{config_data.get('system_prompt', '')}"

    # Setup tools
    tool_keys = config_data.get("enabled_tools", [])
    fnc_ctx = registry.build_context(tool_keys, tenant_id=tenant_id, room_name=ctx.room.name)

    # Initialize AI Plugins from settings / Docker secrets
    stt = deepgram.STT(
        model=config_data["stt_config"]["model"],
        language=config_data["stt_config"]["language"],
        profanity_filter=config_data["stt_config"]["profanity_filter"],
        smart_format=config_data["stt_config"]["smart_format"],
        api_key=settings.deepgram_api_key
    )

    llm_plugin = openai.LLM(
        model=config_data["llm_config"]["model"],
        temperature=config_data["llm_config"]["temperature"],
        max_tokens=config_data["llm_config"]["max_tokens"],
        base_url="https://openrouter.ai/api/v1",
        api_key=settings.openrouter_api_key
    )

    # --- PHASE 2.5b: Dynamic TTS provider ---
    tts_provider = config_data["voice_config"].get("provider", "fish_audio")
    if tts_provider == "fish_audio":
        tts = fishaudio.TTS(
            model=config_data["voice_config"]["model"],
            reference_id=config_data["voice_config"]["voice_id"],
            api_key=settings.fish_audio_api_key,
            latency_mode=config_data["voice_config"]["latency_mode"]
        )
    else:
        # Fallback: OpenAI TTS
        tts = openai.TTS(
            model="tts-1",
            voice=config_data["voice_config"].get("voice_id", "alloy"),
            api_key=settings.openrouter_api_key
        )

    vad = silero.VAD(
        min_silence_duration=config_data["vad_config"]["min_silence_duration"],
        activation_threshold=config_data["vad_config"]["activation_threshold"]
    )

    # Initialize Pipeline Agent
    agent = VoicePipelineAgent(
        vad=vad,
        stt=stt,
        llm=llm_plugin,
        tts=tts,
        fnc_ctx=fnc_ctx,
        chat_ctx=llm.ChatContext().append(role="system", text=system_prompt)
    )

    agent.start(ctx.room)

    greeting = config_data.get("greeting_message", "Hello, how can I help you today?")
    await asyncio.sleep(1)  # Brief pause for audio connection stabilization
    allow_interrupt = config_data.get("allow_interruptions", True)
    await agent.say(greeting, allow_interruptions=allow_interrupt)

    call_start_time = asyncio.get_event_loop().time()

    @ctx.room.on("disconnected")
    def on_disconnect(*args):
        logger.info(f"[{tenant_id}] Call ended. Triggering post-call processing...")
        duration = int(asyncio.get_event_loop().time() - call_start_time)
        asyncio.create_task(
            post_call_processing(agent.chat_ctx, tenant_id, ctx.room.name, duration)
        )


async def post_call_processing(chat_ctx: llm.ChatContext, tenant_id: str, room_name: str, duration_seconds: int):
    """Runs after a call ends: fetch recording URL, fire n8n webhook, log billing."""
    from notifications import send_webhook
    from billing import record_usage

    # 1. Build transcript from chat context
    messages = [
        {"role": m.role, "content": m.text}
        for m in chat_ctx.messages
        if m.role in ["user", "assistant"]
    ]

    # 2. Fetch real recording URL via LiveKit Egress API
    recording_url = None
    try:
        lkapi = livekit_api.LiveKitAPI(
            settings.livekit_url, settings.livekit_api_key, settings.livekit_api_secret
        )
        egresses = await lkapi.egress.list_egress(
            livekit_api.ListEgressRequest(room_name=room_name)
        )
        await lkapi.aclose()
        if egresses and egresses[0].file:
            recording_url = egresses[0].file.location
    except Exception as e:
        logger.warning(f"Could not fetch egress recording URL: {e}")

    # 3. Fire to n8n event bus — n8n will summarize and write InteractionLog to Twenty CRM
    payload = {
        "room_name": room_name,
        "duration_seconds": duration_seconds,
        "recording_url": recording_url,
        "transcript": messages
    }
    await send_webhook(tenant_id, "call_completed", payload)

    # 4. Record usage for billing / Super Admin metering
    await record_usage(tenant_id, room_name, duration_seconds)


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
