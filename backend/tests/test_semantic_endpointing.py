"""
Unit & Integration Tests for Phase 18: Semantic Turn Endpointing & Anti-Interruption Intelligence.
"""

import unittest
from unittest.mock import AsyncMock, MagicMock

from semantic_endpointing import (
    PACING_PRESETS,
    EndpointDecision,
    SemanticEndpointAnalyzer,
)
from migrations import migration_013_semantic_turn_endpointing


class TestSemanticEndpointAnalyzer(unittest.TestCase):
    """Unit tests for the SemanticEndpointAnalyzer logic and presets."""

    def setUp(self):
        self.analyzer_natural = SemanticEndpointAnalyzer(preset="natural")
        self.analyzer_patient = SemanticEndpointAnalyzer(preset="patient")
        self.analyzer_fast = SemanticEndpointAnalyzer(preset="fast")

    def test_empty_and_whitespace_input(self):
        decision = self.analyzer_natural.analyze_text("")
        self.assertFalse(decision.is_incomplete)
        self.assertFalse(decision.is_conclusive)
        self.assertAlmostEqual(decision.silence_threshold_seconds, 0.55)

        decision_ws = self.analyzer_natural.analyze_text("   \n\t  ")
        self.assertFalse(decision_ws.is_incomplete)
        self.assertAlmostEqual(decision_ws.silence_threshold_seconds, 0.55)

    def test_terminal_question_mark(self):
        decision = self.analyzer_natural.analyze_text("Can you tell me your office hours?")
        self.assertTrue(decision.is_conclusive)
        self.assertFalse(decision.is_incomplete)
        self.assertEqual(decision.reason, "terminal_question")
        self.assertEqual(decision.matched_token, "?")
        self.assertAlmostEqual(decision.silence_threshold_seconds, 0.38)

    def test_conclusive_short_answers(self):
        phrases = ["yes", "yeah", "nope", "that's all", "that is all", "thank you", "perfect", "goodbye"]
        for phrase in phrases:
            decision = self.analyzer_natural.analyze_text(phrase)
            self.assertTrue(decision.is_conclusive, f"Failed for phrase: {phrase}")
            self.assertFalse(decision.is_incomplete)
            self.assertEqual(decision.reason, "conclusive_short_answer")
            self.assertAlmostEqual(decision.silence_threshold_seconds, 0.38)

    def test_terminal_punctuation_sentences(self):
        decision = self.analyzer_natural.analyze_text("I need to speak to an attorney about my case.")
        self.assertTrue(decision.is_conclusive)
        self.assertEqual(decision.reason, "terminal_punctuation")
        self.assertAlmostEqual(decision.silence_threshold_seconds, 0.38)

    def test_trailing_hesitation_words(self):
        hesitation_samples = [
            ("I was involved in an accident, um", "um"),
            ("Let me see what happened uh", "uh"),
            ("The policy number is er", "er"),
            ("I think it was on Tuesday hmm", "hmm"),
        ]
        for utterance, expected_token in hesitation_samples:
            decision = self.analyzer_natural.analyze_text(utterance)
            self.assertTrue(decision.is_incomplete, f"Failed for: {utterance}")
            self.assertFalse(decision.is_conclusive)
            self.assertEqual(decision.reason, "hesitation_word")
            self.assertEqual(decision.matched_token, expected_token)
            self.assertAlmostEqual(decision.silence_threshold_seconds, 1.25)

    def test_trailing_hesitation_phrases(self):
        decision = self.analyzer_natural.analyze_text("The other car was turning left, you know")
        self.assertTrue(decision.is_incomplete)
        self.assertEqual(decision.reason, "hesitation_phrase")
        self.assertEqual(decision.matched_token, "you know")
        self.assertAlmostEqual(decision.silence_threshold_seconds, 1.25)

        decision2 = self.analyzer_natural.analyze_text("I need to look at my schedule, let me see")
        self.assertTrue(decision2.is_incomplete)
        self.assertEqual(decision2.reason, "hesitation_phrase")
        self.assertEqual(decision2.matched_token, "let me see")

    def test_trailing_conjunctions(self):
        conjunction_samples = [
            ("I was driving southbound on the highway and", "and"),
            ("We can meet either at your office or", "or"),
            ("I wanted to call sooner but", "but"),
            ("I was feeling dizzy because", "because"),
            ("I am not sure if", "if"),
        ]
        for utterance, expected_token in conjunction_samples:
            decision = self.analyzer_natural.analyze_text(utterance)
            self.assertTrue(decision.is_incomplete, f"Failed for: {utterance}")
            self.assertFalse(decision.is_conclusive)
            self.assertEqual(decision.reason, "trailing_conjunction")
            self.assertEqual(decision.matched_token, expected_token)
            self.assertAlmostEqual(decision.silence_threshold_seconds, 1.25)

    def test_trailing_prepositions(self):
        preposition_samples = [
            ("I need to book a ride for", "for"),
            ("My mother was admitted into", "into"),
            ("I would like to speak with", "with"),
            ("Can you tell me more about", "about"),
        ]
        for utterance, expected_token in preposition_samples:
            decision = self.analyzer_natural.analyze_text(utterance)
            self.assertTrue(decision.is_incomplete, f"Failed for: {utterance}")
            self.assertEqual(decision.reason, "trailing_preposition")
            self.assertEqual(decision.matched_token, expected_token)
            self.assertAlmostEqual(decision.silence_threshold_seconds, 1.25)

    def test_trailing_number_sequences(self):
        decision = self.analyzer_natural.analyze_text("My contact number is 312 555 019")
        self.assertTrue(decision.is_incomplete)
        self.assertEqual(decision.reason, "trailing_number_sequence")
        self.assertAlmostEqual(decision.silence_threshold_seconds, 1.25)

        decision_word_num = self.analyzer_natural.analyze_text("We need a reservation for seven")
        self.assertTrue(decision_word_num.is_incomplete)
        self.assertEqual(decision_word_num.reason, "trailing_number_sequence")

    def test_pacing_presets(self):
        # Patient preset (Elderly/Medical/Legal)
        patient_hesitate = self.analyzer_patient.analyze_text("I was walking down the stairs and")
        self.assertAlmostEqual(patient_hesitate.silence_threshold_seconds, 1.75)
        patient_quick = self.analyzer_patient.analyze_text("yes")
        self.assertAlmostEqual(patient_quick.silence_threshold_seconds, 0.48)
        patient_base = self.analyzer_patient.analyze_text("I arrived yesterday afternoon")
        self.assertAlmostEqual(patient_base.silence_threshold_seconds, 0.75)

        # Fast preset (Dispatch/Logistics)
        fast_hesitate = self.analyzer_fast.analyze_text("I need an Escalade or")
        self.assertAlmostEqual(fast_hesitate.silence_threshold_seconds, 0.85)
        fast_quick = self.analyzer_fast.analyze_text("yes")
        self.assertAlmostEqual(fast_quick.silence_threshold_seconds, 0.28)
        fast_base = self.analyzer_fast.analyze_text("Airport pickup at 6 PM")
        self.assertAlmostEqual(fast_base.silence_threshold_seconds, 0.38)

    def test_invalid_preset_fallback(self):
        analyzer = SemanticEndpointAnalyzer(preset="non_existent_preset")
        self.assertEqual(analyzer.preset_name, "natural")
        self.assertAlmostEqual(analyzer.base_silence, 0.55)

    def test_custom_pacing_overrides(self):
        custom = {"base_silence": 0.60, "extended_silence": 2.00, "quick_silence": 0.30}
        analyzer = SemanticEndpointAnalyzer(preset="natural", custom_pacing=custom)
        self.assertAlmostEqual(analyzer.base_silence, 0.60)
        self.assertAlmostEqual(analyzer.extended_silence, 2.00)
        self.assertAlmostEqual(analyzer.quick_silence, 0.30)

        decision = analyzer.analyze_text("I have a meeting at")
        self.assertAlmostEqual(decision.silence_threshold_seconds, 2.00)


