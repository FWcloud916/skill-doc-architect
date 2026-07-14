# Stack: Android

> **Detection:** `build.gradle`/`build.gradle.kts` **plus** `AndroidManifest.xml`
> (or the `com.android.application` plugin) — the manifest requirement keeps
> JVM-backend gradle repos in the unknown-stack fallback.
> **Design surface:** inherent — offer the `DESIGN.md` module (see `design-template.md`).

## Discovery map

| Overview § | Source of truth |
|---|---|
| §2 versions | `libs.versions.toml`, `build.gradle*` |
| §5/§9 models & data | data classes; Room entities/DAOs, DataStore |
| §6 interface | Activities/Fragments in the manifest; Compose `NavHost`/navigation XML |
| §7 background work | WorkManager workers, manifest services, FCM |
| Design-surface evidence | Compose/XML themes, `res/values/colors.xml`, screens/layouts |

Facet notes: §8 — consumed backend APIs + third-party SDKs (analytics, push, payments);
§10 — build variants/flavors, signing config, Play release.

## Diff → doc section map

| Changed path | Re-verify |
|---|---|
| navigation (Compose `NavHost`, navigation XML), Activities/Fragments | project-overview §6 |
| data classes, Room entities/DAOs, DataStore | project-overview §5, §9; domain-models §1 |
| `AndroidManifest.xml`, `build.gradle*`, `libs.versions.toml` | project-overview §2, §6, §7, §10 |
| API-client layer, SDK config | project-overview §8 |
| signing/release config (keystore refs, `fastlane/`, store metadata) | project-overview §10 |
| theme/token sources (`res/values/colors.xml`, `themes.xml`, Compose `MaterialTheme`) | DESIGN.md tokens + matching prose — when the design module was selected |

## Linter signals

Config: ktlint via `.editorconfig`, `detekt.yml`. Pre-merge: `./gradlew ktlintCheck`,
`./gradlew detekt` — gradle = static check only (audit-checklist §5).

## Minimal test gate

JUnit via `./gradlew test` (static-check only per audit-checklist §5).

## Command safety notes

SAFE probes (audit-checklist §5): `java -version`, checking the task exists in
`build.gradle*`. NOT SAFE — static check only: **any `./gradlew` invocation** (the
wrapper may download distributions and dependencies on first run).
