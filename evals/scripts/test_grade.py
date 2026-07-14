#!/usr/bin/env python3
"""Deterministic regression tests for grade.py's false-green boundaries."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("grade", HERE / "grade.py")
grade = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(grade)


class GradeRunTests(unittest.TestCase):
    def setUp(self):
        self.fixture = grade.FIXTURES / "basic-rails"
        self.expected = {
            "resolution": "single",
            "surfaces": [{"stack": "rails", "role": "primary"}],
        }
        self.valid = {
            "resolution": "single",
            "surfaces": [{"stack": "rails", "role": "primary", "evidence": ["Gemfile"]}],
            "package_json": [],
            "notes": "",
        }

    def failures(self, report):
        return [name for name, passed, _ in grade.grade_run(report, self.expected, self.fixture)
                if not passed]

    def test_valid_report_passes(self):
        self.assertEqual([], self.failures(self.valid))

    def test_missing_evidence_fails(self):
        report = json.loads(json.dumps(self.valid))
        report["surfaces"][0]["evidence"] = []
        self.assertIn("surface_0_evidence_paths", self.failures(report))

    def test_nonexistent_evidence_fails(self):
        report = json.loads(json.dumps(self.valid))
        report["surfaces"][0]["evidence"] = ["not-real"]
        self.assertIn("surface_0_evidence_paths", self.failures(report))

    def test_parent_traversal_evidence_fails(self):
        report = json.loads(json.dumps(self.valid))
        report["surfaces"][0]["evidence"] = ["../basic-go/go.mod"]
        self.assertIn("surface_0_evidence_paths", self.failures(report))

    def test_extra_report_field_fails(self):
        report = json.loads(json.dumps(self.valid))
        report["unexpected"] = True
        self.assertIn("exact_report_keys", self.failures(report))

    def test_package_role_order_is_enforced(self):
        fixture = grade.FIXTURES / "basic-frontend-web"
        expected = {
            "resolution": "single",
            "surfaces": [{"stack": "frontend-web", "role": "primary"}],
            "package_json": [
                {"path": "package.json", "roles": ["ui-framework", "build-tooling"]}
            ],
        }
        report = {
            "resolution": "single",
            "surfaces": [
                {"stack": "frontend-web", "role": "primary", "evidence": ["package.json"]}
            ],
            "package_json": [
                {"path": "package.json", "roles": ["build-tooling", "ui-framework"]}
            ],
            "notes": "",
        }
        failures = [name for name, passed, _ in grade.grade_run(
            report, expected, fixture) if not passed]
        self.assertIn("package_json_entries", failures)
        self.assertIn("package_0_roles", failures)

    def test_wrong_ambiguous_roles_fail(self):
        expected = {
            "resolution": "ambiguous",
            "surfaces": [
                {"stack": "rails", "role": "candidate"},
                {"stack": "go", "role": "candidate"},
            ],
        }
        report = {
            "resolution": "ambiguous",
            "surfaces": [
                {"stack": "rails", "role": "surface", "evidence": ["Gemfile"]},
                {"stack": "go", "role": "surface", "evidence": ["go.mod"]},
            ],
            "package_json": [],
            "notes": "",
        }
        failures = [name for name, passed, _ in grade.grade_run(
            report, expected, grade.FIXTURES / "trap-two-backends") if not passed]
        self.assertIn("surface_stack_roles", failures)
        self.assertIn("resolution_role_invariant", failures)


class SuiteCompletenessTests(unittest.TestCase):
    def validate(self, manifest=None, fixture_dirs=(), run_files=()):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            if manifest is not None:
                (root / "manifest.json").write_text(json.dumps(manifest))
            for fixture in fixture_dirs:
                (root / fixture).mkdir()
            for fixture, filename in run_files:
                (root / fixture / filename).write_text("{}")
            return grade.validate_suite(root)[1]

    def test_empty_results_fail(self):
        self.assertTrue(self.validate())

    def test_zero_selected_fixtures_fail(self):
        errors = self.validate({"runs_per_fixture": 1, "selected_fixtures": []})
        self.assertTrue(errors)

    def test_missing_run_fails(self):
        errors = self.validate(
            {"runs_per_fixture": 2, "selected_fixtures": ["basic-rails"]},
            fixture_dirs=["basic-rails"],
            run_files=[("basic-rails", "run-1.json")],
        )
        self.assertTrue(any("run files mismatch" in error for error in errors))

    def test_complete_suite_shape_passes(self):
        errors = self.validate(
            {"runs_per_fixture": 1, "selected_fixtures": ["basic-rails"]},
            fixture_dirs=["basic-rails"],
            run_files=[("basic-rails", "run-1.json")],
        )
        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
