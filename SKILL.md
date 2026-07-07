---
name: doc-architect
description: >-
  Plans, bootstraps, and maintains a project's core documentation set — README.md,
  AGENTS.md, a modular docs/ set (project-overview.md, domain-models.md,
  coding-style.md, db-observation.md), and an opt-in PROGRESS.md agent-harness state
  file — for any stack: Rails, Go, Node, Python, serverless, or other. Trigger this skill when: (1) the user is starting a NEW project
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
- `references/agents-md-template.md` — agent signpost file (routing + hard constraints; ≤ ~100 lines)
- `references/project-overview-template.md` — 10-section skeleton + per-stack source map
- `references/domain-models-template.md` — 3 layout variants + ASCII ER diagram style
- `references/coding-style-template.md` — generate from the project's own linter config
- `references/db-observation-template.md` — DB observation how-to (DB-owning projects only)
- `references/harness-template.md` — agent-harness state: PROGRESS.md + Mode-B resume state file
- `references/audit-checklist.md` — diff→section mapping, verification invariants,
  executable command checks (§5), Fresh Session Test (§6)

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
| `PROGRESS.md` (repo root) | module | the project is actively developed by AI agents across sessions — **opt-in only** (offer in G, recommended default; offer in B when agent-driven development is stated or evident); selecting it brings the AGENTS.md Session routine with it |

**Plan before you write**: the doc-set selection (modules generated, modules skipped,
one-line reason for each skip) is a plan, not an afterthought. Interactive: present it
**before generating** and wait for confirmation (Mode B step 3, Mode U-1 step 3).
Headless: do not stall — execute the plan as made and record it in the final report.
Either way, restate the selection when presenting results.

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
  + symlinks, the canonical `docs/` files, `docs/domain/`, `PROGRESS.md` when the harness
  module was selected, `docs/.doc-architect-state.md` while Mode B is in flight). Never
  edit or delete anything else under `docs/` (scratch dirs, memos, pending notes…).
- **Feedback beats prose:** the commands that verify work (test, lint, run) are the
  highest-value lines in the doc set — they get executable verification (checklist §5),
  not just a grep. Never write a command you did not find in real config.
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
   (full 10-section structure, partly TBD). Offer `PROGRESS.md` (harness module — see
   doc-set table), seeding its Feature list / Next steps from the interview's task
   breakdown.
5. Modules: `domain-models.md` only if a data-model draft exists (marked
   `planned — no schema yet`); skip `coding-style.md` until a linter is chosen; skip
   `db-observation.md` until a schema exists.
6. **Hand off**: list every TBD section, tell the user when to return for Mode U
   (e.g. "after the first models land, after CI is set up"), and run the Mode-G
   Definition of Done (below), including the Fresh Session Test (checklist §6).

## Mode B — Brownfield bootstrap (write docs from the code)

1. **Detect the stack** from manifests: `Gemfile`→Rails, `go.mod`→Go,
   `package.json`→Node, `pyproject.toml`→Python, `serverless.yml`/`template.yaml`→
   Serverless. Unknown → fall back to README + entrypoint reading; say so in the output.
2. **Discovery reading**, in order (per-stack file map:
   `references/project-overview-template.md` §Per-stack source map): README → dependency
   manifest + lockfile → routes/entrypoints → schema + models → workers/jobs + schedule
   → external-integration clients + settings → env configs, Dockerfile, CI/CD.
3. **Present the plan** (sprint contract): the stack judgment, the selected doc set with
   a one-line skip reason per module, merge-mode handling if docs partially exist,
   whether `PROGRESS.md` is being offered, and the file scope still to be read.
   Interactive: wait for confirmation before writing anything. Headless: record the
   plan in the final report and proceed.
4. Generate **one doc at a time (WIP = 1)**, in order README → AGENTS.md →
   project-overview → selected modules: write a doc → self-verify it (checklist §2
   invariants for that file + §5 executable checks for any commands it states) → only
   then start the next. A doc counts as done when its self-check passes — more files
   written is not more progress.
5. **Merge mode** when docs partially exist: fill gaps, link to existing material,
   confirm any restructure with the user first.
6. **Large repo / interrupted run**: when the work won't fit one session, keep
   `docs/.doc-architect-state.md` (shape: `references/harness-template.md` §state file).
   On session start, if it exists, offer to resume from it. Delete it when Mode B
   completes — leaving it behind fails the clean-state check (checklist §2).
7. **Self-check** with checklist §2 + §5, then run the Fresh Session Test (§6) as the
   final gate before presenting the result.

## Mode U-1 — Diff-driven update

1. Determine the diff range: user-specified branch/range/PR, else
   `git diff <default-branch>...HEAD --name-only` (detect master vs main).
2. Map changed paths → affected doc sections via `references/audit-checklist.md` §1.
3. **Present the mapping**: the changed-paths → doc-sections table about to be
   rewritten. Interactive: wait for confirmation before editing. Headless: record the
   mapping in the final report and proceed.
4. Read the changed source files, then rewrite **only the affected sections**. Bump
   `Last updated` only on files actually edited.
5. Report sections the diff didn't touch but that look semantically related (renamed
   classes, moved flows) — flag, don't silently rewrite.

## Mode U-2 — Full audit

1. Run `references/audit-checklist.md` §2 (machine-checkable invariants), §5 (executable
   command checks — safe commands only), §3 (semantic checks), and §6 (Fresh Session
   Test) over every file in the doc set.
2. **Default is report-first:** output the drift report (checklist §4 format, ending
   with its Verification results block) and change nothing until the user confirms —
   unless they asked to fix directly up front. Running §5's safe read-only commands is
   observation, not a change.
3. When fixing, follow Mode U-1 rules (targeted edits, honest dates).

---

## Definition of Done (per mode)

"Docs written" is not done. A mode completes only when its checklist passes (executable
checks: checklist §5; Fresh Session Test: §6):

- **G** — core files + selected modules exist · every undecided section reads
  `TBD — not yet designed` · TBD list handed off with return triggers · Fresh Session
  Test passes (Q5 via PROGRESS.md if selected, else via the TBD hand-off).
- **B** — plan confirmed (interactive) or recorded in the report (headless) · every
  selected doc generated AND self-checked in WIP = 1 order · all stated commands
  §5-verified or flagged `unverifiable here` · Fresh Session Test passes on the new doc
  set · `docs/.doc-architect-state.md` deleted.
- **U-1** — mapping confirmed (interactive) or recorded in the report (headless) ·
  every mapped section re-verified against the read source · `Last updated` bumped only
  on files actually edited · related-but-untouched sections reported.
- **U-2** — §2 + §5 + §3 + §6 all run · report in §4 format ends with a Verification
  results block · no file changed without user confirmation.

## Quick reference

| Situation | Mode | Entry point |
|---|---|---|
| New project, little or no code | G | interview → advise → record decisions |
| Code exists, docs don't (or partially) | B (merge mode if partial) | stack detection → discovery reading |
| Just finished a feature branch | U-1 | `git diff <base>...HEAD --name-only` → mapping table |
| "Are the docs stale?" | U-2 | checklist → drift report → confirm → fix |
