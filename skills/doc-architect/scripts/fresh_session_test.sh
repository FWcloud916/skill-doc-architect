#!/usr/bin/env bash
# Independent Fresh Session Test (references/audit-checklist.md §6).
#
# Gets answers to the 5 Fresh Session Test questions from a genuinely fresh
# context (a headless claude -p subprocess with zero conversation history),
# instead of the writing session self-simulating "an agent with only the
# repo as context" — which isn't actually fresh, since it remembers every
# decision it just made. The calling session still does the grading
# (blocking-gap vs pass vs honest TBD per checklist §6); this script only
# fetches independent answers.
#
# The 5 questions are hard-coded below from checklist §6's table. If that
# table's wording changes, update this prompt in the same change.
#
# Usage:
#   ./fresh_session_test.sh <target_repo_path> [model]
#   MODEL=claude-sonnet-5 ./fresh_session_test.sh <target_repo_path>
#
# Requires: claude CLI. On failure (CLI missing, API error, parse failure),
# exits non-zero — callers should fall back to self-simulation rather than
# block on a transient issue (e.g. a 529 overload — retry or fall back, not
# a hard blocker).
set -euo pipefail

TARGET="${1:?Usage: fresh_session_test.sh <target_repo_path> [model]}"
MODEL_ARG="${2:-${MODEL:-}}"
MODEL_ARGS=()
[[ -n "$MODEL_ARG" ]] && MODEL_ARGS=(--model "$MODEL_ARG")

if ! command -v claude >/dev/null 2>&1; then
  echo "fresh_session_test: claude CLI not found — fall back to self-simulation (checklist §6)" >&2
  exit 1
fi

PROMPT='You are an agent whose ONLY context is the repository at '"$TARGET"'. You have
no memory of how or why any file was written. Using only the doc set and repo files at
that path, answer these 5 questions, citing the doc file + section (or exact location)
that answers each one. If a question is genuinely unanswerable from the repo alone, say
so plainly instead of guessing.

1. What is this system?
2. How is it organized?
3. How do I run it?
4. How do I verify my work?
5. What work state, if any, does this repository track? If PROGRESS.md is absent,
   answer "N/A — not agent-tracked (PROGRESS.md absent)"; that absence is valid
   repository evidence, not an unanswerable gap.

Output ONLY a JSON object (no prose, no markdown fences) with this shape:
{"answers": [
  {"q": 1, "question": "What is this system?", "answer": "<answer or honest gap>", "citation": "<file + section, or \"none found\">"},
  {"q": 2, "question": "How is it organized?", "answer": "...", "citation": "..."},
  {"q": 3, "question": "How do I run it?", "answer": "...", "citation": "..."},
  {"q": 4, "question": "How do I verify my work?", "answer": "...", "citation": "..."},
  {"q": 5, "question": "What work state, if any, does this repository track?", "answer": "...", "citation": "..."}
]}'

# --output-format json wraps the answer in a result envelope; plain-text -p
# output proved prone to truncated stdout on some runs (evals/scripts/run_detection.sh).
raw="$(claude -p "$PROMPT" \
  --allowedTools "Read,Glob,Grep" \
  --output-format json \
  "${MODEL_ARGS[@]}" \
  2>&1)" || {
  echo "fresh_session_test: claude invocation failed — fall back to self-simulation (checklist §6)" >&2
  exit 1
}

echo "$raw" | python3 -c '
import json, re, sys
raw = sys.stdin.read()
text = raw
try:
    env = json.loads(raw)
    if isinstance(env, dict) and "result" in env:
        if env.get("is_error"):
            print(json.dumps({"_parse_error": "run errored", "_raw": str(env)[:2000]}))
            sys.exit(1)
        text = env["result"]
except Exception:
    pass
m = re.search(r"\{.*\}", text, re.DOTALL)
if not m:
    print(json.dumps({"_parse_error": "no JSON object in output", "_raw": text[:2000]}))
    sys.exit(1)
try:
    result = json.loads(m.group(0))
    answers = result.get("answers") if isinstance(result, dict) else None
    valid = isinstance(answers, list) and len(answers) == 5
    valid = valid and [item.get("q") for item in answers if isinstance(item, dict)] == [1, 2, 3, 4, 5]
    valid = valid and all(
        set(item) == {"q", "question", "answer", "citation"}
        and all(isinstance(item[key], str) for key in ("question", "answer", "citation"))
        for item in answers
    )
    if not valid:
        raise ValueError("answers must contain exactly q=1..5 with string question/answer/citation fields")
    print(json.dumps(result, indent=2))
except Exception as e:
    print(json.dumps({"_parse_error": str(e), "_raw": m.group(0)[:2000]}))
    sys.exit(1)
'
