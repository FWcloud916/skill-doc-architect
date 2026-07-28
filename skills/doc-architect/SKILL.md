---
name: doc-architect
description: >-
  Plans, bootstraps, audits, and maintains a project's complete documentation
  architecture: README.md, AGENTS.md, canonical docs/, optional PROGRESS.md, and
  optional DESIGN.md. Use for greenfield documentation planning; brownfield repos
  that lack core docs; requests to write README or AGENTS; full-set diff-driven sync;
  full documentation drift audits; or /doc-architect (e.g. "新專案要建文件",
  "這個專案沒有文件", "更新 docs", "檢查文件有沒有過時"). This broader skill owns
  doc-set selection, stack discovery, merge preservation, and Fresh Session validation
  across stacks. If an established repo only needs its existing canonical docs/ files
  generated, synchronized, or audited, prefer project-docs when available. Do not use
  for client-facing integration guides, API/OpenAPI/Postman reference generation,
  endpoint descriptions, or changelogs.
---

# Doc Architect

Plan, bootstrap, and maintain the documentation a project needs for both **developers**
and **AI agents** to grasp its architecture, features, and models — everything one must
know before developing in it. Self-contained: all templates live in `references/`.

References:
- `references/readme-template.md` — human-first repo entry point
- `references/agents-md-template.md` — agent signpost file (routing + hard constraints; ≤ ~100 lines)
- `references/project-overview-template.md` — 10-section skeleton + per-section guidance
- `references/stacks/` — detection index (README.md) + one file per stack
- `references/domain-models-template.md` — 3 layout variants + ASCII ER diagram style
- `references/coding-style-template.md` — generate from the project's own linter config
- `references/db-observation-template.md` — DB observation how-to (DB-owning projects only)
- `references/harness-template.md` — agent-harness state: PROGRESS.md + Mode-B resume state file
- `references/design-template.md` — UI design-system doc (opt-in): tokens, extraction map, design interview
- `references/audit-checklist.md` — diff→section mapping, invariants, command checks (§5), Fresh Session Test (§6)

---

## The doc set (modular)

