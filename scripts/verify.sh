#!/usr/bin/env bash
# Consistency gate for the doc-architect skill repo. Requires Bash + Python 3.
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
signal_table=$(awk '/^## Signal table/{inside=1; next} /^Notes:/{inside=0} inside' \
  "$REFS/stacks/README.md")
missing=""
for f in "$REFS"/stacks/*.md; do
  base=$(basename "$f")
  [ "$base" = "README.md" ] && continue
  printf '%s\n' "$signal_table" | grep -q "$base" || missing="$missing $base"
done
report "$([ -z "$missing" ]; echo $?)" "stack index lists every stack file" "not indexed:$missing"

dead=""
for name in $(printf '%s\n' "$signal_table" | grep -o '`[a-z-]*\.md`' | tr -d '\`' | sort -u); do
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

# 3. Canonical stack-label spellings in current user-facing enumerations
hits=$(grep -rn "| iOS " "$SKILL_MD" "$REFS/" 2>/dev/null)
report "$([ -z "$hits" ]; echo $?)" "no bare '| iOS ' stack rows" "$hits"
variants=$(grep -rn "Apple(iOS\|iOS/MacOS\|IOS/macOS" "$SKILL_MD" "$REFS/" 2>/dev/null)
report "$([ -z "$variants" ]; echo $?)" "no 'Apple (iOS/macOS)' spelling variants" "$variants"
label_drift=$(grep -nE 'Windows \.NET|Electron/Tauri/macOS|mobile — iOS' "$SKILL_MD" README.md 2>/dev/null)
report "$([ -z "$label_drift" ]; echo $?)" "README/SKILL use canonical stack labels" "$label_drift"

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

# 5b. Every stack declares one tri-state design surface and its evidence row
bad_design=""
for f in "$REFS"/stacks/*.md; do
  [ "$(basename "$f")" = "README.md" ] && continue
  count=$(grep -cE '^> \*\*Design surface:\*\* (inherent|conditional|none)( |$)' "$f")
  [ "$count" -eq 1 ] || bad_design="$bad_design $(basename "$f"):marker=$count"
  grep -q '^| Design-surface evidence |' "$f" || bad_design="$bad_design $(basename "$f"):evidence"
  if ! grep -q '^> \*\*Design surface:\*\* none' "$f"; then
    grep -q '| DESIGN.md tokens + matching prose' "$f" || bad_design="$bad_design $(basename "$f"):diff-map"
  fi
done
report "$([ -z "$bad_design" ]; echo $?)" "stack design-surface metadata and evidence are complete" "$bad_design"

legacy_ui=$(grep -rn 'UI surface' "$SKILL_MD" "$REFS/" 2>/dev/null)
report "$([ -z "$legacy_ui" ]; echo $?)" "legacy UI-surface marker removed" "$legacy_ui"

stack_npx=$(grep -rnE '\bnpx\b|npm exec|pnpm dlx|yarn dlx|bunx' "$REFS"/stacks/*.md 2>/dev/null)
report "$([ -z "$stack_npx" ]; echo $?)" "stack probes avoid on-demand package runners" "$stack_npx"

safe_block=$(awk '/^\*\*SAFE —/{inside=1} /^\*\*NOT SAFE —/{inside=0} inside' "$REFS/audit-checklist.md")
safe_runner=$(printf '%s\n' "$safe_block" | grep -E '\bnpx\b|npm exec|pnpm dlx|yarn dlx|bunx')
report "$([ -z "$safe_runner" ]; echo $?)" "audit SAFE block avoids on-demand package runners" "$safe_runner"

# 6. Cross-referenced numbered sections stay exact and ordered
project_sections=$(grep '^## [0-9]*\.' "$REFS/project-overview-template.md" | sed -E 's/^## ([0-9]+)\..*/\1/' | tr '\n' ' ')
report "$([ "$project_sections" = '1 2 3 4 5 6 7 8 9 10 ' ]; echo $?)" \
  "project-overview-template keeps sections 1 through 10 in order" "$project_sections"
