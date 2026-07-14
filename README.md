# doc-architect

An agent skill that plans, bootstraps, and maintains a project's core documentation set
— `README.md`, `AGENTS.md`, and a modular `docs/` set — for any stack.

## What it does

- **Greenfield** — interviews you about a new project's purpose, scale, and team, advises
  on undecided choices (language, architecture, datastore), and records decisions with
  rationale into a full docs skeleton.
- **Brownfield** — reads an existing codebase (Rails, Go, Node backend, Python, Rust,
  Serverless, Frontend web, React Native, Apple (iOS/macOS), Android, Flutter,
  Electron, Tauri, Windows desktop (.NET), VS Code extension, or other), presents its
  plan (stack, doc set, skip reasons) for confirmation, then
  writes the documentation from the code one doc at a time with per-doc self-checks
  (WIP = 1); resumable across sessions on large repos; merge mode fills gaps when some
  docs already exist.
- **Update** — syncs docs to a feature-branch diff (the diff→section mapping is
  confirmed before editing), or audits the whole doc set for drift against the current
  code (report-first).
- **Verification, not vibes** — every mode proves documented commands by executing
  safe read-only checks and ends with a 5-question Fresh Session Test. A project with
  no runnable test gate gets an explicit warning (missing feedback loop) plus a
  stack-appropriate suggestion — and, when `PROGRESS.md` is selected, the gate is
  seeded as the feature list's first work item, so agents iterating on the project
  actually build the test boundary and every later "done" is verified against it.

The generated doc set is modular:

| File | Tier |
|---|---|
| `README.md`, `AGENTS.md`, `docs/project-overview.md` | core — always generated |
| `docs/domain-models.md` (+ `docs/domain/`) | when the data model is non-trivial |
| `docs/coding-style.md` | when linter config or clear conventions exist |
| `docs/db-observation.md` | when the project owns a server-side relational datastore |
| `DESIGN.md` (UI design system, repo root) | when the project renders a UI — opt-in; Stitch-compatible design tokens + prose |
| `PROGRESS.md` (agent-harness state, repo root) | when the project is actively developed by AI agents — opt-in |

## Install

### Option 1 — Claude Code plugin (recommended for Claude Code)

The repo is a Claude Code plugin marketplace; installing the plugin gives you the
skill **and** the dedicated `doc-architect` agent in one step, with version-pinned
updates:

```
/plugin marketplace add FWcloud916/skill-doc-architect
/plugin install doc-architect@doc-architect
```

### Option 2 — skills CLI (any of 70+ agents)

[vercel-labs/skills](https://github.com/vercel-labs/skills) installs the skill for
the agent(s) you pick (Claude Code, Cursor, Codex, and more), creating any missing
directories along the way:

```bash
npx skills add FWcloud916/skill-doc-architect                      # interactive: pick agents + scope
npx skills add FWcloud916/skill-doc-architect -g -a claude-code -y # non-interactive, global
```

This route installs the skill only. To also use the dedicated Claude Code agent, add
the agent symlink from Option 3's last step.

### Option 3 — manual clone + symlink

Pick the layout your runtime reads — `~/.claude/skills` for Claude Code, or the
universal `~/.agents/skills` for runtimes that share it. `mkdir -p` covers the case
where the target directory doesn't exist yet:

```bash
git clone https://github.com/FWcloud916/skill-doc-architect.git

# Claude Code layout
mkdir -p ~/.claude/skills
ln -s "$(pwd)/skill-doc-architect/skills/doc-architect" ~/.claude/skills/doc-architect

# or: universal agents layout
mkdir -p ~/.agents/skills
ln -s "$(pwd)/skill-doc-architect/skills/doc-architect" ~/.agents/skills/doc-architect

# optional: dedicated Claude Code agent (requires the skill symlink above)
mkdir -p ~/.claude/agents
ln -s "$(pwd)/skill-doc-architect/agents/doc-architect.md" ~/.claude/agents/doc-architect.md
```

The agent definition preloads the skill via its `skills:` frontmatter, so the skill
symlink is a prerequisite for the agent symlink.

> **Migrating from an older install?** The skill used to live at the repo root;
> symlinks pointing at the clone itself no longer resolve to a skill. Re-link to
> `<clone>/skills/doc-architect` as shown above.

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

## Develop

Working on the skill itself? Read [AGENTS.md](AGENTS.md) first, then verify any change:

```bash
bash scripts/verify.sh   # consistency gate — must pass before a change is done
```

## Project structure

```
doc-architect/
├── .claude-plugin/   # plugin.json + marketplace.json — Claude Code plugin packaging
├── skills/
│   └── doc-architect/
│       ├── SKILL.md      # entry point: modes, doc-set selection, shared conventions
│       ├── references/   # one template per generated file + the audit checklist
│       │   └── stacks/   # detection index (README.md) + one file per stack
│       └── scripts/      # fresh_session_test.sh — independent Fresh Session Test
├── agents/           # dedicated agent definition (preloads the skill)
├── AGENTS.md         # maintainer guide for this repo (CLAUDE.md is a symlink to it)
├── docs/             # design-decisions.md — why the skill is built this way
├── scripts/          # verify.sh — consistency gate for changes to this repo
└── evals/            # detection eval fixtures + graders
```

## Documentation

| Doc | What it covers |
|---|---|
| [SKILL.md](skills/doc-architect/SKILL.md) | Mode selection (greenfield / brownfield / update), doc-set tiers, conventions |
| [AGENTS.md](AGENTS.md) | Maintainer guide: hard constraints, task→doc routing, the verify gate |
| [docs/design-decisions.md](docs/design-decisions.md) | Decision log with rationale: index-pattern boundary, detection gate, safety rules |
| [readme-template.md](skills/doc-architect/references/readme-template.md) | Human-first repo entry point |
| [agents-md-template.md](skills/doc-architect/references/agents-md-template.md) | Agent signpost file (routing + hard constraints, ~100-line budget) |
| [project-overview-template.md](skills/doc-architect/references/project-overview-template.md) | 10-section overview skeleton + per-stack source map |
| [domain-models-template.md](skills/doc-architect/references/domain-models-template.md) | Data-model reference, 3 layout variants |
| [coding-style-template.md](skills/doc-architect/references/coding-style-template.md) | Style guide generated from the project's own linter config |
| [db-observation-template.md](skills/doc-architect/references/db-observation-template.md) | Query/index evidence how-to for DB-owning projects |
| [harness-template.md](skills/doc-architect/references/harness-template.md) | PROGRESS.md state conventions + Mode-B resume state file |
| [design-template.md](skills/doc-architect/references/design-template.md) | DESIGN.md UI design system: YAML design tokens + prose, per-stack extraction map |
| [audit-checklist.md](skills/doc-architect/references/audit-checklist.md) | Diff→section mapping, invariants, executable command verification, Fresh Session Test |
| skills/doc-architect/references/stacks/ | Per-stack references: detection signal, discovery map, diff→section map, linter signals, minimal test gate |
