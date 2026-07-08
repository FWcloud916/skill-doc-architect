# Detection eval suite

Automated regression tests for Mode B step 1 (stack detection). The rest of the
skill's quality is guarded by `scripts/verify.sh` (repo self-consistency) and the
Fresh Session Test (doc quality); this suite guards the one behavior that has
objectively right answers and has already produced real bugs twice: **routing a
repo's manifest signals to stack files**.

## Why this exists

Detection is executed by the model, not by code, so it cannot be unit-tested.
But its output *is* deterministic in spec: given a set of manifests, the
resolve rules in `references/stacks/README.md` define exactly one correct
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
├── fixtures/                  # 32 minimal repos (manifests only, no real code)
│   ├── basic-*/               # 16: one per stack file, single unambiguous signal
│   │   └── expected.json      # ground truth
│   └── trap-*/                # 16: hybrid/ordering/fallback traps
└── scripts/
    ├── run_detection.sh       # headless runner (claude -p), N runs per fixture
    └── grade.py               # deterministic grader, exit 1 on any failure
```

## The detection report contract

The runner asks the skill to emit only this JSON (the prompt embeds the full
shape — see `run_detection.sh`):

```json
{
  "resolution": "single | hybrid | ambiguous | monorepo | unknown",
  "surfaces": [{"stack": "rails", "role": "primary", "evidence": ["Gemfile"]}],
  "package_json_role": "ui-framework | build-tooling | desktop | extension | server | absent",
  "unsafe_commands_flagged": ["./gradlew build"],
  "notes": ""
}
```

`stack` values are stack-file basenames (`rails`, `frontend-web`, ...), so the
contract stays in lockstep with `references/stacks/`. The `evidence` field is
what makes failures debuggable: when a run misroutes, the report says which
file it blamed.

This contract IS the skill's interface: it lives in the "Machine-readable
detection report" subsection of `references/stacks/README.md`, and headless Mode B
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
4. **New stack -> two fixtures minimum.** Any PR adding `references/stacks/X.md`
   must add `basic-X` plus at least one trap exercising its position in the
   signal-table ordering (the table is first-hit-wins inside package.json, so
   every insertion can silently shadow or be shadowed).

## Grading semantics

`grade.py` compares field-by-field:

| Check | Severity |
|---|---|
| report parses as JSON | hard fail |
| `resolution` exact | hard fail |
| primary-stack set exact | hard fail |
| full surface set exact | hard fail |
| no `forbidden_stacks` appear | hard fail |
| `package_json_role` | hard fail |

A fixture passes only if **all N runs pass** (default N=3). Detection is a
routing decision downstream steps depend on; "right 2 out of 3 times" is a
flaky router, and flakiness here is a bug, not variance to average away.

## Running

```bash
# full suite, 3 runs per fixture
./scripts/run_detection.sh

# debug one fixture with a single run
./scripts/run_detection.sh /tmp/out 1 trap-rails-esbuild
```

Requires the `claude` CLI with this skill installed, plus Python 3. The runner
is resumable (skips existing `run-*.json`), keeps per-fixture `stderr.log`, and
calls the grader at the end.

Cost note (measured 2026-07-08, claude CLI 2.1.204, full N=3 sweep validated —
32/32 fixtures passed, zero flaky runs):

| Model | Wall-clock/run | $/run | Full N=1 sweep (32 runs) | Full N=3 sweep (96 runs) |
|---|---|---|---|---|
| no `--model` flag (session default) | ~62s | ~$0.23 | ~33 min / ~$7.30 | ~100 min / ~$22 |
| `--model claude-sonnet-5` | ~29s | ~$0.17 | ~16 min / ~$5.30 | ~47 min / ~$16 |

Dollar cost sampled via instrumented `--output-format json` calls (`total_cost_usd`
field) with a warm prompt cache (SKILL.md + `references/stacks/` shared across
fixtures cache well). The no-flag row resolved to a Sonnet 5 + Haiku 4.5 mix in
this environment — **CI must not rely on that**: a bare `ANTHROPIC_API_KEY`
runner has no local account/settings context, so default-model resolution there
is unverified and could silently land on a pricier model. Always pass
`MODEL=claude-sonnet-5 ./scripts/run_detection.sh` (or `--model claude-sonnet-5`
directly) for a predictable cost. First-run-of-a-sweep (cold-cache) cost per
fixture is higher — these are steady-state estimates, the realistic case once a
sweep is underway. Cheap enough for nightly either way, too slow for per-PR —
that's what the verify.sh fixture lint is for.

## CI recommendation

- **Per PR**: `verify.sh` + a fixture lint (every fixture has `expected.json`,
  every `expected.json` references only existing stack basenames). Fast, free,
  deterministic.
- **Nightly / pre-release / on `references/stacks/**` changes**: full sweep via
  a workflow with `ANTHROPIC_API_KEY`, failing the build on grader exit 1. Pin
  `MODEL=claude-sonnet-5` in the workflow — never rely on the CLI's unpinned
  default in a bare-API-key environment (see cost note above).

## Known limits

- This suite tests routing only. It does not test doc generation quality,
  command verification honesty, or the Fresh Session Test — those stay
  human-in-the-loop by design.
- Fixtures pin today's resolve rules. When rules legitimately change, update
  `expected.json` in the same PR — a red suite after a spec change is the
  suite working, not the suite being wrong.
