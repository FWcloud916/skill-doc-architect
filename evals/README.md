# Evaluation suite

Three complementary layers protect doc-architect without grading model prose by taste:

1. **Detection fixtures** give Mode B stack routing objective ground truth.
2. **End-to-end scenarios** run a full mode in a disposable repo and grade stable
   invariants: change scope, required files/content, merge preservation, frontmatter,
   relative links, and report fields.
3. **Trigger matrix** records the intended boundary between this broad skill,
   `project-docs`, and excluded API/changelog work.

All model-driven runners support Claude Code or Codex CLI. Fast deterministic grader
tests and `scripts/verify.sh` run without provider cost.

## Detection routing

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
├── scenarios/                 # 6 disposable end-to-end repository scenarios
│   └── */scenario.json        # deterministic output/change invariants
├── trigger-matrix.json        # 8 positive + 4 boundary + 4 negative prompts
└── scripts/
    ├── run_detection.sh       # headless Claude/Codex runner, N runs per fixture
    ├── grade.py               # deterministic grader, exit 1 on any failure
    ├── run_scenarios.sh       # full-mode runner in disposable repo copies
    ├── grade_scenarios.py     # invariant grader, no prose matching
    └── test_*.py              # free false-green regression tests
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

Codex validation note (2026-07-14, Codex CLI 0.144.1, `gpt-5.6-sol`): the complete
detection N=1 sweep passed **34/34**, the end-to-end N=1 sweep passed **6/6**, and an
independent Fresh Session canary passed its citation validator. The first scenario
grade exposed one eval-contract bug: Mode U-1 promises a verification report but not
U-2's exact `Verification results` heading. The scenario expectation was corrected to
the mode's real contract, the stored raw run passed, and a fresh U-1 Codex rerun also
passed. Full N=3 remains the release-candidate stability gate.

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

## End-to-end mode scenarios

The six scenarios cover the skill's highest-risk behavioral promises:

| Scenario | Contract under test |
|---|---|
| `greenfield-honest-tbd` | undecided facts stay `TBD`; no invented test gate |
| `brownfield-bootstrap` | applicable core/modules generated from real evidence |
| `merge-preserves-existing` | complete README and non-canonical memo remain byte-identical |
| `diff-update-targeted` | Mode U-1 changes only the mapped canonical doc |
| `audit-report-only` | Mode U-2 reports drift and changes no file |
| `unknown-stack-honesty` | unsupported CMake/C++ stays explicit unknown, never guessed |

Each run copies `scenarios/<name>/repo/` into its results directory, initializes a
disposable Git repository, applies `change.patch` when present, records a pre-agent
hash snapshot, then invokes the selected CLI with write access only to that copy.
The grader compares filesystem state and final report to `scenario.json`; final-report
terms are case-insensitive, and it does not require a particular prose style. Scenario
prompts suppress nested provider-backed
Fresh Session calls and require an explicitly degraded self-simulation, keeping one
scenario equal to one billed model call.

Filesystem snapshots ignore only a narrow set of verification-tool caches permitted by
`audit-checklist.md` §5 (`__pycache__`, `.pytest_cache`, `.ruff_cache`, `.mypy_cache`),
plus `.git`; application files and arbitrary hidden paths remain inside the hard scope
check.

```bash
# all six scenarios, one run each
EVAL_CLI=codex ./evals/scripts/run_scenarios.sh /tmp/doc-scenarios 1

# one targeted scenario
EVAL_CLI=codex ./evals/scripts/run_scenarios.sh /tmp/doc-merge 1 merge-preserves

# free grader regression tests
python3 evals/scripts/test_grade_scenarios.py
```

Changing a mode's allowed file scope, output contract, merge behavior, or targeted
update rules requires updating the affected scenario and grader tests in the same
change. Never broaden `allowed_changes` merely to make a model mistake pass.

## Trigger boundary matrix

`trigger-matrix.json` has 16 representative requests with outcomes
`doc-architect`, `prefer-project-docs`, or `not-doc-architect`. The repository gate
checks its shape, unique IDs, and 8/4/4 category balance. It is a review and future
live-eval contract; it does not pretend metadata-only trigger selection can be proven
without running the surrounding skill catalog.

## Known limits

- Scenario grading covers deterministic behavior, not writing quality or whether a
  nuanced architectural explanation is insightful. Fresh Session answers still need
  human/model judgment for semantic correctness after citation validation.
- Live scenario and detection sweeps cost provider calls. Per-PR gates validate their
  contracts and graders but do not claim the model executed successfully.
- Fixtures pin today's resolve rules. When rules legitimately change, update
  `expected.json` in the same PR — a red suite after a spec change is the
  suite working, not the suite being wrong.
