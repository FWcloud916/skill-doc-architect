# Stack: React Native

> **Detection:** `package.json` with `react-native` or `expo` in dependencies +
> devDependencies — the FIRST `package.json` check, before Electron/Tauri and the
> server/frontend framework checks.

## Discovery map

| Overview § | Source of truth |
|---|---|
| §2 versions | lockfile, `app.json`/`app.config.*`, `ios/` + `android/` configs |
| §5/§9 models & data | store shapes + local persistence (AsyncStorage, SQLite, WatermelonDB) |
| §6 interface | navigation graph: `@react-navigation` navigators, expo-router `app/` |
| §7 background work | background tasks (expo-task-manager, headless JS), push config |

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

## Linter signals

Config: `eslint.config.js` / `.eslintrc*`, `.prettierrc*`, `biome.json`.
Pre-merge: `npx eslint .`, `npx prettier --check .`.

## Minimal test gate

jest (`jest-expo`/`react-native` preset), one component test.

## Command safety notes

SAFE probes (audit-checklist §5): `node --version`, `npx jest --listTests`.
NOT SAFE — static check only: `npm install`, native builds (`pod install`, any
`./gradlew` invocation), EAS builds.
