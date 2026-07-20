# doc-architect — Design Decisions

> **Type:** Explanation
> **Audience:** Maintainers (human and AI) of this skill
> **Last updated:** 2026-07-20
>
> Decision log for this skill's architecture, newest first. Portable source of truth —
> everything a fresh clone needs to modify the skill without prior session context.
> Entries older than 2026-07-09 cite pre-restructure paths (`SKILL.md`, `references/`
> at repo root); those now live under `skills/doc-architect/`.

---

## 2026-07-20 — Native Codex CLI plugin packaging

Codex users could only install the skill through the generic skills CLI or manual
symlinks — no version pinning, no `/plugins` flow. Codex CLI supports native plugins
(`.codex-plugin/plugin.json` + a repo-scoped `.agents/plugins/marketplace.json`), and
the skill's SKILL.md format is already Codex-compatible, so packaging is additive.

Decisions:

- **Mirror identity, lockstep versions.** `.codex-plugin/plugin.json` mirrors the
  Claude manifest's name/description/author and its `interface` block reuses the
  `agents/openai.yaml` wording. verify.sh check 10 now parses both manifests and the
  Codex marketplace, and requires the two `version` fields to be equal.
- **Marketplace paths resolve from the repo root.** `codex plugin marketplace add`
  reports the repo root as the installed marketplace root, so the local source entry
  uses `"path": "./"` — a `"../.."` path relative to the marketplace file fails to
  resolve (verified against codex-cli 0.144.6; install cached the plugin under
  `~/.codex/plugins/cache/doc-architect/doc-architect/2.3.0`).
- **Distribution packaging is user-visible.** Unlike the eval-only Codex work
  (2026-07-14, no bump), native install capability changes what plugin users receive,
  so both manifests advance to `2.3.0` — consistent with the 2.1.0 `openai.yaml`
  precedent.

## 2026-07-15 — Evidence-backed delivery policies and no-PR merge topology

Projects need different delivery contracts: some require review through PR/MR, some
integrate reviewed local work without a hosting artifact, and some intentionally use
trunk development. Treating one workflow as universal would make generated AGENTS.md
contradict repository settings or team decisions.

Decisions:

- **Policy is selected, not assumed.** Existing AGENTS/CONTRIBUTING rules and branch
  protection win, followed by an explicit user choice. Conflicts require clarification;
  headless runs with no evidence leave the policy unselected instead of guessing.
- **No-PR still preserves topology.** Non-trivial work uses a task branch, passes the
  real verification gate, and integrates with `git merge --no-ff`. Squashing is
  forbidden; the merge message records the source branch, summary, and verification.
  The branch ref may be deleted because the merge commit retains its ancestry.
- **Documentation is not delivery authorization.** Generating AGENTS.md records future
  agent behavior. If a development task does not authorize integration, its agent hands
  off the verified branch and exact merge command rather than merging on its own.
- **One dedicated scenario protects the boundary.** `delivery-policy-no-pr` requires
  the sourced merge-commit rules, rejects invented PR/MR requirements, and proves the
  source policy file remains unchanged. This additive user-visible capability advances
  the plugin to `2.2.0`.

## 2026-07-14 — Provider-selectable detection CI with protected OpenAI execution

