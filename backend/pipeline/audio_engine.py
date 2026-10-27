import logging
from typing import Any, Dict, List, Optional, Tuple, Union, cast

try:
    from livekit.agents.voice import Agent, AgentSession
    from livekit.plugins import deepgram, fishaudio, openai, silero
except ImportError:
    Agent = None
    AgentSession = None
    deepgram = None
    fishaudio = None
    openai = None
    silero = None

from cache import CachedOpenAILLM
from config import settings
from pipeline.audio_mesh import (
    CartesiaTTS,
    ElevenLabsTTS,
    FishAudioTTS,
    OpenAITTS,
    DeepgramAuraTTS,
    ResilientTTSMesh,
    ResilientSTTMesh,
    build_default_stt_mesh,
    build_default_tts_mesh,
)
from pipeline.realtime_s2s import EngineMode, OpenAIRealtimeSession
from semantic_endpointing import SemanticEndpointAnalyzer

logger = logging.getLogger("alfie-pipeline-audio")


def create_realtime_s2s_session(
    config_data: Dict[str, Any],
    assembled_prompt: str,
    toolsets: List[Any],
) -> OpenAIRealtimeSession:
    """
    Instantiates an OpenAI Realtime S2S session for native Speech-to-Speech execution (<280ms).
    """
    rt_cfg = config_data.get("openai_realtime_config", {})
    return OpenAIRealtimeSession(
        instructions=assembled_prompt,
        voice=rt_cfg.get("voice") or settings.openai_realtime_voice or "alloy",
        model=rt_cfg.get("model") or settings.openai_realtime_model or "gpt-4o-realtime-preview",
        tools=toolsets,
        temperature=float(rt_cfg.get("temperature", 0.7)),
        api_key=settings.openai_api_key,
    )


async def build_audio_pipeline(
    config_data: Dict[str, Any],
    assembled_prompt: str,
    toolsets: List[Any],
    cache_enabled: bool,
    tenant_id: str,
) -> Tuple[Union[Agent, OpenAIRealtimeSession], AgentSession, SemanticEndpointAnalyzer, Any, bool]:
    """
    Constructs the complete Voice Pipeline Agent and AgentSession across Cascaded and Native S2S modes.
    """
    engine_mode = config_data.get("engine_mode", "cascaded")
    vad, endpoint_analyzer, anti_interruption_enabled = create_vad_and_endpointing(
        config_data.get("vad_config", {})
    )

    if engine_mode in ("native_s2s", EngineMode.NATIVE_S2S):
        logger.info(f"[AUDIO ENGINE] Building Native Speech-to-Speech (S2S) Multimodal Pipeline for tenant {tenant_id}")
        s2s_agent = create_realtime_s2s_session(config_data, assembled_prompt, toolsets)
        session = AgentSession() if AgentSession else cast(Any, {})
        return s2s_agent, session, endpoint_analyzer, vad, anti_interruption_enabled

    # Default: Cascaded Mesh
    stt = create_stt_plugin(config_data.get("stt_config", {}), settings.deepgram_api_key)
    llm_plugin = await create_llm_plugin(
        config_data.get("llm_config", {}),
        tenant_id=tenant_id,
        niche=config_data.get("niche", "general"),
        cache_enabled=cache_enabled,
    )
    tts = create_tts_plugin(config_data.get("voice_config", {}))

    if Agent:
        agent = Agent(
            instructions=assembled_prompt,
            vad=vad,
            stt=stt,
            llm=cast(Any, llm_plugin),
            tts=tts,
            tools=cast(Any, toolsets),
        )
    else:
        agent = cast(Any, {
            "instructions": assembled_prompt,
            "vad": vad,
            "stt": stt,
            "llm": llm_plugin,
            "tts": tts,
            "tools": toolsets,
        })
    session = AgentSession() if AgentSession else cast(Any, {})
    return agent, session, endpoint_analyzer, vad, anti_interruption_enabled


def create_stt_plugin(stt_config: Dict[str, Any], api_key: str) -> Any:
    """
    Instantiates streaming STT with multi-provider fallback.
    Default: Deepgram Nova-3 / Nova-2 with automatic Groq Whisper & AssemblyAI failover mesh.
    """
    if deepgram and hasattr(deepgram, "STT"):
        return deepgram.STT(
            model=stt_config.get("model", "nova-3"),
            language=stt_config.get("language", "multi"),
            profanity_filter=stt_config.get("profanity_filter", False),
            smart_format=stt_config.get("smart_format", True),
            api_key=api_key or settings.deepgram_api_key,
        )
    return build_default_stt_mesh(stt_config)


