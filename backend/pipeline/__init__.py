"""
A.L.F.I.E Voice AI Pipeline Subsystem
Modular kernel separating Context Assembly, Audio Engine, Dialogue Execution, and Telemetry Sinks.
"""

from pipeline.context_factory import (
    get_default_config,
    resolve_call_config,
    assemble_system_prompt,
    prewarm_pipeline,
    safe_uuid,
)
from pipeline.audio_engine import (
    create_stt_plugin,
    create_llm_plugin,
    create_tts_plugin,
    create_vad_and_endpointing,
    build_audio_pipeline,
)
from pipeline.dialogue_engine import DialogueSessionManager
from pipeline.telemetry_sink import CallTelemetrySink, CallMetrics
from pipeline.realtime_s2s import OpenAIRealtimeSession, EngineMode
from pipeline.audio_mesh import (
    CartesiaTTS,
    FishAudioTTS,
    ElevenLabsTTS,
    OpenAITTS,
    DeepgramAuraTTS,
    DeepgramSTT,
    GroqWhisperSTT,
    AssemblyAISTT,
    ResilientTTSMesh,
    ResilientSTTMesh,
    build_default_tts_mesh,
    build_default_stt_mesh,
    CircuitBreaker,
    CircuitState,
)
from pipeline.pathways import (
    PathwayGraph,
    PathwayNode,
    PathwayNodeType,
    PathwayEdge,
    TransitionRule,
    ConditionType,
    PathwayStepResult,
    PathwaySessionRunner,
)
from pipeline.speculative_prefetch import (
    SpeculativeToolPrefetcher,
    SpeculativeExecutionPool,
    SpeculativeToolCandidate,
    SpeculativeExecutionResult,
    FastEntityExtractor,
    SAFE_READ_ONLY_TOOLS,
    MUTATING_TOOLS,
)
from pipeline.agent_squad import (
    AgentSquadMember,
    AgentSquadRoster,
    AgentSquadHandoffManager,
    InMemorySquadHandoffResult,
)

__all__ = [
    "get_default_config",
    "resolve_call_config",
    "assemble_system_prompt",
    "prewarm_pipeline",
    "safe_uuid",
    "create_stt_plugin",
    "create_llm_plugin",
    "create_tts_plugin",
    "create_vad_and_endpointing",
    "build_audio_pipeline",
    "create_realtime_s2s_session",
    "DialogueSessionManager",
    "CallTelemetrySink",
    "CallMetrics",
    "OpenAIRealtimeSession",
    "EngineMode",
    "CartesiaTTS",
    "FishAudioTTS",
    "ElevenLabsTTS",
    "OpenAITTS",
    "DeepgramAuraTTS",
    "DeepgramSTT",
    "GroqWhisperSTT",
    "AssemblyAISTT",
    "ResilientTTSMesh",
    "ResilientSTTMesh",
    "build_default_tts_mesh",
    "build_default_stt_mesh",
    "CircuitState",
    "CircuitBreaker",
    "PathwayGraph",
    "PathwayNode",
    "PathwayNodeType",
    "PathwayEdge",
    "TransitionRule",
    "ConditionType",
    "PathwayStepResult",
    "PathwaySessionRunner",
    "SpeculativeToolPrefetcher",
    "SpeculativeExecutionPool",
    "SpeculativeToolCandidate",
    "SpeculativeExecutionResult",
    "FastEntityExtractor",
    "SAFE_READ_ONLY_TOOLS",
    "MUTATING_TOOLS",
    "AgentSquadMember",
    "AgentSquadRoster",
    "AgentSquadHandoffManager",
    "InMemorySquadHandoffResult",
]