The detection runner already supported `EVAL_CLI=claude|codex`, but GitHub Actions
installed only Claude Code and exposed only an Anthropic model input. Adding Codex by
installing its CLI in the same shell job would have made `OPENAI_API_KEY` visible to
repository-controlled scripts. OpenAI's CI guidance instead recommends
[`openai/codex-action`](https://github.com/openai/codex-action), which keeps the key
behind a Responses API proxy.

Decisions:

- **Providers stay independent.** `provider=anthropic|openai|both` selects separate
  jobs and artifacts. `both` runs them in parallel but never averages or merges their
  grades; either provider can fail the workflow.
- **Models are dispatch inputs.** `anthropic_model` and `openai_model` are free text,
  while `openai_effort` is constrained to low/medium/high. OpenAI defaults to
  `gpt-5.6-luna`; every run can override it. Provider, model, and effort are mandatory
  manifest fields so a result cannot lose its execution identity.
- **OpenAI uses a bounded matrix.** Each fixture/run is one read-only, ephemeral,
  schema-constrained Codex Action invocation. `max-parallel: 3` limits concurrency;
  the CLI and Responses API proxy share one pinned version; a secret-free aggregate
  job reconstructs the expected manifest and lets `grade.py` hard-fail missing
  artifacts.
- **One prompt contract.** `detection_prompt.py` renders the prompt for both local
  CLI runs and hosted Actions. The workflow does not carry a second prompt copy that
  could drift from the tested runner.
- **No plugin version bump.** This changes eval orchestration and provenance only;
  the installed skill behavior and machine-readable detection report remain 2.1.1.

## 2026-07-14 — Claude N=3 contract stabilization

The first Claude 2.1 N=3 release sweep selected the correct stack in every detection
run and produced correct scenario file changes, but exposed three machine-contract
flakes: package-role semantics were implicit, fixture paths sometimes anchored at the
skill checkout, and scenario reports were graded by prose substrings. An independent
Fresh Session run also answered Q5 correctly while omitting its required absence
citation.

Decisions:

- **Package roles are an explicit additive table.** The stack index now owns exact
  signals for every role; `desktop` means Electron/Tauri while React Native is
  `ui-framework`, and tooling can coexist with `plain-node`. Detection runners execute
  at the fixture root, so `package.json` can no longer drift to a checkout-relative
  path. `trap-react-native-role` permanently covers the observed role confusion and
  names this decision via `regression_for`.
- **Report structure is graded as structure.** SKILL.md defines canonical per-mode labels
  that must remain intact inside Markdown headings while allowing descriptive wording.
  Scenario contracts separate `final_required_sections` from semantic prose markers,
  and the grader parses phrase-bounded headings rather than accepting a word anywhere
  in the response. This remains stricter than the previous prose substring check.
- **Q5 absence is prompt-pinned.** The independent runner's JSON example now supplies
  both the canonical answer and `PROGRESS.md absent at repository root` citation. The
  validator remains unchanged and strict; a vague root-listing citation still fails.
- These are backward-compatible stability fixes to the 2.1 feature set, so the plugin
  advances to `2.1.1`.

## 2026-07-14 — End-to-end invariant evals and cross-provider Fresh Session validation

The 2.0 review made stack routing strict but left the larger promise — safe, targeted,
evidence-based documentation changes — protected only by instructions and manual
review. Version 2.1 adds deterministic coverage without pretending prose has one golden
answer:

- **Grade invariants, not wording.** Six disposable-repository scenarios cover honest
  greenfield TBDs, brownfield bootstrap, merge preservation, targeted Mode U-1 edits,
  report-only U-2, and unknown-stack honesty. Their grader checks filesystem scope,
  required/forbidden paths and content, sentinel preservation, canonical frontmatter,
  relative links, and final-report fields. Full-text golden files and LLM judges remain
  rejected because both would reward phrasing rather than correctness. Snapshot scope
  excludes only Git internals and a named set of tool caches that audit §5 already
  permits safe verification commands to create; arbitrary hidden paths remain graded.
- **Provider calls never touch fixture sources.** The scenario runner copies each repo,
  initializes Git in the copy, applies an optional feature patch, snapshots it, and
  grants write access only to the disposable repo. Scenarios suppress nested Fresh
  Session provider calls so one scenario is one billed call; independent Fresh Session
  behavior has its own runner and tests.
- **Fresh Session is cross-provider and citation-checked.** The shipped runner accepts
  `EVAL_CLI=claude|codex`; Codex uses a checked-in output schema. A deterministic
  validator enforces Q1–Q5 ordering and real repo-local Markdown citations. When no CLI
  is available, self-simulation is explicitly degraded and cannot be called an
  independent pass.
- **Trigger scope is a checked contract.** Frontmatter is shortened to reduce always-on
  context, `agents/openai.yaml` supplies Codex UI metadata, and a 16-case matrix records
  the boundary between broad doc architecture, canonical-doc-only `project-docs`, and
  excluded API/changelog work. These are additive capabilities, so the plugin advances
  to `2.1.0` rather than another major contract version.

## 2026-07-14 — Detection contract v2, evidence-based design surfaces, and false-green gates

Review found four correctness gaps that the existing green `verify.sh` did not expose:
the detection grader accepted empty/incomplete suites and ignored non-primary roles and
evidence; SAFE probes used on-demand `npx`; Fresh Session Q5 depended on a report outside
the fresh agent's repository context; and `docs/*.md` invariants accidentally covered
non-canonical ADRs/memos despite the scope guard. Two broad detection signals also
misrouted generic Ruby Gemfiles as Rails and generic Swift packages as Apple apps.

Decisions:

- **Detection report v2 is routing-only.** The lossy singular `package_json_role`
  became one `{path, roles[]}` entry per package manifest, supporting monorepos and
  multi-role packages. Evidence is now a repo-relative path that the grader proves
  exists. The unrelated `unsafe_commands_flagged` field was removed; command safety
  remains centralized in `audit-checklist.md` §5. Because the machine contract is an
  advertised interface, this is a major plugin release (`2.0.0`).
- **Completeness is graded before correctness.** The runner writes a manifest naming
  selected fixtures and N; zero matches, missing fixtures, or missing runs hard-fail.
  The grader checks the exact schema, complete `(stack, role)` pairs, resolution/role
  invariants, package roles, and evidence paths. Free unit tests permanently cover the
  false-green cases.
- **Broad manifests require qualifying evidence.** A Gemfile is Rails only when it
  names `rails`/`railties` or Rails entrypoints exist; Package.swift is Apple only
  when it declares an Apple platform (or an Xcode/Podfile signal exists). Regression
  fixtures: `trap-ruby-gem` and `trap-swift-package-library`.
- **Design applicability is a discovery facet, not a routing field.** Every stack now
  declares `Design surface: inherent | conditional | none` and a discovery evidence
  row. Conditional server-rendered UIs and VS Code webviews can offer DESIGN.md without
  contaminating the manifest-only detection contract; native host UI alone does not.
- **Safety and audit ownership are explicit.** On-demand package runners are NOT SAFE;
  only confirmed local binaries execute. Canonical invariants apply to the fixed docs
  set and Document-Map-owned domain files, never arbitrary `docs/` content. When
  PROGRESS.md is absent, Fresh Session Q5 validly answers `N/A — not agent-tracked`,
  preserving the harness module's opt-in status.

## 2026-07-11 — DESIGN.md UI design-system module (opt-in)

A new opt-in module doc, `DESIGN.md` at the repo root: a Stitch-convention design-system
document (YAML frontmatter of design tokens + prose sections) that AI agents read before
generating or restyling UI. Provenance: Google Stitch's DESIGN.md concept, ecosystem of
examples at [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md).
Design choices:

- **Repo root, not `docs/`** — the cross-tool convention is that any agent finds
  `DESIGN.md` at the root; `PROGRESS.md` set the root-level opt-in precedent. Like
  PROGRESS.md it is exempt from the docs frontmatter convention — its YAML frontmatter
  IS the token block.
- **Offered via a per-stack-file `> **UI surface:** yes` marker**, not a stack list in
  SKILL.md (forbidden: no per-stack residue, verify.sh check 5) and not a signal-table
  column in `stacks/README.md` (the detection-report contract stays untouched, so
  evals/`grade.py`/`expected.json` need no changes). Mode B already reads every
  documented surface's stack file, so the marker costs no extra read. Eight stacks
  carry it (the UI-bearing ones); backend/CLI/`vscode-extension` do not.
- **Token-extraction knowledge is centralized** in `design-template.md` §Extraction map
  (per-ecosystem theme sources); stack files carry only a diff-map row pointing at
  DESIGN.md — mirrors the §5 command-safety centralization (2026-07-07).
- **Machine-checkable boundary**: the audit-checklist §2 DESIGN.md block checks what a
  grep/parse can prove (frontmatter parses, `{group.key}` references resolve, prose/token
  hex agreement, extracted hexes exist in theme sources); aesthetic judgment is
  deliberately out of scope. The same extract-never-invent rule as commands applies:
  Mode B token values must be traceable to a theme source read this session.
- **SKILL.md line budget bumped 215 → 225** (verify.sh) for the doc-set row, plan-gate
  wiring, and Mode G offer — same precedent as the 210→215 bump (2026-07-08). A new
  verify.sh check (5b) pins the marker's canonical spelling.

## 2026-07-09 — Skill moved to `skills/doc-architect/` + Claude plugin packaging

The skill (SKILL.md, references/, fresh_session_test.sh) moved from the repo root into
`skills/doc-architect/`, and the repo gained `.claude-plugin/plugin.json` +
`marketplace.json` making it a single-plugin Claude Code marketplace. Four reasons:

- **Remote one-line install was silently broken.** `npx skills add <repo>` on a
  root-level SKILL.md hits vercel-labs/skills' deliberate special case (`add.ts`:
  "install the skill file, not the whole repository") — only SKILL.md landed, no
  `references/`, and the CLI reported success. The `skills/<name>/` layout gets the
  full-directory copy path. Verified empirically both ways.
