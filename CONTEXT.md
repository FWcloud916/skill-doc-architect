# doc-architect — Context

Agent skill that plans, bootstraps, and maintains a project's core documentation set,
plus the plugin/marketplace packaging and eval suite around it.

## Language

**Mode** — one of the four fixed control flows the skill runs: G (greenfield
interview), B (brownfield bootstrap), U-1 (diff-driven update), U-2 (full audit).
Modes stay inline in [SKILL.md](skills/doc-architect/SKILL.md); they are never
extracted to an index.

**Doc set** — the modular output a mode produces: core files (README.md, AGENTS.md,
project-overview) plus selected modules.
_Avoid_: doc suite (proposed — pending ruling)

**Tier** — a doc-set table column: `core` is always generated, `module` only when its
generate-when rule matches (some modules additionally opt-in).

**Module** — an opt-in or conditional doc-set member: domain-models, coding-style,
db-observation, `DESIGN.md`, `PROGRESS.md`, `CONTEXT.md`.

**Merge mode** — Mode B on a repo where docs partially exist: create only what's
missing, link existing material, never overwrite or rename without approval.

**Sprint contract** — Mode B's plan → confirm/record → execute framing: the step-3
plan is presented (or recorded when headless) and the Definition of Done checks it
was honored.

**Fresh Session Test** — the independent end-to-end gate (audit-checklist §6): a
fresh-context agent answers the §6 questions from the repository alone, citations
validated by `scripts/fresh_session_test.sh`.
_Avoid_: FST (proposed — pending ruling)

**Headless** — a run with no user available: never pauses, executes the plan as made,
records it in the final report, and leaves term rulings `proposed — pending ruling`.
Opposite: **interactive**, which waits for confirmation at each gate.

**Trap fixture** — a detection eval fixture (`evals/fixtures/trap-*`) that pins a
specific mis-detection; regression traps name their decision-log entry via
`regression_for`.

## Relationships

- A Mode selects a Doc set; each member's Tier decides whether it is generated.
- The Fresh Session Test gates Modes G and B in the Definition of Done, and is part
  of every U-2 audit.
- Merge mode is a Mode B behavior, not a separate mode.
- Trap fixtures pin the resolve rules that Mode B's detection step routes through.

## Flagged ambiguities

- "context module" vs "glossary module": both appear in the 2026-07-28
  decision-log entry; proposed ruling — the module is the **context module**
  (matches SKILL.md's doc-set table); "glossary" stays descriptive prose only.
