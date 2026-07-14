# Stack: VS Code extension

> **Detection:** `package.json` with an `engines.vscode` field (authoritative;
> usually accompanied by `@types/vscode`/`@vscode/vsce` in devDependencies) —
> checked after React Native / Electron / Tauri and BEFORE the server/frontend
> framework checks.
> **Design surface:** conditional — offer `DESIGN.md` only for project-styled webviews
> or custom editors; native VS Code commands/views alone use the host theme.

## Discovery map

| Overview § | Source of truth |
|---|---|
| §2 versions | lockfile, `engines.vscode`, `@types/vscode` version |
| §5/§9 models & data | extension state: `Memento` (workspaceState/globalState), secrets storage, on-disk caches |
| §6 interface | **the `contributes` block in package.json IS the interface table** (commands, views, menus, configuration) + activation events + webview panels |
| §7 background work | activation events, file watchers, language-server/child processes |
| Design-surface evidence | webview/custom-editor HTML, components, CSS, theme/token sources |

Facet notes: §3 — extension host vs webview split (message passing is the boundary);
§8 — VS Code API surface + external service SDKs; §10 — `vsce package`, marketplace
publishing, CI.

## Diff → doc section map

| Changed path | Re-verify |
|---|---|
| `contributes` block, activation events | project-overview §6 |
| webview source (`web/`, panel code) | project-overview §3, §6 |
| state storage (Memento keys, secrets) | project-overview §9; domain-models §1 if non-trivial |
| packaging/publish config (`.vscodeignore`, CI release) | project-overview §10 |
| webview/custom-editor CSS, theme, or token sources | DESIGN.md tokens + matching prose — when the design module was selected |

## Linter signals

Config: `eslint.config.js` / `.eslintrc*`, `.prettierrc*`, `biome.json`.
Prefer a real package script; otherwise use a confirmed local binary such as
`./node_modules/.bin/eslint .` or `./node_modules/.bin/prettier --check .`.

## Minimal test gate

vitest/jest unit tests on extension logic; `@vscode/test-electron` integration
tests are NOT SAFE to execute (downloads VS Code — static check only per
audit-checklist §5).

## Command safety notes

SAFE probes (audit-checklist §5): `node --version`; after confirming it exists,
`./node_modules/.bin/vitest list` or `./node_modules/.bin/jest --listTests`.
NOT SAFE — static check only: on-demand package runners, `vsce package`/`vsce publish`,
`@vscode/test-electron` runs.
