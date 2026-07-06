# Template: `AGENTS.md`

The AI-agent entry point for the repository. Its job is **routing, not content**: a
one-line project identity, a table that maps *the task an agent is about to do* to *the
doc it should read first*, the commands that must not be guessed, and the doc-maintenance
rules. Everything else lives in `docs/` — AGENTS.md points there.

**Hard budget: keep the generated file under ~60 lines.** If it is growing past that,
content is leaking in that belongs in `docs/` — move it and leave a link. An AGENTS.md
that tries to explain the architecture inline goes stale fast and gets skimmed, which
defeats its purpose.

---

## Skeleton

```markdown
# <Project Name> — Agent Guide

<One sentence: what this project is and what it owns.>

## Read before you work

Read the matching doc **before non-trivial work**. Small fixes (typos, single-line
edits, running tests) can skip; do not pre-load all docs.

| Task | Read first |
|---|---|
| Architecture, request flow, directory layout, integrations | [docs/project-overview.md](docs/project-overview.md) |
| Touching domain behavior, data models, state machines | [docs/domain-models.md](docs/domain-models.md) |
| Style, lint rules, error handling, layering conventions | [docs/coding-style.md](docs/coding-style.md) |
| Changing query shape (`WHERE`/`JOIN`/`ORDER BY`/pagination) on a hot table | [docs/db-observation.md](docs/db-observation.md) |

## Commands

```bash
<setup command>     # install dependencies
<test command>      # run the test suite
<lint command>      # lint / format check
```

## Conventions

- <2–4 bullets max: the rules an agent breaks most easily in THIS repo —
  e.g. commit message format, "never edit generated dir X", branch naming.>

## Docs maintenance

When modifying any file under `docs/`, update its `> **Last updated:** YYYY-MM-DD`
frontmatter to today's date. Requirement keywords (MUST, SHOULD, MAY) follow RFC 2119.
```

## Writing rules

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
