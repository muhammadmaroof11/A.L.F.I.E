import asyncio
import json
import time
import pytest
from unittest.mock import AsyncMock, MagicMock

from pipeline.speculative_prefetch import (
    FastEntityExtractor,
    SpeculativeToolPrefetcher,
    SpeculativeExecutionPool,
    SpeculativeToolCandidate,
    SAFE_READ_ONLY_TOOLS,
    MUTATING_TOOLS,
)
from pipeline.agent_squad import (
    AgentSquadMember,
    AgentSquadRoster,
    AgentSquadHandoffManager,
    InMemorySquadHandoffResult,
)
from pipeline.pathways import (
    PathwayGraph,
    PathwayNode,
    PathwayNodeType,
    PathwayEdge,
    TransitionRule,
    ConditionType,
    PathwaySessionRunner,
)
from tools.core import CoreTools


class TestFastEntityExtractor:
    """Validates real-time heuristic entity extraction on partial speech tokens."""

    def test_date_and_time_extraction(self):
        text = "I would like to come in tomorrow afternoon around 3pm for a checkup"
        entities = FastEntityExtractor.extract_entities(text)
        assert "date_expression" in entities
        assert entities["date_expression"].lower() == "tomorrow"
        assert "time_expression" in entities
        assert "3pm" in entities["time_expression"].lower()

    def test_case_number_extraction(self):
        text = "Hi, I am calling to check on case number 94821 regarding my accident"
        entities = FastEntityExtractor.extract_entities(text)
        assert "case_id" in entities
        assert entities["case_id"] == "94821"

    def test_vehicle_category_extraction(self):
        text = "Do you have any cadillac escalade or luxury sedan available for the weekend?"
        entities = FastEntityExtractor.extract_entities(text)
        assert "vehicle_type" in entities
        assert entities["vehicle_type"] in ("escalade", "cadillac", "sedan")

    def test_property_feature_extraction(self):
        text = "Looking for a 3 bedroom near downtown austin"
        entities = FastEntityExtractor.extract_entities(text)
        assert "property_query" in entities
        assert "3 bedroom" in entities["property_query"].lower()


class TestSpeculativeToolPrefetcher:
    """Validates partial STT stream monitoring and candidate tool generation."""

    def test_calendar_intent_generation(self):
        prefetcher = SpeculativeToolPrefetcher(tenant_id="tenant_123", niche="medical")
        partial_text = "I want to schedule an appointment for next Tuesday"
        candidates = prefetcher.on_partial_transcript(partial_text)
        assert len(candidates) >= 1
        cand = candidates[0]
        assert cand.tool_name == "check_calendar_availability"
        assert "next tuesday" in cand.arguments.get("date", "").lower()

    def test_case_inquiry_intent_generation(self):
        prefetcher = SpeculativeToolPrefetcher(tenant_id="tenant_123", niche="legal")
        partial_text = "Can you look up claim number CL-88231?"
        candidates = prefetcher.on_partial_transcript(partial_text)
        assert len(candidates) >= 1
        cand = candidates[0]
        assert cand.tool_name == "lookup_case"
        assert cand.arguments.get("case_id") == "CL-88231"

    def test_duplicate_partial_text_debouncing(self):
        prefetcher = SpeculativeToolPrefetcher(tenant_id="tenant_123", niche="medical")
        partial_text = "I want to schedule an appointment for next Tuesday"
        candidates1 = prefetcher.on_partial_transcript(partial_text)
        assert len(candidates1) >= 1
        # Repeated identical partial stream returns empty list to avoid redundant task spam
        candidates2 = prefetcher.on_partial_transcript(partial_text)
        assert len(candidates2) == 0

    def test_safe_vs_mutating_tool_guard(self):
        prefetcher = SpeculativeToolPrefetcher(tenant_id="tenant_123")
        assert prefetcher.is_safe_tool("check_calendar_availability") is True
        assert prefetcher.is_safe_tool("lookup_case") is True
        assert prefetcher.is_safe_tool("search_properties") is True
        assert prefetcher.is_safe_tool("get_vehicle_rates") is True

        # Mutation tools must be strictly rejected
        assert prefetcher.is_safe_tool("book_appointment") is False
        assert prefetcher.is_safe_tool("charge_payment") is False
        assert prefetcher.is_safe_tool("send_sms") is False
        assert prefetcher.is_safe_tool("transfer_to_squad_agent") is False


