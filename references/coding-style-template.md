# Template: `docs/coding-style.md`

Style reference covering both **linter-enforced rules** and **team conventions the linter
cannot check**. Generate it from the project's own configuration and code — do not import
another project's style guide wholesale, and do not invent rules the codebase doesn't follow.

**Applicability:** generate only when the project has linter config or discernible
conventions (consistent patterns across the codebase). Neither → skip the file and note
the absence in `project-overview.md`; or, if the user wants a record anyway, write a short
factual stub (e.g. "formatting: gofmt, enforced by CI") rather than padding with generic
advice. Greenfield (Mode G): skip until a linter is chosen — but the advisory step MAY
propose one.

---

## Frontmatter (verbatim shape)

```markdown
# Coding Style Guide

> **Type:** Reference / How-to
> **Audience:** Developers, AI assistants, code reviewers
> **Last updated:** YYYY-MM-DD
>
> This document describes the coding style conventions for <project>.
> It covers both **linter-enforced rules** and **team conventions** that cannot be auto-checked.
>
> Configuration source: <.rubocop.yml / eslint.config.js / ruff.toml / .golangci.yml / analysis_options.yaml / .swiftlint.yml / ...>
>
> **Terminology:** This document uses RFC 2119 keywords —
> **MUST** (mandatory), **SHOULD** (recommended), **MAY** (optional).

---
```

## Section skeleton

```markdown
## 1. Linter Overview                 <!-- tool, plugins, target versions, excluded paths -->
## 2. Linter Rules Summary            <!-- the rules actually configured, grouped, with values -->
## 3. Project-Specific Code Examples  <!-- 2-4 real patterns: how this codebase satisfies the strictest rules -->
## 4. Team Conventions (Not Enforced by the Linter)   <!-- numbered 4.1, 4.2, ... with good/bad examples -->
## 5. Architecture Conventions        <!-- layering rules: who may call whom, error handling, settings/secrets -->
## 6. Running the Linter (Pre-merge)  <!-- exact commands, incl. changed-files-only variant -->
## 7. References
```

## How to fill each section

| § | Source |
|---|---|
| 1–2 | Parse the linter config file(s) directly. Report configured values (line length, metric thresholds, enabled plugins, target language version) — not the tool's defaults unless the config inherits them explicitly. |
| 3 | Find 2–4 real files that exemplify compliance with the strictest metrics (long-method refactors, constant freezing, etc.) and quote short excerpts with paths. |
| 4 | Mine conventions from the code itself: consistent patterns across ≥3 files that no linter enforces (naming, guard-clause style, parameter-object usage, controller thinness…). Confirm with the user anything you infer from fewer than 3 examples. Each convention gets a MUST/SHOULD/MAY keyword and a good/bad example pair. |
| 5 | Layering rules ("controllers delegate to services", "models never call services", "no direct external API calls outside the client-wrapper layer"), error-handling pattern, settings/secrets rules. Derive from the code and any org-level guidance the user points to; cross-link `project-overview.md` §3. |
| 6 | Exact commands from CI config / Makefile / package scripts, verified runnable. |

## Per-stack linter signals

| Stack | Config files to read | Pre-merge command shape |
|---|---|---|
| Ruby/Rails | `.rubocop.yml` (+ inherited files) | `bundle exec rubocop`; changed-only: `git diff <base>...HEAD --name-only \| grep '\.rb$' \| xargs bundle exec rubocop` |
| Go | `.golangci.yml`, `Makefile` lint target | `golangci-lint run`, `gofmt -l .` |
| Python | `ruff.toml` / `[tool.ruff]` in `pyproject.toml`, `setup.cfg` | `ruff check`, `ruff format --check` |
| JS/TS (incl. frontend web & React Native) | `eslint.config.js` / `.eslintrc*`, `.prettierrc*`, `biome.json` | `npx eslint .`, `npx prettier --check .` |
| Swift | `.swiftlint.yml`, `.swift-format` | `swiftlint`, `swift-format lint -r Sources/` |
| Kotlin/Android | ktlint via `.editorconfig`, `detekt.yml` | `./gradlew ktlintCheck`, `./gradlew detekt` (gradle = static check only, audit-checklist §5) |
| Dart/Flutter | `analysis_options.yaml` | `dart analyze`, `dart format --output=none --set-exit-if-changed .` |
| None found | CI config for any lint step; else ask the user | — |
