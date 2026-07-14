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
- **A dedicated backend manifest (Rails-qualified `Gemfile`/`go.mod`/`pyproject.toml`/`Cargo.toml`/
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
                "evidence": ["<repo-relative path that triggered this>"]}],
  "package_json": [{"path": "<repo-relative package.json path>",
                    "roles": ["server | ui-framework | build-tooling | desktop | extension | workspace | plain-node | frontend-entrypoint"]}],
  "notes": ""
}
```

- `surfaces` is empty iff `resolution` is `unknown`; every surface carries ≥1
  evidence entry naming a real repo-relative file. Dependency/key detail belongs in
  `notes`; evidence entries themselves are paths so the report is mechanically
  verifiable.
- `role`: `primary` for the main stack of a single-rooted repo (`single`/`hybrid`
  — in a hybrid the backend is the one primary); `surface` for additional hybrid
  surfaces and for **every** monorepo sub-project (a monorepo report has no
  primary — sub-projects are coequal; "backend facets first" orders
  documentation, it does not confer primacy); `candidate` for ambiguous
  alternatives.
- `package_json` has one entry per discovered `package.json` (empty when none).
  `roles` records every matching role, sorted in the report vocabulary order above;
  multiple roles are valid (for example a full-stack package may be both `server`
  and `ui-framework`). A workspace-only root is `workspace`; a package that reaches
  the plain-Node fallback is `plain-node`; `vite` + root `index.html` adds
  `frontend-entrypoint`.
- Every reported path is relative to the **target repository root**, never the skill
  checkout or caller working directory. A root manifest is exactly `package.json`.
- Command-safety findings do not belong in this routing contract; they are classified
  and reported by `audit-checklist.md` §5 during command verification.

### Package role table

Roles are additive; scan dependencies + devDependencies and emit every match in the
JSON vocabulary order.

| Role | Exact signal |
|---|---|
| `server` | `express`, `fastify`, `@nestjs/core`, or `koa` |
| `ui-framework` | `react-native`, `expo`, `next`, `nuxt`, `react`, `vue`, or `svelte` |
| `build-tooling` | `typescript`, `esbuild`, `webpack`, `vite`, `vitest`, `postcss`, or `tailwindcss` |
| `desktop` | `electron` or `@tauri-apps/*` (React Native remains `ui-framework`) |
| `extension` | top-level `engines.vscode` |
| `workspace` | a workspace-only root (`workspaces`, `pnpm-workspace.yaml`, or `lerna.json`) |
| `plain-node` | package reaches the plain-Node fallback; may coexist with `build-tooling` |
| `frontend-entrypoint` | `vite` plus root `index.html` |

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
| `Gemfile` containing `rails`/`railties`, or Rails entrypoints / `go.mod` / `pyproject.toml` | Rails → `rails.md` / Go → `go.md` / Python → `python.md` |
| `Cargo.toml` (no `src-tauri/`) | Rust → `rust.md` |
| `serverless.yml`/`template.yaml` | Serverless → `serverless.md` |
| `*.xcodeproj`/`*.xcworkspace`/`Podfile`, or `Package.swift` declaring an Apple platform | Apple (iOS/macOS) → `apple.md` |
| `build.gradle*` **plus** `AndroidManifest.xml` | Android → `android.md` |
| `*.sln`/`*.csproj` with desktop markers (`<UseWPF>`/`<UseWindowsForms>`/`net*-windows`/WinUI/MAUI) | Windows desktop (.NET) → `windows-dotnet.md` |

Notes:

- `package.json` dep checks scan dependencies + devDependencies — the desktop checks
  MUST precede the frontend check (Electron/Tauri renderers depend on react/vue too).
- `.csproj` with `Microsoft.NET.Sdk.Web` or no desktop marker, Qt/C++ (CMake), anything
  else → unknown stack: fall back to README + entrypoint reading; say so in the output.
- Every stack file declares `> **Design surface:** inherent | conditional | none`.
  `inherent` means the stack owns project-styled UI by definition; `conditional` means
  Mode B MUST inspect that stack file's `Design-surface evidence` discovery row. The
  step-3 gate offers `DESIGN.md` when any documented surface is inherent or when
  conditional evidence exists. Unknown stacks get the same generic evidence scan.
