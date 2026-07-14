# Detection eval suite

Automated regression tests for Mode B step 1 (stack detection), runnable through
Claude Code or Codex CLI. The rest of the
skill's quality is guarded by `scripts/verify.sh` (repo self-consistency) and the
Fresh Session Test (doc quality); this suite guards the one behavior that has
objectively right answers and has already produced real bugs twice: **routing a
repo's manifest signals to stack files**.

## Why this exists

Detection is executed by the model, not by code, so it cannot be unit-tested.
But its output *is* deterministic in spec: given a set of manifests, the
resolve rules in `skills/doc-architect/references/stacks/README.md` define exactly one correct
answer. That makes it eval-able: run headless Claude against tiny fixture
repos, demand a machine-readable report, and diff it against ground truth
with a plain script — no LLM judge required.

Both bugs in the decision log (vitest -> vite substring misdetection; Rails +
esbuild misread as hybrid) would have been caught by fixtures
`trap-ts-lib-vitest` and `trap-rails-esbuild`. They are now permanent
regression tests.

## Layout

```
evals/
├── README.md                  # this file
├── fixtures/                  # 34 minimal repos (manifests only, no real code)
│   ├── basic-*/               # 16: one per stack file, single unambiguous signal
│   │   └── expected.json      # ground truth
│   └── trap-*/                # 18: hybrid/ordering/fallback traps
└── scripts/
    ├── run_detection.sh       # headless Claude/Codex runner, N runs per fixture
    ├── grade.py               # deterministic grader, exit 1 on any failure
    └── test_grade.py          # free false-green regression tests
```

## The detection report contract

The runner asks the skill to emit only this JSON (the prompt embeds the full
shape — see `run_detection.sh`):

```json
{
  "resolution": "single | hybrid | ambiguous | monorepo | unknown",
  "surfaces": [{"stack": "rails", "role": "primary", "evidence": ["Gemfile"]}],
  "package_json": [{"path": "package.json", "roles": ["server", "ui-framework"]}],
  "notes": ""
}
```

`stack` values are stack-file basenames (`rails`, `frontend-web`, ...), so the
contract stays in lockstep with `skills/doc-architect/references/stacks/`. The `evidence` field is
what makes failures debuggable: when a run misroutes, the report says which
file it blamed. Evidence values are repo-relative paths and the grader proves they
exist. `package_json` records every package manifest independently, so monorepos and
multi-role full-stack packages are representable without a lossy singular field.

This contract IS the skill's interface: it lives in the "Machine-readable
detection report" subsection of `skills/doc-architect/references/stacks/README.md`, and headless Mode B
always emits it. The evals therefore test the real interface, not a lookalike.
Vocabulary changes go to the contract, `grade.py`, and `expected.json` in the
same PR.

## Fixture design rules

Rules 3–4 are hard constraints in [AGENTS.md](../AGENTS.md), enforced on every
contributor (human or agent).

1. **Manifests only.** Detection reads manifests, so fixtures contain nothing
   else. Whole suite is a few KB; runs stay cheap and fast.
2. **One assertion focus per trap.** Each `trap-*` fixture exists to break one
   specific resolve rule: ordering (desktop before frontend), role
   classification (tooling vs UI framework), fallback honesty (unknown means
   unknown), collection completeness (monorepo, two backends).
3. **Bug -> fixture, permanently.** Every detection bug that reaches the
   decision log must gain a `trap-*` fixture with a `regression_for` field
   pointing at the log entry. Same discipline as the log itself.
4. **New stack -> two fixtures minimum.** Any PR adding `skills/doc-architect/references/stacks/X.md`
   must add `basic-X` plus at least one trap exercising its position in the
   signal-table ordering (the table is first-hit-wins inside package.json, so
   every insertion can silently shadow or be shadowed).

## Grading semantics

`grade.py` compares field-by-field:

| Check | Severity |
|---|---|
| report parses as JSON | hard fail |
| exact report schema + vocabulary | hard fail |
| `resolution` exact | hard fail |
| full `(stack, role)` set exact | hard fail |
| resolution/role invariant | hard fail |
| every evidence path exists | hard fail |
| no `forbidden_stacks` appear | hard fail |
| every package path + roles exact | hard fail |
| selected fixture/run set complete | hard fail |

