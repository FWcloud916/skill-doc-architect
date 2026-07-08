# Stack: Rails

> **Detection:** `Gemfile` at the repo root.

## Discovery map

| Overview § | Source of truth |
|---|---|
| §2 versions | `Gemfile.lock`, `.ruby-version` |
| §5/§9 models & schema | `app/models/`, `db/schema.rb` |
| §6 interface | `config/routes.rb` |
| §7 background work | `app/workers/`, `app/jobs/`, `config/schedule.rb`, `config/sidekiq.yml` |

Facet notes: §8 — API-client wrappers (`app/services/`, `lib/`), SDK gems in the
Gemfile; §10 — `config/environments/`, credentials/settings files, Dockerfile, CI/CD.

## Diff → doc section map

| Changed path | Re-verify |
|---|---|
| `config/routes.rb` | project-overview §6 |
| `db/schema.rb`, `db/migrate/` | project-overview §9; domain-models ER + field notes |
| `app/models/` | project-overview §5; domain-models §1 + affected mechanisms |
| `app/workers/`, `app/jobs/`, schedule/cron config | project-overview §7 |
| `app/services/` (business logic) | domain-models mechanism/flow sections naming those classes |
| `app/controllers/` | project-overview §6; domain-models flow sections if behavior changed |

## Linter signals

Config: `.rubocop.yml` (+ inherited files). Pre-merge: `bundle exec rubocop`;
changed-only: `git diff <base>...HEAD --name-only | grep '\.rb$' | xargs bundle exec rubocop`.

## Minimal test gate

`rspec` or minitest, one smoke test.

## Command safety notes

SAFE probes (audit-checklist §5): `ruby --version`, `bundle exec rspec --dry-run`,
`bundle exec rubocop --version`. NOT SAFE — static check only: migrations, seeds,
`rails console` / DB consoles.