async def create_llm_plugin(
    llm_config: Dict[str, Any],
    tenant_id: str,
    niche: str,
    cache_enabled: bool,
) -> Any:
    """
    Instantiates the LLM plugin using LiteLLM gateway with direct OpenRouter fallback.
    """
    llm_base_url = settings.litellm_url
    llm_api_key = settings.litellm_master_key or settings.openrouter_api_key

    try:
        async with httpx.AsyncClient(timeout=1.0) as client:
            resp = await client.get(f"{settings.litellm_url}/health")
            if resp.status_code != 200:
                llm_base_url = "https://openrouter.ai/api/v1"
                llm_api_key = settings.openrouter_api_key
    except Exception:
        llm_base_url = "https://openrouter.ai/api/v1"
        llm_api_key = settings.openrouter_api_key
        logger.info("LiteLLM unavailable; routed directly to OpenRouter gateway.")

    return CachedOpenAILLM(
        tenant_id=tenant_id,
        niche=niche or "general",
        cache_enabled=cache_enabled,
        model=llm_config.get("model", "meta-llama/llama-3.1-8b-instruct"),
        temperature=float(llm_config.get("temperature", 0.7)),
        max_tokens=int(llm_config.get("max_tokens", 1000)),
        base_url=llm_base_url,
        api_key=llm_api_key,
    )


def create_tts_plugin(voice_config: Dict[str, Any]) -> Any:
    """
    Instantiates the TTS plugin with multi-provider resilient tiering:
    1. Cartesia Sonic 3.0 (Tier-1 Ultra-Low Latency ~90ms TTFB)
    2. Fish Audio S2.1-Pro (Emotional / High-Fidelity)
    3. ElevenLabs Flash v2.5
    4. OpenAI TTS-1
    5. Deepgram Aura TTS (Zero-Config Fallback)
    """
    tts_provider = voice_config.get("provider") or settings.tts_primary_provider or "cartesia"

    if tts_provider == "cartesia" and (settings.cartesia_api_key or hasattr(voice_config, "get")):
        return CartesiaTTS(
            voice_id=voice_config.get("voice_id", "a0e99841-438c-4a64-b679-ae501e7d6091"),
            model=voice_config.get("model", "sonic-english"),
            api_key=settings.cartesia_api_key,
        )
    elif tts_provider == "fish_audio" and settings.fish_audio_api_key and fishaudio and hasattr(fishaudio, "TTS"):
        return fishaudio.TTS(
            model=voice_config.get("model", "s2.1-pro"),
            voice_id=voice_config.get("voice_id", "224a2257dd4943209a683d27a5e41439"),
            api_key=settings.fish_audio_api_key,
            latency_mode=voice_config.get("latency_mode", "balanced"),
        )
    elif tts_provider == "elevenlabs" and settings.elevenlabs_api_key:
        return ElevenLabsTTS(
            voice_id=voice_config.get("voice_id", "21m00Tcm4TlvDq8ikWAM"),
            model=voice_config.get("model", "eleven_flash_v2_5"),
            api_key=settings.elevenlabs_api_key,
        )
    elif settings.openai_api_key and openai and hasattr(openai, "TTS"):
        return openai.TTS(
            model="tts-1",
            voice=voice_config.get("voice_id", "alloy"),
            api_key=settings.openai_api_key,
        )
    elif deepgram and hasattr(deepgram, "TTS"):
        return deepgram.TTS(
            model="aura-asteria-en",
            api_key=settings.deepgram_api_key,
        )
    else:
        return build_default_tts_mesh(voice_config)


def create_vad_and_endpointing(vad_config: Dict[str, Any]) -> Tuple[Any, SemanticEndpointAnalyzer, bool]:
    """
    Instantiates Silero VAD coupled with the dynamic Semantic Turn Endpointing analyzer.
    """
    endpoint_preset = vad_config.get("endpointing_preset", "natural")
    anti_interruption_enabled = vad_config.get("anti_interruption_enabled", True)
    custom_pacing = {
        "base_silence": float(vad_config.get("min_silence_duration", 0.55)),
        "extended_silence": float(vad_config.get("extended_silence_duration", 1.25)),
        "quick_silence": float(vad_config.get("quick_silence_duration", 0.38)),
    }
    endpoint_analyzer = SemanticEndpointAnalyzer(preset=endpoint_preset, custom_pacing=custom_pacing)

    vad: Any = (
        silero.VAD.load(
            min_silence_duration=endpoint_analyzer.base_silence,
            activation_threshold=float(vad_config.get("activation_threshold", 0.3)),
        )
        if silero and hasattr(silero, "VAD")
        else None
    )
    return vad, endpoint_analyzer, anti_interruption_enabled
