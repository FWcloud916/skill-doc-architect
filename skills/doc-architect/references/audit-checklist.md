# Audit Checklist & Diff→Section Mapping

Used by Mode U-1 (diff-driven update) to locate affected sections, and by Mode U-2
(full audit) / Mode B self-check to verify the doc set against the code.

---

## 1. Diff path → doc section mapping (Mode U-1)

Map each changed path to the sections to re-verify. The table below lists
stack-agnostic paths; stack-specific paths (routes/navigation, models/stores, workers,
platform manifests, signing config…) live in the matched stack file's
§Diff → doc section map (`references/stacks/<stack>.md`), whose rows follow this
table's shape.

| Changed path | Re-verify |
|---|---|
| Interface surface (see stack file: routes, pages/screens, navigation, IPC) | project-overview §6 |
| Data layer (see stack file: schema/migrations, models, stores, client persistence) | project-overview §5, §9; domain-models §1 + ER |
| Background work (see stack file: workers/jobs, tasks, schedules) | project-overview §7 |
| Business-logic layer (services, mechanisms) | domain-models mechanism/flow sections naming those classes |
| API-client wrappers / external-integration layer | project-overview §8; domain-models integration sections |
| Dependency manifest/lockfile (major bumps or new key deps only) | project-overview §2 |
| Settings/env config | project-overview §8, §10 |
| `Dockerfile`, CI/CD config, environment definitions, packaging/signing config | project-overview §10 |
| Linter config | coding-style §1–2 (and §6 if commands changed) |
| Setup/run/test commands (Makefile, package scripts, CI) | README Quickstart; AGENTS.md Commands |
| New/changed query shape (`WHERE`/`JOIN`/`ORDER BY`/pagination) on a hot table | db-observation is the *process* doc — don't edit it; check the diff followed it |
| Theme/design-token sources (see stack file diff map: tailwind/CSS custom properties, theme objects, asset catalogs, theme XML, XAML resources) | DESIGN.md frontmatter tokens + the matching prose section (Colors/Typography/Shapes/Components) — only when `DESIGN.md` exists |
| Any other source dir (mailers, serializers, decorators, project-specific layers…) | grep the docs for the changed class/file names — re-verify every section that mentions them, plus the §4 directory-structure annotation for that dir |

After the mapped edits, list any section the diff did **not** touch but that reads as
semantically related (e.g. a flow description mentioning a renamed class) — report these
even if you don't edit them.

## 2. Machine-checkable invariants (Mode U-2 / Mode B self-check)

Run per file; each check is a grep/ls-level comparison, not a judgment call.

**Every canonical doc file** — the fixed set is `docs/project-overview.md` plus
selected modules that exist (`docs/domain-models.md`, `docs/coding-style.md`,
`docs/db-observation.md`). Under `docs/domain/`, apply these invariants only to files
listed by `domain-models.md`'s Document Map. Other ADRs, memos, scratch docs, and
pre-existing files are source material, not doc-architect-owned audit targets.
- [ ] Frontmatter present and complete: `# <Project> — <Doc>` title, `> **Type:**`,
      `> **Audience:**`, `> **Last updated:** YYYY-MM-DD`
- [ ] `Last updated` is a valid date, not in the future
- [ ] Relative links resolve (`docs/domain/*.md` targets exist; `../app/...` paths exist)
- [ ] RFC 2119 keywords are uppercase where used normatively

**README.md**
- [ ] Quickstart commands exist in the project's real config (CI / Makefile / package
      scripts) and pass §5 executable verification
- [ ] Documentation table rows point at files that exist
- [ ] Project-structure tree matches the actual top-level dirs

**AGENTS.md**
- [ ] Under ~100 lines (~60 when no Session routine)
- [ ] `## Hard constraints` present directly under the identity line (top of file), ≤ 15 rules
- [ ] Every hard-constraint rule has a source in parentheses, and the source still
      exists (config key / file / stated rule) — retire rules whose source is gone
- [ ] Task→doc table only lists docs that exist (no dead links, no missing generated docs)
- [ ] Commands exist in the project's real config and pass §5 executable verification
- [ ] If `CLAUDE.md`/`GEMINI.md` exist they are symlinks to `AGENTS.md`, not divergent copies
- [ ] Session routine section present iff `PROGRESS.md` exists

**PROGRESS.md (only when the harness module was selected)**
- [ ] Header line present: last-session date, short commit hash, test status ∈
      {passing, failing, not run}
- [ ] Commit hash resolves in `git log`
- [ ] Sections present: Now (WIP = 1) / Feature list / Done / Blockers / Next steps / Decision log
- [ ] At most one Feature-list row in state `active` (WIP = 1)
- [ ] Every Feature-list row has a `Verify with` command; states ∈
      {not_started, active, blocked, passing}
- [ ] No `passing` row whose `Verify with` command fails when run (§5 safety rules
      apply; unsafe commands → static check + flag)

