"""
Unit Tests for Phase 5: Deterministic Conversational Pathways & Node State Graph Engine.
Verifies Graph Validation, Rule Evaluation, Prompt Scoping, Multi-turn State Machine Progression,
and REST API Validation/Simulation Endpoints.
"""

import asyncio
import json
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from pipeline.pathways import (
    ConditionType,
    PathwayEdge,
    PathwayGraph,
    PathwayNode,
    PathwayNodeType,
    PathwaySessionRunner,
    PathwayStepResult,
    TransitionRule,
)


def asyncio_run(coro):
    return asyncio.run(coro)


class TestTransitionRuleEvaluation(unittest.TestCase):
    """Verifies deterministic conditional logic evaluation across all rule types."""

    def test_always_condition(self):
        rule = TransitionRule(condition_type=ConditionType.ALWAYS)
        self.assertTrue(rule.evaluate(user_utterance="anything", extracted_slots={}))

    def test_slot_present_condition(self):
        rule = TransitionRule(
            condition_type=ConditionType.SLOT_PRESENT,
            slot_name="pickup_location",
        )
        self.assertFalse(rule.evaluate(user_utterance="hi", extracted_slots={}))
        self.assertFalse(rule.evaluate(user_utterance="hi", extracted_slots={"pickup_location": ""}))
        self.assertTrue(rule.evaluate(user_utterance="hi", extracted_slots={"pickup_location": "JFK Airport"}))

    def test_intent_equals_condition(self):
        rule = TransitionRule(
            condition_type=ConditionType.INTENT_EQUALS,
            expected_intent="book_ride",
        )
        self.assertFalse(rule.evaluate(user_utterance="book ride", extracted_slots={}, detected_intent="cancel"))
        self.assertTrue(rule.evaluate(user_utterance="book ride", extracted_slots={}, detected_intent="BOOK_RIDE"))

    def test_regex_match_condition(self):
        rule = TransitionRule(
            condition_type=ConditionType.REGEX_MATCH,
            regex_pattern=r"\b(yes|yeah|sure|correct)\b",
        )
        self.assertTrue(rule.evaluate(user_utterance="Yes, that's right", extracted_slots={}))
        self.assertTrue(rule.evaluate(user_utterance="sure thing", extracted_slots={}))
        self.assertFalse(rule.evaluate(user_utterance="no, incorrect", extracted_slots={}))

    def test_tool_success_and_failure_conditions(self):
        success_rule = TransitionRule(condition_type=ConditionType.TOOL_SUCCESS)
        failure_rule = TransitionRule(condition_type=ConditionType.TOOL_FAILURE)

        self.assertFalse(success_rule.evaluate(user_utterance="", extracted_slots={}, tool_result=None))
        self.assertFalse(failure_rule.evaluate(user_utterance="", extracted_slots={}, tool_result=None))

        good_res = {"status": "ok", "booking_id": "BK-100"}
        bad_res = {"status": "failed", "error": "No tables available"}

        self.assertTrue(success_rule.evaluate(user_utterance="", extracted_slots={}, tool_result=good_res))
        self.assertFalse(failure_rule.evaluate(user_utterance="", extracted_slots={}, tool_result=good_res))

        self.assertFalse(success_rule.evaluate(user_utterance="", extracted_slots={}, tool_result=bad_res))
        self.assertTrue(failure_rule.evaluate(user_utterance="", extracted_slots={}, tool_result=bad_res))


