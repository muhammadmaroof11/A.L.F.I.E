import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("alfie-agent-squad")


@dataclass
class AgentSquadMember:
    """Represents a specialized sub-agent within a tenant's multi-agent squad."""
    agent_id: str
    name: str
    role: str
    niche: str = "general"
    system_prompt: str = ""
    voice_config: Dict[str, Any] = field(default_factory=dict)
    enabled_tools: List[str] = field(default_factory=lambda: ["core_tools"])
    greeting_message: Optional[str] = None
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "niche": self.niche,
            "system_prompt": self.system_prompt,
            "voice_config": self.voice_config,
            "enabled_tools": self.enabled_tools,
            "greeting_message": self.greeting_message,
            "description": self.description,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentSquadMember":
        return cls(
            agent_id=str(data.get("agent_id") or uuid.uuid4()),
            name=data.get("name", "Specialist Agent"),
            role=data.get("role", "specialist"),
            niche=data.get("niche", "general"),
            system_prompt=data.get("system_prompt", ""),
            voice_config=data.get("voice_config", {}),
            enabled_tools=data.get("enabled_tools", ["core_tools"]),
            greeting_message=data.get("greeting_message"),
            description=data.get("description", ""),
            metadata=data.get("metadata", {}),
        )


class AgentSquadRoster:
    """Manages the squad roster of specialized agents available for in-memory transfers."""

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self._members_by_id: Dict[str, AgentSquadMember] = {}
        self._members_by_role: Dict[str, AgentSquadMember] = {}

    def register_member(self, member: AgentSquadMember):
        """Registers a sub-agent into the squad roster."""
        self._members_by_id[str(member.agent_id).lower()] = member
        self._members_by_role[member.role.strip().lower()] = member
        logger.info(f"Registered squad member: {member.name} ({member.role}) for tenant {self.tenant_id}")

    def get_member(self, identifier: str) -> Optional[AgentSquadMember]:
        """Resolves member by UUID, ID string, or normalized role/name."""
        if not identifier:
            return None
        norm = identifier.strip().lower()
        if norm in self._members_by_id:
            return self._members_by_id[norm]
        if norm in self._members_by_role:
            return self._members_by_role[norm]
        for m in self._members_by_id.values():
            if norm in m.name.lower() or norm in m.role.lower() or norm in m.niche.lower():
                return m
        return None

    def list_members(self) -> List[Dict[str, Any]]:
        return [m.to_dict() for m in self._members_by_id.values()]

    @classmethod
    def from_dict(cls, tenant_id: str, data: Dict[str, Any]) -> "AgentSquadRoster":
        roster = cls(tenant_id=tenant_id)
        members_data = data.get("members", []) or data.get("squad_members", [])
        if isinstance(members_data, list):
            for item in members_data:
                if isinstance(item, dict):
                    roster.register_member(AgentSquadMember.from_dict(item))
        return roster


@dataclass
class InMemorySquadHandoffResult:
    """Result of an in-memory sub-agent squad handoff execution."""
    status: str
    previous_agent: str
    target_agent: str
    target_role: str
    handoff_duration_ms: float
    transferred_context_summary: Dict[str, Any]
    spoken_bridge_message: Optional[str] = None
    error: Optional[str] = None


