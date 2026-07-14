# Stack: Tauri

> **Detection:** `package.json` with `@tauri-apps/api`/`@tauri-apps/cli` in
> dependencies + devDependencies, or a `src-tauri/` directory — checked BEFORE the
> frontend-framework signal (the frontend depends on react/vue too).
> **Design surface:** inherent — offer the `DESIGN.md` module (see `design-template.md`).

## Discovery map

| Overview § | Source of truth |
|---|---|
| §2 versions | lockfile + `src-tauri/Cargo.toml`/`Cargo.lock`, `tauri.conf.json` |
| §5/§9 models & data | frontend stores; tauri-plugin-store/-sql, app-data dirs |
| §6 interface | windows in `tauri.conf.json` + frontend routes; **`#[tauri::command]` fns are a §6 surface** |
| §7 background work | Rust-side threads/async tasks, updater config |
| Design-surface evidence | frontend routes/components plus CSS/theme/token sources |

Facet notes: §3 — frontend + Rust command-layer architecture (the IPC boundary);
§8 — consumed backend APIs + third-party SDKs + the update server;
§10 — `tauri.conf.json` bundle targets, signing, updater config.

## Diff → doc section map

| Changed path | Re-verify |
|---|---|
| `src-tauri/` code (`#[tauri::command]`s, window setup, plugins) | project-overview §3, §6 |
| frontend `components/`, `store/`, routes | project-overview §3, §5, §6 |
| local persistence (tauri-plugin-store/-sql schemas) | project-overview §9; domain-models §1 |
| `tauri.conf.json`, `src-tauri/Cargo.toml` | project-overview §2, §10 (bundle/signing/updater) |
| frontend theme/token sources (tailwind config, `:root` CSS custom properties, theme objects) | DESIGN.md tokens + matching prose — when the design module was selected |

## Linter signals

Frontend: `eslint.config.js` / `.eslintrc*`, `.prettierrc*`; prefer a real package
script, otherwise a confirmed local binary such as `./node_modules/.bin/eslint .`.
Rust side: `rustfmt.toml`, `clippy.toml` — `cargo fmt --check` (safe, read-only);
`cargo clippy` (static check only, audit-checklist §5).

## Minimal test gate

`cargo test` in `src-tauri` (static-check only per audit-checklist §5) + vitest/jest
on the frontend.

## Command safety notes

SAFE probes (audit-checklist §5): `cargo --version`, `rustc --version`,
`cargo fmt --check`; after confirming it exists, `./node_modules/.bin/vitest list`.
NOT SAFE — static check only: on-demand package runners,
`cargo build`/`cargo test`/`cargo clippy` (download and compile crates),
`tauri build`, signing/updater steps.
