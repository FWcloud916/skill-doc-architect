# freightd — Agent Guide

Freight booking daemon: accepts Shipment orders and schedules Carrier pickups.

## Hard constraints

- Keep model docs synchronized (source: `src/models.py`).

## Read before you work

| Task | Read first |
|---|---|
| Architecture, request flow | [docs/project-overview.md](docs/project-overview.md) |
| Touching domain behavior, data models | [docs/domain-models.md](docs/domain-models.md) |
| Unsure what a term means | [CONTEXT.md](CONTEXT.md) |

## Commands

```bash
python3 -m unittest discover -s tests
```

## Docs maintenance

When modifying any file under `docs/`, update its `> **Last updated:**` date.