A fixture passes only if **all N runs pass** (default N=3). Detection is a
routing decision downstream steps depend on; "right 2 out of 3 times" is a
flaky router, and flakiness here is a bug, not variance to average away.

## Running

```bash
# full suite, 3 runs per fixture
./evals/scripts/run_detection.sh

# debug one fixture with a single run
./evals/scripts/run_detection.sh /tmp/out 1 trap-rails-esbuild

# run the same fixture through Codex CLI
EVAL_CLI=codex ./evals/scripts/run_detection.sh /tmp/out-codex 1 trap-rails-esbuild
```

Requires Python 3 plus the selected CLI (`EVAL_CLI=claude|codex`, default Claude).
Claude uses its installed skill; both providers are explicitly pointed at this
checkout's SKILL.md, and Codex runs ephemeral + read-only with the checked-in JSON
Schema. The runner
is resumable (skips existing `run-*.json`), keeps per-fixture `stderr.log`, and
calls the grader at the end.

Claude cost note (measured 2026-07-08, claude CLI 2.1.204, full N=3 sweep validated —
32/32 fixtures passed, zero flaky runs). The current 34-fixture totals below are
extrapolated from those measured per-run values; remeasure after the first v2 sweep:

| Model | Wall-clock/run | $/run | Full N=1 sweep (34 runs) | Full N=3 sweep (102 runs) |
|---|---|---|---|---|
| no `--model` flag (session default) | ~62s | ~$0.23 | ~35 min / ~$7.80 | ~105 min / ~$23.50 |
| `--model claude-sonnet-5` | ~29s | ~$0.17 | ~17 min / ~$5.80 | ~50 min / ~$17.30 |

Dollar cost sampled via instrumented `--output-format json` calls (`total_cost_usd`
field) with a warm prompt cache (SKILL.md + `skills/doc-architect/references/stacks/` shared across
fixtures cache well). The no-flag row resolved to a Sonnet 5 + Haiku 4.5 mix in
this environment — **CI must not rely on that**: a bare `ANTHROPIC_API_KEY`
runner has no local account/settings context, so default-model resolution there
is unverified and could silently land on a pricier model. Always pass
`MODEL=claude-sonnet-5 ./evals/scripts/run_detection.sh` (or `--model claude-sonnet-5`
directly) for a predictable cost. First-run-of-a-sweep (cold-cache) cost per
fixture is higher — these are steady-state estimates, the realistic case once a
sweep is underway. Cheap enough for nightly either way, too slow for per-PR —
that's what the verify.sh fixture lint is for.

## CI

- **Per PR**: `verify.sh` + fixture/schema lint + `test_grade.py`. Fast, free,
  deterministic. No GitHub Actions workflow for this yet — it's currently
  enforced as an `AGENTS.md` hard constraint (agents must run it before
  declaring a change done), not by push-triggered CI.
- **Full sweep**: [`.github/workflows/detection-evals.yml`](../.github/workflows/detection-evals.yml),
  **manual trigger only** (`workflow_dispatch`) — deliberately not on push, PR,
  or a schedule, since each run costs real API spend (~$17 at the N=3 default;
  see cost note above). Requires an `ANTHROPIC_API_KEY` repo secret (Settings →
  Secrets and variables → Actions) before the first run. A `model` dispatch
  input lets you pick the model per run (defaults to `claude-sonnet-5`) — always
  set it to some real model explicitly, never leave the CLI's unpinned default
  in a bare-API-key environment. Dispatch inputs also let you run a cheap
  single-fixture debug pass (`filter: basic-rails`, ~$0.20) before committing to
  a full sweep. Results (including `stderr.log` per fixture) upload as a
  workflow artifact whether the run passes or fails.

## Known limits

- This suite tests routing only. It does not test doc generation quality,
  command verification honesty, or the Fresh Session Test — those stay
  human-in-the-loop by design.
- Fixtures pin today's resolve rules. When rules legitimately change, update
  `expected.json` in the same PR — a red suite after a spec change is the
  suite working, not the suite being wrong.
