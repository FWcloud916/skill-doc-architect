#!/usr/bin/env python3
"""Grade end-to-end doc-architect scenarios using deterministic invariants."""

import fnmatch
import json
import re
import sys
from datetime import date
from pathlib import Path

from scenario_common import snapshot

SCENARIOS = Path(__file__).resolve().parent.parent / "scenarios"
EXPECTED_KEYS = {
    "mode",
    "request",
    "allowed_changes",
    "required_changes",
    "required_paths",
    "forbidden_paths",
    "unchanged_paths",
    "required_contains",
    "forbidden_contains",
    "canonical_docs",
    "validate_relative_links",
    "final_required_sections",
    "final_required_contains",
}
MODES = {"G", "B", "U-1", "U-2"}


def load(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception as exc:  # noqa: BLE001
        return {"_parse_error": str(exc)}


def matches(path, patterns):
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def exists(path):
    return path.exists() or path.is_symlink()


def needle_label(needle):
    """Render a needle for the check name; a list is an any-of alternation."""
    return " | ".join(needle) if isinstance(needle, list) else needle


def valid_needle(needle):
    """A needle is a string, or a non-empty list of strings (any-of alternation)."""
    if isinstance(needle, str):
        return True
    return (
        isinstance(needle, list)
        and bool(needle)
        and all(isinstance(item, str) for item in needle)
    )


def markdown_links_ok(path, repo):
    text = path.read_text(errors="replace")
    links = re.findall(r"\[[^\]]*\]\(([^)]+)\)", text)
    failures = []
    for target in links:
        target = target.strip().strip("<>").split("#", 1)[0]
        if not target or re.match(r"^(https?://|mailto:)", target):
            continue
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(repo.resolve())
        except ValueError:
            failures.append(target)
            continue
        if not exists(resolved):
            failures.append(target)
    return failures


def canonical_frontmatter_ok(path):
    lines = path.read_text(errors="replace").splitlines()[:12]
    if not lines or not lines[0].startswith("# "):
        return False
    fields = {}
    for line in lines[1:]:
        match = re.match(r"> \*\*(Type|Audience|Last updated):\*\*\s*(.+)$", line)
        if match:
            fields[match.group(1)] = match.group(2).strip()
    if set(fields) != {"Type", "Audience", "Last updated"}:
        return False
    try:
        updated = date.fromisoformat(fields["Last updated"])
    except ValueError:
        return False
    return updated <= date.today()


def markdown_headings(text):
    """Return case-folded ATX headings, excluding prose keyword matches."""
    headings = set()
    for line in text.splitlines():
        match = re.match(r"^ {0,3}#{1,6}[ \t]+(.+?)[ \t]*$", line)
        if not match:
            continue
        heading = re.sub(r"[ \t]+#+[ \t]*$", "", match.group(1)).strip()
        if heading:
            headings.add(heading.casefold())
    return headings


def heading_has_section(headings, section):
    """Match a canonical section label as a phrase within an ATX heading."""
    pattern = re.compile(rf"(?<!\w){re.escape(section.casefold())}(?!\w)")
    return any(pattern.search(heading) for heading in headings)


def validate_scenario_definition(scenario_dir, expected):
    errors = []
    if not isinstance(expected, dict) or set(expected) != EXPECTED_KEYS:
        return [f"scenario.json keys: want={sorted(EXPECTED_KEYS)} got={sorted(expected)}"]
    if expected["mode"] not in MODES:
        errors.append(f"invalid mode: {expected['mode']}")
    if not isinstance(expected["request"], str) or not expected["request"].strip():
        errors.append("request must be a non-empty string")
    for key in (
        "allowed_changes", "required_changes", "required_paths", "forbidden_paths",
        "unchanged_paths", "canonical_docs", "final_required_sections",
        "final_required_contains",
    ):
        value = expected[key]
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            errors.append(f"{key} must be a string list")
    for key in ("required_contains", "forbidden_contains"):
        value = expected[key]
        if not isinstance(value, dict) or not all(
            isinstance(path, str) and isinstance(items, list)
            and all(valid_needle(item) for item in items)
            for path, items in value.items()
        ):
            errors.append(
                f"{key} must map paths to lists of strings or non-empty string lists"
            )
    if not isinstance(expected["validate_relative_links"], bool):
        errors.append("validate_relative_links must be boolean")
    if not (scenario_dir / "repo").is_dir():
        errors.append("repo/ missing")
    return errors


def grade_run(run_dir, scenario_dir, expected):
    checks = []

    def check(name, passed, evidence=""):
        checks.append((name, bool(passed), evidence))

    before = load(run_dir / "before.json")
    repo = run_dir / "repo"
    check("before_snapshot_valid", isinstance(before, dict) and "_parse_error" not in before)
    check("repo_exists", repo.is_dir())
    if not repo.is_dir() or "_parse_error" in before:
        return checks

    after = snapshot(repo)
    changed = sorted(
        path for path in set(before) | set(after) if before.get(path) != after.get(path)
    )
    disallowed = [path for path in changed if not matches(path, expected["allowed_changes"])]
    check("allowed_change_scope", not disallowed, str(disallowed))
    for pattern in expected["required_changes"]:
        check(f"required_change:{pattern}", any(fnmatch.fnmatchcase(path, pattern) for path in changed),
              str(changed))

    for relative in expected["required_paths"]:
        check(f"required_path:{relative}", exists(repo / relative))
    for relative in expected["forbidden_paths"]:
        check(f"forbidden_path:{relative}", not exists(repo / relative))
    for relative in expected["unchanged_paths"]:
        check(f"unchanged_path:{relative}", before.get(relative) == after.get(relative),
              f"before={before.get(relative)} after={after.get(relative)}")

    for relative, needles in expected["required_contains"].items():
        path = repo / relative
        text = path.read_text(errors="replace") if path.is_file() else ""
        for needle in needles:
            alternatives = needle if isinstance(needle, list) else [needle]
            check(f"required_contains:{relative}:{needle_label(needle)}",
                  any(alternative in text for alternative in alternatives))
    for relative, needles in expected["forbidden_contains"].items():
        path = repo / relative
        text = path.read_text(errors="replace") if path.is_file() else ""
        for needle in needles:
            alternatives = needle if isinstance(needle, list) else [needle]
            check(f"forbidden_contains:{relative}:{needle_label(needle)}",
                  not any(alternative in text for alternative in alternatives))

    for relative in expected["canonical_docs"]:
        path = repo / relative
        check(f"canonical_frontmatter:{relative}", path.is_file() and canonical_frontmatter_ok(path))

    if expected["validate_relative_links"]:
        for path in repo.rglob("*.md"):
            if ".git" in path.relative_to(repo).parts:
                continue
            failures = markdown_links_ok(path, repo)
            check(f"relative_links:{path.relative_to(repo)}", not failures, str(failures))

    final_path = run_dir / "final.txt"
    final = final_path.read_text(errors="replace") if final_path.is_file() else ""
    check("final_report_present", bool(final.strip()))
    headings = markdown_headings(final)
    for section in expected["final_required_sections"]:
        check(f"final_section:{section}", heading_has_section(headings, section))
    for needle in expected["final_required_contains"]:
        # Semantic markers remain prose checks; structure is graded separately above.
        check(f"final_contains:{needle}", needle.casefold() in final.casefold())
    return checks


def validate_suite(results):
    manifest = load(results / "manifest.json")
    if "_parse_error" in manifest:
        return None, [f"manifest.json: {manifest['_parse_error']}"]
    selected = manifest.get("selected_scenarios")
    runs = manifest.get("runs_per_scenario")
    errors = []
    if not isinstance(selected, list) or not selected or len(selected) != len(set(selected)):
        errors.append(f"invalid selected_scenarios: {selected}")
        return None, errors
    if not isinstance(runs, int) or runs < 1:
        errors.append(f"invalid runs_per_scenario: {runs}")
        return None, errors
    actual = sorted(path.name for path in results.iterdir() if path.is_dir())
    if actual != sorted(selected):
        errors.append(f"scenario dirs mismatch: want={sorted(selected)} got={actual}")
    for name in selected:
        if not (SCENARIOS / name / "scenario.json").is_file():
            errors.append(f"unknown scenario: {name}")
            continue
        got = sorted(path.name for path in (results / name).glob("run-*"))
        want = [f"run-{index}" for index in range(1, runs + 1)]
        if got != want:
            errors.append(f"{name}: run dirs mismatch: want={want} got={got}")
        for run_name in want:
            run_dir = results / name / run_name
            for required in ("before.json", "repo", "final.txt", "done"):
                if not exists(run_dir / required):
                    errors.append(f"{name}/{run_name}: missing {required}")
    return manifest, errors


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: grade_scenarios.py <results_dir>")
    results = Path(sys.argv[1])
    manifest, errors = validate_suite(results)
    if errors:
        for error in errors:
            print(f"XX suite: {error}")
        sys.exit(1)

    failures = []
    for name in manifest["selected_scenarios"]:
        scenario_dir = SCENARIOS / name
        expected = load(scenario_dir / "scenario.json")
        definition_errors = validate_scenario_definition(scenario_dir, expected)
        if definition_errors:
            for error in definition_errors:
                print(f"XX {name}: invalid definition ({error})")
            failures.append(name)
            continue
        passed = True
        lines = []
        for index in range(1, manifest["runs_per_scenario"] + 1):
            run_dir = results / name / f"run-{index}"
            for check_name, ok, evidence in grade_run(run_dir, scenario_dir, expected):
                if not ok:
                    passed = False
                    lines.append(f"    run-{index}: FAIL {check_name} ({evidence})")
        print(f"{'ok' if passed else 'XX'} {name}: {'PASS' if passed else 'FAIL'}")
        for line in lines:
            print(line)
        if not passed:
            failures.append(name)

    total = len(manifest["selected_scenarios"])
    print(f"\n{total - len(failures)}/{total} scenarios passed")
    if failures:
        print("failed:", ", ".join(failures))
        sys.exit(1)


if __name__ == "__main__":
    main()
