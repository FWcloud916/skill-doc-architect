# doc-architect — Design Decisions

> **Type:** Explanation
> **Audience:** Maintainers (human and AI) of this skill
> **Last updated:** 2026-07-07
>
> Decision log for this skill's architecture, newest first. Portable source of truth —
> everything a fresh clone needs to modify the skill without prior session context.

---

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
`Node backend`, `Python`, `Serverless`, `Frontend web`, `React Native`,
`Apple (iOS/macOS)`, `Android`, `Flutter`, `Electron`, `Tauri`,
`Windows desktop (.NET)`.

**Adding a stack (standard procedure):**
1. Create `references/stacks/<stack>.md` using the 5-section skeleton (copy an existing
   file, e.g. `rails.md`).
2. Add one row to the detection table in `references/stacks/README.md` (mind the
   check order — disambiguation is top-down, first hit wins).
3. Run `bash scripts/verify.sh`; all checks must pass. Do not touch SKILL.md or the
   templates.