class AgentSquadHandoffManager:
    """
    Executes in-memory, zero-reconnect sub-agent context handoffs during live phone calls.
    Preserves active WebRTC audio streams and SIP trunks while hot-swapping agent prompt,
    niche guardrails, and tools in <50ms.
    """

    def __init__(self, tenant_id: str, roster: AgentSquadRoster, redis_client: Any = None):
        self.tenant_id = tenant_id
        self.roster = roster
        self.redis_client = redis_client
        self.active_agent_id: Optional[str] = None
        self.active_agent_role: str = "primary"
        self.active_agent_name: str = "A.L.F.I.E Primary"
        self.handoff_history: List[Dict[str, Any]] = []

    async def execute_in_memory_handoff(
        self,
        target_identifier: str,
        reason: str = "specialized_intake",
        transfer_notes: str = "",
        dialogue_manager: Any = None,
        realtime_session: Any = None,
    ) -> InMemorySquadHandoffResult:
        """
        Executes immediate in-memory hot-swap from current agent to target specialist agent.
        """
        t0 = time.time()
        target_member = self.roster.get_member(target_identifier)

        if not target_member:
            err_msg = f"Squad member '{target_identifier}' not found in tenant roster."
            logger.warning(err_msg)
            return InMemorySquadHandoffResult(
                status="failed",
                previous_agent=self.active_agent_name,
                target_agent="unknown",
                target_role="unknown",
                handoff_duration_ms=(time.time() - t0) * 1000,
                transferred_context_summary={},
                error=err_msg,
            )

        previous_name = self.active_agent_name
        previous_role = self.active_agent_role

        # 1. Extract and preserve active conversation state
        slots = {}
        if dialogue_manager and getattr(dialogue_manager, "slot_tracker", None):
            try:
                res = dialogue_manager.slot_tracker.get_all_slots()
                if isinstance(res, dict):
                    slots = res
            except Exception:
                pass

        frustration_score = 0.0
        if dialogue_manager and getattr(dialogue_manager, "frustration_tracker", None):
            try:
                score_val = dialogue_manager.frustration_tracker.current_score
                if isinstance(score_val, (int, float)):
                    frustration_score = float(score_val)
            except Exception:
                pass

        call_id = getattr(dialogue_manager.room, "name", "live_call") if (dialogue_manager and getattr(dialogue_manager, "room", None)) else "live_call"

        # 2. Formulate seamless incoming agent transition briefing
        handoff_briefing = (
            f"\n\n=== INCOMING SQUAD HANDOFF BRIEFING ===\n"
            f"You have just taken over this live call in-memory from {previous_name} ({previous_role}).\n"
            f"Transfer Reason: {reason}\n"
            f"Transfer Notes: {transfer_notes}\n"
            f"Extracted Caller Slots: {json.dumps(slots, default=str)}\n"
            f"Frustration Score: {frustration_score:.2f}\n"
            f"Maintain smooth conversational momentum. Greet the caller naturally as {target_member.name} ({target_member.role}) "
            f"and proceed with the specialized assistance immediately without asking them to repeat basic information."
        )

        # 3. Hot-swap dialogue manager state (Cascaded Pipeline Mode)
        if dialogue_manager:
            dialogue_manager.config_data["agent_name"] = target_member.name
            dialogue_manager.config_data["niche"] = target_member.niche
            dialogue_manager.config_data["system_prompt"] = f"{target_member.system_prompt}\n{handoff_briefing}"
            if target_member.voice_config:
                dialogue_manager.config_data["voice_config"] = target_member.voice_config
            if target_member.enabled_tools:
                dialogue_manager.config_data["enabled_tools"] = target_member.enabled_tools

        # 4. Hot-swap Realtime S2S session if Native S2S Mode is active
        if realtime_session and hasattr(realtime_session, "update_instructions"):
            try:
                asyncio.create_task(
                    realtime_session.update_instructions(
                        instructions=f"{target_member.system_prompt}\n{handoff_briefing}",
                        voice=target_member.voice_config.get("voice", "alloy"),
                    )
                )
            except Exception as e:
                logger.warning(f"Error updating Realtime S2S session instructions: {e}")

        # 5. Formulate natural spoken bridge greeting
        spoken_bridge = target_member.greeting_message or (
            f"Hello, I'm {target_member.name} from the {target_member.role.replace('_', ' ').title()} squad. "
            f"I have your details here regarding {reason.replace('_', ' ')}. How can I finalize this for you?"
        )

        # 6. Update squad active pointers
        self.active_agent_id = target_member.agent_id
        self.active_agent_name = target_member.name
        self.active_agent_role = target_member.role

        duration_ms = (time.time() - t0) * 1000

        handoff_record = {
            "timestamp": time.time(),
            "previous_agent": previous_name,
            "target_agent": target_member.name,
            "target_role": target_member.role,
            "reason": reason,
            "duration_ms": duration_ms,
            "slots": slots,
        }
        self.handoff_history.append(handoff_record)

        # 7. Publish live telemetry event over Redis
        if self.redis_client:
            try:
                asyncio.create_task(
                    self.redis_client.publish(
                        f"telemetry:live:{self.tenant_id}",
                        json.dumps({
                            "event": "agent_squad_handoff",
                            "call_id": call_id,
                            "previous_agent": previous_name,
                            "target_agent": target_member.name,
                            "target_role": target_member.role,
                            "reason": reason,
                            "transfer_notes": transfer_notes,
                            "handoff_duration_ms": round(duration_ms, 2),
                            "timestamp": time.time(),
                        }),
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to publish squad handoff telemetry: {e}")

        logger.info(
            f"⚡ In-Memory Squad Handoff SUCCESS: {previous_name} -> {target_member.name} ({target_member.role}) in {duration_ms:.2f}ms"
        )

        return InMemorySquadHandoffResult(
            status="success",
            previous_agent=previous_name,
            target_agent=target_member.name,
            target_role=target_member.role,
            handoff_duration_ms=duration_ms,
            transferred_context_summary={
                "slots": slots,
                "frustration_score": frustration_score,
                "transfer_notes": transfer_notes,
            },
            spoken_bridge_message=spoken_bridge,
        )
