# Stack: Python

> **Detection:** `pyproject.toml` at the repo root.

## Discovery map

| Overview § | Source of truth |
|---|---|
| §2 versions | lockfile, `.python-version` |
| §5/§9 models & schema | Django models / SQLAlchemy / Pydantic |
| §6 interface | FastAPI/Django/Flask routers, `urls.py` |
| §7 background work | Celery tasks, `celery beat` config |

Facet notes: §8 — API-client modules, SDK deps in the manifest; §10 — env/settings
modules, Dockerfile, CI/CD.

## Diff → doc section map

| Changed path | Re-verify |
|---|---|
| routers, `urls.py` | project-overview §6 |
| Django models / SQLAlchemy / Pydantic models | project-overview §5, §9; domain-models §1 |
| Celery tasks + beat config | project-overview §7 |
| `pyproject.toml`, `ruff.toml` | project-overview §2; coding-style §1–2 |

## Linter signals

Config: `ruff.toml` / `[tool.ruff]` in `pyproject.toml`, `setup.cfg`.
Pre-merge: `ruff check`, `ruff format --check`.

## Minimal test gate

`pytest`, one smoke test.

## Command safety notes

SAFE probes (audit-checklist §5): `python --version`, `pytest --collect-only -q`,
`ruff --version`. NOT SAFE — static check only: migrations, seeds, `manage.py` shells.
