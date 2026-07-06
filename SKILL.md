---
name: doc-architect
description: >-
  Plans, bootstraps, and maintains a project's core documentation set — README.md,
  AGENTS.md, and a modular docs/ set (project-overview.md, domain-models.md,
  coding-style.md, db-observation.md) — for any stack: Rails, Go, Node, Python,
  serverless, or other. Trigger this skill when: (1) the user is starting a NEW project
  and wants its documentation architecture planned — "新專案要建文件", "幫我規劃專案文件
  架構", "set up docs for a new project", "greenfield docs"; (2) an EXISTING codebase
  lacks docs and needs them written from the code — "這個專案沒有文件", "幫 X 建 docs",
  "generate project docs", "create documentation for this repo", "寫 AGENTS.md",
  "補 README"; (3) code changed and docs need a diff-driven sync — "更新 docs",
  "把這次改動同步到文件", "update docs for this branch"; (4) the user wants a drift
  audit of existing docs against the code — "檢查文件有沒有過時", "audit the docs";
  (5) the user invokes /doc-architect explicitly. Do NOT trigger for client-facing
  integration guides, API reference generation (OpenAPI/Postman), or changelogs.
---

# Doc Architect

Plan, bootstrap, and maintain the documentation a project needs for both **developers**
and **AI agents** to grasp its architecture, features, and models — everything one must
know before developing in it. Self-contained: all templates live in `references/`.

References:
- `references/readme-template.md` — human-first repo entry point
- `references/agents-md-template.md` — agent signpost file (routing, not content; ≤ ~60 lines)
- `references/project-overview-template.md` — 10-section skeleton + per-stack source map
- `references/domain-models-template.md` — 3 layout variants + ASCII ER diagram style
- `references/coding-style-template.md` — generate from the project's own linter config
- `references/db-observation-template.md` — DB observation how-to (DB-owning projects only)
- `references/audit-checklist.md` — diff→section mapping + verification invariants

---

## The doc set (modular)

| File | Tier | Generate when |
|---|---|---|
| `README.md` | **core** | always (existing one → fill gaps only, with approval) |
| `AGENTS.md` (+ `CLAUDE.md` symlink) | **core** | always; routing only — one-line identity, task→doc table, real commands, doc-maintenance rules |
| `docs/project-overview.md` | **core** | always; greenfield sections may read `TBD — not yet designed` |
| `docs/domain-models.md` (+ `docs/domain/` when large) | module | the project has a non-trivial data model or business mechanisms worth explaining |
| `docs/coding-style.md` | module | linter config or discernible conventions exist; else skip (or short factual stub on request) |
| `docs/db-observation.md` | module | the project owns a relational datastore |

**State the selection**: when presenting results, list which modules were generated and
which were skipped, with the one-line reason for each skip.

## Shared conventions (all modes)