| File | Tier | Generate when |
|---|---|---|
| `README.md` | **core** | always (existing one → fill gaps only, with approval) |
| `AGENTS.md` (+ `CLAUDE.md` symlink) | **core** | always; routing only — one-line identity, task→doc table, real commands, doc-maintenance rules |
| `docs/project-overview.md` | **core** | always; greenfield sections may read `TBD — not yet designed` |
| `docs/domain-models.md` (+ `docs/domain/` when large) | module | the project has a non-trivial data model or business mechanisms worth explaining |
| `docs/coding-style.md` | module | linter config or discernible conventions exist; else skip (or short factual stub on request) |
| `docs/db-observation.md` | module | the project owns a server-side relational datastore (a client-embedded store — SQLite/Core Data/Room — doesn't qualify; record it in project-overview §9) |
| `DESIGN.md` (repo root) | module | the project owns a styled visual surface (stack metadata says `inherent`, or `conditional` discovery finds evidence) — **opt-in only**; Mode B extracts tokens from theme sources (`design-template.md` §Extraction map), gaps stay honest `TODO` |
| `PROGRESS.md` (repo root) | module | the project is actively developed by AI agents across sessions — **opt-in only** (offer in G, recommended default; offer in B when agent-driven development is stated or evident); selecting it brings the AGENTS.md Session routine with it |

**Plan before you write**: the doc-set selection (modules generated, modules skipped,
one-line reason for each skip) is a plan, not an afterthought. Interactive: present it
**before generating** and wait for confirmation (Mode B step 3, Mode U-1 step 3).
Headless: execute the plan as made and record it in the final report. Either way,
restate the selection when presenting results.

## Shared conventions (all modes)

- **Frontmatter** on every `docs/` file: `# <Project> — <Doc Name>` title, then a
  blockquote with `> **Type:**`, `> **Audience:**`, `> **Last updated:** YYYY-MM-DD`,
  then `---`. (README and AGENTS.md use their own templates' shapes.)
- **Bump `Last updated` only on real content change** — a no-op audit pass bumps nothing.
- Requirement keywords (**MUST/SHOULD/MAY**) follow RFC 2119, uppercase.
- Entity-relationship diagrams are ASCII in fenced code blocks — not mermaid.
- Links to code and sibling docs are relative paths.
- **Scope guard:** this skill touches ONLY the files it generates (README.md, AGENTS.md
  + symlinks, the canonical `docs/` files, `docs/domain/`, `PROGRESS.md` when the
  harness module was selected, `DESIGN.md` when the design module was selected,
  `docs/.doc-architect-state.md` while Mode B is in flight). Never edit or delete
  anything else under `docs/` (scratch dirs, memos, pending notes…).
- **Feedback beats prose:** the commands that verify work (test, lint, run) are the
  highest-value lines in the doc set — they get executable verification (checklist §5),
  not just a grep. Never write a command you did not find in real config.
- **Verify, don't guess:** every claim written must be traceable to a file read in this
  session or a decision the user explicitly stated. Missing or contradictory source →
  ask the user; never fill gaps from memory of similar projects.
- **Delivery policy:** when generating `AGENTS.md`, prefer existing policy evidence,
  then explicit user choice; headless with neither leaves it unselected. Read the
  template's §Delivery policy variants — evidence or the user decides, never a guess.
- **Headless report headings:** each canonical label gets its own Markdown heading
  (prefixes/suffixes MAY clarify it; the label itself stays intact): G — `Plan`,
  `Verification`, `Fresh Session Test`, `Hand-off`; B — `Plan`, `Verification`,
  `Fresh Session Test`; U-1 — `Mapping`, `Verification`; U-2 — `Verification results`.

## Mode selection

| Situation | Mode | Entry point |
|---|---|---|
| New project, little or no code | **G** | interview → advise → record decisions |
| Code exists, docs don't | **B** | stack detection (stacks index) → discovery reading |
| Some docs already exist | **B (merge mode)** | create only what's missing; existing docs are source material — link to them, never overwrite/rename without approval |
| Just finished a feature branch | **U-1** | `git diff <base>...HEAD --name-only` → mapping table |
| "Are the docs stale?" | **U-2** | checklist → drift report → confirm → fix |

---

## Mode G — Greenfield (plan docs for a new project)

1. **Interview** (AskUserQuestion or conversational): purpose/problem; target users;
   scale/team size; interface (API / CLI / web / worker); data; deployment; team skills;
   delivery policy (PR/MR, no-PR merge commit, or trunk).
2. **Advise** on what the user has NOT yet decided: language/framework (2–3 candidates
   with trade-offs, recommendation marked), architecture shape (layered / modular
   monolith / serverless / …), datastore, initial directory layout, linter. Decisions
   the user already made are respected as-is — record, don't re-litigate.
3. **Record decisions with rationale**: chosen stack + why (and rejected alternatives,
   one line each) → `project-overview.md` §2; architecture shape + Key Principles → §3.
   Undecided sections get `TBD — not yet designed` — never silently filled in.
4. Generate `README.md` (skeleton + known info), `AGENTS.md`, `project-overview.md`
   (full 10-section structure, partly TBD). Offer `PROGRESS.md` (harness module),
   seeding its Feature list / Next steps from the interview's task breakdown. When a
   UI is planned, also offer `DESIGN.md` (design module): interview the design
   direction (`references/design-template.md` §Mode G design interview).
5. Modules: `domain-models.md` only if a data-model draft exists (marked
   `planned — no schema yet`); skip `coding-style.md` until a linter is chosen; skip
   `db-observation.md` until a schema exists.
6. **Hand off and report** under headings containing the canonical G labels above:
   list every TBD section with its Mode-U return trigger (e.g. "after the first
   models land"), then run the Mode-G Definition of Done (below), including the Fresh
   Session Test (checklist §6).

## Mode B — Brownfield bootstrap (write docs from the code)

1. **Detect the stack** — two-phase, per the detection index
   (`references/stacks/README.md`): **collect** every manifest signal present, then
   **resolve** by the index's signal table and package-role rules — the desktop checks
   MUST precede the frontend check. Hybrid / monorepo / ambiguous → the step-3 gate;
   no match → unknown stack (README + entrypoint reading, say so). Read every
   documented surface's stack file before discovery reading.
2. **Discovery reading**, in order (per-stack sources + facet notes: the stack file's
   §Discovery map): README → dependency manifest + lockfile → interface surface →
   data → background work → external-integration clients + settings → env configs,
   Dockerfile, CI/CD, policy docs + branch-protection evidence,
   packaging/signing/release config; design-surface evidence.
3. **Present the plan** (sprint contract): the stack judgment **with its detection
   evidence** (which manifest, which deps matched) so the user can correct it; the
   selected doc set with a one-line skip reason per module; merge-mode handling and
   delivery-policy judgment; whether `PROGRESS.md` and `DESIGN.md` are offered
   (design-surface rule: detection index notes; selected → `design-template.md`
   §Extraction map); and the file scope still to be read. Hybrid / ambiguous /
   monorepo resolve here per the detection index's step-3 gate rule. Then follow
   **Plan before you write** (above).
4. Generate **one doc at a time (WIP = 1)**, in order README → AGENTS.md →
   project-overview → selected modules: write a doc → self-verify it (checklist §2
   invariants + §5 checks for any commands it states) → only then start the next. A
   doc counts as done when its self-check passes — more files written is not more
   progress.
5. **Merge mode** when docs partially exist: fill gaps, link to existing material,
   confirm any restructure with the user first.
6. **Large repo / interrupted run**: work that won't fit one session keeps
   `docs/.doc-architect-state.md` (`references/harness-template.md` §state file);
   offer to resume from it on session start; delete it when Mode B completes —
   leaving it behind fails the §2 clean-state check.
7. **Self-check** with checklist §2 + §5, then run the Fresh Session Test (§6) as the
   final gate. Present the result under headings containing the canonical B labels
   above, then close out the Mode-B Definition of Done (below).

## Mode U-1 — Diff-driven update

1. Determine the diff range: user-specified branch/range/PR, else
   `git diff <default-branch>...HEAD --name-only` (detect master vs main).
2. Map changed paths → affected doc sections via `references/audit-checklist.md` §1.
3. **Present the mapping**: the changed-paths → doc-sections table about to be
   rewritten, per **Plan before you write** (above).
4. Read the changed source files, then rewrite **only the affected sections**. Bump
   `Last updated` only on files actually edited.
5. Finish under headings containing the canonical U-1 labels `Mapping` and
   `Verification`: restate the map and checks, then report semantically related
   untouched sections (renamed classes, moved flows) — flag, don't silently rewrite.

## Mode U-2 — Full audit

1. Run `references/audit-checklist.md` §2 (machine-checkable invariants), §5 (safe
   executable command checks), §3 (semantic checks), and §6 (Fresh Session Test) over
   every file in the doc set.
2. **Default is report-first:** output the drift report (checklist §4 format, ending
   with its Verification results block); change nothing until the user confirms,
   unless they asked to fix directly up front. Running §5's safe read-only commands
   is observation, not a change.
3. When fixing, follow Mode U-1 rules (targeted edits, honest dates).

---

## Definition of Done (per mode)

"Docs written" is not done. A mode completes only when its checklist passes (executable
checks: checklist §5; Fresh Session Test: §6). Prefer the independent cross-provider
runner (`scripts/fresh_session_test.sh`, checklist §6). Self-simulation is a degraded
fallback and MUST NOT be reported as an independent pass.

- **G** — core files + selected modules exist · every undecided section reads
  `TBD — not yet designed` · TBD list handed off with return triggers · Fresh Session
  Test passes (Q5 via PROGRESS.md, or its absence proves `N/A — not agent-tracked`) · no test
  gate → warning attached + gate item seeded (§6).
- **B** — plan confirmed (interactive) or recorded in the report (headless) · every
  selected doc generated AND self-checked in WIP = 1 order · all stated commands
  §5-verified or flagged `unverifiable here` · Fresh Session Test passes on the new doc
  set · no test gate → warning attached + gate item seeded (§6) ·
  `docs/.doc-architect-state.md` deleted.
- **U-1** — mapping confirmed (interactive) or recorded in the report (headless) ·
  every mapped section re-verified against the read source · `Last updated` bumped only
  on files actually edited · related-but-untouched sections reported.
- **U-2** — §2 + §5 + §3 + §6 all run · report in §4 format ends with a Verification
  results block · no file changed without user confirmation.
