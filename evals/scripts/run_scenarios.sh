#!/usr/bin/env bash
# Run end-to-end doc-architect scenarios in disposable repository copies.
set -euo pipefail

EVALS_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="$(cd "$EVALS_DIR/.." && pwd)"
SCENARIOS_DIR="$EVALS_DIR/scenarios"
RESULTS_DIR="${1:-$EVALS_DIR/results/scenarios-$(date +%Y%m%d-%H%M%S)}"
RUNS="${2:-1}"
FILTER="${3:-}"
EVAL_CLI="${EVAL_CLI:-claude}"
MODEL_NAME="${MODEL:-}"

if ! [[ "$RUNS" =~ ^[1-9][0-9]*$ ]]; then
  echo "runs_per_scenario must be a positive integer: $RUNS" >&2
  exit 2
fi
if [[ "$EVAL_CLI" != "claude" && "$EVAL_CLI" != "codex" ]]; then
  echo "EVAL_CLI must be claude or codex: $EVAL_CLI" >&2
  exit 2
fi
if ! command -v "$EVAL_CLI" >/dev/null 2>&1; then
  echo "$EVAL_CLI CLI not found" >&2
  exit 2
fi

selected=()
for scenario in "$SCENARIOS_DIR"/*/; do
  name="$(basename "$scenario")"
  [[ -n "$FILTER" && "$name" != *"$FILTER"* ]] && continue
  selected+=("$name")
done
if [[ "${#selected[@]}" -eq 0 ]]; then
  echo "scenario filter matched nothing: ${FILTER:-<all>}" >&2
  exit 2
fi

mkdir -p "$RESULTS_DIR"
python3 - "$RESULTS_DIR/manifest.json" "$RUNS" "${selected[@]}" <<'PY'
import json
import sys

path, runs, *scenarios = sys.argv[1:]
with open(path, "w") as output:
    json.dump({"runs_per_scenario": int(runs), "selected_scenarios": scenarios}, output, indent=2)
    output.write("\n")
PY

for name in "${selected[@]}"; do
  scenario="$SCENARIOS_DIR/$name"
  request="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["request"])' "$scenario/scenario.json")"
  for i in $(seq 1 "$RUNS"); do
    run_dir="$RESULTS_DIR/$name/run-$i"
    [[ -f "$run_dir/done" ]] && continue
    echo "[$name] run $i/$RUNS"
    mkdir -p "$run_dir/repo"
    cp -R "$scenario/repo/." "$run_dir/repo/"
    git -C "$run_dir/repo" init -q
    git -C "$run_dir/repo" add -A
    git -C "$run_dir/repo" -c user.name=Eval -c user.email=eval@example.invalid \
      commit -qm fixture-baseline
    if [[ -f "$scenario/change.patch" ]]; then
      git -C "$run_dir/repo" apply "$scenario/change.patch"
    fi
    python3 "$EVALS_DIR/scripts/scenario_common.py" snapshot \
      "$run_dir/repo" "$run_dir/before.json"

    prompt="Use the doc-architect skill at $REPO_ROOT/skills/doc-architect/SKILL.md on
the disposable repository at $run_dir/repo. Execute this request headlessly:

$request

Follow the skill exactly. Do not pause for confirmation; record the mode's plan or
mapping in the final report and proceed. Give every canonical mode-specific headless
report label from SKILL.md its own Markdown heading; descriptive wording may surround
the intact label. Do not
modify application source files. For this scenario run, do not start a nested
Claude/Codex Fresh Session call; self-simulate the checklist §6 questions and label that result degraded.
Return the normal doc-architect final report."

    if [[ "$EVAL_CLI" = "claude" ]]; then
      if [[ -n "$MODEL_NAME" ]]; then
        raw="$(cd "$run_dir/repo" && claude -p "$prompt" \
          --allowedTools "Read,Glob,Grep,Skill,Bash,Write,Edit" \
          --permission-mode bypassPermissions --output-format json \
          --no-session-persistence --model "$MODEL_NAME" \
          2>>"$run_dir/stderr.log" || true)"
      else
        raw="$(cd "$run_dir/repo" && claude -p "$prompt" \
          --allowedTools "Read,Glob,Grep,Skill,Bash,Write,Edit" \
          --permission-mode bypassPermissions --output-format json \
          --no-session-persistence \
          2>>"$run_dir/stderr.log" || true)"
      fi
      printf '%s' "$raw" | python3 -c '
import json, sys
raw = sys.stdin.read()
try:
    value = json.loads(raw)
    print(value.get("result", raw) if isinstance(value, dict) else raw)
except Exception:
    print(raw)
' > "$run_dir/final.txt"
    else
      if [[ -n "$MODEL_NAME" ]]; then
        codex exec --ephemeral --sandbox workspace-write --cd "$run_dir/repo" \
          --output-last-message "$run_dir/final.txt" --model "$MODEL_NAME" \
          "$prompt" >>"$run_dir/stderr.log" 2>&1 || true
      else
        codex exec --ephemeral --sandbox workspace-write --cd "$run_dir/repo" \
          --output-last-message "$run_dir/final.txt" \
          "$prompt" >>"$run_dir/stderr.log" 2>&1 || true
      fi
      [[ -f "$run_dir/final.txt" ]] || : > "$run_dir/final.txt"
    fi
    : > "$run_dir/done"
  done
done

echo
python3 "$EVALS_DIR/scripts/grade_scenarios.py" "$RESULTS_DIR"
