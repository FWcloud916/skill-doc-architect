#!/usr/bin/env python3
"""Render the shared detection-eval prompt for CLI and CI runners."""

import argparse
from pathlib import Path


PROMPT_TEMPLATE = '''Use the doc-architect skill, but perform ONLY Mode B step 1
(stack detection) on the repository at __FIXTURE_PATH__. Read the current checkout
skill at __SKILL_PATH__ and follow its references/stacks/README.md two-phase
collect-then-resolve procedure and Package role table exactly. Treat
__FIXTURE_PATH__ as the repository root: every evidence/package path is relative to
that directory, so its root package manifest is exactly "package.json". Do NOT
generate or modify any documentation.

Output ONLY a JSON object (no prose, no markdown fences) with this shape:
{
  "resolution": "single" | "hybrid" | "ambiguous" | "monorepo" | "unknown",
  "surfaces": [
    {"stack": "<stack file basename without .md>",
     "role": "primary" | "surface" | "candidate",
     "evidence": ["<repo-relative path that triggered this>"]}
  ],
  "package_json": [
    {"path": "<repo-relative package.json path>",
     "roles": ["server" | "ui-framework" | "build-tooling" | "desktop" | "extension" | "workspace" | "plain-node" | "frontend-entrypoint"]}
  ],
  "notes": "<one line, optional>"
}

Rules for the report:
- "surfaces" is empty for resolution=unknown.
- role=primary for the main stack of a single-rooted repo (single/hybrid; in a
  hybrid the backend is the one primary). surface for additional hybrid surfaces
  and for EVERY monorepo sub-project (a monorepo report has no primary).
  candidate for ambiguous alternatives.
- Every surface needs at least one evidence entry naming a real repo-relative file.
  Put dependency/key details in notes, not in evidence.
- package_json has one entry per package.json and is empty when none. roles includes
  every matching role in this order: server, ui-framework, build-tooling, desktop,
  extension, workspace, plain-node, frontend-entrypoint. Multiple roles are valid.'''


def render_prompt(fixture_path, skill_path):
    fixture = str(Path(fixture_path).resolve())
    skill = str(Path(skill_path).resolve())
    return PROMPT_TEMPLATE.replace("__FIXTURE_PATH__", fixture).replace(
        "__SKILL_PATH__", skill
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture_path")
    parser.add_argument("skill_path")
    args = parser.parse_args()
    print(render_prompt(args.fixture_path, args.skill_path))


if __name__ == "__main__":
    main()
