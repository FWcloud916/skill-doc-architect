#!/usr/bin/env python3
"""Unit tests for Fresh Session Test parsing and citation validation."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "validate_fresh_session", HERE / "validate_fresh_session.py"
)
fresh = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fresh)


class FreshSessionValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name)
        (self.repo / "README.md").write_text("# Sample\n")
        docs = self.repo / "docs"
        docs.mkdir()
        (docs / "project-overview.md").write_text("# Overview\n")
        self.report = {
            "answers": [
                {"q": 1, "question": fresh.QUESTIONS[0], "answer": "Sample.",
                 "citation": "README.md — first paragraph"},
                {"q": 2, "question": fresh.QUESTIONS[1], "answer": "One module.",
                 "citation": "docs/project-overview.md §3"},
                {"q": 3, "question": fresh.QUESTIONS[2], "answer": "See README.",
                 "citation": "README.md — Run"},
                {"q": 4, "question": fresh.QUESTIONS[3], "answer": "No gate yet.",
                 "citation": "README.md — Verify"},
                {"q": 5, "question": fresh.QUESTIONS[4],
                 "answer": "N/A — not agent-tracked (PROGRESS.md absent)",
                 "citation": "PROGRESS.md absent at repository root"},
            ]
        }

    def tearDown(self):
        self.temp.cleanup()

    def test_valid_report_passes(self):
        self.assertEqual([], fresh.validate_report(self.report, self.repo))

    def test_claude_envelope_unwraps(self):
        raw = json.dumps({"result": json.dumps(self.report), "is_error": False})
        self.assertEqual(self.report, fresh.parse_report(raw))

    def test_missing_question_fails(self):
        self.report["answers"].pop()
        self.assertTrue(fresh.validate_report(self.report, self.repo))

    def test_nonexistent_citation_fails(self):
        self.report["answers"][1]["citation"] = "docs/missing.md §3"
        errors = fresh.validate_report(self.report, self.repo)
        self.assertTrue(any("does not exist" in error for error in errors))

    def test_q5_absence_contract_fails_when_vague(self):
        self.report["answers"][4]["answer"] = "Nothing tracked."
        self.assertTrue(fresh.validate_report(self.report, self.repo))

    def test_q5_absence_contract_fails_when_citation_is_vague(self):
        self.report["answers"][4]["citation"] = "repository root listing"
        errors = fresh.validate_report(self.report, self.repo)
        self.assertTrue(any("absence citation" in error for error in errors))

    def test_q5_requires_real_progress_file_when_present(self):
        (self.repo / "PROGRESS.md").write_text("# Progress\n")
        self.report["answers"][4]["answer"] = "Work is active."
        self.report["answers"][4]["citation"] = "PROGRESS.md — Now"
        self.assertEqual([], fresh.validate_report(self.report, self.repo))

    def test_parent_traversal_citation_fails(self):
        self.report["answers"][0]["citation"] = "../README.md"
        self.assertTrue(fresh.validate_report(self.report, self.repo))

    def _q6_row(self):
        return {"q": 6, "question": fresh.QUESTIONS[5],
                "answer": "A Widget is the billable unit; avoid 'Gadget'.",
                "citation": "CONTEXT.md — Language"}

    def test_q6_required_when_context_present(self):
        (self.repo / "CONTEXT.md").write_text("# Sample — Context\n")
        errors = fresh.validate_report(self.report, self.repo)
        self.assertTrue(any("exactly 6" in error for error in errors))
        self.report["answers"].append(self._q6_row())
        self.assertEqual([], fresh.validate_report(self.report, self.repo))

    def test_q6_forbidden_when_context_absent(self):
        self.report["answers"].append(self._q6_row())
        errors = fresh.validate_report(self.report, self.repo)
        self.assertTrue(any("exactly 5" in error for error in errors))

    def test_q6_citation_must_name_context(self):
        (self.repo / "CONTEXT.md").write_text("# Sample — Context\n")
        row = self._q6_row()
        row["citation"] = "README.md — first paragraph"
        self.report["answers"].append(row)
        errors = fresh.validate_report(self.report, self.repo)
        self.assertTrue(any("q6" in error for error in errors))

    def test_q6_prose_mention_of_context_does_not_bypass(self):
        (self.repo / "CONTEXT.md").write_text("# Sample — Context\n")
        row = self._q6_row()
        row["citation"] = "README.md — see CONTEXT.md"
        self.report["answers"].append(row)
        errors = fresh.validate_report(self.report, self.repo)
        self.assertTrue(any("q6" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
