# Stack: Node backend

> **Detection:** `package.json` with a server framework
> (`express`/`fastify`/`@nestjs/core`/`koa`) in dependencies + devDependencies —
> checked after the React Native / Electron / Tauri signals. Also the fallback for a
> `package.json` matching none of the disambiguation rules (plain Node).

## Discovery map

| Overview § | Source of truth |
|---|---|
| §2 versions | lockfile, `.nvmrc`, `engines` |
| §5/§9 models & schema | ORM models (Prisma schema, TypeORM entities) |
| §6 interface | Express/Nest route definitions |
| §7 background work | Bull/Agenda queues, `node-cron` |

Facet notes: §8 — API-client modules, SDK deps in the manifest; §10 — env config,
Dockerfile, CI/CD, package scripts.

## Diff → doc section map

| Changed path | Re-verify |
|---|---|
| route/controller definitions | project-overview §6 |
| ORM models (Prisma schema, TypeORM entities) | project-overview §5, §9; domain-models §1 |
| queue/task definitions (Bull/Agenda, cron) | project-overview §7 |

## Linter signals

Config: `eslint.config.js` / `.eslintrc*`, `.prettierrc*`, `biome.json`.
Pre-merge: `npx eslint .`, `npx prettier --check .`.

## Minimal test gate

Built-in `node --test` (zero-dependency) or vitest/jest.

## Command safety notes

SAFE probes (audit-checklist §5): `node --version`, `npx jest --listTests`,
`npx vitest list`. NOT SAFE — static check only: `npm install`, migrations, seeds.