class TestVADDynamicAdaptation(unittest.TestCase):
    """Integration tests for VAD option updates during streaming transcript turns."""

    def test_mock_vad_update_stream(self):
        analyzer = SemanticEndpointAnalyzer(preset="natural")

        # Mock silero.VAD object
        mock_vad = MagicMock()
        current_silence = 0.55

        def mock_update_options(*, min_silence_duration=None, **kwargs):
            nonlocal current_silence
            if min_silence_duration is not None:
                current_silence = min_silence_duration

        mock_vad.update_options.side_effect = mock_update_options

        # Step 1: Caller begins speaking neutral clause
        delta1 = "I am calling about a hit and run accident"
        decision1 = analyzer.analyze_text(delta1)
        mock_vad.update_options(min_silence_duration=decision1.silence_threshold_seconds)
        self.assertAlmostEqual(current_silence, 0.55)

        # Step 2: Caller hesitates mid-sentence ("and...")
        delta2 = "I am calling about a hit and run accident and"
        decision2 = analyzer.analyze_text(delta2)
        mock_vad.update_options(min_silence_duration=decision2.silence_threshold_seconds)
        self.assertAlmostEqual(current_silence, 1.25)

        # Step 3: Caller completes sentence ("...the driver fled.")
        delta3 = "I am calling about a hit and run accident and the driver fled."
        decision3 = analyzer.analyze_text(delta3)
        mock_vad.update_options(min_silence_duration=decision3.silence_threshold_seconds)
        self.assertAlmostEqual(current_silence, 0.38)

        # Step 4: Turn committed -> Reset to base silence
        mock_vad.update_options(min_silence_duration=analyzer.base_silence)
        self.assertAlmostEqual(current_silence, 0.55)


class TestMigration013(unittest.IsolatedAsyncioTestCase):
    """Test Database Migration 013 (Endpointing Preset & Anti-Interruption Columns)."""

    async def test_migration_013_execution(self):
        mock_conn = AsyncMock()
        await migration_013_semantic_turn_endpointing(mock_conn)
        mock_conn.execute.assert_called_once()
        sql = mock_conn.execute.call_args[0][0]
        self.assertIn("endpointing_preset", sql)
        self.assertIn("anti_interruption_enabled", sql)
        self.assertIn("alfie_tenant_agents", sql)


if __name__ == "__main__":
    unittest.main()
