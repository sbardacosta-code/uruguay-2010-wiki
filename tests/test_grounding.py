"""Regression checks for ambiguous questions and rejection of unsupported drafts."""

import json
import unittest
from unittest.mock import patch

import wiki
from grounding import clarification_needed, review_support
from local_model import LocalModel


class GroundingTests(unittest.TestCase):
    def test_unresolved_match_does_not_retrieve_or_call_model(self):
        with patch(
            "wiki.search", side_effect=AssertionError("Must clarify first")
        ), patch.object(
            LocalModel, "chat", side_effect=AssertionError("Must not guess")
        ), patch(
            "wiki.save_record", return_value="test"
        ):
            result = wiki.ask("What did Abreu do in that match?", wiki.load_config())
        self.assertEqual(result["status"], "needs_clarification")
        self.assertIn("name the match", result["answer"])

    def test_explicit_questions_are_not_blocked(self):
        for question in [
            "What did Abreu do against Ghana?",
            "Who did Uruguay play after the quarter-finals, and where did they finish?",
            "How was Uruguay vs Ghana decided?",
        ]:
            self.assertIsNone(clarification_needed(question))

    def test_factual_pronoun_routes_to_clarification_but_drafting_keeps_history(self):
        self.assertTrue(wiki.needs_notes("What did he do in that match?"))
        self.assertFalse(wiki.needs_notes("Make that shorter"))
        self.assertFalse(
            wiki.needs_notes("Draft an imaginary story about their adventures")
        )

    def test_review_requires_every_claim_once_and_explicit_true_verdicts(self):
        answer = {
            "claims": [
                {
                    "text": "Uruguay won.",
                    "evidence": [{"passage": "P1", "quote": "Uruguay won"}],
                }
            ]
        }
        passages = [{"section": "Match", "text": "Uruguay won"}]
        for checks in [
            [],
            [{"claim": 1, "supported": False, "relevant": True}],
            [{"claim": 1, "supported": True, "relevant": False}],
            [{"claim": 2, "supported": True, "relevant": True}],
            [{"claim": 1, "supported": "true", "relevant": True}],
        ]:
            with self.subTest(checks=checks), patch.object(
                LocalModel, "chat", return_value=(json.dumps({"checks": checks}), {})
            ):
                self.assertFalse(
                    review_support("Who won?", answer, passages, wiki.load_config())[
                        "accepted"
                    ]
                )

    def test_rejected_support_never_displays_generated_claim(self):
        passage = {
            "id": "S1",
            "section": "Final standings",
            "path": "source.txt",
            "text": "Uruguay finished fourth.",
        }
        draft = {
            "status": "answered",
            "claims": [
                {
                    "text": "Uruguay won the tournament.",
                    "evidence": [
                        {"passage": "P1", "quote": "Uruguay finished fourth."}
                    ],
                }
            ],
            "reason": "",
        }
        with patch("wiki.search", return_value=[passage]), patch.object(
            LocalModel, "chat", return_value=(json.dumps(draft), {})
        ), patch(
            "wiki.review_support", return_value={"accepted": False, "checks": []}
        ), patch(
            "wiki.save_record", return_value="test"
        ):
            result = wiki.ask("Where did Uruguay finish?", wiki.load_config())
        self.assertEqual(result["status"], "insufficient_evidence")
        self.assertNotIn("won the tournament", result["answer"])
        self.assertEqual(result["suppressed_claims"], draft["claims"])

    def test_uncited_reason_does_not_bypass_claim_checks(self):
        result = wiki.validate_answer(
            {
                "status": "answered",
                "claims": [
                    {
                        "text": "Uruguay finished fourth.",
                        "evidence": [
                            {"passage": "P1", "quote": "Uruguay finished fourth."}
                        ],
                    }
                ],
                "reason": "Their hotel password was INVENTED.",
            },
            [{"id": "S1", "text": "Uruguay finished fourth."}],
        )
        self.assertNotIn("INVENTED", result)


if __name__ == "__main__":
    unittest.main()