- **Spec compliance.** The Agent Skills spec requires the SKILL.md frontmatter `name`
  to match the parent directory name; at the repo root that held only after an
  aptly-named symlink.
- **Ecosystem convention.** anthropics/skills, index sites (SkillsMP, LobeHub), and
  Claude Code plugins all standardize on `skills/<name>/SKILL.md`.
- **Plugin route installs the agent too.** A plugin auto-discovers `skills/` and
  `agents/`, so `/plugin install` ships the dedicated subagent that the skills CLI
  cannot (it installs skills only).

Trade-offs accepted: existing root-pointing symlinks broke (README carries a migration
note); the plugin cache copy includes the whole repo (evals/ fixtures included — inert,
~1MB) because the plugin root is the repo root; splitting a separate plugin root was
rejected as it would break the skills-CLI discovery and symlink ergonomics.
`fresh_session_test.sh` moved inside the skill because SKILL.md instructs agents to run
it — it must ship with every install route; `verify.sh` stays at the repo root as a
maintainer-only tool. User-visible skill changes must bump `plugin.json` `version`
(plugin users only see updates on a bump; see AGENTS.md hard constraints).

## 2026-07-08 — Detection eval suite (`evals/`) + machine-readable report contract

Detection routing gets automated evals; nothing else in the skill does. The boundary:
detection is the only behavior with **objective ground truth** — given a set of
manifests, the resolve rules in `references/stacks/README.md` define exactly one
correct answer, so a plain script can grade it (no LLM judge). Doc generation quality,
command-verification honesty, and the Fresh Session Test stay human-in-the-loop by
design. Both historical detection bugs (vitest→vite substring misdetection;
Rails+esbuild hybrid misread — see the two 2026-07-07 entries below) now have
permanent `trap-*` regression fixtures with `regression_for` pointing at their entry.

