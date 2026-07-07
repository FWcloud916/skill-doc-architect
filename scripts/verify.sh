#!/usr/bin/env bash
# Consistency gate for the doc-architect skill repo. Pure bash, no dependencies.
# Every check prints PASS/FAIL; any failure exits 1.
set -u
cd "$(dirname "$0")/.."

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
for f in references/stacks/*.md; do
  base=$(basename "$f")
  [ "$base" = "README.md" ] && continue
  grep -q "$base" references/stacks/README.md || missing="$missing $base"
done
report "$([ -z "$missing" ]; echo $?)" "stack index lists every stack file" "not indexed:$missing"

dead=""
for name in $(grep -o '`[a-z-]*\.md`' references/stacks/README.md | tr -d '\`' | sort -u); do
  [ -f "references/stacks/$name" ] || dead="$dead $name"
done
report "$([ -z "$dead" ]; echo $?)" "every indexed stack file exists" "missing:$dead"

# 2. Five-section skeleton in every stack file
broken=""
for f in references/stacks/*.md; do
  [ "$(basename "$f")" = "README.md" ] && continue
  for s in "Discovery map" "Diff → doc section map" "Linter signals" "Minimal test gate" "Command safety notes"; do
    grep -q "^## $s" "$f" || broken="$broken $(basename "$f"):[$s]"
  done
done
report "$([ -z "$broken" ]; echo $?)" "stack files have the 5-section skeleton" "$broken"

# 3. Canonical tokens — no bare iOS rows, no Apple-token spelling variants
hits=$(grep -rn "| iOS " SKILL.md references/ 2>/dev/null)
report "$([ -z "$hits" ]; echo $?)" "no bare '| iOS ' stack rows" "$hits"
variants=$(grep -rn "Apple(iOS\|iOS/MacOS\|IOS/macOS" SKILL.md references/ 2>/dev/null)
report "$([ -z "$variants" ]; echo $?)" "no 'Apple (iOS/macOS)' spelling variants" "$variants"

# 4. Safety annotation: stack files mentioning build tools must point back to §5
unref=""
for f in references/stacks/*.md; do
  [ "$(basename "$f")" = "README.md" ] && continue
  if grep -qE 'gradlew|cargo (build|test|clippy)|dotnet (build|test|format)' "$f"; then
    grep -q "§5" "$f" || unref="$unref $(basename "$f")"
  fi
done
report "$([ -z "$unref" ]; echo $?)" "build-tool mentions point back to audit-checklist §5" "missing §5 ref:$unref"

# 5. No per-stack residue in SKILL.md (stack filenames or stack-specific terms)
residue=$(grep -nE 'flutter\.md|electron\.md|node-backend\.md|Zustand|WorkManager|go_router' SKILL.md)
report "$([ -z "$residue" ]; echo $?)" "SKILL.md has no per-stack residue" "$residue"

# 6. project-overview-template keeps sections ## 1. through ## 10.
n=$(grep -c '^## [0-9]*\.' references/project-overview-template.md)
report "$([ "$n" -eq 10 ]; echo $?)" "project-overview-template has exactly 10 numbered sections" "found $n"

# 7. Line budgets
skill_lines=$(wc -l < SKILL.md)
report "$([ "$skill_lines" -le 210 ]; echo $?)" "SKILL.md within 210-line budget" "$skill_lines lines"
agents_lines=$(wc -l < AGENTS.md)
report "$([ "$agents_lines" -le 100 ]; echo $?)" "AGENTS.md within 100-line budget" "$agents_lines lines"

# 8. Reference integrity: paths cited in SKILL.md References list and README doc table exist
dead_refs=""
for p in $(grep -hoE 'references/[a-z-]+\.md' SKILL.md README.md | sort -u); do
  [ -f "$p" ] || dead_refs="$dead_refs $p"
done
for p in $(grep -hoE '\]\((docs/[a-z-]+\.md|SKILL\.md|AGENTS\.md)\)' README.md AGENTS.md 2>/dev/null | sed -E 's/.*\((.*)\)/\1/' | sort -u); do
  [ -f "$p" ] || dead_refs="$dead_refs $p"
done
report "$([ -z "$dead_refs" ]; echo $?)" "cited reference/doc paths exist" "missing:$dead_refs"

# CLAUDE.md symlink sanity
link=$(readlink CLAUDE.md 2>/dev/null || true)
report "$([ "$link" = "AGENTS.md" ]; echo $?)" "CLAUDE.md is a symlink to AGENTS.md" "got: ${link:-not a symlink}"

echo
if [ "$fail" -eq 0 ]; then echo "verify.sh: all checks passed"; else echo "verify.sh: FAILURES above"; fi
exit "$fail"