@pytest.mark.asyncio
class TestSpeculativeExecutionPool:
    """Validates promise caching, 0ms latency hits, and safety gates."""

    async def test_prefetch_and_cache_hit(self):
        pool = SpeculativeExecutionPool(ttl_seconds=10.0)

        mock_tool_called = False

        async def mock_calendar_tool(tool_name, args):
            nonlocal mock_tool_called
            mock_tool_called = True
            await asyncio.sleep(0.05)  # Simulate 50ms backend latency
            return {"status": "available", "slots": ["10:00 AM", "02:00 PM"]}

        candidate = SpeculativeToolCandidate(
            tool_name="check_calendar_availability",
            arguments={"date": "2026-09-20", "preferred_time": "morning"},
            confidence=0.9,
            intent="check_availability",
            matched_phrase="available on 2026-09-20 morning",
        )

        key = await pool.prefetch_candidate(candidate, mock_calendar_tool)
        assert key is not None

        # Give async task time to resolve into pool cache
        await asyncio.sleep(0.08)

        # Retrieve result when LLM commits turn
        result, is_hit, saved_ms = await pool.get_or_execute(
            tool_name="check_calendar_availability",
            arguments={"date": "2026-09-20", "preferred_time": "morning"},
            default_executor=mock_calendar_tool,
        )

        assert is_hit is True
        assert result["status"] == "available"
        assert len(result["slots"]) == 2
        assert saved_ms > 0
        assert pool.cache_hits == 1

    async def test_mutation_tool_rejected_from_speculative_pool(self):
        pool = SpeculativeExecutionPool()
        candidate = SpeculativeToolCandidate(
            tool_name="book_appointment",
            arguments={"date": "tomorrow", "time": "3pm"},
            confidence=0.95,
            intent="book",
            matched_phrase="book it now",
        )
        key = await pool.prefetch_candidate(candidate, AsyncMock())
        assert key is None
        assert pool.total_dispatched == 0

    async def test_cache_miss_fallback(self):
        pool = SpeculativeExecutionPool()

        async def fallback_exec(name, args):
            return {"status": "fresh_execution", "val": 42}

        result, is_hit, saved_ms = await pool.get_or_execute(
            tool_name="lookup_case",
            arguments={"case_id": "999"},
            default_executor=fallback_exec,
        )

        assert is_hit is False
        assert result["status"] == "fresh_execution"
        assert pool.cache_misses == 1

    async def test_metrics_reporting(self):
        pool = SpeculativeExecutionPool()
        metrics = pool.get_metrics()
        assert "total_dispatched" in metrics
        assert "cache_hits" in metrics
        assert "hit_ratio" in metrics
        assert "total_latency_saved_ms" in metrics


class TestAgentSquadRoster:
    """Validates multi-agent squad roster indexing and resolution."""

    def test_roster_registration_and_lookup(self):
        roster = AgentSquadRoster(tenant_id="tenant_abc")
        member1 = AgentSquadMember(
            agent_id="agent_1",
            name="Sarah Miller",
            role="receptionist",
            niche="general",
            system_prompt="You are Sarah, a warm front-desk receptionist.",
        )
        member2 = AgentSquadMember(
            agent_id="agent_2",
            name="Robert Vance",
            role="legal_intake_specialist",
            niche="legal",
            system_prompt="You are Robert Vance, a senior personal injury intake attorney.",
            enabled_tools=["core_tools", "legal_intake_tools"],
        )
        roster.register_member(member1)
        roster.register_member(member2)

        # Lookup by role
        found = roster.get_member("receptionist")
        assert found is not None
        assert found.name == "Sarah Miller"

        # Lookup by name fragment
        found2 = roster.get_member("robert")
        assert found2 is not None
        assert found2.role == "legal_intake_specialist"

        # Lookup by id
        found3 = roster.get_member("agent_2")
        assert found3 is not None
        assert found3.agent_id == "agent_2"

    def test_roster_from_dict(self):
        data = {
            "members": [
                {
                    "agent_id": "sub_1",
                    "name": "Dr. Emily Watson",
                    "role": "medical_triage",
                    "niche": "medical",
                    "system_prompt": "Medical triage specialist",
                }
            ]
        }
        roster = AgentSquadRoster.from_dict("tenant_med", data)
        m = roster.get_member("medical_triage")
        assert m is not None
        assert m.name == "Dr. Emily Watson"