class TestPathwayGraphValidationAndScoping(unittest.TestCase):
    """Verifies structural integrity validation and localized prompt scoping."""

    def _create_sample_graph(self) -> PathwayGraph:
        nodes = [
            PathwayNode(
                id="n_greeting",
                name="Welcome Greeting",
                node_type=PathwayNodeType.GREETING,
                prompt_template="Thank you for calling Alfie Luxury Transport! How can I assist you today?",
            ),
            PathwayNode(
                id="n_ask_pickup",
                name="Ask Pickup Location",
                node_type=PathwayNodeType.QUESTION,
                prompt_template="Where would you like us to pick you up?",
                required_slots=["pickup_location"],
            ),
            PathwayNode(
                id="n_ask_dropoff",
                name="Ask Dropoff Location",
                node_type=PathwayNodeType.QUESTION,
                prompt_template="Great, pickup at {pickup_location}. Where are you heading?",
                required_slots=["dropoff_location"],
            ),
            PathwayNode(
                id="n_book_ride",
                name="Execute Booking",
                node_type=PathwayNodeType.TOOL_EXECUTION,
                prompt_template="Booking your chauffeur now from {pickup_location} to {dropoff_location}.",
                tool_name="book_luxury_ride",
                tool_params={"pickup": "{pickup_location}", "dropoff": "{dropoff_location}"},
            ),
            PathwayNode(
                id="n_confirmation",
                name="Booking Confirmed",
                node_type=PathwayNodeType.END_CALL,
                prompt_template="Your booking is confirmed! Have a great ride.",
            ),
            PathwayNode(
                id="n_transfer",
                name="Transfer to Staff",
                node_type=PathwayNodeType.TRANSFER,
                prompt_template="Let me connect you to our concierge specialist immediately.",
                transfer_sip_uri="sip:staff@telephony.alfie.internal",
            ),
        ]

        edges = [
            PathwayEdge(
                source_node_id="n_greeting",
                target_node_id="n_ask_pickup",
                rule=TransitionRule(condition_type=ConditionType.ALWAYS),
            ),
            PathwayEdge(
                source_node_id="n_ask_pickup",
                target_node_id="n_ask_dropoff",
                rule=TransitionRule(
                    condition_type=ConditionType.SLOT_PRESENT,
                    slot_name="pickup_location",
                ),
            ),
            PathwayEdge(
                source_node_id="n_ask_dropoff",
                target_node_id="n_book_ride",
                rule=TransitionRule(
                    condition_type=ConditionType.SLOT_PRESENT,
                    slot_name="dropoff_location",
                ),
            ),
            PathwayEdge(
                source_node_id="n_book_ride",
                target_node_id="n_confirmation",
                rule=TransitionRule(condition_type=ConditionType.TOOL_SUCCESS),
            ),
            PathwayEdge(
                source_node_id="n_book_ride",
                target_node_id="n_transfer",
                rule=TransitionRule(condition_type=ConditionType.TOOL_FAILURE),
            ),
        ]

        return PathwayGraph(
            id="pathway_transport_demo",
            name="Luxury Transport Flow",
            start_node_id="n_greeting",
            nodes=nodes,
            edges=edges,
            global_instructions="You are an ultra-polite executive chauffeur assistant.",
        )

    def test_valid_graph_passes_validation(self):
        graph = self._create_sample_graph()
        errors = graph.validate()
        self.assertEqual(errors, [])

    def test_invalid_start_node_detected(self):
        graph = self._create_sample_graph()
        graph.start_node_id = "non_existent_node"
        errors = graph.validate()
        self.assertTrue(any("Start node 'non_existent_node' does not exist" in e for e in errors))

    def test_broken_edge_target_detected(self):
        graph = self._create_sample_graph()
        graph.edges_map["n_greeting"].append(
            PathwayEdge(
                source_node_id="n_greeting",
                target_node_id="ghost_node",
                rule=TransitionRule(condition_type=ConditionType.ALWAYS),
            )
        )
        errors = graph.validate()
        self.assertTrue(any("ghost_node" in e for e in errors))

    def test_unreachable_orphaned_node_detected(self):
        graph = self._create_sample_graph()
        orphan = PathwayNode(
            id="n_orphan",
            name="Orphan Node",
            node_type=PathwayNodeType.QUESTION,
            prompt_template="I am lost.",
        )
        graph.nodes_map[orphan.id] = orphan
        errors = graph.validate()
        self.assertTrue(any("Unreachable orphaned nodes" in e and "n_orphan" in e for e in errors))

    def test_missing_terminal_node_detected(self):
        graph = PathwayGraph(
            id="p_no_term",
            name="No Terminal",
            start_node_id="n_greet",
            nodes=[
                PathwayNode(
                    id="n_greet",
                    name="Greet",
                    node_type=PathwayNodeType.GREETING,
                    prompt_template="Hi",
                ),
            ],
            edges=[],
        )
        errors = graph.validate()
        self.assertTrue(any("no terminal nodes" in e for e in errors))

    def test_scoped_prompt_generation(self):
        graph = self._create_sample_graph()
        scoped = graph.get_scoped_prompt(
            node_id="n_ask_dropoff",
            accumulated_slots={"pickup_location": "The Ritz-Carlton"},
        )
        self.assertIn("The Ritz-Carlton", scoped)
        self.assertIn("[REQUIRED SLOTS TO EXTRACT]: You MUST capture: dropoff_location", scoped)
        self.assertIn("ultra-polite executive chauffeur", scoped)

    def test_graph_serialization_roundtrip(self):
        graph = self._create_sample_graph()
        data = graph.to_dict()
        reconstructed = PathwayGraph.from_dict(data)

        self.assertEqual(graph.id, reconstructed.id)
        self.assertEqual(graph.name, reconstructed.name)
        self.assertEqual(graph.start_node_id, reconstructed.start_node_id)
        self.assertEqual(len(graph.nodes_map), len(reconstructed.nodes_map))
        self.assertEqual(graph.validate(), reconstructed.validate())


