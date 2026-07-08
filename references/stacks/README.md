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
- **A dedicated backend manifest (`Gemfile`/`go.mod`/`pyproject.toml`/`Cargo.toml`/
  serverless manifest) + `package.json`** → the backend stack is primary; classify the
  package.json's **role**:
  - `engines.vscode` field → hybrid with a VS Code extension surface.
  - UI framework (`react`/`vue`/`svelte`/`next`/`nuxt`) in deps → **hybrid**: backend
    surface + Frontend web surface.
  - `react-native`/`expo`/`electron`/`@tauri-apps/*` → hybrid with that surface.
  - Build tooling only (`esbuild`/`webpack`/`vite`/`postcss`/`tailwindcss`, no UI
    framework) → **single stack (the backend)**; note the asset pipeline in
    project-overview §2. `vite`/`vitest` are tooling, never a framework signal on
    their own.
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

## Machine-readable detection report

Detection's result is reported in this JSON shape. Headless Mode B always emits it
(into PROGRESS.md state when PROGRESS.md is in use) so every run is auditable after
the fact; interactive runs emit it on request. The eval suite (`evals/`) grades
against this exact contract — vocabulary changes here require updating
`evals/scripts/grade.py` and every `expected.json` in the same PR.

```json
{
  "resolution": "single | hybrid | ambiguous | monorepo | unknown",
  "surfaces": [{"stack": "<stack file basename, no .md>",
                "role": "primary | surface | candidate",
                "evidence": ["<file or signal that triggered this>"]}],
  "package_json_role": "ui-framework | build-tooling | desktop | extension | server | absent",
  "unsafe_commands_flagged": ["<commands to mark NOT SAFE per audit-checklist §5>"],
  "notes": ""
}
```

- `surfaces` is empty iff `resolution` is `unknown`; every surface carries ≥1
  evidence entry naming a real file.
- `role`: `primary` for the main stack, `surface` for additional hybrid/monorepo
  surfaces, `candidate` for ambiguous alternatives.

## Signal table

| Signal (`package.json` rows checked in order) | Stack → stack file |
|---|---|
| `pubspec.yaml` | Flutter → `flutter.md` |
| `package.json`: `react-native`/`expo` | React Native → `react-native.md` |
| `package.json`: `electron` | Electron → `electron.md` |
| `package.json`: `@tauri-apps/*` or `src-tauri/` dir | Tauri → `tauri.md` |
| `package.json`: `engines.vscode` field | VS Code extension → `vscode-extension.md` |
| `package.json`: `express`/`fastify`/`@nestjs/core`/`koa` | Node backend → `node-backend.md` |
| `package.json`: `next`/`nuxt`/`react`/`vue`/`svelte`, or `vite` + root `index.html` | Frontend web → `frontend-web.md` |
| `package.json`: none of the above | plain Node → `node-backend.md` |
| `Gemfile` / `go.mod` / `pyproject.toml` | Rails → `rails.md` / Go → `go.md` / Python → `python.md` |
| `Cargo.toml` (no `src-tauri/`) | Rust → `rust.md` |
| `serverless.yml`/`template.yaml` | Serverless → `serverless.md` |
| `*.xcodeproj`/`Package.swift`/`Podfile` | Apple (iOS/macOS) → `apple.md` |
| `build.gradle*` **plus** `AndroidManifest.xml` | Android → `android.md` |
| `*.sln`/`*.csproj` with desktop markers (`<UseWPF>`/`<UseWindowsForms>`/`net*-windows`/WinUI/MAUI) | Windows desktop (.NET) → `windows-dotnet.md` |

Notes:

- `package.json` dep checks scan dependencies + devDependencies — the desktop checks
  MUST precede the frontend check (Electron/Tauri renderers depend on react/vue too).
- `.csproj` with `Microsoft.NET.Sdk.Web` or no desktop marker, Qt/C++ (CMake), anything
  else → unknown stack: fall back to README + entrypoint reading; say so in the output.
