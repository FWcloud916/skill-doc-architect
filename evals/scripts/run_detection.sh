#!/usr/bin/env bash
# Run detection-only evals against every fixture using Claude Code or Codex CLI.
#
# Usage:
#   ./run_detection.sh [results_dir] [runs_per_fixture] [fixture_filter]
#
# Examples:
#   ./run_detection.sh                          # all fixtures, N=3
#   ./run_detection.sh out 1 trap-rails-esbuild # one fixture, single run (debug)
#
# Requires: Python 3 plus the selected CLI (`EVAL_CLI=claude|codex`, default claude).
set -euo pipefail

EVALS_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPO_ROOT="$(cd "$EVALS_DIR/.." && pwd)"
FIXTURES_DIR="$EVALS_DIR/fixtures"
RESULTS_DIR="${1:-$EVALS_DIR/results/$(date +%Y%m%d-%H%M%S)}"
RUNS="${2:-3}"
FILTER="${3:-}"
EVAL_CLI="${EVAL_CLI:-claude}"
MODEL_NAME="${MODEL:-}"

if ! [[ "$RUNS" =~ ^[1-9][0-9]*$ ]]; then
  echo "runs_per_fixture must be a positive integer: $RUNS" >&2
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
if [[ "$EVAL_CLI" = "claude" ]]; then
  PROVIDER="anthropic"
  EFFORT="not-applicable"
else
  PROVIDER="openai"
  EFFORT="cli-default"
fi
RECORDED_MODEL="${MODEL_NAME:-cli-default}"

selected=()
for fixture in "$FIXTURES_DIR"/*/; do
  name="$(basename "$fixture")"
  [[ -n "$FILTER" && "$name" != *"$FILTER"* ]] && continue
  selected+=("$name")
done

if [[ "${#selected[@]}" -eq 0 ]]; then
  echo "fixture filter matched nothing: ${FILTER:-<all>}" >&2
  exit 2
fi

mkdir -p "$RESULTS_DIR"
echo "results -> $RESULTS_DIR"
python3 "$EVALS_DIR/scripts/detection_ci.py" manifest \
  --fixtures "$FIXTURES_DIR" --runs "$RUNS" --filter "$FILTER" \
  --provider "$PROVIDER" --model "$RECORDED_MODEL" --effort "$EFFORT" \
  --results "$RESULTS_DIR"

for fixture in "$FIXTURES_DIR"/*/; do
  name="$(basename "$fixture")"
  [[ -n "$FILTER" && "$name" != *"$FILTER"* ]] && continue
  mkdir -p "$RESULTS_DIR/$name"

  for i in $(seq 1 "$RUNS"); do
    out="$RESULTS_DIR/$name/run-$i.json"
    [[ -s "$out" ]] && continue  # resumable
    echo "[$name] run $i/$RUNS"
    prompt="$(python3 "$EVALS_DIR/scripts/detection_prompt.py" \
      "$fixture" "$REPO_ROOT/skills/doc-architect/SKILL.md")"

    if [[ "$EVAL_CLI" = "claude" ]]; then
      # --output-format json wraps the answer in a result envelope; plain-text -p
      # output proved prone to truncated stdout on some runs.
      if [[ -n "$MODEL_NAME" ]]; then
        raw="$(cd "$fixture" && claude -p "$prompt" \
          --allowedTools "Read,Glob,Grep,Skill" \
          --output-format json --model "$MODEL_NAME" \
          2>>"$RESULTS_DIR/$name/stderr.log" || true)"
      else
        raw="$(cd "$fixture" && claude -p "$prompt" \
          --allowedTools "Read,Glob,Grep,Skill" \
          --output-format json \
          2>>"$RESULTS_DIR/$name/stderr.log" || true)"
      fi
    else
      raw_file="$RESULTS_DIR/$name/run-$i.raw.txt"
      if [[ -n "$MODEL_NAME" ]]; then
        codex exec --ephemeral --sandbox read-only --cd "$fixture" \
          --output-schema "$EVALS_DIR/detection-report.schema.json" \
          --output-last-message "$raw_file" --model "$MODEL_NAME" \
          "$prompt" >>"$RESULTS_DIR/$name/stderr.log" 2>&1 || true
      else
        codex exec --ephemeral --sandbox read-only --cd "$fixture" \
          --output-schema "$EVALS_DIR/detection-report.schema.json" \
          --output-last-message "$raw_file" \
          "$prompt" >>"$RESULTS_DIR/$name/stderr.log" 2>&1 || true
      fi
      if [[ -f "$raw_file" ]]; then
        raw="$(sed -n '1,$p' "$raw_file")"
      else
        raw=""
      fi
    fi

    # Unwrap the envelope, then extract the outermost JSON object from the
    # answer text; models occasionally add prose anyway.
    echo "$raw" | python3 -c '
import json, re, sys
raw = sys.stdin.read()
text = raw
try:
    env = json.loads(raw)
    if isinstance(env, dict) and "result" in env:
        if env.get("is_error"):
            print(json.dumps({"_parse_error": "run errored", "_raw": str(env)[:2000]}))
            sys.exit()
        text = env["result"]
except Exception:
    pass
m = re.search(r"\{.*\}", text, re.DOTALL)
if not m:
    print(json.dumps({"_parse_error": "no JSON object in output", "_raw": text[:2000]}))
else:
    try:
        print(json.dumps(json.loads(m.group(0))))
    except Exception as e:
        print(json.dumps({"_parse_error": str(e), "_raw": m.group(0)[:2000]}))
' > "$out"
  done
done

echo
python3 "$EVALS_DIR/scripts/grade.py" "$RESULTS_DIR"