- **Suite shape:** 32 manifest-only fixtures (16 `basic-*`, one per stack + plain
  Node; 16 `trap-*` for ordering/role/fallback/monorepo traps), headless runner
  (`claude -p`, N=3, all-runs-must-pass — a flaky router is a bug, not variance),
  deterministic grader. See `evals/README.md`.
- **Contract adopted into the skill:** the detection report JSON (resolution /
  surfaces with evidence / package_json_role / unsafe_commands_flagged) lives in
  `references/stacks/README.md`, and headless Mode B **always emits it** into
  PROGRESS.md state when in use — ~150 tokens buys post-hoc auditability of every
  run, the same verification philosophy as the rest of the skill. Consequently
  `package_json_role` grades as a hard fail (it is spec, not suite invention).
- **Free gate:** `verify.sh` lints fixtures on every run — each fixture has
  `expected.json`, and every referenced stack name resolves to
  `references/stacks/<name>.md`, so fixtures cannot drift from the stack set.
- **Status:** live sweep validated — **32/32 fixtures pass at N=3, zero flaky
  runs**. Runner bring-up found two real bugs, both fixed: (1) `--max-turns` is
  not a valid CLI flag on 2.1.204 — removed; (2) plain-text `-p` stdout truncated
  on some runs (`basic-python`) — switched to `--output-format json` and unwrap
  the envelope. Triage also caught a report-contract ambiguity: `trap-monorepo-pnpm`
  correctly resolved `monorepo` but marked a sub-project `primary`, which the
  original role spec didn't actually forbid — fixed by clarifying that a
  monorepo report has **no primary**, every sub-project is `surface` (contract +
  runner prompt + `references/stacks/README.md` updated together). Cost/wall-clock
  measured in `evals/README.md`; process rules (bug→fixture, new-stack→two-fixtures,
  resolve-rule→expected.json) now hard constraints in `AGENTS.md`. CI wiring (E4)
  landed as `.github/workflows/detection-evals.yml`, **manual trigger only**
  (`workflow_dispatch`) — deliberately not on push/PR/schedule, since each run
  costs real API spend. **The independent Fresh Session Test (E6) landed**:
  `scripts/fresh_session_test.sh` gets answers to the 5 Fresh Session Test questions
  from a headless `claude -p` subprocess with zero conversation history — the writing
  session self-simulating "a fresh agent" isn't actually fresh, since it remembers
  every decision it just made, which systematically overestimates doc quality.
  Grading stays the writing session's job (blocking-gap vs pass vs honest `TBD` is a
  judgment call); the script only supplies independent answers. Design call: routes
  through `Bash` + a plain `claude -p` call rather than the `Agent`/Task tool, because
  `agents/doc-architect.md`'s tool list (`Read, Grep, Glob, Bash, Write, Edit`) has no
  Agent tool in either its headless-subagent or main-session mode — `Bash` is the one
  mechanism available everywhere doc-architect runs. `SKILL.md`'s line budget was
  bumped 210→215 to fit one pointer line in the Definition of Done section (checked in
  `scripts/verify.sh`); the mechanism detail itself lives in
  `references/audit-checklist.md` §6, which has no line cap.

