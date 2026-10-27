import asyncio
import json
import logging
import pathlib
from typing import Any, Optional

try:
    from livekit.agents import AutoSubscribe, JobContext, WorkerOptions, cli
except ImportError:
    AutoSubscribe = None
    JobContext = Any
    WorkerOptions = None
    cli = None

from config import settings
from logging_config import setup_logging
from pipeline import (
    CallMetrics,
    CallTelemetrySink,
    DialogueSessionManager,
    assemble_system_prompt,
    build_audio_pipeline,
    get_default_config,
    prewarm_pipeline,
    resolve_call_config,
)
from telemetry import get_redis
from tools.calendar import CalendarTools
from tools.car_rental import CarRentalTools
from tools.core import CoreTools
from tools.hospitality import HospitalityTools
from tools.legal import LegalIntakeTools
from tools.luxury_transport import LuxuryTransportTools
from tools.medical import MedicalTools
from tools.real_estate import RealEstateTools
from tools.registry import registry

# Register available vertical tools in the global registry
registry.register("core_tools", CoreTools)
registry.register("real_estate_tools", RealEstateTools)
registry.register("car_rental_tools", CarRentalTools)
registry.register("calendar_tools", CalendarTools)
registry.register("luxury_transport_tools", LuxuryTransportTools)
registry.register("legal_intake_tools", LegalIntakeTools)
registry.register("medical_tools", MedicalTools)
registry.register("hospitality_tools", HospitalityTools)

setup_logging()
logger = logging.getLogger("alfie-agent")

HEARTBEAT_FILE = pathlib.Path("/tmp/agent_heartbeat")
arq_pool: Optional[Any] = None


async def _heartbeat_loop():
    """Periodically touches the heartbeat file so Docker healthcheck detects worker liveness."""
    while True:
        try:
            HEARTBEAT_FILE.touch()
        except Exception as e:
            logger.warning(f"Failed to touch heartbeat file: {e}")
        await asyncio.sleep(15)


async def prewarm(proc):
    """
    Runs once when the worker process starts — before any incoming calls.
    Warms up DB pool, Redis connection, semantic vector cache, and FAQ knowledge bases.
    """
    global arq_pool
    try:
        HEARTBEAT_FILE.touch()
    except Exception:
        pass
    arq_pool = await prewarm_pipeline()


async def entrypoint(ctx: JobContext):
    """
    Real-Time Voice Agent Entrypoint.
    Connects to WebRTC audio room and executes the decoupled voice pipeline.
    """
    logger.info(f"Connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # 1. Parse tenant_id and agent_id from room metadata or SIP name
    try:
        metadata = json.loads(ctx.room.metadata or "{}")
    except json.JSONDecodeError:
        metadata = {}

    tenant_id = metadata.get("tenant_id")
    agent_id = metadata.get("agent_id")

    if not tenant_id:
        parts = ctx.room.name.split("_")
        if len(parts) >= 1 and parts[0]:
            tenant_id = parts[0]
        if len(parts) >= 2 and parts[1]:
            agent_id = parts[1]

    if not tenant_id:
        logger.error(f"No tenant_id found in room {ctx.room.name}. Aborting call.")
        return

    caller_phone = metadata.get("caller_phone") or metadata.get("phone") or metadata.get("caller_number")
    redis_client = await get_redis()

    # 2. Resolve Config & Assemble Prompt Context
    config_data = await resolve_call_config(
        tenant_id=tenant_id,
        agent_id=agent_id,
        metadata=metadata,
        redis_client=redis_client,
    )

    assembled_prompt, slot_tracker, cache_enabled = await assemble_system_prompt(
        tenant_id=tenant_id,
        agent_id=agent_id,
        config_data=config_data,
        metadata=metadata,
        room_name=ctx.room.name,
        redis_client=redis_client,
    )

    if not assembled_prompt:
        logger.warning(f"[{tenant_id}] Prompt assembly rejected call (duplicate/spam). Exiting.")
        return

    # 3. Build Dynamic Toolsets
    tool_keys = config_data.get("enabled_tools", ["core_tools"])
    calendar_api_key = config_data.get("calendar_api_key", "")
    calendar_event_type_id = config_data.get("calendar_event_type_id", "")
    custom_tools_list = config_data.get("custom_tools", [])

    toolsets = await registry.build_toolsets(
        tool_keys,
        custom_tools=custom_tools_list,
        niche=config_data.get("niche", "general"),
        tenant_id=tenant_id,
        room_name=ctx.room.name,
        room=ctx.room,
        caller_phone=caller_phone,
        calendar_api_key=calendar_api_key,
        calendar_event_type_id=calendar_event_type_id,
    )

    # 4. Construct Audio Pipeline (STT, LLM, TTS, VAD)
    agent, session, endpoint_analyzer, vad_plugin, anti_interruption_enabled = await build_audio_pipeline(
        config_data=config_data,
        assembled_prompt=assembled_prompt,
        toolsets=toolsets,
        cache_enabled=cache_enabled,
        tenant_id=tenant_id,
    )

    # 5. Initialize Telemetry Sink & Dialogue Session Manager
    telemetry_sink = CallTelemetrySink(
        tenant_id=tenant_id,
        call_id=ctx.room.name,
        agent_id=agent_id,
        agent_name=config_data.get("agent_name", "A.L.F.I.E Voice Agent"),
        niche=config_data.get("niche", "general"),
        caller_phone=caller_phone,
        redis_client=redis_client,
        arq_pool=arq_pool,
    )
    await telemetry_sink.initialize()

    dialogue_manager = DialogueSessionManager(
        tenant_id=tenant_id,
        room=ctx.room,
        session=session,
        agent=agent,
        config_data=config_data,
        endpoint_analyzer=endpoint_analyzer,
        vad_plugin=vad_plugin,
        slot_tracker=slot_tracker,
        anti_interruption_enabled=anti_interruption_enabled,
        redis_client=redis_client,
        telemetry_sink=telemetry_sink,
    )
    dialogue_manager.bind_event_listeners()

    # 6. Start Voice Agent Session & Deliver Instant Opening Greeting (<150ms TTFA)
    heartbeat_task = asyncio.create_task(_heartbeat_loop())
    try:
        greeting = config_data.get(
            "greeting_message",
            "Hello, thank you for calling. How can I assist you today?",
        )
        await session.say(greeting, allow_interruptions=True)
    except Exception as e:
        logger.warning(f"Error speaking opening greeting: {e}")

    # 7. Listen for Room Disconnection & Finalize Session
    disconnect_future = asyncio.get_event_loop().create_future()

    @ctx.room.on("disconnected")
    def on_disconnected():
        if not disconnect_future.done():
            disconnect_future.set_result(True)

    try:
        await disconnect_future
    except asyncio.CancelledError:
        pass
    finally:
        heartbeat_task.cancel()
        dialogue_manager.cleanup()
        await telemetry_sink.finalize(
            turns_count=dialogue_manager.current_turn_counter,
            interruption_count=dialogue_manager.interruption_count,
            dtmf_events=dialogue_manager.dtmf_events,
            frustration_tracker=dialogue_manager.frustration_tracker,
            slot_tracker=dialogue_manager.slot_tracker,
        )
        logger.info(f"Call session {ctx.room.name} teardown complete.")


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
