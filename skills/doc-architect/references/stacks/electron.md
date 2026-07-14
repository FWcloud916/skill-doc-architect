# Stack: Electron

> **Detection:** `package.json` with `electron` in dependencies + devDependencies —
> checked BEFORE the frontend-framework signal (the renderer depends on react/vue too).
> **Design surface:** inherent — offer the `DESIGN.md` module (see `design-template.md`).

## Discovery map

| Overview § | Source of truth |
|---|---|
| §2 versions | lockfile, `.nvmrc`, pinned `electron` version |
| §5/§9 models & data | renderer store shapes; electron-store, SQLite, `app.getPath('userData')` files |
| §6 interface | windows (`BrowserWindow`s) + renderer routes; **`ipcMain.handle` channels are a §6 surface** |
| §7 background work | tray/menubar tasks, main-process timers, auto-update checks |
| Design-surface evidence | renderer routes/components plus CSS/theme/token sources |

Facet notes: §3 — main/renderer process architecture + the IPC boundary;
§8 — consumed backend APIs + third-party SDKs + the update server;
§10 — packaging + signing + distribution: electron-builder/forge config, notarization
(macOS target), MSI/MSIX (Windows target), update channel.

## Diff → doc section map

| Changed path | Re-verify |
|---|---|
| main-process code (`ipcMain` handlers, window setup, preload scripts) | project-overview §3, §6 |
| renderer `components/`, `store/`, routes | project-overview §3, §5, §6 |
| local persistence (electron-store schema, SQLite) | project-overview §9; domain-models §1 |
| `electron-builder`/forge config | project-overview §2, §10 (packaging/signing/update channel) |
| renderer theme/token sources (tailwind config, `:root` CSS custom properties, theme objects) | DESIGN.md tokens + matching prose — when the design module was selected |

## Linter signals

Config: `eslint.config.js` / `.eslintrc*`, `.prettierrc*`, `biome.json`.
Prefer a real package script; otherwise use a confirmed local binary such as
`./node_modules/.bin/eslint .` or `./node_modules/.bin/prettier --check .`.

## Minimal test gate

vitest/jest on main + renderer units, one smoke test.

## Command safety notes

SAFE probes (audit-checklist §5): `node --version`; after confirming it exists,
`./node_modules/.bin/vitest list` or `./node_modules/.bin/jest --listTests`.
NOT SAFE — static check only: on-demand package runners, installs, packaging builds
(electron-builder/forge), notarization/signing steps.
