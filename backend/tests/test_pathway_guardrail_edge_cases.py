import asyncio
import json
import time
import pytest
from unittest.mock import AsyncMock, MagicMock

from pipeline.pathways import (
    PathwayGraph,
    PathwayNode,
    PathwayNodeType,
    PathwayEdge,
    TransitionRule,
    ConditionType,
    PathwaySessionRunner,
)
from guardrails.anti_hallucination import AntiHallucinationEngine
from guardrails.safety_filter import ZeroLiabilityFilter
from dtmf_utils import validate_dtmf_sequence, DTMFKeypadBuffer


class TestComplexPathwayGraphEdgeCases:
    """Stress tests complex multi-branch state graphs, circular edges, and tool chaining."""

    @pytest.mark.asyncio
    async def test_multi_hop_pathway_with_slot_branching(self):
        # Build 4-node deterministic graph:
        # GREETING -> (ask_injury) -> (if injury exists -> CHECK_AVAILABILITY tool -> BOOKING_CONFIRMATION)
        #                          -> (if no injury -> GENERAL_FAQ)
        n_greet = PathwayNode(id="n_greet", name="Greeting", node_type=PathwayNodeType.GREETING, prompt_template="Hello, welcome to Apex Legal.")
        n_ask = PathwayNode(id="n_ask", name="AskInjury", node_type=PathwayNodeType.QUESTION, prompt_template="Were you injured in the incident?", required_slots=["injury_type"])
        n_tool = PathwayNode(id="n_tool", name="CheckCalendar", node_type=PathwayNodeType.TOOL_EXECUTION, prompt_template="", tool_name="check_calendar_availability", tool_params={"date": "tomorrow"})
        n_confirm = PathwayNode(id="n_confirm", name="Confirmed", node_type=PathwayNodeType.END_CALL, prompt_template="Your appointment has been scheduled.")
        n_faq = PathwayNode(id="n_faq", name="GeneralFAQ", node_type=PathwayNodeType.QUESTION, prompt_template="How else may I help you with our firm?")

        e1 = PathwayEdge(source_node_id="n_greet", target_node_id="n_ask", rule=TransitionRule(condition_type=ConditionType.ALWAYS))
        e2_injured = PathwayEdge(source_node_id="n_ask", target_node_id="n_tool", rule=TransitionRule(condition_type=ConditionType.SLOT_PRESENT, slot_name="injury_type"))
        e2_not_injured = PathwayEdge(source_node_id="n_ask", target_node_id="n_faq", rule=TransitionRule(condition_type=ConditionType.ALWAYS))
        e3_tool_success = PathwayEdge(source_node_id="n_tool", target_node_id="n_confirm", rule=TransitionRule(condition_type=ConditionType.TOOL_SUCCESS))

        graph = PathwayGraph(
            id="g_legal_flow",
            name="Legal Flow",
            start_node_id="n_greet",
            nodes=[n_greet, n_ask, n_tool, n_confirm, n_faq],
            edges=[e1, e2_injured, e2_not_injured, e3_tool_success],
        )

        # 1. Validation check: graph is structurally sound
        errors = graph.validate()
        assert len(errors) == 0

        # 2. Execution steps:
        # Turn 1: GREETING -> ASK_INJURY
        runner = PathwaySessionRunner(graph=graph)
        step_1 = await runner.step(user_utterance="Hello")
        assert step_1.current_node_id == "n_ask"
        assert "Were you injured" in step_1.spoken_response

        # Turn 2: User provides injury slot -> chains through tool execution automatically into Confirmed
        async def mock_tool(name, args):
            return {"status": "success", "available": True}

        step_2 = await runner.step(
            user_utterance="I had a serious car accident and broke my leg",
            detected_slots={"injury_type": "broken_leg"},
            tool_executor=mock_tool,
        )

        assert step_2.current_node_id == "n_confirm"
        assert step_2.should_end_call is True
        assert step_2.tool_executed == "check_calendar_availability"
        assert step_2.tool_result["status"] == "success"

    def test_graph_validation_detects_orphaned_nodes_and_missing_terminals(self):
        # Graph with unreachable node and no terminal node
        n1 = PathwayNode(id="start", name="Start", node_type=PathwayNodeType.GREETING, prompt_template="Hi")
        n_orphan = PathwayNode(id="orphan", name="Orphan", node_type=PathwayNodeType.QUESTION, prompt_template="Who are you?")
        graph = PathwayGraph(
            id="invalid_g",
            name="Invalid Graph",
            start_node_id="start",
            nodes=[n1, n_orphan],
            edges=[],
        )
        errors = graph.validate()
        assert len(errors) >= 2
        assert any("Unreachable" in e for e in errors)
        assert any("terminal" in e for e in errors)


class TestAntiHallucinationAndZeroLiabilityStress:
    """Stress tests anti-hallucination sanitization against adversarial claims."""

    def test_phantom_booking_claim_interception(self):
        engine = AntiHallucinationEngine(tenant_id="tenant_guard_test")
        raw_text = "I have officially scheduled your dental cleaning for tomorrow at 2:00 PM with Dr. Smith."
        
        # Turn with NO tool executed -> must be sanitized or flagged
        cleaned, was_intercepted, violations = engine.sanitize_turn(
            assistant_text=raw_text,
            tool_executed=None,
            tool_result=None,
            niche="clinic",
        )
        assert was_intercepted is True
        assert len(violations) > 0

    def test_unauthorized_legal_guarantee_scrubbing(self):
        filter_engine = ZeroLiabilityFilter(tenant_id="tenant_legal_test")
        guarantee_text = "I guarantee our firm will win your case and secure at least $500,000 for you."
        
        cleaned, has_violation, details = filter_engine.scrub_text(
            text=guarantee_text,
            niche="legal",
        )
        assert has_violation is True
        # Must replace unauthorized guarantee with compliant consultation disclaimer
        assert "legal team" in cleaned.lower() or "attorneys" in cleaned.lower() or "represent" in cleaned.lower()

    def test_grounded_tool_turn_passes_cleanly(self):
        engine = AntiHallucinationEngine(tenant_id="tenant_grounded")
        factual_text = "I checked our schedule and we have an opening tomorrow at 10:00 AM."
        
        cleaned, was_intercepted, violations = engine.sanitize_turn(
            assistant_text=factual_text,
            tool_executed="check_calendar_availability",
            tool_result={"status": "available", "slots": ["10:00 AM"]},
            niche="general",
        )
        assert was_intercepted is False
        assert len(violations) == 0


class TestDTMFTelephonyEdgeCases:
    """Stress tests DTMF touch-tone pulse validation and buffering."""

    def test_dtmf_validation_rules(self):
        assert validate_dtmf_sequence("1234#") is True
        assert validate_dtmf_sequence("*67,402#") is True
        assert validate_dtmf_sequence("1,2,3,ABCD") is True
        assert validate_dtmf_sequence("INVALID_XYZ") is False
        assert validate_dtmf_sequence("") is False

    @pytest.mark.asyncio
    async def test_dtmf_keypad_buffer_debounce_completion(self):
        completed_sequence = None

        def on_complete(seq):
            nonlocal completed_sequence
            completed_sequence = seq

        buffer = DTMFKeypadBuffer(on_sequence_completed=on_complete, debounce_seconds=0.1)
        buffer.add_digit("4")
        buffer.add_digit("0")
        buffer.add_digit("2")

        # Wait for debounce timer to fire
        await asyncio.sleep(0.15)
        assert completed_sequence == "402"