**project-overview.md**
- [ ] All 10 `## N.` sections present, numbered 1–10 in order (missing ones must say `N/A — <reason>` or `TBD — not yet designed`)
- [ ] §5/§9 model & table names ⊆ actual model files / schema tables (flag docs-only ghosts)
- [ ] Actual models/tables ⊄ doc (flag undocumented ones; new-since-last-update is the usual cause)
- [ ] §6 surface list matches the router (every namespace/version in routes appears; no retired ones linger)
- [ ] §7 worker table matches the workers dir (both directions)
- [ ] §2 pinned versions match lockfile / version files
- [ ] §10 environment list matches the env config dir

**domain-models.md (+ docs/domain/)**
- [ ] §1 Model Details entries ↔ actual model files (both directions)
- [ ] Index-variant: every Document Map row's file exists; every `docs/domain/*.md` is listed
- [ ] State machine states/events match the current definitions
- [ ] Classes/functions named in mechanism sections still exist at the cited paths

**coding-style.md**
- [ ] §1–2 values match the current linter config (target versions, thresholds, excluded paths)
- [ ] §6 commands still run (check against CI config / scripts)

**db-observation.md**
- [ ] Example table names exist in the current schema

**DESIGN.md (only when the design module was selected)**
- [ ] YAML frontmatter parses; top-level keys ⊆ {colors, typography, rounded, spacing,
      components}
- [ ] Every `{group.key}` reference in `components` resolves to a defined token
- [ ] Color values are valid hex (`#RGB`/`#RRGGBB`); no empty token values — gaps say
      `TODO — <reason>`
- [ ] Hex values named in prose sections match the frontmatter tokens (no prose/token drift)
- [ ] Mode B-extracted docs: each non-TODO hex appears in the project's theme sources
      (grep; sources per stack: `design-template.md` §Extraction map) — flag docs-only
      ghost colors
- [ ] Required prose sections present: Overview, Colors, Typography, Layout, Components,
      Do's and Don'ts (Elevation & Depth/Shapes/Responsive Behavior/Agent Prompt Guide
      MAY read `N/A — <reason>`)
- [ ] AGENTS.md task→doc table has the DESIGN.md row iff `DESIGN.md` exists

**Scope guard & clean state**
- [ ] No edits outside the generated file set (README.md, AGENTS.md + its symlinks, the
      canonical `docs/` files, `docs/domain/`, `PROGRESS.md` when the harness module was
      selected, `DESIGN.md` when the design module was selected,
      `docs/.doc-architect-state.md` while Mode B is in flight). Pre-existing
      scratch/memo/pending directories and any other non-canonical files under `docs/`
      are untouched.
- [ ] No leftover `docs/.doc-architect-state.md` after a completed Mode B run

## 3. Semantic checks (judgment required — report, don't silently rewrite)

- Deprecated/not-yet-enabled status notes: still accurate? (a feature may have shipped or been removed)
- `TBD — not yet designed` sections: has the decision since been made or the code since been written? (greenfield docs rot in this direction)
- Flow descriptions vs current code paths for the 2–3 most business-critical mechanisms
- §1.2 relationships with other systems: callers/callees still correct?
- Anything the git log since `Last updated` touched heavily but the doc never mentions

## 4. Report format (Mode U-2 default output)

Group findings by file, ordered most-stale first:

```markdown
## <file> (Last updated: <date>)
- **[invariant]** §6 lists `api/v4` but the router has no such namespace (removed in <commit>)
- **[semantic]** §3 delivery flow still describes X; code now does Y (src/services/... )
- **[missing]** model `Foo` (src/models/foo.ts, added <date>) absent from §1
```

Use the `[command]` tag for §5 failures, e.g.
``- **[command]** AGENTS.md test command `npm test` — script not defined in package.json``.

End every U-2 report (and every Mode B/G result presentation) with a **Verification
results** block: each command checked, with `pass | fail | unverifiable here (<reason>)`,
plus the Fresh Session Test answers (§6) — Q1–Q5, each citing the doc + section that
answers it; Q5 may cite `PROGRESS.md absent at repository root` for the valid
`N/A — not agent-tracked` answer.

Fix only after the user confirms — unless they asked for fix-directly up front. Bump each
file's `Last updated` only if its content actually changed.

## 5. Executable command verification (safe commands only)

Grep-level checks prove a command is *written down* in real config; executing it is the
only proof it *works*. For every command stated in README Quickstart, AGENTS.md
Commands, coding-style §6, and PROGRESS.md `Verify with` cells: classify it, then verify.

**SAFE — execute it, report pass/fail.** A command is safe iff it is read-only (writes
nothing but stdout / tool caches), touches no network state, needs no credentials, and
finishes in seconds:

- tool existence + version: `command -v <tool>`, `<tool> --version`
- test-runner discovery / dry-run: `bundle exec rspec --dry-run`,
  `pytest --collect-only -q`, a confirmed local binary such as
  `./node_modules/.bin/jest --listTests`, `go test -list '.*' ./...`
- linter presence: `<linter> --version`; a check-only mode on a single file MAY be run
- `make -n <target>` (dry-run)
- script existence: the named script/target appears in package scripts / Makefile / CI config
- frontend/mobile probes: a confirmed local binary such as
  `./node_modules/.bin/vitest list`, `flutter --version`, `dart --version`,
  `xcodebuild -list` (reads project metadata only)
