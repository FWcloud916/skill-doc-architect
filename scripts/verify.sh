#!/usr/bin/env bash
# Consistency gate for the doc-architect skill repo. Pure bash, no dependencies.
# Every check prints PASS/FAIL; any failure exits 1.
set -u
cd "$(dirname "$0")/.."

SKILL_DIR="skills/doc-architect"
SKILL_MD="$SKILL_DIR/SKILL.md"
REFS="$SKILL_DIR/references"

fail=0
report() { # $1=status(0 ok) $2=label $3=detail-on-fail
  if [ "$1" -eq 0 ]; then
    echo "PASS  $2"
  else
    echo "FAIL  $2${3:+ — $3}"
    fail=1
  fi
}

# 1. Bidirectional stack index
missing=""
for f in "$REFS"/stacks/*.md; do
  base=$(basename "$f")
  [ "$base" = "README.md" ] && continue
  grep -q "$base" "$REFS/stacks/README.md" || missing="$missing $base"
done
report "$([ -z "$missing" ]; echo $?)" "stack index lists every stack file" "not indexed:$missing"

dead=""
for name in $(grep -o '`[a-z-]*\.md`' "$REFS/stacks/README.md" | tr -d '\`' | sort -u); do
  [ -f "$REFS/stacks/$name" ] || dead="$dead $name"
done
report "$([ -z "$dead" ]; echo $?)" "every indexed stack file exists" "missing:$dead"

# 2. Five-section skeleton in every stack file
broken=""
for f in "$REFS"/stacks/*.md; do
  [ "$(basename "$f")" = "README.md" ] && continue
  for s in "Discovery map" "Diff → doc section map" "Linter signals" "Minimal test gate" "Command safety notes"; do
    grep -q "^## $s" "$f" || broken="$broken $(basename "$f"):[$s]"
  done
done
report "$([ -z "$broken" ]; echo $?)" "stack files have the 5-section skeleton" "$broken"

# 3. Canonical tokens — no bare iOS rows, no Apple-token spelling variants
hits=$(grep -rn "| iOS " "$SKILL_MD" "$REFS/" 2>/dev/null)
report "$([ -z "$hits" ]; echo $?)" "no bare '| iOS ' stack rows" "$hits"
variants=$(grep -rn "Apple(iOS\|iOS/MacOS\|IOS/macOS" "$SKILL_MD" "$REFS/" 2>/dev/null)
report "$([ -z "$variants" ]; echo $?)" "no 'Apple (iOS/macOS)' spelling variants" "$variants"

# 4. Safety annotation: stack files mentioning build tools must point back to §5
unref=""
for f in "$REFS"/stacks/*.md; do
  [ "$(basename "$f")" = "README.md" ] && continue
  if grep -qE 'gradlew|cargo (build|test|clippy)|dotnet (build|test|format)' "$f"; then
    grep -q "§5" "$f" || unref="$unref $(basename "$f")"
  fi
done
report "$([ -z "$unref" ]; echo $?)" "build-tool mentions point back to audit-checklist §5" "missing §5 ref:$unref"

# 5. No per-stack residue in SKILL.md (stack filenames or stack-specific terms)
residue=$(grep -nE 'flutter\.md|electron\.md|node-backend\.md|Zustand|WorkManager|go_router' "$SKILL_MD")
report "$([ -z "$residue" ]; echo $?)" "SKILL.md has no per-stack residue" "$residue"

# 5b. UI-surface marker: any stack file mentioning it must spell it exactly
bad_ui=""
for f in "$REFS"/stacks/*.md; do
  [ "$(basename "$f")" = "README.md" ] && continue
  if grep -q "UI surface" "$f" && ! grep -q '^> \*\*UI surface:\*\* yes' "$f"; then
    bad_ui="$bad_ui $(basename "$f")"
  fi
done
report "$([ -z "$bad_ui" ]; echo $?)" "UI-surface markers spelled canonically" "malformed:$bad_ui"

# 6. project-overview-template keeps sections ## 1. through ## 10.
n=$(grep -c '^## [0-9]*\.' "$REFS/project-overview-template.md")
report "$([ "$n" -eq 10 ]; echo $?)" "project-overview-template has exactly 10 numbered sections" "found $n"

# 7. Line budgets
skill_lines=$(wc -l < "$SKILL_MD")
report "$([ "$skill_lines" -le 225 ]; echo $?)" "SKILL.md within 225-line budget" "$skill_lines lines"
agents_lines=$(wc -l < AGENTS.md)
report "$([ "$agents_lines" -le 100 ]; echo $?)" "AGENTS.md within 100-line budget" "$agents_lines lines"

# 8. Reference integrity. Two bases: paths inside SKILL.md are relative to the
#    skill root ($SKILL_DIR); paths in README.md/AGENTS.md are repo-relative.
dead_refs=""
for p in $(grep -hoE '(references|scripts)/[a-z_-]+\.(md|sh)' "$SKILL_MD" | sort -u); do
  [ -f "$SKILL_DIR/$p" ] || dead_refs="$dead_refs SKILL.md:$p"
done
for p in $(grep -hoE 'skills/doc-architect/[a-z/_-]+\.(md|sh)' README.md AGENTS.md 2>/dev/null | sort -u); do
  [ -f "$p" ] || dead_refs="$dead_refs $p"
done
for p in $(grep -hoE '\]\((docs/[a-z-]+\.md|AGENTS\.md)\)' README.md AGENTS.md 2>/dev/null | sed -E 's/.*\((.*)\)/\1/' | sort -u); do
  [ -f "$p" ] || dead_refs="$dead_refs $p"
done
report "$([ -z "$dead_refs" ]; echo $?)" "cited reference/doc paths exist" "missing:$dead_refs"

script_hits=$(grep -rl "fresh_session_test\.sh" "$SKILL_MD" AGENTS.md "$REFS/" 2>/dev/null)
report "$([ -n "$script_hits" ] && [ -f "$SKILL_DIR/scripts/fresh_session_test.sh" ]; echo $?)" \
  "fresh_session_test.sh is referenced and exists" \
  "referenced: ${script_hits:-none}; exists: $([ -f "$SKILL_DIR/scripts/fresh_session_test.sh" ] && echo yes || echo no)"

# 9. Eval fixture lint: every fixture has expected.json; every stack name
#    referenced in any expected.json resolves to $REFS/stacks/<name>.md
no_expected=""
for d in evals/fixtures/*/; do
  [ -f "${d}expected.json" ] || no_expected="$no_expected $(basename "$d")"
