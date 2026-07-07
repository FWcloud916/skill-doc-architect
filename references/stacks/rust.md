# Stack: Rust

> **Detection:** `Cargo.toml` at the repo root (package or workspace) and no
> `src-tauri/` directory (that combination is Tauri). Also a dedicated backend
> manifest for hybrid resolution (see the index): `Cargo.toml` + `package.json`
> → Rust is primary, package.json classified by role.

## Discovery map

| Overview § | Source of truth |
|---|---|
| §2 versions | `Cargo.toml`/`Cargo.lock`, `rust-version` field |
| §5/§9 models & schema | struct definitions; diesel/sqlx/sea-orm `migrations/` |
| §6 interface | HTTP routes (axum/actix-web/rocket/warp router setup); clap CLI commands; or the lib's pub API / napi/pyo3 binding exports |
| §7 background work | tokio spawned tasks/loops, cron crates |

Facet notes: §8 — API-client crates, SDK deps in `Cargo.toml`; §10 — release
profiles, Dockerfile, CI/CD.

## Diff → doc section map

| Changed path | Re-verify |
|---|---|
| router setup / handlers / CLI command definitions | project-overview §6 |
| struct definitions, `migrations/` | project-overview §5, §9; domain-models §1 + ER |
| tokio tasks, cron setup | project-overview §7 |
| `Cargo.toml`, `rustfmt.toml`/`clippy.toml` | project-overview §2; coding-style §1–2 |

## Linter signals

Config: `rustfmt.toml`, `clippy.toml`. Pre-merge: `cargo fmt --check` (safe,
read-only); `cargo clippy` (static check only, audit-checklist §5).

## Minimal test gate

Built-in `cargo test`, one `#[test]` (static-check only per audit-checklist §5).

## Command safety notes

SAFE probes (audit-checklist §5): `cargo --version`, `rustc --version`,
`cargo fmt --check`. NOT SAFE — static check only: `cargo build`/`cargo test`/
`cargo clippy` (download and compile crates).
