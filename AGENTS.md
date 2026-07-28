# doc-architect — Agent Guide

An agent skill that plans, bootstraps, and maintains a project's core documentation set
(README.md, AGENTS.md, modular docs/) for any stack. The skill itself lives in
`skills/doc-architect/` (SKILL.md + references/ + scripts/); the repo doubles as a
Claude Code plugin (`.claude-plugin/`) and marketplace for it, and as a native
Codex CLI plugin (`.codex-plugin/` + `.agents/plugins/` marketplace).

## Hard constraints

- MUST run `bash scripts/verify.sh` and see it pass before declaring any change done
  (source: this repo's verification gate)
- MUST NOT renumber `project-overview-template.md`'s 10 sections or
  `audit-checklist.md` §1–§6 — cross-references cite them by number
  (source: docs/design-decisions.md)
- MUST keep SAFE/NOT-SAFE command-safety rules centralized in
  `skills/doc-architect/references/audit-checklist.md` §5; stack files only restate and point back
  (source: docs/design-decisions.md)
- MUST spell canonical stack tokens identically everywhere: `Apple (iOS/macOS)`,
  `Windows desktop (.NET)`, `Electron`, `Tauri` (source: scripts/verify.sh token check)
- Adding a stack = create `skills/doc-architect/references/stacks/<stack>.md` with the
  5-section skeleton + one row in `skills/doc-architect/references/stacks/README.md` + `evals/fixtures/basic-<stack>/` and
  ≥1 `trap-*` fixture exercising its signal-table position; MUST NOT add per-stack
  rows back into SKILL.md or the templates (source: docs/design-decisions.md)
- Every detection bug that reaches the decision log MUST add a `trap-*` fixture
  with `regression_for` naming the log entry (source: evals/README.md)
- Changing a resolve rule or the report contract MUST update the affected
  `evals/fixtures/*/expected.json` (+ `grade.py` for vocabulary) in the same
  change — never loosen the grader to make a red suite pass (source: evals/README.md)
- Changing a mode's file scope, output contract, or merge/update behavior MUST update
  the affected `evals/scenarios/*/scenario.json` and grader tests in the same change
  (source: evals/README.md)
- MUST annotate `./gradlew` / `cargo build|test|clippy` / `dotnet build|test|format`
  as static-check-only (per §5) wherever they appear (source: scripts/verify.sh)
- MUST NOT label on-demand package runners (`npx`, `npm exec`, `pnpm dlx`, `yarn dlx`,
  `bunx`) SAFE; only confirmed local binaries may execute (source: audit-checklist §5)
- MUST NOT extract modes (G/B/U) out of SKILL.md into an index — they are fixed,
  tightly coupled control flow (source: docs/design-decisions.md, 2026-07-07)
- MUST edit `AGENTS.md`, never `CLAUDE.md` (symlink) (source: agents-md-template)
- User-visible skill changes MUST bump `version` in BOTH `.claude-plugin/plugin.json`
  and `.codex-plugin/plugin.json`, kept equal (verify.sh enforces) — plugin users on
  either runtime only receive updates on a version bump (source: plugins reference)

## Read before you work

Read the matching doc **before non-trivial work**. Small fixes (typos, single-line
edits) can skip; do not pre-load all docs.

| Task | Read first |
|---|---|
| Changing mode flow (G/B/U) or cross-stack logic | [SKILL.md](skills/doc-architect/SKILL.md) |
| Adding or updating a stack | [stacks/README.md](skills/doc-architect/references/stacks/README.md) + an existing stack file as skeleton example (e.g. [rails.md](skills/doc-architect/references/stacks/rails.md)) |
| Changing verification/audit behavior | [audit-checklist.md](skills/doc-architect/references/audit-checklist.md) |
| Changing detection rules or eval fixtures | [evals/README.md](evals/README.md) |
| Changing a generated doc's shape | the matching `skills/doc-architect/references/*-template.md` |
| Understanding why it's built this way | [docs/design-decisions.md](docs/design-decisions.md) |

## Commands

```bash
bash scripts/verify.sh              # consistency gate — the verification gate for "done"
./evals/scripts/run_detection.sh    # live detection sweep (Claude/Codex; costs runs)
./evals/scripts/run_scenarios.sh    # live end-to-end scenario sweep (costs runs)
skills/doc-architect/scripts/fresh_session_test.sh <repo> # independent Fresh Session Test (paid; checklist §6)
```

## Conventions

- Enhance over rewrite: extend existing tables/sections; restructure only when scale
  justifies it (precedent: the stacks/ index, docs/design-decisions.md).
- Requirement keywords (MUST/SHOULD/MAY) follow RFC 2119, uppercase.
- Changing SKILL.md or references → walk the six failure modes first
  (docs/design-decisions.md §Appendix, "SKILL.md change checklist").

## Docs maintenance

When modifying any file under `docs/`, update its `> **Last updated:** YYYY-MM-DD`
frontmatter to today's date.
