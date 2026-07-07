# Stack detection index

Routes a repository's manifest signals to stack files (routed from SKILL.md Mode B
step 1). Detection is two-phase: **collect** every signal present, then **resolve** —
never stop at the first manifest found.

## Phase 1 — Collect

Scan the repo root for every signal in the table below, plus monorepo markers:
`workspaces` in package.json, `pnpm-workspace.yaml`, `lerna.json`, `apps/` +
`packages/` conventions.

## Phase 2 — Resolve

- **Exactly one signal** → its stack file. Within `package.json`, apply the dep checks
  in table order — first hit wins there (fast path, unchanged).
- **A dedicated backend manifest (`Gemfile`/`go.mod`/`pyproject.toml`/serverless
  manifest) + `package.json`** → the backend stack is primary; classify the
  package.json's **role** by its deps:
  - UI framework (`react`/`vue`/`svelte`/`next`/`nuxt`) → **hybrid**: backend surface
    + Frontend web surface.
  - `react-native`/`expo`/`electron`/`@tauri-apps/*` → hybrid with that surface.
  - Build tooling only (`esbuild`/`webpack`/`vite`/`postcss`/`tailwindcss`, no UI
    framework) → **single stack (the backend)**; note the asset pipeline in
    project-overview §2. `vite` alone counts as a frontend signal ONLY when no
    backend manifest exists.
- **A single `package.json` containing both a server and a UI framework** → hybrid
  likewise.
- **Two+ backend manifests**, or any combination not covered above → **ambiguous**.
- **Monorepo markers** → enumerate sub-projects (workspace globs, `apps/*`), run
  detection per sub-project; treat as multi-surface.

**Hybrid / ambiguous / monorepo resolve at the Mode B step-3 gate**: list every
detected surface with its evidence; interactive: ask which surface(s) to document
(default: all); headless: document all, backend facets first. Read the stack file of
every surface being documented. The templates already carry multi-surface output:
project-overview §2 lists each stack; §6 gets one subsection per surface.

## Signal table

| Signal (`package.json` rows checked in order) | Stack → stack file |
|---|---|
| `pubspec.yaml` | Flutter → `flutter.md` |
| `package.json`: `react-native`/`expo` | React Native → `react-native.md` |
| `package.json`: `electron` | Electron → `electron.md` |
| `package.json`: `@tauri-apps/*` or `src-tauri/` dir | Tauri → `tauri.md` |
| `package.json`: `express`/`fastify`/`@nestjs/core`/`koa` | Node backend → `node-backend.md` |
| `package.json`: `next`/`nuxt`/`react`/`vue`/`svelte`/`vite` | Frontend web → `frontend-web.md` |
| `package.json`: none of the above | plain Node → `node-backend.md` |
| `Gemfile` / `go.mod` / `pyproject.toml` | Rails → `rails.md` / Go → `go.md` / Python → `python.md` |
| `serverless.yml`/`template.yaml` | Serverless → `serverless.md` |
| `*.xcodeproj`/`Package.swift`/`Podfile` | Apple (iOS/macOS) → `apple.md` |
| `build.gradle*` **plus** `AndroidManifest.xml` | Android → `android.md` |
| `*.sln`/`*.csproj` with desktop markers (`<UseWPF>`/`<UseWindowsForms>`/`net*-windows`/WinUI/MAUI) | Windows desktop (.NET) → `windows-dotnet.md` |

Notes:

- `package.json` dep checks scan dependencies + devDependencies — the desktop checks
  MUST precede the frontend check (Electron/Tauri renderers depend on react/vue too).
- `.csproj` with `Microsoft.NET.Sdk.Web` or no desktop marker, Qt/C++ (CMake), anything
  else → unknown stack: fall back to README + entrypoint reading; say so in the output.
