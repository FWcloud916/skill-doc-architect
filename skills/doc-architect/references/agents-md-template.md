# Template: `AGENTS.md`

The AI-agent entry point for the repository. Its job is **routing, not content**: a
one-line project identity, a table that maps *the task an agent is about to do* to *the
doc it should read first*, the commands that must not be guessed, and the doc-maintenance
rules. Everything else lives in `docs/` — AGENTS.md points there.

**Hard budget: keep the generated file under ~100 lines** — and near ~60 when the
harness module (`PROGRESS.md`) was skipped, since the Session routine then drops out.
The extra headroom over the original ~60 exists only for the Hard-constraints block and
the Session routine; if the file grows past the budget, content is leaking in that
belongs in `docs/` — move it and leave a link. An AGENTS.md that tries to explain the
architecture inline goes stale fast and gets skimmed, which defeats its purpose.

---

## Skeleton

```markdown
# <Project Name> — Agent Guide

<One sentence: what this project is and what it owns.>

## Hard constraints

<Non-negotiables only — the rules that break the build, the data, or the team's process
 if violated. ≤ 15. Each is a MUST / MUST NOT with its source in parentheses, found in
 THIS repo's config, CI, and team rules — the test-gate rule (run `<test command>`
 before declaring done) is always one of them.>

## Read before you work

Read the matching doc **before non-trivial work**. Small fixes (typos, single-line
edits, running tests) can skip; do not pre-load all docs.

| Task | Read first |
|---|---|
| Architecture, request flow, directory layout, integrations | [docs/project-overview.md](docs/project-overview.md) |
| Touching domain behavior, data models, state machines | [docs/domain-models.md](docs/domain-models.md) |
| Style, lint rules, error handling, layering conventions | [docs/coding-style.md](docs/coding-style.md) |
| Changing query shape (`WHERE`/`JOIN`/`ORDER BY`/pagination) on a hot table | [docs/db-observation.md](docs/db-observation.md) |
| Unsure what a project-specific term means | [CONTEXT.md](CONTEXT.md) |

## Commands

```bash
<setup command>     # install dependencies
<run command>       # start locally
<test command>      # run the test suite — the verification gate for "done"
<lint command>      # lint / format check
```

## Session routine

<Include this section ONLY when PROGRESS.md exists (harness module selected).>

- **Clock-in:** read [PROGRESS.md](PROGRESS.md) → `git log -3` + `git status` → run the
  test command → pick up the single active item (WIP = 1).
- **Clock-out:** verification command passes → update PROGRESS.md (state, commit hash,
  test status) → remove stale artifacts (debug logs, commented-out code) → commit.
  Session complete = task verified AND clean state — not before.

## Conventions

- <2–4 bullets max: the rules an agent breaks most easily in THIS repo —
  e.g. commit message format, "never edit generated dir X", branch naming.>

## Docs maintenance

When modifying any file under `docs/`, update its `> **Last updated:** YYYY-MM-DD`
frontmatter to today's date. Requirement keywords (MUST, SHOULD, MAY) follow RFC 2119.
```

## Writing rules

- **Hard constraints are positional and sourced.** The block sits directly under the
  identity line and MUST NOT be moved lower — models attend to the extremes of a file,
  not its middle ("lost in the middle"); `Docs maintenance` holds the other extreme, so
  nothing critical goes between them. ≤ 15 rules; each cites its source (linter/CI
  config, an incident, an explicit user statement) so an audit can retire it when the
  source disappears — actively delete stale rules, never let the list ratchet up. No
  generic best-practice filler: a rule with no repo-specific source doesn't belong here.
- **Session routine is conditional**: include it only when the harness module
  (`harness-template.md`) was selected and `PROGRESS.md` exists; adapt its wording to
  the project's real commands. Without PROGRESS.md the section is omitted entirely.
- **Every instruction earns its lines**: when the file nears the ~100 budget, cut from
  the middle sections first (Conventions overflow → `docs/coding-style.md`) — never
  from Hard constraints or Docs maintenance.
- **The task→doc table only lists docs that actually exist.** Rows for modules the doc
  set skipped (no `domain-models.md`, no `db-observation.md`, …) are removed, not left
  as dead links.
- **Commands come from the project's real configuration** (CI, Makefile, package
  scripts) — same rule as the README; never invent them. Greenfield: `TBD` is honest.
- **Conventions bullets are repo-specific**, mined from the code/config or stated by the
  user — not generic best-practice filler. Zero real conventions found → omit the section.
- **Agent-file symlinks**: many tools read different filenames for the same purpose.
  After writing `AGENTS.md`, offer to create `CLAUDE.md` as a symlink to it (and others
  the user's toolchain reads, e.g. `GEMINI.md`). Ask rather than assume; if created,
  always edit `AGENTS.md`, never the symlinks.
- **Merge mode**: an existing AGENTS.md (or CLAUDE.md acting as one) is repaired, not
  replaced — add the missing routing table or maintenance block, keep the project's own
  wording, and confirm any restructure with the user.

## Delivery policy variants

Delivery rules describe how future development work reaches the default branch; merely
generating docs does not authorize the current agent to create, merge, or delete a
branch. Resolve the policy from existing `AGENTS.md`, `CONTRIBUTING.md`, repository
settings/branch protection, or equivalent evidence first; an explicit user choice is
second. If sources conflict, ask. In headless mode with no evidence, omit delivery
rules and report the policy as unselected — never invent one. A source-approved trivial
change exception MAY be recorded; never add that exception as generic advice.

Adapt exactly one evidence-backed variant into the generated Hard constraints and
Conventions while staying within their budgets:

- **PR/MR workflow:** non-trivial work MUST use a task branch and MUST NOT commit
  directly to the protected default branch. Verification MUST pass before merge. Open
  the required PR/MR and preserve the repository's configured merge method and review
  rules; do not invent approval counts or a squash/rebase policy.
- **No-PR merge-commit workflow:** non-trivial work MUST use the project's task-branch
  naming convention and MUST NOT commit directly to the default branch. Verification
  MUST pass before integration. Integrate with `git merge --no-ff <branch>`; MUST NOT
  squash. The merge commit message MUST record the source branch, change summary, and
  verification result. If the task does not authorize integration, hand off the
  verified branch and exact merge command instead of merging. The branch ref MAY be
  deleted afterward; the merge commit preserves branch topology.
- **Trunk workflow:** state direct-commit permission only when project evidence or the
  user explicitly selects it. Preserve its real verification and commit rules.

Do not combine PR/MR and no-PR requirements. “Keep branch history” means preserving
topology with a merge commit; it does not require retaining the branch ref forever.
