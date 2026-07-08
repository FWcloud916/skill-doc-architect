# Template: `docs/db-observation.md`

How-to for validating index/query decisions with evidence when query shape changes on a
hot table. **Applicability rule:** only generate this doc for projects that own a
server-side relational datastore. If the project has no DB of its own, skip the file and
record `N/A — <reason>` in `project-overview.md` §9. A client-embedded store (SQLite /
Core Data / Room / electron-store in a mobile, desktop, or frontend app) does not
qualify — this doc is about
observing a server-owned datastore; record the local store in `project-overview.md` §9
instead. Greenfield (Mode G): skip until a schema exists and real query patterns can be
observed.

---

## Frontmatter (verbatim shape)

```markdown
# db-observation

> **Type:** How-to
> **Audience:** Developers, AI assistants, code reviewers
> **Last updated:** YYYY-MM-DD
>
> Practical database observation helpers (<engine>) for validating index decisions and
> sharing evidence during reviews.
```

## Section skeleton

```markdown
## When to use this
## Picking an index type (when you decide to add one)
## Console scripts (copy/paste)
## Monitoring dashboards (screenshots checklist)
## How to reply back (minimum)
```

## How to fill each section

- **When to use this** — two bullets: (1) you changed query patterns
  (`WHERE`/`JOIN`/`ORDER BY`/pagination) and need evidence to justify adding or deferring
  an index; (2) local data is not representative and you need production/replica validation.
- **Picking an index type** — table of index types offered by the project's engine mapped
  to query shapes (for PostgreSQL: btree / partial / composite / GIN / BRIN…). State the
  team rule: when a diff changes query shape on a large or high-QPS table, add the matching
  index **in the same migration**, or defer only with written justification (expected data
  size / QPS + what will be monitored after deploy).
- **Console scripts** — 3–4 copy/paste snippets in the project's console idiom
  (Rails console, `psql`, a Go/Python REPL helper), each with realistic **table names from
  this project's schema**:
  1. `EXPLAIN (ANALYZE, BUFFERS)` for a representative query
  2. table + index sizes
  3. index usage stats (`pg_stat_user_indexes` or engine equivalent)
  4. slow-query stats (`pg_stat_statements` or engine equivalent)
- **Monitoring dashboards** — where the team actually looks (Datadog DBM, RDS Performance
  Insights, Grafana…): which panels to screenshot for a review. Ask the user if unknown —
  do not invent dashboards.
- **How to reply back** — the minimum evidence block to paste into a review: query, plan
  before/after, row estimates vs actuals, index chosen and why.
