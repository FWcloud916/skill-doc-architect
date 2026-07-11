# Stack: Flutter

> **Detection:** `pubspec.yaml` at the repo root — checked BEFORE `package.json`.
> **UI surface:** yes — offer the `DESIGN.md` module (see `design-template.md`).

## Discovery map

| Overview § | Source of truth |
|---|---|
| §2 versions | `pubspec.lock`, SDK constraint in `pubspec.yaml` |
| §5/§9 models & data | model classes; drift/sqflite/hive/isar |
| §6 interface | `MaterialApp` routes / `go_router` config, `Navigator` calls |
| §7 background work | `workmanager`/`background_fetch`, `firebase_messaging` |

Facet notes: §3 — state-management approach (bloc/riverpod/provider) + platform-channel
boundary; §8 — consumed backend APIs + third-party SDKs; §10 — build flavors, signing
(`android/` + `ios/` configs), store release.

## Diff → doc section map

| Changed path | Re-verify |
|---|---|
| routes/navigation (`go_router` config, `Navigator` calls) | project-overview §6 |
| model classes, drift/sqflite/hive/isar definitions | project-overview §5, §9; domain-models §1 |
| `pubspec.yaml`/`pubspec.lock` | project-overview §2 |
| `android/`/`ios/` configs, signing/release setup | project-overview §10 |
| theme/token sources (`ThemeData`/`ColorScheme`/`TextTheme`, `ThemeExtension`s) | DESIGN.md tokens + matching prose — when the design module was selected |

## Linter signals

Config: `analysis_options.yaml`. Pre-merge: `dart analyze`,
`dart format --output=none --set-exit-if-changed .`.

## Minimal test gate

Built-in `flutter test`, one widget test.

## Command safety notes

SAFE probes (audit-checklist §5): `flutter --version`, `dart --version`,
`dart analyze --help`-level probes. NOT SAFE — static check only: `flutter pub get`,
`flutter build`, platform-side `pod install` / `./gradlew` invocations.
