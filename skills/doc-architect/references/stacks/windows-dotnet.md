# Stack: Windows desktop (.NET)

> **Detection:** `*.sln`/`*.csproj` with desktop markers — `<UseWPF>`,
> `<UseWindowsForms>`, a `net*-windows` TFM, or WinUI/MAUI packages.
> A `.csproj` with `Microsoft.NET.Sdk.Web` or no desktop marker is out of scope —
> treat as unknown stack and say so.
> **Design surface:** inherent — offer the `DESIGN.md` module (see `design-template.md`).

## Discovery map

| Overview § | Source of truth |
|---|---|
| §2 versions | `*.csproj` TFM + `PackageReference`s, `global.json` |
| §5/§9 models & data | model classes; EF Core/SQLite, `%APPDATA%` files |
| §6 interface | windows/pages: XAML views + ViewModels, App manifest |
| §7 background work | `BackgroundService`/timers, tray icon, updater (Squirrel/MSIX) |
| Design-surface evidence | XAML views plus `ResourceDictionary`, Colors/Brushes/Styles |

Facet notes: §3 — MVVM (or equivalent) layering + the view/view-model boundary;
§8 — consumed backend APIs + third-party SDKs + the update server;
§10 — MSI/MSIX packaging, signing, distribution channel.

## Diff → doc section map

| Changed path | Re-verify |
|---|---|
| XAML views, ViewModels, App manifest | project-overview §6 |
| model classes, EF Core entities/migrations | project-overview §5, §9; domain-models §1 |
| `*.sln`/`*.csproj`, `global.json` | project-overview §2, §10 |
| packaging/signing config (MSIX manifest, installer scripts) | project-overview §10 |
| theme/token sources (XAML `ResourceDictionary`: `App.xaml`, `Themes/*.xaml`) | DESIGN.md tokens + matching prose — when the design module was selected |

## Linter signals

Config: `.editorconfig` (analyzer rules), `Directory.Build.props`.
Pre-merge: `dotnet format --verify-no-changes` (static check only, audit-checklist §5 —
implicit restore).

## Minimal test gate

xUnit/MSTest via `dotnet test` (static-check only per audit-checklist §5).

## Command safety notes

SAFE probes (audit-checklist §5): `dotnet --version`. NOT SAFE — static check only:
`dotnet build`/`dotnet test`/`dotnet format` (implicit restore touches the network),
packaging/signing steps.
