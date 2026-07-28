# Template: `CONTEXT.md`

The repo-root project glossary — the ruling on what things are called. It names the
project's own terms, the synonyms to avoid, and the ambiguities that were settled.
Opt-in module (doc-set table): generate only when the project has recurring terms of
its own — Mode B's term extraction finds them; Mode G's interview surfaces ≥3.

**Hard budget: keep the generated file under ~80 lines.** Value comes from ruling
density, not completeness — a term earns an entry only when misnaming it costs real
work. Past the budget, the least-consequential terms go first.

**Boundary with `docs/domain-models.md`:** CONTEXT.md owns naming — canonical term,
short definition, `_Avoid_:` synonyms, settled ambiguities. domain-models.md owns
structure — entities, fields, relationships, ER diagrams. A term living in both
links to its domain-models section by relative path instead of restating it;
restating is duplication and fails review.

**Rulings are decisions, not facts.** A canonical name and its Avoid list are chosen
by the user, never derived from the code alone. Interactive runs settle terms one at
a time (candidate + recommended ruling + one-line reason); headless runs mark every
candidate `proposed — pending ruling` and leave the decision open.

---

## Skeleton

```markdown
# <Project> — Context

<One sentence: what this project is, in its own words.>

## Language

**<Canonical term>** — <definition, ≤2 sentences; link structure to
[docs/domain-models.md](docs/domain-models.md) when that doc exists.>
_Avoid_: <synonym>, <synonym> — <one-line reason when not obvious>

**<Candidate term>** (proposed — pending ruling) — <observed meaning>.
_Avoid_: <observed drift synonyms>

## Relationships

- <Term A> <verb phrase> <Term B> — one line per relation, no diagrams.

## Flagged ambiguities

- "<word>" meant both <X> and <Y>; ruled <date>: <X>. <Y> is now "<term>".
```

## Writing rules

- Terms come from Mode B term extraction or the Mode G interview — never from generic
  stack vocabulary. `handler`, `service`, `controller`, `model`, `util`, `manager`
  and friends are stack words; defining them is noise, not context.
- **Synonym drift is the highest-value finding**: the same concept named differently
  in code and docs (code `Shipment`, docs `Delivery`). Record both spellings, rule
  one canonical, and list the loser under `_Avoid_:`.
- Every `_Avoid_:` entry is a drift tripwire: audit-checklist §2 greps the generated
  doc set for Avoid terms, and flags defined terms with zero occurrences across code
  and docs as orphans (stale).
- Like `DESIGN.md` and `PROGRESS.md`, `CONTEXT.md` lives at the repo root and is
  exempt from the `docs/` frontmatter convention.