@pytest.mark.asyncio
class TestAgentSquadHandoffManager:
    """Validates in-memory zero-reconnect sub-agent context handoffs."""

    async def test_successful_in_memory_handoff(self):
        roster = AgentSquadRoster(tenant_id="tenant_legal")
        specialist = AgentSquadMember(
            agent_id="spec_101",
            name="David Ross, Esq.",
            role="litigation_specialist",
            niche="legal",
            system_prompt="You handle complex litigation intake.",
            voice_config={"voice_id": "cartesia_david"},
            enabled_tools=["core_tools", "legal_intake_tools"],
            greeting_message="Hello, this is David Ross. I see you were speaking about the commercial accident.",
        )
        roster.register_member(specialist)

        mock_redis = AsyncMock()
        manager = AgentSquadHandoffManager(tenant_id="tenant_legal", roster=roster, redis_client=mock_redis)

        # Mock active dialogue manager
        mock_dm = MagicMock()
        mock_dm.config_data = {
            "agent_name": "Front Desk AI",
            "niche": "general",
            "system_prompt": "Initial front desk prompt",
        }
        mock_dm.room = MagicMock()
        mock_dm.room.name = "call_room_7788"
        mock_dm.slot_tracker = MagicMock()
        mock_dm.slot_tracker.get_all_slots.return_value = {"accident_date": "yesterday", "injury": "whiplash"}
        mock_dm.frustration_tracker = MagicMock()
        mock_dm.frustration_tracker.current_score = 0.15

        res = await manager.execute_in_memory_handoff(
            target_identifier="litigation_specialist",
            reason="Complex liability intake",
            transfer_notes="Caller mentioned commercial truck involved",
            dialogue_manager=mock_dm,
        )

        assert res.status == "success"
        assert res.target_agent == "David Ross, Esq."
        assert res.target_role == "litigation_specialist"
        assert res.handoff_duration_ms < 50.0  # Must complete in sub-50ms
        assert "David Ross" in res.spoken_bridge_message

        # Verify state hot-swapped in dialogue manager
        assert mock_dm.config_data["agent_name"] == "David Ross, Esq."
        assert mock_dm.config_data["niche"] == "legal"
        assert "INCOMING SQUAD HANDOFF BRIEFING" in mock_dm.config_data["system_prompt"]
        assert "whiplash" in mock_dm.config_data["system_prompt"]

        # Verify Redis live telemetry published
        mock_redis.publish.assert_called_once()
        call_args = mock_redis.publish.call_args[0]
        assert "telemetry:live:tenant_legal" in call_args[0]
        payload = json.loads(call_args[1])
        assert payload["event"] == "agent_squad_handoff"
        assert payload["target_agent"] == "David Ross, Esq."

    async def test_handoff_member_not_found(self):
        roster = AgentSquadRoster(tenant_id="tenant_x")
        manager = AgentSquadHandoffManager(tenant_id="tenant_x", roster=roster)

        res = await manager.execute_in_memory_handoff(
            target_identifier="non_existent_role",
            reason="test",
        )
        assert res.status == "failed"
        assert "not found" in res.error.lower()


@pytest.mark.asyncio
class TestCoreToolsSquadTransfer:
    """Validates transfer_to_squad_agent function tool integration."""

    async def test_core_tools_squad_transfer_execution(self):
        roster = AgentSquadRoster(tenant_id="tenant_1")
        roster.register_member(
            AgentSquadMember(
                agent_id="sub_2",
                name="Jessica VIP Concierge",
                role="concierge",
                niche="hospitality",
                system_prompt="VIP Concierge",
            )
        )
        squad_manager = AgentSquadHandoffManager(tenant_id="tenant_1", roster=roster)
        mock_dm = MagicMock()
        mock_dm.config_data = {"agent_name": "Triage"}
        mock_dm.room = MagicMock()
        mock_dm.room.name = "room_1"

        tools = CoreTools(
            tenant_id="tenant_1",
            room_name="room_1",
            dialogue_manager=mock_dm,
            squad_manager=squad_manager,
        )

        res_str = await tools.transfer_to_squad_agent(
            target_role_or_id="concierge",
            reason="VIP table reservation",
            transfer_notes="Party of 6 at 8pm",
        )

        assert "HANDOFF_SUCCESS" in res_str
        assert "Jessica VIP Concierge" in res_str


@pytest.mark.asyncio
class TestPathwaysSquadHandoff:
    """Validates deterministic node graph traversal leading to a SQUAD_HANDOFF node."""

    async def test_pathway_squad_handoff_node(self):
        n1 = PathwayNode(
            id="start",
            name="Greeting",
            node_type=PathwayNodeType.GREETING,
            prompt_template="How can I help you?",
        )
        n2 = PathwayNode(
            id="handoff_node",
            name="TransferToLegalSpecialist",
            node_type=PathwayNodeType.SQUAD_HANDOFF,
            prompt_template="Connecting you with our legal attorney.",
            squad_target_role="legal_intake_specialist",
        )
        edge = PathwayEdge(
            source_node_id="start",
            target_node_id="handoff_node",
            rule=TransitionRule(
                condition_type=ConditionType.ALWAYS,
            ),
        )
        graph = PathwayGraph(
            id="graph_squad",
            name="Squad Handoff Graph",
            start_node_id="start",
            nodes=[n1, n2],
            edges=[edge],
        )

        runner = PathwaySessionRunner(graph=graph)
        step_res = await runner.step(user_utterance="I need to speak with a lawyer")

        assert step_res.current_node_id == "handoff_node"
        assert step_res.squad_handoff_triggered is True
        assert step_res.squad_target_role == "legal_intake_specialist"