done
report "$([ -z "$no_expected" ]; echo $?)" "every eval fixture has expected.json" "missing:$no_expected"

bad_stacks=""
stacks_refd=$( { grep -hoE '"stack": *"[a-z-]+"' evals/fixtures/*/expected.json | grep -oE '[a-z-]+"$' | tr -d '"'; \
  awk '/"forbidden_stacks"/,/\]/' evals/fixtures/*/expected.json | grep -oE '"[a-z-]+"' | tr -d '"'; } | sort -u)
for name in $stacks_refd; do
  [ -f "$REFS/stacks/$name.md" ] || bad_stacks="$bad_stacks $name"
done
report "$([ -z "$bad_stacks" ]; echo $?)" "eval fixtures reference only existing stack files" "unknown stacks:$bad_stacks"

# 10. Plugin manifests: parseable, names consistent with the skill layout
plugin_ok=1
if command -v python3 >/dev/null 2>&1; then
  python3 - <<'PY' && plugin_ok=0
import json, sys
p = json.load(open(".claude-plugin/plugin.json"))
m = json.load(open(".claude-plugin/marketplace.json"))
assert p["name"] == "doc-architect", "plugin.json name"
assert any(e["name"] == "doc-architect" for e in m["plugins"]), "marketplace entry"
assert "version" in p, "plugin.json version"
PY
else
  plugin_ok=0  # python3 unavailable — skip rather than fail
fi
report "$plugin_ok" "plugin manifests parse and name doc-architect" ""

# CLAUDE.md symlink sanity
link=$(readlink CLAUDE.md 2>/dev/null || true)
report "$([ "$link" = "AGENTS.md" ]; echo $?)" "CLAUDE.md is a symlink to AGENTS.md" "got: ${link:-not a symlink}"

echo
if [ "$fail" -eq 0 ]; then echo "verify.sh: all checks passed"; else echo "verify.sh: FAILURES above"; fi
exit "$fail"