- **Frontmatter** on every `docs/` file: `# <Project> — <Doc Name>` title, then a
  blockquote with `> **Type:**`, `> **Audience:**`, `> **Last updated:** YYYY-MM-DD`,
  then `---`. (README and AGENTS.md use their own templates' shapes.)
- **Bump `Last updated` only when a file's content actually changes** — an audit pass
  that changes nothing bumps nothing.
- Requirement keywords (**MUST/SHOULD/MAY**) follow RFC 2119, uppercase.
- Entity-relationship diagrams are ASCII in fenced code blocks — not mermaid.
- Links to code and sibling docs are relative paths.
- **Scope guard:** this skill touches ONLY the files it generates (README.md, AGENTS.md
  + symlinks, the canonical `docs/` files, `docs/domain/`). Never edit or delete anything
  else under `docs/` (scratch dirs, memos, pending notes…).
- **Verify, don't guess:** every claim written must be traceable to a file read in this
  session or a decision the user explicitly stated. Missing or contradictory source →
  ask the user; never fill gaps from memory of similar projects.

## Mode selection

- Project has no (or almost no) code yet → **Mode G** (greenfield).
- Code exists but the doc set doesn't → **Mode B** (brownfield bootstrap). Some docs
  already exist → **Mode B in merge mode**: create only what's missing, treat existing
  docs as source material and link to them — never overwrite or rename without approval.
- Doc set exists and needs maintenance → **Mode U** (U-1 with a diff/branch in hand;
  U-2 for an audit).

---

## Mode G — Greenfield (plan docs for a new project)

1. **Interview** (AskUserQuestion or conversational): purpose and the problem being
   solved; target users/callers; expected scale and team size; interface shape
   (API / CLI / web / worker); data characteristics; deployment preferences; the team's
   existing skills.
2. **Advise** on what the user has NOT yet decided: language/framework (2–3 candidates
   with trade-offs, recommendation marked), architecture shape (layered / modular
   monolith / serverless / …), datastore, initial directory layout, linter. Decisions
   the user already made are respected as-is — record, don't re-litigate.
3. **Record decisions with rationale**: chosen stack + why (and rejected alternatives,
   one line each) → `project-overview.md` §2; architecture shape + Key Principles → §3.
   Undecided sections get `TBD — not yet designed` — an honest fact, never silently
   filled in.
4. Generate `README.md` (skeleton + known info), `AGENTS.md`, `project-overview.md`
   (full 10-section structure, partly TBD).
5. Modules: `domain-models.md` only if a data-model draft exists (marked
   `planned — no schema yet`); skip `coding-style.md` until a linter is chosen; skip
   `db-observation.md` until a schema exists.
6. **Hand off**: list every TBD section and tell the user when to return for Mode U
   (e.g. "after the first models land, after CI is set up").

## Mode B — Brownfield bootstrap (write docs from the code)

1. **Detect the stack** from manifests: `Gemfile`→Rails, `go.mod`→Go,
   `package.json`→Node, `pyproject.toml`→Python, `serverless.yml`/`template.yaml`→
   Serverless. Unknown → fall back to README + entrypoint reading; say so in the output.
2. **Discovery reading**, in order (per-stack file map:
   `references/project-overview-template.md` §Per-stack source map): README → dependency
   manifest + lockfile → routes/entrypoints → schema + models → workers/jobs + schedule
   → external-integration clients + settings → env configs, Dockerfile, CI/CD.
3. **Select the doc set** (table above) and generate each file from its template:
   README → AGENTS.md → project-overview → selected modules.
4. **Merge mode** when docs partially exist: fill gaps, link to existing material,
   confirm any restructure with the user first.
5. **Self-check** with `references/audit-checklist.md` §2 before presenting the result.

## Mode U-1 — Diff-driven update

1. Determine the diff range: user-specified branch/range/PR, else
   `git diff <default-branch>...HEAD --name-only` (detect master vs main).
2. Map changed paths → affected doc sections via `references/audit-checklist.md` §1.
3. Read the changed source files, then rewrite **only the affected sections**. Bump
   `Last updated` only on files actually edited.
4. Report sections the diff didn't touch but that look semantically related (renamed
   classes, moved flows) — flag, don't silently rewrite.

## Mode U-2 — Full audit

1. Run `references/audit-checklist.md` §2 (machine-checkable invariants) and §3
   (semantic checks) over every file in the doc set.
2. **Default is report-first:** output the drift report (checklist §4 format) and change
   nothing until the user confirms — unless they asked to fix directly up front.
3. When fixing, follow Mode U-1 rules (targeted edits, honest dates).

---

## Quick reference

| Situation | Mode | Entry point |
|---|---|---|
| New project, little or no code | G | interview → advise → record decisions |
| Code exists, docs don't (or partially) | B (merge mode if partial) | stack detection → discovery reading |
| Just finished a feature branch | U-1 | `git diff <base>...HEAD --name-only` → mapping table |
| "Are the docs stale?" | U-2 | checklist → drift report → confirm → fix |
