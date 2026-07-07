# doc-architect

An agent skill that plans, bootstraps, and maintains a project's core documentation set
— `README.md`, `AGENTS.md`, and a modular `docs/` set — for any stack.

## What it does

- **Greenfield** — interviews you about a new project's purpose, scale, and team, advises
  on undecided choices (language, architecture, datastore), and records decisions with
  rationale into a full docs skeleton.
- **Brownfield** — reads an existing codebase (Rails, Go, Node, Python, serverless, or
  other), presents its plan (stack, doc set, skip reasons) for confirmation, then
  writes the documentation from the code one doc at a time with per-doc self-checks
  (WIP = 1); resumable across sessions on large repos; merge mode fills gaps when some
  docs already exist.
- **Update** — syncs docs to a feature-branch diff (the diff→section mapping is
  confirmed before editing), or audits the whole doc set for drift against the current
  code (report-first); audits execute safe read-only commands to prove documented
  commands actually work, and finish with a 5-question Fresh Session Test. A project
  with no runnable test gate gets an explicit warning (missing feedback loop) plus a
  stack-appropriate suggestion — and, when PROGRESS.md is selected, the gate is seeded
  as the feature list's first work item so iterating agents actually build it.

The generated doc set is modular:

| File | Tier |
|---|---|
| `README.md`, `AGENTS.md`, `docs/project-overview.md` | core — always generated |
| `docs/domain-models.md` (+ `docs/domain/`) | when the data model is non-trivial |
| `docs/coding-style.md` | when linter config or clear conventions exist |
| `docs/db-observation.md` | when the project owns a relational datastore |
| `PROGRESS.md` (agent-harness state, repo root) | when the project is actively developed by AI agents — opt-in |

## Install

Clone and symlink the skill (and optionally the dedicated agent) into place:

```bash
git clone https://github.com/FWcloud916/skill-doc-architect.git
ln -s "$(pwd)/skill-doc-architect" ~/.claude/skills/doc-architect
ln -s "$(pwd)/skill-doc-architect/agents/doc-architect.md" ~/.claude/agents/doc-architect.md
```

Any agent runtime that discovers `SKILL.md`-based skills (Claude Code, or others reading
the same layout) will pick the skill up. The agent definition preloads the skill via its
`skills:` frontmatter, so the skill symlink is a prerequisite for the agent symlink.

## Use

**As a skill** — invoke `/doc-architect` explicitly, or just ask in natural language:

- "set up docs for a new project" / "新專案要建文件" → greenfield
- "create documentation for this repo" / "這個專案沒有文件" → brownfield
- "update docs for this branch" / "把這次改動同步到文件" → diff-driven update
- "audit the docs" / "檢查文件有沒有過時" → drift audit

**As a dedicated agent** (requires the agent symlink):

- In any session, Claude Code can delegate brownfield bootstraps and doc updates/audits
  to the `doc-architect` subagent, which runs them autonomously and reports back files
  written, skipped modules, and open questions.
- Greenfield planning needs interaction (interview → advice → recorded decisions), so
  run it as the main session: `claude --agent doc-architect`.

## Project structure

```
doc-architect/
├── SKILL.md          # entry point: modes, doc-set selection, shared conventions
├── agents/           # dedicated agent definition (preloads the skill)
└── references/       # one template per generated file + the audit checklist
```

## Documentation

| Doc | What it covers |
|---|---|
| [SKILL.md](SKILL.md) | Mode selection (greenfield / brownfield / update), doc-set tiers, conventions |
| [references/readme-template.md](references/readme-template.md) | Human-first repo entry point |
| [references/agents-md-template.md](references/agents-md-template.md) | Agent signpost file (routing + hard constraints, ~100-line budget) |
| [references/project-overview-template.md](references/project-overview-template.md) | 10-section overview skeleton + per-stack source map |
| [references/domain-models-template.md](references/domain-models-template.md) | Data-model reference, 3 layout variants |
| [references/coding-style-template.md](references/coding-style-template.md) | Style guide generated from the project's own linter config |
| [references/db-observation-template.md](references/db-observation-template.md) | Query/index evidence how-to for DB-owning projects |
| [references/harness-template.md](references/harness-template.md) | PROGRESS.md state conventions + Mode-B resume state file |
| [references/audit-checklist.md](references/audit-checklist.md) | Diff→section mapping, invariants, executable command verification, Fresh Session Test |