class TestPathwaySessionRunner(unittest.TestCase):
    """Verifies end-to-end multi-turn runtime execution across pathway states."""

    def setUp(self):
        self.test_helper = TestPathwayGraphValidationAndScoping()
        self.graph = self.test_helper._create_sample_graph()

    def test_multi_turn_successful_intake_and_tool_execution(self):
        runner = PathwaySessionRunner(graph=self.graph)

        # Turn 1: Caller says "Hi I need a ride" (From greeting -> ask pickup)
        res1 = asyncio_run(runner.step(user_utterance="Hi, I need a luxury ride"))
        self.assertEqual(res1.current_node_id, "n_ask_pickup")
        self.assertIn("Where would you like us to pick you up?", res1.spoken_response)
        self.assertFalse(res1.should_end_call)

        # Turn 2: Caller provides pickup location
        res2 = asyncio_run(
            runner.step(
                user_utterance="Pick me up at JFK Terminal 4",
                detected_slots={"pickup_location": "JFK Terminal 4"},
            )
        )
        self.assertEqual(res2.current_node_id, "n_ask_dropoff")
        self.assertEqual(res2.extracted_slots["pickup_location"], "JFK Terminal 4")
        self.assertIn("JFK Terminal 4", res2.spoken_response)

        # Turn 3: Caller provides dropoff -> transitions to tool execution and then confirmation
        mock_tool_executed = []

        def mock_tool_fn(name, params):
            mock_tool_executed.append((name, params))
            return {"status": "success", "booking_id": "LUX-9988"}

        res3 = asyncio_run(
            runner.step(
                user_utterance="Dropping off at Hudson Yards",
                detected_slots={"dropoff_location": "Hudson Yards"},
                tool_executor=mock_tool_fn,
            )
        )
        # Should execute tool and route via TOOL_SUCCESS to confirmation (END_CALL)
        self.assertEqual(res3.current_node_id, "n_confirmation")
        self.assertTrue(res3.should_end_call)
        self.assertIn("Your booking is confirmed", res3.spoken_response)

        # Verify tool parameters were dynamically hydrated from slots
        self.assertEqual(len(mock_tool_executed), 1)
        self.assertEqual(mock_tool_executed[0][0], "book_luxury_ride")
        self.assertEqual(
            mock_tool_executed[0][1],
            {"pickup": "JFK Terminal 4", "dropoff": "Hudson Yards"},
        )

    def test_tool_failure_branches_to_staff_transfer(self):
        runner = PathwaySessionRunner(
            graph=self.graph,
            initial_slots={
                "pickup_location": "Times Square",
                "dropoff_location": "LaGuardia",
            },
        )
        runner.current_node_id = "n_ask_dropoff"

        def failing_tool_fn(name, params):
            return {"status": "failed", "error": "No chauffeurs available"}

        res = asyncio_run(
            runner.step(
                user_utterance="Proceed with booking",
                tool_executor=failing_tool_fn,
            )
        )
        # Should transition to transfer node on failure
        self.assertEqual(res.current_node_id, "n_transfer")
        self.assertTrue(res.should_transfer)
        self.assertEqual(res.transfer_sip_uri, "sip:staff@telephony.alfie.internal")
        self.assertIn("connect you to our concierge", res.spoken_response)


