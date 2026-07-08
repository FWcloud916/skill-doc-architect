# doc-architect — Design Decisions

> **Type:** Explanation
> **Audience:** Maintainers (human and AI) of this skill
> **Last updated:** 2026-07-08
>
> Decision log for this skill's architecture, newest first. Portable source of truth —
> everything a fresh clone needs to modify the skill without prior session context.

---

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
1. Create `references/stacks/<stack>.md` using the 5-section skeleton (copy an existing
   file, e.g. `rails.md`).
2. Add one row to the detection table in `references/stacks/README.md` (mind the
   check order — disambiguation is top-down, first hit wins).
3. Add `evals/fixtures/basic-<stack>/` plus at least one `trap-*` fixture exercising
   the new row's position in the first-hit-wins ordering (every insertion can shadow
   or be shadowed).
4. Run `bash scripts/verify.sh`; all checks must pass. Do not touch SKILL.md or the
   templates.
