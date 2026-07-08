#!/usr/bin/env bash
# Run detection-only evals against every fixture using headless Claude Code.
#
# Usage:
#   ./run_detection.sh [results_dir] [runs_per_fixture] [fixture_filter]
#
# Examples:
#   ./run_detection.sh                          # all fixtures, N=3
#   ./run_detection.sh out 1 trap-rails-esbuild # one fixture, single run (debug)
#
# Requires: claude CLI, doc-architect installed as a skill, jq.
set -euo pipefail

EVALS_DIR="$(cd "$(dirname "$0")/.." && pwd)"
FIXTURES_DIR="$EVALS_DIR/fixtures"
RESULTS_DIR="${1:-$EVALS_DIR/results/$(date +%Y%m%d-%H%M%S)}"
RUNS="${2:-3}"
FILTER="${3:-}"

PROMPT_TEMPLATE='Use the doc-architect skill, but perform ONLY Mode B step 1
(stack detection) on the repository at __FIXTURE_PATH__. Follow the two-phase
collect-then-resolve procedure in references/stacks/README.md exactly. Do NOT
generate or modify any documentation.

Output ONLY a JSON object (no prose, no markdown fences) with this shape:
{
  "resolution": "single" | "hybrid" | "ambiguous" | "monorepo" | "unknown",
  "surfaces": [
    {"stack": "<stack file basename without .md>",
     "role": "primary" | "surface" | "candidate",
     "evidence": ["<file or signal that triggered this>"]}
  ],
  "package_json_role": "ui-framework" | "build-tooling" | "desktop" | "extension" | "server" | "absent",
  "unsafe_commands_flagged": ["<any build/verify command you would mark NOT SAFE>"],
  "notes": "<one line, optional>"
}

Rules for the report:
- "surfaces" is empty for resolution=unknown.
- role=primary for the main stack, surface for additional hybrid/monorepo
  surfaces, candidate for ambiguous alternatives.
- Every surface needs at least one evidence entry naming a real file.'

mkdir -p "$RESULTS_DIR"
echo "results -> $RESULTS_DIR"

for fixture in "$FIXTURES_DIR"/*/; do
  name="$(basename "$fixture")"
  [[ -n "$FILTER" && "$name" != *"$FILTER"* ]] && continue
  mkdir -p "$RESULTS_DIR/$name"

  for i in $(seq 1 "$RUNS"); do
    out="$RESULTS_DIR/$name/run-$i.json"
    [[ -s "$out" ]] && continue  # resumable
    echo "[$name] run $i/$RUNS"
    prompt="${PROMPT_TEMPLATE//__FIXTURE_PATH__/$fixture}"

    raw="$(claude -p "$prompt" \
      --allowedTools "Read,Glob,Grep,Skill" \
      --max-turns 15 2>>"$RESULTS_DIR/$name/stderr.log" || true)"

    # Extract the outermost JSON object; models occasionally add prose anyway.
    echo "$raw" | python3 -c '
import json, re, sys
raw = sys.stdin.read()
m = re.search(r"\{.*\}", raw, re.DOTALL)
if not m:
    print(json.dumps({"_parse_error": "no JSON object in output", "_raw": raw[:2000]}))
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
