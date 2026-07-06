# Template: `docs/domain-models.md`

Data-model and business-mechanism reference. This is the doc that reviewers and AI agents
cite before touching domain behavior, so precision beats coverage: document what the code
actually does today, flag what is deprecated, and never describe intended behavior as
current behavior.

**Applicability:** generate this doc only when the project has a non-trivial data model
(more than a couple of entities, or any business mechanism worth explaining). A stateless
proxy or a tiny CLI records its few types in `project-overview.md` §5 and skips this file.

---

## Frontmatter (verbatim shape)

```markdown
# Domain Models & Business Mechanisms

> **Type:** Reference            <!-- "Reference Index" if the index variant -->
> **Audience:** Developers, AI assistants, code reviewers
> **Last updated:** YYYY-MM-DD

---
```

## Pick a variant (by expected size)

| Variant | When | Shape |
|---|---|---|
| **Self-contained** (default) | Expected < ~500 lines | Everything in one file |
| **Index + `docs/domain/`** | ≥ ~500 lines, or ≥ ~4 clearly separable topics | `domain-models.md` becomes a short index; per-topic deep-dives live in `docs/domain/<topic>.md` |
| **Hybrid** | Foundational sections are small but a few topics are huge | Keep §1 Model Details (+ ER map) inline; split only the oversized topics into `docs/domain/` |

An existing doc that outgrows ~500 lines SHOULD be migrated to the index variant —
move topics out, keep an index table behind.

## Self-contained skeleton

```markdown
## 1. Model Details
### <ModelA>
### <ModelB>            <!-- one ### per model/entity, schema-backed field notes -->
## 2. <Core mechanism>   <!-- one ## per business mechanism, numbered -->
## 3. <Core flow>        <!-- e.g. checkout flow, sync pipeline, state machines -->
...
## N-1. Deprecated Components
## N. Developer Tooling / Maintenance Scripts
```

Per-model `###` blocks cover: purpose (1–2 sentences), key fields/columns worth knowing,
associations, state machine (if any — show states + transitions), and a bold status note
when deprecated/unused (`> **⚠️ Deprecated (Unused):** ... Do not add new code that
depends on this model.`).

## Index variant skeleton

```markdown
## Document Map

| Topic | File | Covers |
|---|---|---|
| <Topic A> | [domain/<topic-a>.md](domain/<topic-a>.md) | <one-line summary> |
...

## 1. Model Map        <!-- optional: keep the ER diagram + thin model table inline -->
```

Each `docs/domain/<topic>.md` reuses the same frontmatter (optionally with
`> **Parent doc:** [../domain-models.md](../domain-models.md)`), numbered `## 1..N`
sections, ~200–600 lines.

## ASCII entity-relationship diagram (use this style, not mermaid)

```
┌────────────┐ 1     * ┌──────────────┐
│  Customer  │─────────│    Order     │
└────────────┘         └──────┬───────┘
      │ 1                     │ 1
      │ *                     ▼ *
┌────────────┐         ┌──────────────┐
│  Address   │         │  OrderItem   │
└────────────┘         └──────────────┘
```

Simpler arrow form is also fine for small models:
`Customer 1──* Order`, `Order 1──* OrderItem`.

## Writing rules

- Field/association claims come from the schema and model files read this session —
  not from memory of similar projects.
- State machines: enumerate states and events from the actual definitions (state-machine
  library blocks, enum columns, status constants), including guard conditions that block
  transitions.
- Business mechanisms: describe trigger → steps → side effects, naming the classes/functions
  involved so readers can jump to code.
- Deprecated ≠ deleted: keep documenting deprecated models that still exist in the schema,
  with an explicit "do not build on this" warning and (if known) the migration target.
- Greenfield (Mode G): if the user has a data-model draft, capture it here marked
  `(planned — no schema yet)`; otherwise skip this file until models exist.
