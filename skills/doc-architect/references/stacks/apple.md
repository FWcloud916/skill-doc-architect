# Stack: Apple (iOS/macOS)

> **Detection:** `*.xcodeproj`/`*.xcworkspace`, `Package.swift`, or `Podfile`.
> Read the platform (iOS vs macOS vs both) from the deployment target/SDK in the
> project settings — the facets below differ per platform.
> **UI surface:** yes — offer the `DESIGN.md` module (see `design-template.md`).

## Discovery map

| Overview § | Source of truth |
|---|---|
| §2 versions | `Package.resolved`/`Podfile.lock`, deployment target in project settings |
| §5/§9 models & data | model types; Core Data `.xcdatamodeld`/SwiftData/Realm |
| §6 interface | screens/windows + navigation: SwiftUI `App`/`Scene`, storyboards, coordinators; `NSWindow`/menu bar (macOS) |
| §7 background work | `BGTaskScheduler` + `Info.plist` background modes, push (iOS); login items, `launchd` agents (macOS) |

Facet notes: §8 — consumed backend APIs + third-party SDKs; §10 — signing +
App Store/TestFlight (iOS); notarization + DMG + Sparkle updates (macOS).

## Diff → doc section map

| Changed path | Re-verify |
|---|---|
| screens/navigation (SwiftUI scenes, storyboards, coordinators) | project-overview §6 |
| model types, `.xcdatamodeld`/SwiftData/Realm definitions | project-overview §5, §9; domain-models §1 |
| `Info.plist`, entitlements, Xcode project settings | project-overview §2, §7 (background modes), §10 (signing; macOS: notarization) |
| API-client layer, SDK config | project-overview §8 |
| signing/release config (`fastlane/`, provisioning, store metadata) | project-overview §10 |
| theme/token sources (asset-catalog `.colorset`s, `Color`/`Font` extensions) | DESIGN.md tokens + matching prose — when the design module was selected |

## Linter signals

Config: `.swiftlint.yml`, `.swift-format`. Pre-merge: `swiftlint`,
`swift-format lint -r Sources/`.

## Minimal test gate

XCTest target, run via `xcodebuild test`.

## Command safety notes

SAFE probes (audit-checklist §5): `xcodebuild -list` (reads project metadata only),
`swiftlint --version`, `swift --version`. NOT SAFE — static check only:
`xcodebuild build`/`test` (compiles; may resolve packages), `pod install`, archive/
notarization steps.
