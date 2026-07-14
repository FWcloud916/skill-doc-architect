#!/usr/bin/env bash
# Independent Fresh Session Test (references/audit-checklist.md §6).
#
# Gets answers to the 5 Fresh Session Test questions from a genuinely fresh
# context (a headless Claude or Codex subprocess with zero conversation history),
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
#   EVAL_CLI=codex ./fresh_session_test.sh <target_repo_path>
#
# Requires: selected EVAL_CLI=claude|codex (default claude). On failure, exits
# non-zero; callers may self-simulate only as an explicitly degraded result.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="${1:?Usage: fresh_session_test.sh <target_repo_path> [model]}"
TARGET="$(cd "$TARGET" && pwd)"
MODEL_NAME="${2:-${MODEL:-}}"
EVAL_CLI="${EVAL_CLI:-claude}"
SCHEMA="$SCRIPT_DIR/../references/fresh-session-report.schema.json"

if [[ "$EVAL_CLI" != "claude" && "$EVAL_CLI" != "codex" ]]; then
  echo "fresh_session_test: EVAL_CLI must be claude or codex: $EVAL_CLI" >&2
  exit 2
fi
if ! command -v "$EVAL_CLI" >/dev/null 2>&1; then
  echo "fresh_session_test: $EVAL_CLI CLI not found — independent test unavailable" >&2
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

temp_dir="$(mktemp -d)"
trap 'rm -rf "$temp_dir"' EXIT

if [[ "$EVAL_CLI" = "claude" ]]; then
  if [[ -n "$MODEL_NAME" ]]; then
    raw="$(claude -p "$PROMPT" --allowedTools "Read,Glob,Grep" \
      --output-format json --no-session-persistence --model "$MODEL_NAME" \
      2>"$temp_dir/stderr.log")" || {
      cat "$temp_dir/stderr.log" >&2
      echo "fresh_session_test: claude invocation failed — independent test unavailable" >&2
      exit 1
    }
  else
    raw="$(claude -p "$PROMPT" --allowedTools "Read,Glob,Grep" \
      --output-format json --no-session-persistence \
      2>"$temp_dir/stderr.log")" || {
      cat "$temp_dir/stderr.log" >&2
      echo "fresh_session_test: claude invocation failed — independent test unavailable" >&2
      exit 1
    }
  fi
else
  if [[ -n "$MODEL_NAME" ]]; then
    codex exec --ephemeral --sandbox read-only --cd "$TARGET" \
      --output-schema "$SCHEMA" --output-last-message "$temp_dir/result.json" \
      --model "$MODEL_NAME" "$PROMPT" >"$temp_dir/stdout.log" 2>"$temp_dir/stderr.log" || {
      cat "$temp_dir/stderr.log" >&2
      echo "fresh_session_test: codex invocation failed — independent test unavailable" >&2
      exit 1
    }
  else
    codex exec --ephemeral --sandbox read-only --cd "$TARGET" \
      --output-schema "$SCHEMA" --output-last-message "$temp_dir/result.json" \
      "$PROMPT" >"$temp_dir/stdout.log" 2>"$temp_dir/stderr.log" || {
      cat "$temp_dir/stderr.log" >&2
      echo "fresh_session_test: codex invocation failed — independent test unavailable" >&2
      exit 1
    }
  fi
  raw="$(sed -n '1,$p' "$temp_dir/result.json")"
fi

printf '%s' "$raw" | python3 "$SCRIPT_DIR/validate_fresh_session.py" "$TARGET"