## 2026-07-07 — Real-repo test fallout: vite demoted, Rust + VS Code extension stacks

A detection dry-run on a real repo (vscode-git-braid: VS Code extension + Rust native
core via napi + pnpm workspace) confirmed collect-then-resolve correctly stops at the
gate instead of misdetecting, and exposed three gaps, all fixed:

1. **`vite` demoted from framework signal** (bug-level): vitest pulls vite into
   devDependencies, so any pure-TS project (e.g. a VS Code extension without a Cargo
   side) hit the frontend row on the single-manifest fast path. Frontend web now
   requires a UI framework (react/vue/svelte/next/nuxt) or `vite` + a root
   `index.html` (the vanilla-vite-site shape). Trade-off: a vanilla vite site without
   a root index.html would fall to plain Node — rarer than vite-as-tooling.
2. **Rust** (`rust.md`): `Cargo.toml` (without `src-tauri/`) is now a signal AND a
   dedicated backend manifest for hybrid resolution — Cargo + package.json resolves
   backend-primary with role classification.
3. **VS Code extension** (`vscode-extension.md`): `engines.vscode` is the authoritative
   signal, checked after Tauri and before the server/frontend checks; the `contributes`
   block is documented as the §6 interface table. Also added to the hybrid role
   classification (before the UI-framework check).

## 2026-07-07 — Collect-then-resolve detection (hybrid repos)

First-hit-wins detection misclassified hybrid repos: Rails 7 + esbuild (Gemfile +
package.json holding only build tools) resolved to **plain Node**, and Rails + React
in one repo resolved to **Frontend web** — the package.json rows sit above the backend
manifests in the signal table. Fix: detection is now **two-phase** — collect every
manifest signal present, then resolve. A dedicated backend manifest + package.json →
the backend is primary, and the package.json's **role** is classified by deps: a UI
framework (react/vue/svelte/next/nuxt) makes it a real frontend surface (**hybrid**,
both surfaces documented); build tooling only (esbuild/webpack/vite/postcss/tailwind)
makes it the backend's asset pipeline, noted in project-overview §2. `vite` alone is a
frontend signal only when no backend manifest exists. Monorepos (workspaces,
pnpm-workspace, lerna, apps/+packages/) enumerate sub-projects and detect per
sub-project. Hybrid / ambiguous / monorepo all resolve at the Mode B step-3 gate
(list every surface with evidence; interactive: ask, default all; headless: document
all, backend first). No template changes were needed — project-overview §2 lists
multiple stacks and §6 is one-subsection-per-surface by design.

## 2026-07-07 — Modes stay inline in SKILL.md (index-pattern boundary)

Extracting per-stack guidance into `references/stacks/` paid off; extracting modes
(G/B/U) into `references/modes/` was evaluated and **rejected**. The boundary: extract
to an index only content that is **many-variant** (and growing), **one-variant-per-run**,
and **reference data**. Stacks meet all three (13 files, one read per run, lookup data).
Modes meet none: fixed at 4, mode selection needs the full picture, and they are
tightly coupled control flow (merge mode inside B, U-2 reuses U-1 rules, DoD maps per
mode). Procedures that MUST be followed stay inline where they are always in context;
data that can be looked up on demand moves out. Same judgment keeps the SAFE/NOT-SAFE
safety rules centralized in `audit-checklist.md` §5 rather than scattered per stack.