class TestPathwaysRESTEndpoints(unittest.TestCase):
    """Verifies REST endpoints for pathway validation and simulation."""

    def test_validate_endpoint_valid_and_invalid_payloads(self):
        from routes.client_routes import validate_pathway_graph, PathwayValidateRequest, PathwayNodePayload, PathwayEdgePayload, TransitionRulePayload

        valid_req = PathwayValidateRequest(
            start_node_id="start",
            nodes=[
                PathwayNodePayload(id="start", name="Start", node_type="greeting", prompt_template="Hello"),
                PathwayNodePayload(id="end", name="End", node_type="end_call", prompt_template="Bye"),
            ],
            edges=[
                PathwayEdgePayload(source_node_id="start", target_node_id="end", rule=TransitionRulePayload(condition_type="always")),
            ],
        )
        res_valid = asyncio_run(validate_pathway_graph(valid_req, current_user={"role": "client_admin", "sub": "t1"}))
        self.assertTrue(res_valid["valid"])
        self.assertEqual(res_valid["errors"], [])

        # Invalid (missing terminal)
        invalid_req = PathwayValidateRequest(
            start_node_id="start",
            nodes=[
                PathwayNodePayload(id="start", name="Start", node_type="greeting", prompt_template="Hello"),
            ],
            edges=[],
        )
        res_invalid = asyncio_run(validate_pathway_graph(invalid_req, current_user={"role": "client_admin", "sub": "t1"}))
        self.assertFalse(res_invalid["valid"])
        self.assertGreater(len(res_invalid["errors"]), 0)

    def test_simulate_endpoint_execution(self):
        from routes.client_routes import simulate_pathway_step, PathwaySimulateRequest

        sim_graph = {
            "id": "sim_graph",
            "name": "Sim Graph",
            "start_node_id": "q1",
            "nodes": [
                {"id": "q1", "name": "Ask Color", "node_type": "question", "prompt_template": "What is your favorite color?", "required_slots": ["color"]},
                {"id": "q2", "name": "End Step", "node_type": "end_call", "prompt_template": "Your color {color} is recorded."},
            ],
            "edges": [
                {
                    "source_node_id": "q1",
                    "target_node_id": "q2",
                    "rule": {"condition_type": "slot_present", "slot_name": "color"},
                }
            ],
        }

        req = PathwaySimulateRequest(
            graph=sim_graph,
            current_node_id="q1",
            user_utterance="My color is Emerald Blue",
            accumulated_slots={"color": "Emerald Blue"},
        )
        res = asyncio_run(simulate_pathway_step(req, current_user={"role": "client_admin", "sub": "t1"}))

        self.assertEqual(res["current_node_id"], "q2")
        self.assertTrue(res["should_end_call"])
        self.assertIn("Emerald Blue", res["spoken_response"])


if __name__ == "__main__":
    unittest.main()
