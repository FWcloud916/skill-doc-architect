# Stack: Frontend web

> **Detection:** `package.json` with a frontend framework
> (`next`/`nuxt`/`react`/`vue`/`svelte`/`vite`) and no server framework — checked
> after the React Native / Electron / Tauri and server-framework signals. SSR
> frameworks (Next/Nuxt) still count as frontend; their API routes become a §6 surface.

## Discovery map

| Overview § | Source of truth |
|---|---|
| §2 versions | lockfile, `.nvmrc`, framework config (`next.config.*`, `vite.config.*`, `nuxt.config.*`) |
| §5/§9 models & data | store definitions (Redux/Zustand/Pinia), API types; §9 usually `N/A — client of <backend>` |
| §6 interface | pages/routes: Next `app/`/`pages/`, Nuxt `pages/`, router config (React Router, `vue-router`); SSR API routes |
| §7 background work | usually `N/A`; service workers, client-side scheduled sync |

Facet notes: §3 — rendering strategy (SPA/SSR/SSG) + state-management approach;
§8 — consumed backend APIs + third-party SDKs (analytics, auth, payments);
§10 — build/bundle pipeline + hosting/CDN.

## Diff → doc section map

| Changed path | Re-verify |
|---|---|
| `pages/`/`app/` routes, router config | project-overview §6 |
| `components/`, `store/` (Redux/Zustand/Pinia slices) | project-overview §3, §5; domain-models §1 if store shapes are documented |
| API-client layer (fetch wrappers, generated clients), SDK config | project-overview §8 |
| framework/build config | project-overview §2, §10 |

## Linter signals

Config: `eslint.config.js` / `.eslintrc*`, `.prettierrc*`, `biome.json`.
Pre-merge: `npx eslint .`, `npx prettier --check .`.

## Minimal test gate

vitest or jest + Testing Library, one component smoke test.

## Command safety notes

SAFE probes (audit-checklist §5): `node --version`, `npx vitest list`,
`npx jest --listTests`. NOT SAFE — static check only: `npm install`, builds, deploys.
