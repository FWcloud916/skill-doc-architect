# Stack: Node backend

> **Detection:** `package.json` with a server framework
> (`express`/`fastify`/`@nestjs/core`/`koa`) in dependencies + devDependencies —
> checked after the React Native / Electron / Tauri signals. Also the fallback for a
> `package.json` matching none of the disambiguation rules (plain Node).
> **Design surface:** conditional — offer `DESIGN.md` only when the evidence row matches.

## Discovery map

| Overview § | Source of truth |
|---|---|
| §2 versions | lockfile, `.nvmrc`, `engines` |
| §5/§9 models & schema | ORM models (Prisma schema, TypeORM entities) |
| §6 interface | Express/Nest route definitions |
| §7 background work | Bull/Agenda queues, `node-cron` |
| Design-surface evidence | `views/`/templates, public styles/assets, SSR/admin theme sources |

Facet notes: §8 — API-client modules, SDK deps in the manifest; §10 — env config,
Dockerfile, CI/CD, package scripts.

## Diff → doc section map

| Changed path | Re-verify |
|---|---|
| route/controller definitions | project-overview §6 |
| ORM models (Prisma schema, TypeORM entities) | project-overview §5, §9; domain-models §1 |
| queue/task definitions (Bull/Agenda, cron) | project-overview §7 |
| template/public styles, SSR/admin theme sources | DESIGN.md tokens + matching prose — when the design module was selected |

## Linter signals

Config: `eslint.config.js` / `.eslintrc*`, `.prettierrc*`, `biome.json`.
Prefer a real package script; otherwise use a confirmed local binary such as
`./node_modules/.bin/eslint .` or `./node_modules/.bin/prettier --check .`.

## Minimal test gate

Built-in `node --test` (zero-dependency) or vitest/jest.

## Command safety notes

SAFE probes (audit-checklist §5): `node --version`; after confirming it exists,
`./node_modules/.bin/jest --listTests` or `./node_modules/.bin/vitest list`.
NOT SAFE — static check only: on-demand package runners, installs, migrations, seeds.
