# Template: `PROGRESS.md` (agent-harness state module)

Cross-session state for AI agents working in the repo. The repo is the system of record:
a fresh session MUST be able to recover what is done, what is active, and what is next
from this file alone — never from chat history. This is the file that answers Fresh
Session Test Q5 (`audit-checklist.md` §6).

**Applicability:** generate only when the project is (or will be) actively developed by
AI agents across sessions, and only with the user's explicit opt-in — it creates a
maintenance duty (the AGENTS.md session routine). Mode G: offer it, recommended default.
Mode B: offer it when agent-driven development is stated or evident. Skipped → one-line
reason in the module-selection report, like any other module.

**Location: repo root**, next to `AGENTS.md` — it is harness state, not documentation,
so it does NOT live under `docs/` and does NOT use the docs frontmatter convention.

---

## Skeleton

```markdown
# <Project Name> — Progress

> **Last session:** YYYY-MM-DD · commit `<short-hash>` · tests: <passing | failing | not run>

## Now (WIP = 1)

<the single active work unit, or `none`>

## Feature list

| # | Behavior | Verify with | State |
|---|---|---|---|
| 1 | <observable behavior, in user terms> | `<command>` | not_started |

## Done

## Blockers

## Next steps

## Decision log

<one line per decision, newest first — rationale lives in
 [docs/project-overview.md](docs/project-overview.md) §2–3; link, don't duplicate>
```

## Writing rules

- **The header is evidence, not hope**: the commit hash comes from `git log -1`; the
  test status comes from a suite actually run in that session — `not run` is honest,
  "should pass" is banned.
- **WIP = 1**: at most one Feature-list row in state `active` at any time. One work
  unit is finished and verified before the next starts.
- **States** are exactly `not_started | active | blocked | passing`. A row transitions
  to `passing` only after its `Verify with` command passed **in the current session** —
  "code written" is not `passing`; Definition of Done = verification passed.
- **`Verify with` commands are real** — same rule as README commands: copied from CI /
  Makefile / package scripts, never invented. Greenfield: `TBD` until tooling exists.
- **Seed the verification gate first**: when the project has no runnable test gate
  (`audit-checklist.md` §6 Verification-gate warning), Feature-list **row 1** MUST be
  `Establish verification gate — <stack's suggested minimal gate>`, with `Verify with`
  set to `TBD → becomes the project's test command` and state `not_started`. When a
  working agent completes it: that row's `Verify with` gets the real command, and the
  `<test command>` in AGENTS.md Commands and Hard constraints is updated to match
  (per the Docs maintenance rules). Until the gate exists, the session routine's
  clock-in "run the test command" step is naturally skipped — the header's tests field
  honestly reads `not run`.
- **This skill generates the skeleton and the initial seed only** (Mode G: Feature list
  and Next steps from the interview's task breakdown; Mode B: current state as read from
  the repo). Ongoing maintenance belongs to the project's working agents via the
  AGENTS.md session routine — not to this skill. It never writes test files — it seeds
  the work item, not the test code.

## Coupling with AGENTS.md

When this module is selected, the AGENTS.md **Session routine** block
(`agents-md-template.md`) MUST be included, and "update PROGRESS.md at clock-out" is a
strong Hard-constraints candidate. Do NOT add PROGRESS.md to the task→doc routing
table — it belongs to the session routine, not to task routing.

---

## The skill's own state file (Mode B resumability)

For large repos where discovery + generation won't fit one session, Mode B keeps its own
progress at `docs/.doc-architect-state.md`:

```markdown
# doc-architect — Mode B state (DELETE when Mode B completes)

> Started: YYYY-MM-DD · mode: B<(merge)> · stack: <detected> · target: <repo purpose, one line>

## Discovery reading

- [x] README                 - [x] manifest + lockfile
- [ ] routes/entrypoints     - [ ] schema + models
- [ ] workers/jobs           - [ ] integrations + settings
- [ ] env/Docker/CI

## Docs (WIP = 1)

| Doc | State |
|---|---|
| README.md | passing (self-checked YYYY-MM-DD) |
| AGENTS.md | active |
| docs/project-overview.md | not_started |

## Open questions

<numbered; or "none">
```

Rules:

- Create it only when the run will span sessions; write it before ending an unfinished
  session (the skill practicing its own clock-out).
- At session start, if this file exists, offer to resume from it; trust `passing` rows
  but cheaply re-run their §2 invariants (`audit-checklist.md`).
- Tell the user not to commit it — this skill MUST NOT edit `.gitignore` (scope guard).
- **Delete it when Mode B completes.** A leftover state file after completion is an
  audit finding (clean-state check, `audit-checklist.md` §2 Scope guard block).