- desktop probes: `dotnet --version`, `cargo --version`, `rustc --version`;
  `cargo fmt --check` MAY be run (read-only, seconds; rustfmt missing → `unverifiable here`)

**NOT SAFE — static check only, never execute:** setup/install, migrations, seeds,
deploys, `docker compose up`, DB consoles, anything that writes files, mutates network
state, or needs credentials — including any `./gradlew` invocation (the wrapper may
download distributions and dependencies on first run), `dotnet build`/`dotnet test`/
`dotnet format` (implicit restore touches the network), and `cargo build`/`cargo test`/
`cargo clippy` (download and compile crates). On-demand package runners (`npx`,
`npm exec`, `pnpm dlx`, `yarn dlx`, `bunx`) are also NOT SAFE as probes because a
missing local package may trigger a download. For these the check stays "exists in
real config"; a JavaScript tool may execute only after its local binary is confirmed.

Rules:

- NEVER install missing dependencies to make a check runnable. A command that cannot run
  in this environment is reported `unverifiable here (<reason>)` — never guessed green.
- A failing safe command is a **finding**, not a license to rewrite the command until
  something passes — the corrected command must come from the project's real config, or
  the question goes to the user.
- Executing safe commands is observation, not modification: it is permitted even in
  Mode U-2 report-first, where file changes are not.

## 6. Fresh Session Test (end-to-end self-check)

The final gate for Modes G and B, and part of every Mode U-2 audit. Simulate an agent
whose only context is the repository: answer each question **using only the doc set plus
repo files**, citing the doc + section that answers it.

| # | Question | Expected answer location |
|---|---|---|
| 1 | What is this system? | README first paragraph / AGENTS.md identity line |
| 2 | How is it organized? | project-overview §3–4 |
| 3 | How do I run it? | README Quickstart Run / AGENTS.md Commands |
| 4 | How do I verify my work? | test + lint commands — §5-verified, or honest greenfield `TBD` |
| 5 | What work state, if any, does this repository track? | PROGRESS.md (harness module); when absent, `N/A — not agent-tracked (PROGRESS.md absent)` is a valid repository-derived answer |

A question unanswerable from the repo alone is a **blocking gap** in Modes G/B (fix
before presenting) and a **drift finding** in Mode U-2. An honest `TBD` answer passes
for greenfield; a wrong or absent answer never does. Q5 is not a gap when PROGRESS.md
is absent: its absence proves that this repository does not track agent work state.

### Running it independently (preferred)

Self-simulating "an agent with only the repo as context" in the same session that just
wrote the docs isn't actually a fresh context — it remembers every decision it just
made, which systematically overestimates doc quality. Prefer a genuinely independent
context instead:

- If either supported CLI is available, run `scripts/fresh_session_test.sh <repo root>`
  (`EVAL_CLI=claude|codex`, default Claude). It spawns a headless subprocess with zero
  conversation history and returns the 5 answers as validated JSON. Citations for
  Q1–Q4 (and Q5 when PROGRESS.md exists) MUST name a real repository Markdown file.
- Only fall back to self-simulation when the selected CLI or script is unavailable.
  Label it `degraded — independent runner unavailable`; it MAY support a best-effort
  handoff but MUST NOT be reported as an independent pass or an unqualified `complete`.
  A transient provider failure is a reason to retry or record degradation, not to
  fabricate a green independent result.
- **Grading is unchanged and stays this session's job.** The script only supplies
  answers; judging blocking-gap vs pass vs honest `TBD` is still the rules above,
  applied by the session that has full context of what the project actually needs.
- Cost note: one extra headless call per independent Fresh Session Test — modest
  compared to doc generation itself, paid for context purity. End-to-end eval scenarios
  deliberately self-simulate and label degradation to avoid nested provider calls.
- The 5 questions are hard-coded in the script's prompt from this table. If this
  table's wording changes, update the script's prompt in the same change.

### Verification-gate warning

Triggers when Q4 finds no runnable test gate at all — no test command in real config,
or one that exists but fails §5 execution with no working alternative. Q4 still scores
by the rules above (greenfield `TBD` passes; the warning is additive, not a re-verdict),
but the report MUST then include a prominent warning with three parts (what / why / fix):

1. **What**: this project has no executable verification gate.
2. **Why**: agents (and humans) cannot verify their own work — the harness's Feedback
   subsystem is missing, so "done" can only be declared by feel.
3. **Fix** (suggest, never build): the stack's minimal next step — the matched stack
   file's §Minimal test gate (`references/stacks/<stack>.md`); unknown stack / no
   stack file → the generic floor: at least one locally runnable invoke/verify path.

Establishing the test framework is the project's (working agents') job, not this
skill's — the skill warns, suggests, and seeds the work item (`harness-template.md`
§Seed the verification gate first); it never writes test files. When `PROGRESS.md` was
not selected, the warning additionally suggests opting into the harness module so the
gap has a carrier an agent can pick up — suggest, don't force.

Mode U-2: a project still without a test gate gets this warning in the drift report as
a `[missing]`-level finding; a `PROGRESS.md` whose feature list lacks the gate work
item is likewise a finding.