audit_sections=$(grep '^## [0-9]*\.' "$REFS/audit-checklist.md" | sed -E 's/^## ([0-9]+)\..*/\1/' | tr '\n' ' ')
report "$([ "$audit_sections" = '1 2 3 4 5 6 ' ]; echo $?)" \
  "audit-checklist keeps sections 1 through 6 in order" "$audit_sections"

# 7. Line budgets
skill_lines=$(wc -l < "$SKILL_MD")
report "$([ "$skill_lines" -le 225 ]; echo $?)" "SKILL.md within 225-line budget" "$skill_lines lines"
description_words=$(awk 'NR >= 4 { if ($0 == "---") exit; print }' "$SKILL_MD" | wc -w | tr -d ' ')
report "$([ "$description_words" -ge 60 ] && [ "$description_words" -le 140 ]; echo $?)" \
  "SKILL.md trigger description stays concise" "$description_words words (expected 60..140)"
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

fresh_tests_ok=1
python3 "$SKILL_DIR/scripts/test_fresh_session.py" >/dev/null 2>&1 && fresh_tests_ok=0
report "$fresh_tests_ok" "Fresh Session parser and citation tests pass" "test_fresh_session.py failed"

fresh_prompt_ok=1
grep -q 'citation exactly' "$SKILL_DIR/scripts/fresh_session_test.sh" && \
  grep -q 'PROGRESS.md absent at repository root' "$SKILL_DIR/scripts/fresh_session_test.sh" && \
  fresh_prompt_ok=0
report "$fresh_prompt_ok" "Fresh Session prompt pins the Q5 absence citation" \
  "fresh_session_test.sh prompt drifted from the validator contract"

fresh_schema_ok=1
python3 - <<'PY' && fresh_schema_ok=0
import json
from pathlib import Path

schema = json.loads(Path("skills/doc-architect/references/fresh-session-report.schema.json").read_text())
assert schema["required"] == ["answers"]
answers = schema["properties"]["answers"]
assert answers["minItems"] == answers["maxItems"] == 5
assert set(answers["items"]["required"]) == {"q", "question", "answer", "citation"}
PY
report "$fresh_schema_ok" "Fresh Session report schema is valid" "schema validation failed"

# 9. Eval fixture lint: every fixture has expected.json; every stack name
#    referenced in any expected.json resolves to $REFS/stacks/<name>.md
no_expected=""
for d in evals/fixtures/*/; do
  [ -f "${d}expected.json" ] || no_expected="$no_expected $(basename "$d")"
done
report "$([ -z "$no_expected" ]; echo $?)" "every eval fixture has expected.json" "missing:$no_expected"

fixture_count=$(find evals/fixtures -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
basic_count=$(find evals/fixtures -mindepth 1 -maxdepth 1 -type d -name 'basic-*' | wc -l | tr -d ' ')
trap_count=$(find evals/fixtures -mindepth 1 -maxdepth 1 -type d -name 'trap-*' | wc -l | tr -d ' ')
count_docs_ok=0
grep -q "# $fixture_count minimal repos" evals/README.md || count_docs_ok=1
grep -q "# $basic_count: one per stack file" evals/README.md || count_docs_ok=1
grep -q "# $trap_count: hybrid/ordering/fallback traps" evals/README.md || count_docs_ok=1
report "$count_docs_ok" "eval README fixture counts match the filesystem" \
  "actual total/basic/trap=$fixture_count/$basic_count/$trap_count"

bad_stacks=""
stacks_refd=$( { grep -hoE '"stack": *"[a-z-]+"' evals/fixtures/*/expected.json | grep -oE '[a-z-]+"$' | tr -d '"'; \
  awk '/"forbidden_stacks"/,/\]/' evals/fixtures/*/expected.json | grep -oE '"[a-z-]+"' | tr -d '"'; } | sort -u)
for name in $stacks_refd; do
  [ -f "$REFS/stacks/$name.md" ] || bad_stacks="$bad_stacks $name"
done
report "$([ -z "$bad_stacks" ]; echo $?)" "eval fixtures reference only existing stack files" "unknown stacks:$bad_stacks"

fixture_schema_ok=1
python3 - <<'PY' && fixture_schema_ok=0
import json
from pathlib import Path

roles = {"primary", "surface", "candidate"}
resolutions = {"single", "hybrid", "ambiguous", "monorepo", "unknown"}
package_roles = {"server", "ui-framework", "build-tooling", "desktop", "extension",
                 "workspace", "plain-node", "frontend-entrypoint"}
package_role_order = ["server", "ui-framework", "build-tooling", "desktop", "extension",
                      "workspace", "plain-node", "frontend-entrypoint"]
for expected_path in Path("evals/fixtures").glob("*/expected.json"):
    fixture = expected_path.parent
    data = json.loads(expected_path.read_text())
    assert data["resolution"] in resolutions, expected_path
    assert isinstance(data["surfaces"], list), expected_path
    assert "package_json_role" not in data, expected_path
    for surface in data["surfaces"]:
        assert set(surface) == {"stack", "role"}, (expected_path, surface)
        assert surface["role"] in roles, (expected_path, surface)
    for package in data.get("package_json", []):
        assert set(package) == {"path", "roles"}, (expected_path, package)
        assert (fixture / package["path"]).is_file(), (expected_path, package["path"])
        assert Path(package["path"]).name == "package.json", (expected_path, package["path"])
        assert package["roles"] and len(package["roles"]) == len(set(package["roles"])), package
        assert set(package["roles"]) <= package_roles, (expected_path, package)
        assert package["roles"] == sorted(package["roles"], key=package_role_order.index), package
