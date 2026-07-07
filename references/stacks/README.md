# Stack detection index

Routes a repository's manifest signals to its stack file (routed from SKILL.md
Mode B step 1). Match top-down — the first hit wins; then read the matched
`<stack>.md` before discovery reading.

| Signal (checked in order) | Stack → stack file |
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

- `package.json` checks scan dependencies + devDependencies in the listed order — the
  desktop checks MUST precede the frontend check (Electron/Tauri renderers depend on
  react/vue too).
- Both frontend and server deps, or a workspaces monorepo → fullstack: handled at the
  Mode B step-3 gate (interactive: ask which surface(s); headless: document both,
  backend facets first).
- `.csproj` with `Microsoft.NET.Sdk.Web` or no desktop marker, Qt/C++ (CMake), anything
  else → unknown stack: fall back to README + entrypoint reading; say so in the output.
