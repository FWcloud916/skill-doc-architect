# Audit Checklist & Diff→Section Mapping

Used by Mode U-1 (diff-driven update) to locate affected sections, and by Mode U-2
(full audit) / Mode B self-check to verify the doc set against the code.

---

## 1. Diff path → doc section mapping (Mode U-1)

Map each changed path to the sections to re-verify. The first table uses Rails shapes as
the reference example; the per-stack table below gives the equivalents, and the per-stack
source map in `project-overview-template.md` covers anything not listed.

| Changed path | Re-verify |
|---|---|
| `config/routes.rb` (routers, handler registration) | project-overview §6 |
| `db/schema.rb`, `db/migrate/` (schema, migrations) | project-overview §9; domain-models ER + field notes |
| `app/models/` (entities) | project-overview §5; domain-models §1 Model Details + affected mechanisms |
| `app/workers/`, `app/jobs/`, schedule/cron config | project-overview §7 |
| `app/services/` (business logic) | domain-models mechanism/flow sections naming those classes |
| API-client wrappers / external-integration layer | project-overview §8; domain-models integration sections |
| `app/controllers/`, handlers | project-overview §6; domain-models flow sections if behavior changed |
| Dependency manifest/lockfile (major bumps or new key deps only) | project-overview §2 |
| Settings/env config | project-overview §8, §10 |
| `Dockerfile`, CI/CD config, environment definitions | project-overview §10 |
| Linter config | coding-style §1–2 (and §6 if commands changed) |
| Setup/run/test commands (Makefile, package scripts, CI) | README Quickstart; AGENTS.md Commands |
| New/changed query shape (`WHERE`/`JOIN`/`ORDER BY`/pagination) on a hot table | db-observation is the *process* doc — don't edit it; check the diff followed it |
| Any other source dir (mailers, serializers, decorators, project-specific layers…) | grep the docs for the changed class/file names — re-verify every section that mentions them, plus the §4 directory-structure annotation for that dir |

### Per-stack equivalents

| Changed path | Stack | Re-verify |
|---|---|---|
| `main.go` / handler package (router setup) | Go | project-overview §6 |
| struct definitions | Go | project-overview §5; domain-models §1 Model Details |
| `migrations/` | Go | project-overview §9; domain-models ER + field notes |
| goroutine loops, cron libs | Go | project-overview §7 |
| `go.mod`, `.golangci.yml` | Go | project-overview §2; coding-style §1–2 |
| route/controller definitions (Express/Nest/Next, FastAPI/Django `urls.py`) | Node / Python | project-overview §6 |
| ORM models (Prisma schema, TypeORM entities, Django models, SQLAlchemy) | Node / Python | project-overview §5, §9; domain-models §1 |
| queue/task definitions (Bull/Agenda, Celery + beat config) | Node / Python | project-overview §7 |
| `serverless.yml` / `template.yaml` `functions:` | Serverless | project-overview §6 (function → trigger table) |
| `schedule:` events in the manifest | Serverless | project-overview §7 |
| handler payload types | Serverless | project-overview §5 |
| manifest + runtime deps | Serverless | project-overview §2 |

After the mapped edits, list any section the diff did **not** touch but that reads as
semantically related (e.g. a flow description mentioning a renamed class) — report these
even if you don't edit them.

## 2. Machine-checkable invariants (Mode U-2 / Mode B self-check)

Run per file; each check is a grep/ls-level comparison, not a judgment call.

**Every canonical doc file (`docs/*.md`, `docs/domain/*.md`)**
- [ ] Frontmatter present and complete: `# <Project> — <Doc>` title, `> **Type:**`,
      `> **Audience:**`, `> **Last updated:** YYYY-MM-DD`
- [ ] `Last updated` is a valid date, not in the future
- [ ] Relative links resolve (`docs/domain/*.md` targets exist; `../app/...` paths exist)
- [ ] RFC 2119 keywords are uppercase where used normatively

**README.md**
- [ ] Quickstart commands exist in the project's real config (CI / Makefile / package scripts)
- [ ] Documentation table rows point at files that exist
- [ ] Project-structure tree matches the actual top-level dirs

**AGENTS.md**
- [ ] Under ~60 lines
- [ ] Task→doc table only lists docs that exist (no dead links, no missing generated docs)
- [ ] Commands exist in the project's real config
- [ ] If `CLAUDE.md`/`GEMINI.md` exist they are symlinks to `AGENTS.md`, not divergent copies

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

**Scope guard**
- [ ] No edits outside the generated file set (README.md, AGENTS.md + its symlinks, the
      canonical `docs/` files, `docs/domain/`). Pre-existing scratch/memo/pending
      directories and any other non-canonical files under `docs/` are untouched.

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

Fix only after the user confirms — unless they asked for fix-directly up front. Bump each
file's `Last updated` only if its content actually changed.
