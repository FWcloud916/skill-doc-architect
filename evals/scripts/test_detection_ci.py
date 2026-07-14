#!/usr/bin/env python3
"""Regression tests for shared detection prompt and CI orchestration helpers."""

import importlib.util
import json
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ci = load_module("detection_ci")
prompt = load_module("detection_prompt")


class DetectionPromptTests(unittest.TestCase):
    def test_prompt_anchors_paths_to_fixture_root(self):
        fixture = REPO / "evals/fixtures/basic-rails"
        skill = REPO / "skills/doc-architect/SKILL.md"
        rendered = prompt.render_prompt(fixture, skill)
        self.assertIn(str(fixture.resolve()), rendered)
        self.assertIn(str(skill.resolve()), rendered)
        self.assertIn('root package manifest is exactly "package.json"', rendered)
        self.assertNotIn("__FIXTURE_PATH__", rendered)


class DetectionCiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        for name in ("basic-a", "basic-b", "trap-a"):
            (self.root / name).mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def test_filter_and_matrix_expand_every_run(self):
        selected = ci.select_fixtures(self.root, "basic-")
        matrix = ci.build_matrix(selected, 2)
        self.assertEqual(["basic-a", "basic-b"], selected)
        self.assertEqual(
            [
                {"fixture": "basic-a", "run": 1},
                {"fixture": "basic-a", "run": 2},
                {"fixture": "basic-b", "run": 1},
                {"fixture": "basic-b", "run": 2},
            ],
            matrix["include"],
        )

    def test_empty_filter_match_fails(self):
        with self.assertRaises(ValueError):
            ci.select_fixtures(self.root, "missing")

    def test_matrix_limit_fails_before_github_rejects_workflow(self):
        with self.assertRaisesRegex(ValueError, "GitHub Actions limit"):
            ci.build_matrix(["fixture"] * 129, 2)

    def test_selected_provider_requires_its_model(self):
        with self.assertRaisesRegex(ValueError, "anthropic_model"):
            ci.validate_request("anthropic", " ", "", "medium")
        with self.assertRaisesRegex(ValueError, "openai_model"):
            ci.validate_request("openai", "", " ", "medium")
        ci.validate_request("both", "claude-model", "gpt-model", "medium")

    def test_manifest_records_provider_model_and_effort(self):
        data = ci.manifest_data(["basic-a"], 3, "openai", "gpt-model", "medium")
        self.assertEqual("openai", data["provider"])
        self.assertEqual("gpt-model", data["model"])
        self.assertEqual("medium", data["effort"])

    def test_github_output_is_single_line_json(self):
        output = self.root / "github-output"
        selected = ["basic-a"]
        ci.write_github_output(output, ci.build_matrix(selected, 1), selected)
        lines = output.read_text().splitlines()
        self.assertEqual(2, len(lines))
        self.assertEqual(
            {"include": [{"fixture": "basic-a", "run": 1}]},
            json.loads(lines[0].split("=", 1)[1]),
        )


class WorkflowContractTests(unittest.TestCase):
    def test_openai_action_keeps_key_out_of_shell_environment(self):
        workflow = (REPO / ".github/workflows/detection-evals.yml").read_text()
        for needle in (
            "provider:",
            "anthropic_model:",
            "openai_model:",
            "openai_effort:",
            "openai/codex-action@v1",
            "openai-api-key: ${{ secrets.OPENAI_API_KEY }}",
            'permission-profile: ":read-only"',
            "working-directory:",
            "output-schema-file:",
        ):
            self.assertIn(needle, workflow)
        self.assertIn('default: "gpt-5.6-luna"', workflow)
        self.assertNotIn("sandbox: read-only", workflow)
        self.assertNotIn("--ignore-user-config", workflow)
        self.assertIsNone(re.search(r"(?m)^\s+OPENAI_API_KEY\s*:", workflow))


class LocalRunnerIntegrationTests(unittest.TestCase):
    def test_codex_runner_records_model_and_grades_fake_structured_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fake_bin = root / "bin"
            fake_bin.mkdir()
            log = root / "codex-args.log"
            executable = fake_bin / "codex"
            executable.write_text(
                """#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' "$@" > "$FAKE_CODEX_LOG"
out=''
while [[ "$#" -gt 0 ]]; do
  if [[ "$1" = "--output-last-message" ]]; then
    out="$2"
    shift 2
  else
    shift
  fi
done
printf '%s\n' '{"resolution":"single","surfaces":[{"stack":"rails","role":"primary","evidence":["Gemfile"]}],"package_json":[],"notes":""}' > "$out"
"""
            )
            executable.chmod(0o755)
            results = root / "results"
            env = os.environ.copy()
            env.update({
                "PATH": f"{fake_bin}:{env['PATH']}",
                "EVAL_CLI": "codex",
                "MODEL": "gpt-test",
                "FAKE_CODEX_LOG": str(log),
            })
            completed = subprocess.run(
                [
                    str(REPO / "evals/scripts/run_detection.sh"),
                    str(results),
                    "1",
                    "basic-rails",
                ],
                cwd=REPO,
                env=env,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
            manifest = json.loads((results / "manifest.json").read_text())
            self.assertEqual("openai", manifest["provider"])
            self.assertEqual("gpt-test", manifest["model"])
            self.assertEqual("cli-default", manifest["effort"])
            args = log.read_text().splitlines()
            self.assertIn("--ephemeral", args)
            self.assertIn("--output-schema", args)
            self.assertIn("--model", args)
            self.assertIn("gpt-test", args)


if __name__ == "__main__":
    unittest.main()
