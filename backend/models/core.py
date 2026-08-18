from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class MongoBaseModel(BaseModel):
    id: Optional[str] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class VoiceConfig(BaseModel):
    provider: str
    model: str
    voice_id: str
    latency_mode: str = "balanced"


class STTConfig(BaseModel):
    provider: str
    model: str
    language: str = "multi"
    keyterms: List[str] = []


class LLMConfig(BaseModel):
    provider: str
    model: str
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 256


class AgentConfig(BaseModel):
    niche: str
    agent_name: str
    system_prompt: str
    greeting_message: str
    enabled_tools: List[str]
    voice_config: VoiceConfig
    stt_config: STTConfig
    llm_config: LLMConfig
    supported_languages: List[str]
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ToolRegistryEntry(BaseModel):
    tool_name: str
    niche: str
    enabled: bool = True
    description: str
    parameters_schema: Dict[str, Any]
    config: Optional[Dict[str, Any]] = None
    filler_phrases: Optional[Dict[str, str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class LeadQualification(BaseModel):
    budget_confirmed: bool = False
    timeline: Optional[str] = None
    financing: Optional[str] = None
    decision_maker: bool = False
    motivation: Optional[str] = None


class Lead(BaseModel):
    call_id: Optional[str] = None
    name: Optional[str] = None
    phone: str
    email: Optional[str] = None
    preferred_language: str = "en"
    niche: str
    interests: Dict[str, Any] = {}
    qualification: LeadQualification = Field(default_factory=LeadQualification)
    lead_score: str = "cold"  # hot, warm, cold, dormant
    status: str = "active"
    interaction_history: List[Dict[str, Any]] = []
    first_contact: datetime = Field(default_factory=datetime.utcnow)
    last_contact: datetime = Field(default_factory=datetime.utcnow)


class CallMetrics(BaseModel):
    avg_stt_latency_ms: Optional[float] = None
    avg_llm_ttft_ms: Optional[float] = None
    avg_tts_ttfa_ms: Optional[float] = None
    total_llm_tokens: int = 0
    interruptions_count: int = 0
    context_prunes_count: int = 0


class CallSession(BaseModel):
    call_id: str
    room_name: str
    direction: str = "inbound"
    caller_number: str
    detected_language: Optional[str] = None
    niche_context: str
    status: str = "in_progress"
    disposition: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    duration_seconds: int = 0
    total_turns: int = 0
    tools_invoked: List[Dict[str, Any]] = []
    metrics: CallMetrics = Field(default_factory=CallMetrics)
    summary: Optional[str] = None
