# Stack: Electron

> **Detection:** `package.json` with `electron` in dependencies + devDependencies —
> checked BEFORE the frontend-framework signal (the renderer depends on react/vue too).

## Discovery map

| Overview § | Source of truth |
|---|---|
| §2 versions | lockfile, `.nvmrc`, pinned `electron` version |
| §5/§9 models & data | renderer store shapes; electron-store, SQLite, `app.getPath('userData')` files |
| §6 interface | windows (`BrowserWindow`s) + renderer routes; **`ipcMain.handle` channels are a §6 surface** |
| §7 background work | tray/menubar tasks, main-process timers, auto-update checks |

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

## Linter signals

Config: `eslint.config.js` / `.eslintrc*`, `.prettierrc*`, `biome.json`.
Pre-merge: `npx eslint .`, `npx prettier --check .`.

## Minimal test gate

vitest/jest on main + renderer units, one smoke test.

## Command safety notes

SAFE probes (audit-checklist §5): `node --version`, `npx vitest list`,
`npx jest --listTests`. NOT SAFE — static check only: `npm install`, packaging builds
(electron-builder/forge), notarization/signing steps.
