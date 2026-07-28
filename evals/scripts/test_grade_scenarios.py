#!/usr/bin/env python3
"""Regression tests for end-to-end scenario grading boundaries."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("grade_scenarios", HERE / "grade_scenarios.py")
grade = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(grade)


class ScenarioRunTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.run = self.root / "run-1"
        self.repo = self.run / "repo"
        self.repo.mkdir(parents=True)
        (self.repo / "source.txt").write_text("source\n")
        (self.run / "before.json").write_text(json.dumps(grade.snapshot(self.repo)))
        (self.run / "final.txt").write_text("## Verification\n\nTBD\n")
        self.expected = {
            "mode": "B",
            "request": "Write docs.",
            "allowed_changes": ["README.md", "docs/**"],
            "required_changes": ["README.md"],
            "required_paths": ["README.md"],
            "forbidden_paths": ["PROGRESS.md"],
            "unchanged_paths": ["source.txt"],
            "required_contains": {"README.md": ["Project"]},
            "forbidden_contains": {"README.md": ["npm test"]},
            "canonical_docs": [],
            "validate_relative_links": True,
            "final_required_sections": ["Verification"],
            "final_required_contains": ["TBD"],
        }

    def tearDown(self):
        self.temp.cleanup()

    def failures(self):
        return [name for name, ok, _ in grade.grade_run(self.run, self.root, self.expected)
                if not ok]

    def write_valid_readme(self):
        (self.repo / "README.md").write_text("# Project\n\nSee [source](source.txt).\n")

    def test_valid_run_passes(self):
        self.write_valid_readme()
        self.assertEqual([], self.failures())

    def test_out_of_scope_change_fails(self):
        self.write_valid_readme()
        (self.repo / "source.txt").write_text("changed\n")
        self.assertIn("allowed_change_scope", self.failures())
        self.assertIn("unchanged_path:source.txt", self.failures())

    def test_known_tool_cache_is_ignored(self):
        self.write_valid_readme()
        cache = self.repo / ".ruff_cache"
        cache.mkdir()
        (cache / "cache-entry").write_text("generated\n")
        self.assertEqual([], self.failures())

    def test_missing_required_change_fails(self):
        self.assertIn("required_change:README.md", self.failures())

    def test_broken_relative_link_fails(self):
        (self.repo / "README.md").write_text("# Project\n\n[missing](nope.md)\n")
        self.assertIn("relative_links:README.md", self.failures())

    def test_forbidden_content_fails(self):
        (self.repo / "README.md").write_text("# Project\n\nnpm test\n")
        self.assertIn("forbidden_contains:README.md:npm test", self.failures())

    def test_required_alternation_passes_on_any_variant(self):
        (self.repo / "README.md").write_text(
            "# Project\n\nMUST NOT be squashed.\n\nSee [source](source.txt).\n"
        )
        self.expected["required_contains"]["README.md"] = [
            "Project", ["MUST NOT squash", "MUST NOT be squashed"]
        ]
        self.assertEqual([], self.failures())

    def test_required_alternation_fails_when_no_variant_present(self):
        self.write_valid_readme()
        self.expected["required_contains"]["README.md"] = [
            "Project", ["MUST NOT squash", "MUST NOT be squashed"]
        ]
        self.assertIn(
            "required_contains:README.md:MUST NOT squash | MUST NOT be squashed",
            self.failures(),
        )

    def test_forbidden_alternation_fails_when_any_variant_present(self):
        (self.repo / "README.md").write_text(
            "# Project\n\nSquash merges are fine.\n\nSee [source](source.txt).\n"
        )
        self.expected["forbidden_contains"]["README.md"] = [
            ["Squash merges are fine", "squash and merge"]
        ]
        self.assertIn(
            "forbidden_contains:README.md:Squash merges are fine | squash and merge",
            self.failures(),
        )

    def test_empty_alternation_is_an_invalid_contract(self):
        errors = grade.validate_scenario_definition(
            self.root, {**self.expected, "required_contains": {"README.md": [[]]}}
        )
        self.assertTrue(any("required_contains" in error for error in errors))

    def test_missing_final_report_fails(self):
        self.write_valid_readme()
        (self.run / "final.txt").write_text("")
        self.assertIn("final_report_present", self.failures())

    def test_final_required_sections_are_case_insensitive(self):
        self.write_valid_readme()
        self.expected["final_required_sections"] = ["VERIFICATION"]
        self.assertEqual([], self.failures())

    def test_descriptive_heading_preserves_canonical_section(self):
        self.write_valid_readme()
        (self.run / "final.txt").write_text("## Verification results\n\nTBD\n")
        self.assertEqual([], self.failures())

    def test_section_word_in_prose_does_not_pass(self):
        self.write_valid_readme()
        (self.run / "final.txt").write_text("Verification completed.\n\nTBD\n")
        self.assertIn("final_section:Verification", self.failures())

    def test_section_substring_inside_another_heading_word_does_not_pass(self):
        self.write_valid_readme()
        self.expected["final_required_sections"] = ["Plan"]
        (self.run / "final.txt").write_text("## Explanation\n\nTBD\n")
        self.assertIn("final_section:Plan", self.failures())

    def test_missing_final_required_content_fails(self):
        self.write_valid_readme()
        (self.run / "final.txt").write_text("## Verification\n")
        self.assertIn("final_contains:TBD", self.failures())


class FrontmatterTests(unittest.TestCase):
    def test_valid_frontmatter(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "doc.md"
            path.write_text(
                "# Project — Overview\n\n> **Type:** Explanation\n"
                "> **Audience:** Developers\n> **Last updated:** 2026-07-14\n\n---\n"
            )
            self.assertTrue(grade.canonical_frontmatter_ok(path))

    def test_future_date_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "doc.md"
            path.write_text(
                "# Project — Overview\n\n> **Type:** Explanation\n"
                "> **Audience:** Developers\n> **Last updated:** 2999-01-01\n\n---\n"
            )
            self.assertFalse(grade.canonical_frontmatter_ok(path))


class DeliveryPolicyScenarioTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.run = self.root / "run-1"
        self.repo = self.run / "repo"
        (self.repo / "src").mkdir(parents=True)
        (self.repo / "README.md").write_text("# Relay service\n")
        (self.repo / "CONTRIBUTING.md").write_text("No-PR policy\n")
        (self.repo / "package.json").write_text("{}\n")
        (self.repo / "src/server.js").write_text("// source\n")
        (self.run / "before.json").write_text(json.dumps(grade.snapshot(self.repo)))
        (self.repo / "docs").mkdir()
        (self.repo / "docs/project-overview.md").write_text(
            "# Relay — Project Overview\n\n> **Type:** Explanation\n"
            "> **Audience:** Developers\n> **Last updated:** 2026-07-15\n\n---\n"
        )
        self.valid_policy = (
            "# Relay — Agent Guide\n\n"
            "task/<short-name>\n"
            "git merge --no-ff <branch>\n"
            "MUST NOT squash\n"
            "source branch\n"
            "verification result\n"
        )
        (self.repo / "AGENTS.md").write_text(self.valid_policy)
        (self.run / "final.txt").write_text(
            "## Plan\n\n## Verification\n\n## Fresh Session Test\n"
        )
        scenario = HERE.parent / "scenarios/delivery-policy-no-pr/scenario.json"
        self.expected = json.loads(scenario.read_text())

    def tearDown(self):
        self.temp.cleanup()

    def failures(self):
        return [name for name, ok, _ in grade.grade_run(self.run, self.root, self.expected)
                if not ok]

    def test_valid_no_pr_policy_passes(self):
        self.assertEqual([], self.failures())

    def test_invented_pr_requirement_fails(self):
        (self.repo / "AGENTS.md").write_text(self.valid_policy + "MUST open a PR\n")
        self.assertIn("forbidden_contains:AGENTS.md:MUST open a PR", self.failures())


class SuiteCompletenessTests(unittest.TestCase):
    def make_run(self, root, done=True):
        run = root / "merge-preserves-existing" / "run-1"
        (run / "repo").mkdir(parents=True)
        (run / "before.json").write_text("{}")
        (run / "final.txt").write_text("report")
        if done:
            (run / "done").write_text("")

    def test_missing_manifest_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertTrue(grade.validate_suite(Path(temp))[1])

    def test_missing_done_marker_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "manifest.json").write_text(json.dumps({
                "runs_per_scenario": 1,
                "selected_scenarios": ["merge-preserves-existing"],
            }))
            self.make_run(root, done=False)
            errors = grade.validate_suite(root)[1]
            self.assertTrue(any("missing done" in error for error in errors))

    def test_complete_suite_shape_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "manifest.json").write_text(json.dumps({
                "runs_per_scenario": 1,
                "selected_scenarios": ["merge-preserves-existing"],
            }))
            self.make_run(root)
            self.assertEqual([], grade.validate_suite(root)[1])


if __name__ == "__main__":
    unittest.main()
