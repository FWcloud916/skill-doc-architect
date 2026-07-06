# doc-architect

An agent skill that plans, bootstraps, and maintains a project's core documentation set
— `README.md`, `AGENTS.md`, and a modular `docs/` set — for any stack.

## What it does

- **Greenfield** — interviews you about a new project's purpose, scale, and team, advises
  on undecided choices (language, architecture, datastore), and records decisions with
  rationale into a full docs skeleton.
- **Brownfield** — reads an existing codebase (Rails, Go, Node, Python, serverless, or
  other) and writes its documentation from the code; merge mode fills gaps when some
  docs already exist.
- **Update** — syncs docs to a feature-branch diff, or audits the whole doc set for
  drift against the current code (report-first).

The generated doc set is modular:

| File | Tier |
|---|---|
| `README.md`, `AGENTS.md`, `docs/project-overview.md` | core — always generated |
| `docs/domain-models.md` (+ `docs/domain/`) | when the data model is non-trivial |
| `docs/coding-style.md` | when linter config or clear conventions exist |
| `docs/db-observation.md` | when the project owns a relational datastore |

## Install

Clone and symlink into your agent's skills directory:

```bash
git clone https://github.com/FWcloud916/skill-doc-architect.git
ln -s "$(pwd)/skill-doc-architect" ~/.claude/skills/doc-architect
```

Any agent runtime that discovers `SKILL.md`-based skills (Claude Code, or others reading
the same layout) will pick it up.

## Use

Invoke `/doc-architect` explicitly, or just ask in natural language:

- "set up docs for a new project" / "新專案要建文件" → greenfield
- "create documentation for this repo" / "這個專案沒有文件" → brownfield
- "update docs for this branch" / "把這次改動同步到文件" → diff-driven update
- "audit the docs" / "檢查文件有沒有過時" → drift audit

## Project structure

```
doc-architect/
├── SKILL.md          # entry point: modes, doc-set selection, shared conventions
└── references/       # one template per generated file + the audit checklist
```

## Documentation

| Doc | What it covers |
|---|---|
| [SKILL.md](SKILL.md) | Mode selection (greenfield / brownfield / update), doc-set tiers, conventions |
| [references/readme-template.md](references/readme-template.md) | Human-first repo entry point |
| [references/agents-md-template.md](references/agents-md-template.md) | Agent signpost file (routing only, ~60-line budget) |
| [references/project-overview-template.md](references/project-overview-template.md) | 10-section overview skeleton + per-stack source map |
| [references/domain-models-template.md](references/domain-models-template.md) | Data-model reference, 3 layout variants |
| [references/coding-style-template.md](references/coding-style-template.md) | Style guide generated from the project's own linter config |
| [references/db-observation-template.md](references/db-observation-template.md) | Query/index evidence how-to for DB-owning projects |
| [references/audit-checklist.md](references/audit-checklist.md) | Diff→section mapping + machine-checkable invariants |
