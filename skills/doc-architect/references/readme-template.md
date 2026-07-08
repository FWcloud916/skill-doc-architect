# Template: `README.md`

The human-first entry point to the repository. A newcomer (or a hiring manager, or a
future maintainer) should be able to answer three questions within one screen: *what is
this*, *how do I run it*, *where do I learn more*.

Division of labor with the sibling docs:

| File | Reader | Job |
|---|---|---|
| `README.md` | Humans arriving at the repo | Orientation + quickstart |
| `AGENTS.md` | AI coding agents | Signpost to the right doc for the task at hand |
| `docs/*` | Both, when depth is needed | The actual reference material |

The README does **not** duplicate `docs/` content — it links to it.

---

## Skeleton

```markdown
# <Project Name>

<One-sentence description: what it is and who it is for.>

## What it does

<2–5 bullets or a short paragraph: the core capabilities, in user terms.
 Optionally a small usage example (CLI invocation, API call, screenshot).>

## Quickstart

### Prerequisites
<Runtime + version, datastore, required accounts/keys — only what is truly required.>

### Setup
<Numbered install steps, copy-pasteable.>

### Run
<The command(s) to start it locally.>

### Test
<The command to run the test suite.>

## Project structure

<A short annotated tree — top-level dirs only, one line each. Deep detail lives in
 docs/project-overview.md §4; link it instead of expanding here.>

## Documentation

| Doc | What it covers |
|---|---|
| [docs/project-overview.md](docs/project-overview.md) | Architecture, directory map, integrations, environments |
| <other generated docs, one row each> | |

## License

<Only if the repo has a license file or the user states one. Omit the section otherwise.>
```

## Writing rules

- **Every command must be real**: copy commands from CI config, `Makefile`, or package
  scripts — verified to exist, not invented. Greenfield projects with no tooling yet
  write `TBD — tooling not set up yet` rather than aspirational commands.
- **The Test command is the verification gate**: it is what the audit executes
  (safe-command rules, `audit-checklist.md` §5) and what AGENTS.md points agents at for
  "done". It MUST come from real config.
- **PROGRESS.md is never listed in the Documentation table** — it is harness state, not
  documentation; AGENTS.md's session routine owns the pointer to it.
- **No marketing language.** "Fast, blazing, enterprise-grade" style adjectives are
  banned; describe capabilities factually.
- **One screen of orientation**: if a section grows past ~15 lines, the overflow
  probably belongs in `docs/` — move it and link.
- **Badges, logos, screenshots** are optional and user-supplied; never fabricate them.
- **Merge mode**: if a README already exists, treat it as the source of truth for tone
  and structure — only fill gaps (e.g. a missing Documentation section) after confirming
  with the user. Never rewrite an existing README wholesale without explicit approval.
