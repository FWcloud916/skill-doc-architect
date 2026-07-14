# Stack: React Native

> **Detection:** `package.json` with `react-native` or `expo` in dependencies +
> devDependencies — the FIRST `package.json` check, before Electron/Tauri and the
> server/frontend framework checks.
> **Design surface:** inherent — offer the `DESIGN.md` module (see `design-template.md`).

## Discovery map

| Overview § | Source of truth |
|---|---|
| §2 versions | lockfile, `app.json`/`app.config.*`, `ios/` + `android/` configs |
| §5/§9 models & data | store shapes + local persistence (AsyncStorage, SQLite, WatermelonDB) |
| §6 interface | navigation graph: `@react-navigation` navigators, expo-router `app/` |
| §7 background work | background tasks (expo-task-manager, headless JS), push config |
| Design-surface evidence | screens/components plus theme modules, StyleSheet constants, NativeWind config |

Facet notes: §3 — state-management approach + native-module boundary;
§8 — consumed backend APIs + third-party SDKs (analytics, push, payments);
§10 — build pipeline (EAS/fastlane), signing, app store release.

## Diff → doc section map

| Changed path | Re-verify |
|---|---|
| navigation config (`@react-navigation`, expo-router `app/`) | project-overview §6 |
| `components/`, `store/`, local persistence | project-overview §3, §5, §9; domain-models §1 |
| API-client layer, SDK config | project-overview §8 |
| `app.json`/`app.config.*`, `ios/`/`android/` configs | project-overview §2, §10 |
| signing/release config (fastlane, EAS profiles, store metadata) | project-overview §10 |
| theme/token sources (theme modules, NativeWind config, tamagui/restyle themes) | DESIGN.md tokens + matching prose — when the design module was selected |

## Linter signals

Config: `eslint.config.js` / `.eslintrc*`, `.prettierrc*`, `biome.json`.
Prefer a real package script; otherwise use a confirmed local binary such as
`./node_modules/.bin/eslint .` or `./node_modules/.bin/prettier --check .`.

## Minimal test gate

jest (`jest-expo`/`react-native` preset), one component test.

## Command safety notes

SAFE probes (audit-checklist §5): `node --version`; after confirming it exists,
`./node_modules/.bin/jest --listTests`. NOT SAFE — static check only: on-demand
package runners, installs, native builds (`pod install`, any
`./gradlew` invocation), EAS builds.
