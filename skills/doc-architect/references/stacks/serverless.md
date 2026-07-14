# Stack: Serverless

> **Detection:** `serverless.yml` or `template.yaml` at the repo root.
> **Design surface:** conditional — offer `DESIGN.md` only when the evidence row matches.

## Discovery map

| Overview § | Source of truth |
|---|---|
| §2 versions | the manifest + runtime deps |
| §5/§9 models & schema | handler payload types |
| §6 interface | **function → trigger (event source) table** from the manifest |
| §7 background work | `schedule:` events in the manifest |
| Design-surface evidence | project-owned static site/app assets, templates, styles, theme/token sources |

Facet notes: §8 — SDK clients in handler code, resources/permissions in the manifest;
§10 — stages in the manifest, deploy pipeline, IaC files.

## Diff → doc section map

| Changed path | Re-verify |
|---|---|
| `functions:` in the manifest | project-overview §6 (function → trigger table) |
| `schedule:` events | project-overview §7 |
| handler payload types | project-overview §5 |
| manifest + runtime deps | project-overview §2 |
| project-owned web/static theme, style, or token sources | DESIGN.md tokens + matching prose — when the design module was selected |

## Linter signals

Per runtime language — follow the matching language's linter config (JS/TS: eslint;
Python: ruff; Go: golangci-lint).

## Minimal test gate

At least one locally runnable invoke/verify path (e.g. `serverless invoke local`,
`sam local invoke` — these are NOT SAFE to execute; static check only).

## Command safety notes

SAFE probes (audit-checklist §5): `serverless --version`, `sam --version`, runtime
version probes. NOT SAFE — static check only: deploys, `sam build`, local invokes
(may pull container images).