**Settled architecture:** `SKILL.md` = control flow + cross-stack logic;
`references/` = per-doc-type templates; `references/stacks/` = per-stack reference
data + detection index (`README.md`).

## 2026-07-07 — Detection table moved to `references/stacks/README.md` (commit 773ef15)

The 14-row signal→stack table was the last per-stack data inline in SKILL.md; only
Mode B/U need it, and adding a stack forced a SKILL.md edit. Now adding a stack touches
only `references/stacks/` (new file + one index row). SKILL.md keeps a summary of the
load-bearing order only. The trailing Quick-reference table merged into Mode selection
(230 → 207 lines).

## 2026-07-07 — Per-stack index restructure + desktop support + detection gate (commit c66b419)

- 13 stack files with a unified 5-section skeleton (Discovery map / Diff→section map /
  Linter signals / Minimal test gate / Command safety notes).
- Desktop stacks added: Electron, Tauri, Windows desktop (.NET); Apple generalized from
  iOS to iOS/macOS (notarization, DMG, Sparkle, launchd). Qt/C++ (CMake) deliberately
  stays in the unknown-stack fallback.
- `package.json` disambiguation order: React Native → **Electron → Tauri** → Node
  backend → Frontend web → plain Node. Desktop checks MUST precede the frontend check —
  Electron/Tauri renderers depend on react/vue and were previously misdetected.
- Stack confirmation is **detect-first + confirmation gate**, not ask-first: auto-detect
  from manifests (evidence-based), present the judgment with its detection evidence at
  the Mode B plan gate for correction; ask only on ambiguous signals
  (fullstack / multi-manifest / unknown). Headless stays fully autonomous.

## 2026-07-07 — Frontend web + mobile support (commit cae3f92)

- `package.json` no longer means "Node backend" unconditionally; frontend frameworks,
  React Native, and server frameworks are disambiguated by dependencies.
- Android detection requires `build.gradle*` **plus** `AndroidManifest.xml`, keeping
  JVM-backend gradle repos in the unknown fallback.
- **Any `./gradlew` invocation is NOT SAFE** to execute (wrapper downloads distributions
  and dependencies on first run); later extended to `dotnet build/test/format` (implicit
  restore) and `cargo build/test/clippy` (downloads and compiles crates).
  `cargo fmt --check` and version probes are SAFE.
- `db-observation.md` applies only to **server-side** relational datastores; a
  client-embedded store (SQLite / Core Data / Room / electron-store) is recorded in
  project-overview §9 instead.

## 2026-07-07 — Harness-engineering upgrade (commits 884b5ac…bb44443)

Design source: the Learn Harness Engineering tutorial
(https://walkinglabs.github.io/learn-harness-engineering/en/, 12 lectures). Additions:
executable command verification inside a safety boundary (audit-checklist §5),
per-mode Definition of Done, Fresh Session Test (§6) as the final gate, the opt-in
PROGRESS.md harness module, and the verification-gate warning for test-less projects.
A five-subsystem phase-based rewrite was considered and rejected in favor of
**enhance-over-rewrite**: keep the 3-mode organization (G/B/U) and layer substance on
top. (Later refined: restructures are acceptable when scale justifies them — see the
stacks/ index above — but the mode organization itself stands.)

---

## Appendix

**Canonical stack tokens** (spell identically everywhere): `Rails`, `Go`,
`Node backend`, `Python`, `Rust`, `Serverless`, `Frontend web`, `React Native`,
`Apple (iOS/macOS)`, `Android`, `Flutter`, `Electron`, `Tauri`,
`Windows desktop (.NET)`, `VS Code extension`.

**Adding a stack (standard procedure):**
1. Create `skills/doc-architect/references/stacks/<stack>.md` using the 5-section skeleton (copy an existing
   file, e.g. `rails.md`).
2. Add one row to the detection table in `skills/doc-architect/references/stacks/README.md` (mind the
   check order — disambiguation is top-down, first hit wins).
3. Add `evals/fixtures/basic-<stack>/` plus at least one `trap-*` fixture exercising
   the new row's position in the first-hit-wins ordering (every insertion can shadow
   or be shadowed).
4. Run `bash scripts/verify.sh`; all checks must pass. Do not touch SKILL.md or the
   templates.