for name in ("trap-react-native-role", "trap-ruby-gem", "trap-swift-package-library"):
    data = json.loads((Path("evals/fixtures") / name / "expected.json").read_text())
    assert data.get("regression_for"), name

schema = json.loads(Path("evals/detection-report.schema.json").read_text())
schema_stacks = set(schema["properties"]["surfaces"]["items"]["properties"]["stack"]["enum"])
stack_files = {path.stem for path in Path("skills/doc-architect/references/stacks").glob("*.md")
               if path.name != "README.md"}
assert schema_stacks == stack_files, (schema_stacks, stack_files)
PY
report "$fixture_schema_ok" "eval expected.json files satisfy the v2 schema" "schema validation failed"

grade_tests_ok=1
python3 evals/scripts/test_grade.py >/dev/null 2>&1 && grade_tests_ok=0
report "$grade_tests_ok" "detection grader false-green regression tests pass" "test_grade.py failed"

detection_ci_tests_ok=1
python3 evals/scripts/test_detection_ci.py >/dev/null 2>&1 && detection_ci_tests_ok=0
report "$detection_ci_tests_ok" "shared detection prompt and CI contracts pass" \
  "test_detection_ci.py failed"

# 9b. End-to-end scenarios and trigger boundary contract
scenario_count=$(find evals/scenarios -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')
scenario_layout_ok=1
python3 - <<'PY' && scenario_layout_ok=0
import json
from pathlib import Path

expected_keys = {
    "mode", "request", "allowed_changes", "required_changes", "required_paths",
    "forbidden_paths", "unchanged_paths", "required_contains", "forbidden_contains",
    "canonical_docs", "validate_relative_links", "final_required_sections",
    "final_required_contains",
}
root = Path("evals/scenarios")
scenarios = sorted(path for path in root.iterdir() if path.is_dir())
assert len(scenarios) == 7, len(scenarios)
for scenario in scenarios:
    assert (scenario / "repo").is_dir(), scenario
    data = json.loads((scenario / "scenario.json").read_text())
    assert set(data) == expected_keys, (scenario, set(data))
    assert data["mode"] in {"G", "B", "U-1", "U-2"}, scenario
    assert isinstance(data["request"], str) and data["request"].strip(), scenario
    assert isinstance(data["validate_relative_links"], bool), scenario
    assert data["final_required_sections"], scenario
PY
report "$scenario_layout_ok" "seven end-to-end scenario contracts are valid" \
  "actual scenario count=$scenario_count"

bad_patches=""
for patch in evals/scenarios/*/change.patch; do
  [ -f "$patch" ] || continue
  scenario_dir=$(dirname "$patch")
  (cd "$scenario_dir/repo" && git apply --check ../change.patch) >/dev/null 2>&1 || \
    bad_patches="$bad_patches $(basename "$scenario_dir")"
done
report "$([ -z "$bad_patches" ]; echo $?)" "scenario feature patches apply cleanly" "$bad_patches"

scenario_tests_ok=1
python3 evals/scripts/test_grade_scenarios.py >/dev/null 2>&1 && scenario_tests_ok=0
report "$scenario_tests_ok" "scenario grader false-green regression tests pass" \
  "test_grade_scenarios.py failed"

trigger_matrix_ok=1
python3 - <<'PY' && trigger_matrix_ok=0
import json
from collections import Counter

cases = json.load(open("evals/trigger-matrix.json"))
assert len(cases) == 16
assert all(set(case) == {"id", "prompt", "expected", "reason"} for case in cases)
assert len({case["id"] for case in cases}) == len(cases)
assert all(case["prompt"].strip() and case["reason"].strip() for case in cases)
assert Counter(case["expected"] for case in cases) == {
    "doc-architect": 8,
    "prefer-project-docs": 4,
    "not-doc-architect": 4,
}
PY
report "$trigger_matrix_ok" "trigger boundary matrix has the 8/4/4 contract" \
  "trigger-matrix.json validation failed"

legacy_contract=$(grep -rn 'package_json_role\|unsafe_commands_flagged' \
  "$REFS/stacks/README.md" evals/scripts evals/README.md evals/fixtures/*/expected.json 2>/dev/null)
