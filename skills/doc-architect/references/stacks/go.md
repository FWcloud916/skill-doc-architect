# Stack: Go

> **Detection:** `go.mod` at the repo root.

## Discovery map

| Overview § | Source of truth |
|---|---|
| §2 versions | `go.mod`, `Makefile` |
| §5/§9 models & schema | struct definitions, `migrations/` |
| §6 interface | router setup in `main.go` / handler packages |
| §7 background work | goroutine loops, cron libraries |

Facet notes: §8 — API-client packages, SDK modules in `go.mod`; §10 — env config,
Dockerfile, CI/CD, Makefile deploy targets.

## Diff → doc section map

| Changed path | Re-verify |
|---|---|
| `main.go` / handler packages (router setup) | project-overview §6 |
| struct definitions | project-overview §5; domain-models §1 |
| `migrations/` | project-overview §9; domain-models ER + field notes |
| goroutine loops, cron libs | project-overview §7 |
| `go.mod`, `.golangci.yml` | project-overview §2; coding-style §1–2 |

## Linter signals

Config: `.golangci.yml`, Makefile lint target. Pre-merge: `golangci-lint run`, `gofmt -l .`.

## Minimal test gate

Built-in `go test ./...`, one `_test.go`.

## Command safety notes

SAFE probes (audit-checklist §5): `go version`, `go test -list '.*' ./...`, `gofmt -l .`,
`make -n <target>`. NOT SAFE — static check only: `go build` on network-fetching setups,
migrations, deploy targets.
