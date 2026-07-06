# Template: `docs/project-overview.md`

Skeleton + per-section writing guidance for a project's `project-overview.md`.
The 10 numbered sections below are **fixed** — keep the numbering stable even when a
section barely applies (write `N/A — <reason>` instead of deleting), because other docs,
AGENTS.md files, and reviews cite sections by number (e.g. "§6 API Structure").

Typical length: 300–600 lines for a brownfield service. Greenfield projects start much
shorter — full structure, many sections `TBD — not yet designed` (see Greenfield notes
at the bottom).

---

## Frontmatter (verbatim shape)

```markdown
# <Project Name> — Project Overview

> **Type:** Explanation
> **Audience:** Developers, AI assistants, and any tooling that needs project context
> **Last updated:** YYYY-MM-DD
>
> <One-line purpose. Optionally: Related docs: [domain-models.md](domain-models.md), ...>

---
```

## Section skeleton

```markdown
## 1. Purpose
### 1.1 Core Responsibilities
### 1.2 Relationship with Other Systems
### 1.3 Deprecated / Retired or Not-Yet-Enabled Features
## 2. Tech Stack
## 3. Architecture Overview
### Key Principles
## 4. Directory Structure
## 5. Domain Models (High-Level)
### Core Entity Relationships
### Model Details
## 6. API / Interface Structure
## 7. Background Jobs & Scheduled Tasks
## 8. External Service Integrations
## 9. Database / Data Stores
## 10. Environments & Deployment
### Environments
### Deployment Pipeline
### Configuration Hierarchy
```

## Per-section guidance (what to write, where the truth lives)

Read the listed sources before writing — never infer a claim you cannot trace to a file
you read in this session (or, for greenfield, to a decision the user stated).

| § | Write | Generic source of truth |
|---|---|---|
| 1 Purpose | What the project owns; who calls it / what it calls; deprecated features worth flagging | `README.md`, entrypoints, outbound-client code, org/workspace-level docs |
| 2 Tech Stack | Language + framework with pinned versions, datastore, queue/cache, key dependencies with their role. Greenfield: record the chosen stack **and the rationale for the choice** | dependency manifest **and lockfile** (see per-stack table), version files (`.ruby-version`, `.nvmrc`, `.python-version`, `go.mod`) |
| 3 Architecture | Request/message flow through the layers; 3–6 Key Principles bullets (layering rules, "X never calls Y"). Greenfield: record the chosen architecture shape and why | source tree layout, existing style docs |
| 4 Directory Structure | Annotated tree of the main source dir, one-line comment per dir/notable file — usually the longest section | `ls -R` the source tree yourself; annotate from actual file contents |
| 5 Domain Models | ASCII entity-relationship diagram (fenced code block, NOT mermaid) + one short paragraph per model. Deep detail goes to `domain-models.md` — link it | model/entity definitions, schema |
| 6 API / Interface | One subsection per surface (public API versions, internal API, callbacks/webhooks, health checks, admin UIs); route table per surface. For non-HTTP projects: CLI commands, event topics, exported functions | router/routes file, handler registrations, CLI arg parser |
| 7 Background Jobs | Worker/job table (name, queue, purpose) + scheduled task table | worker/job source dir, cron/schedule config, CI schedule |
| 8 External Integrations | Other internal services called (via which client class) + third-party services (cloud, payment, messaging…) | API-client/tool wrapper dir, settings files, SDK deps in manifest |
| 9 Database | Engine, extensions, replica topology, key-table summary (table, purpose, notable indexes). `N/A — <reason>` if the project owns no datastore | schema file / migrations, database config |
| 10 Environments | Full environment list — do not assume just dev/test/prod; enumerate what the config actually defines — plus deploy pipeline and settings/secrets hierarchy | env config dir, `Dockerfile`/compose, CI/CD config, IaC files |

## Per-stack source map

| Stack (signal) | §2 versions | §6 interface | §5/§9 models & schema | §7 jobs |
|---|---|---|---|---|
| Rails (`Gemfile`) | `Gemfile.lock`, `.ruby-version` | `config/routes.rb` | `app/models/`, `db/schema.rb` | `app/workers|jobs/`, `config/schedule.rb`, `config/sidekiq.yml` |
| Go (`go.mod`) | `go.mod`, `Makefile` | router setup in `main.go` / handler packages | struct definitions, `migrations/` | goroutine loops, cron libs |
| Node (`package.json`) | lockfile, `.nvmrc`, `engines` | Express/Nest/Next route definitions | ORM models (Prisma schema, TypeORM entities) | Bull/Agenda queues, `node-cron` |
| Python (`pyproject.toml`) | lockfile, `.python-version` | FastAPI/Django/Flask routers, `urls.py` | Django models / SQLAlchemy / Pydantic | Celery tasks, `celery beat` config |
| Serverless (`serverless.yml`/`template.yaml`) | the manifest + runtime deps | **function → trigger (event source) table** from the manifest | handler payload types | `schedule:` events in the manifest |
| Unknown stack | README + whatever manifest exists | grep for port binding / server start / `main` | grep for schema/DDL/entity keywords | grep for cron/queue/worker keywords |

## Writing rules

- Every table row must be traceable to a file read in this session; when a source is
  missing or contradictory, ask the user instead of guessing.
- Prefer tables for enumerable facts (routes, workers, tables); prose for flows and rationale.
- Link to code with relative paths (`../app/models/foo.rb`) so links work in the repo browser.
- Mark deprecated/not-yet-enabled features inline with a bold status note — these are the
  facts that rot first and mislead hardest.

## Greenfield notes (Mode G)

- Keep the full 10-section skeleton. Sections with no decision yet get
  `TBD — not yet designed`, which is a factual statement, not a placeholder to be
  quietly forgotten — list all TBD sections in the hand-off summary.
- §2 and §3 are where decisions from the interview/advisory step land: record **what was
  chosen and why** (including alternatives that were considered and rejected, one line
  each). This rationale is the part future maintainers can't reconstruct from code.
- §4 records the *planned* directory layout if one was agreed; mark it
  `(planned — not yet created)` until the tree exists.