report "$([ -z "$legacy_contract" ]; echo $?)" "legacy detection-report fields removed" "$legacy_contract"

# 10. Plugin manifests: parseable, names consistent with the skill layout
plugin_ok=1
if command -v python3 >/dev/null 2>&1; then
  python3 - <<'PY' && plugin_ok=0
import json, sys
p = json.load(open(".claude-plugin/plugin.json"))
m = json.load(open(".claude-plugin/marketplace.json"))
assert p["name"] == "doc-architect", "plugin.json name"
assert any(e["name"] == "doc-architect" for e in m["plugins"]), "marketplace entry"
parts = p["version"].split(".")
assert len(parts) == 3 and all(part.isdigit() for part in parts), "plugin.json semver"
PY
else
  plugin_ok=0  # python3 unavailable — skip rather than fail
fi
report "$plugin_ok" "plugin manifests parse and name doc-architect" ""

openai_yaml_ok=1
python3 - <<'PY' && openai_yaml_ok=0
from pathlib import Path

lines = Path("skills/doc-architect/agents/openai.yaml").read_text().splitlines()
assert lines[0] == "interface:"
values = {}
for line in lines[1:]:
    key, value = line.strip().split(": ", 1)
    assert value.startswith('"') and value.endswith('"')
    values[key] = value[1:-1]
assert set(values) == {"display_name", "short_description", "default_prompt"}
assert values["display_name"] == "Doc Architect"
assert 25 <= len(values["short_description"]) <= 64
assert "$doc-architect" in values["default_prompt"]
PY
report "$openai_yaml_ok" "Codex agents/openai.yaml metadata is complete" \
  "openai.yaml validation failed"

shell_syntax_ok=0
bash -n evals/scripts/run_detection.sh evals/scripts/run_scenarios.sh \
  "$SKILL_DIR/scripts/fresh_session_test.sh" || shell_syntax_ok=1
report "$shell_syntax_ok" "eval and Fresh Session shell syntax is valid" "bash -n failed"

# CLAUDE.md symlink sanity
link=$(readlink CLAUDE.md 2>/dev/null || true)
report "$([ "$link" = "AGENTS.md" ]; echo $?)" "CLAUDE.md is a symlink to AGENTS.md" "got: ${link:-not a symlink}"

echo
if [ "$fail" -eq 0 ]; then echo "verify.sh: all checks passed"; else echo "verify.sh: FAILURES above"; fi
exit "$fail"
