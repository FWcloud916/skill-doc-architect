#!/usr/bin/env python3
"""Grade detection reports against fixture ground truth and suite completeness."""

import json
import sys
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"
RESOLUTIONS = {"single", "hybrid", "ambiguous", "monorepo", "unknown"}
SURFACE_ROLES = {"primary", "surface", "candidate"}
PACKAGE_ROLE_ORDER = (
    "server",
    "ui-framework",
    "build-tooling",
    "desktop",
    "extension",
    "workspace",
    "plain-node",
    "frontend-entrypoint",
)
PACKAGE_ROLES = set(PACKAGE_ROLE_ORDER)
REPORT_KEYS = {"resolution", "surfaces", "package_json", "notes"}
MANIFEST_KEYS = {
    "runs_per_fixture", "selected_fixtures", "provider", "model", "effort"
}
PROVIDERS = {"anthropic", "openai"}


def load(path):
    try:
        return json.loads(Path(path).read_text())
    except Exception as exc:  # noqa: BLE001
        return {"_parse_error": str(exc)}


def check(name, passed, evidence=""):
    return name, bool(passed), evidence


def surface_pairs(value):
    if not isinstance(value, list):
        return []
    pairs = []
    for item in value:
        if isinstance(item, dict):
            stack = item.get("stack")
            role = item.get("role")
            pairs.append((stack if isinstance(stack, str) else repr(stack),
                          role if isinstance(role, str) else repr(role)))
    return sorted(pairs)


def package_entries(value):
    if not isinstance(value, list):
        return []
    entries = []
    for item in value:
        if isinstance(item, dict):
            path = item.get("path")
            roles = item.get("roles")
            safe_roles = tuple(roles) if isinstance(roles, list) and all(
                isinstance(role, str) for role in roles
            ) else (repr(roles),)
            entries.append((path if isinstance(path, str) else repr(path), safe_roles))
    return sorted(entries)


def repo_relative_file(root, value, basename=None):
    if not isinstance(value, str) or not value:
        return False
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        return False
    if basename is not None and path.name != basename:
        return False
    return (root / path).is_file()


def grade_run(report, expected, fixture_dir):
    checks = []
    if "_parse_error" in report:
        return [check("valid_json_report", False, report["_parse_error"])]

    checks.append(check("report_is_object", isinstance(report, dict)))
    if not isinstance(report, dict):
        return checks

    checks.append(check("exact_report_keys", set(report) == REPORT_KEYS,
                        f"want={sorted(REPORT_KEYS)} got={sorted(report)}"))
    resolution = report.get("resolution")
    surfaces = report.get("surfaces")
    packages = report.get("package_json")
    checks.append(check("resolution_vocabulary", resolution in RESOLUTIONS, str(resolution)))
    checks.append(check("surfaces_is_list", isinstance(surfaces, list)))
    checks.append(check("package_json_is_list", isinstance(packages, list)))
    checks.append(check("notes_is_string", isinstance(report.get("notes"), str)))

    expected_resolution = expected.get("resolution")
    checks.append(check("resolution", resolution == expected_resolution,
                        f"want={expected_resolution} got={resolution}"))

    got_pairs = surface_pairs(surfaces)
    want_pairs = surface_pairs(expected.get("surfaces", []))
    checks.append(check("surface_stack_roles", got_pairs == want_pairs,
                        f"want={want_pairs} got={got_pairs}"))

    forbidden = set(expected.get("forbidden_stacks", []))
    got_stacks = {stack for stack, _ in got_pairs}
    hit = forbidden & got_stacks
    checks.append(check("no_forbidden_stacks", not hit,
                        f"forbidden hit: {sorted(hit)}" if hit else ""))

    if isinstance(surfaces, list):
        for index, surface in enumerate(surfaces):
            valid_object = isinstance(surface, dict)
            checks.append(check(f"surface_{index}_is_object", valid_object))
            if not valid_object:
                continue
            checks.append(check(f"surface_{index}_exact_keys",
                                set(surface) == {"stack", "role", "evidence"},
                                str(sorted(surface))))
            checks.append(check(f"surface_{index}_role_vocabulary",
                                surface.get("role") in SURFACE_ROLES,
                                str(surface.get("role"))))
            evidence = surface.get("evidence")
            evidence_ok = isinstance(evidence, list) and evidence and all(
                repo_relative_file(fixture_dir, path) for path in evidence
            )
            checks.append(check(f"surface_{index}_evidence_paths", evidence_ok,
                                str(evidence)))

    role_counts = {role: 0 for role in SURFACE_ROLES}
    for _, role in got_pairs:
        if role in role_counts:
            role_counts[role] += 1
    invariant = {
        "unknown": len(got_pairs) == 0,
        "single": len(got_pairs) == 1 and role_counts["primary"] == 1,
        "hybrid": len(got_pairs) >= 2 and role_counts["primary"] == 1
                  and role_counts["surface"] == len(got_pairs) - 1,
        "ambiguous": len(got_pairs) >= 2 and role_counts["candidate"] == len(got_pairs),
        "monorepo": len(got_pairs) >= 1 and role_counts["surface"] == len(got_pairs),
    }.get(resolution, False)
    checks.append(check("resolution_role_invariant", invariant, str(role_counts)))

    expected_packages = expected.get("package_json", [])
    got_packages = package_entries(packages)
    want_packages = package_entries(expected_packages)
    checks.append(check("package_json_entries", got_packages == want_packages,
                        f"want={want_packages} got={got_packages}"))
    if isinstance(packages, list):
        for index, package in enumerate(packages):
            valid_object = isinstance(package, dict)
            checks.append(check(f"package_{index}_is_object", valid_object))
            if not valid_object:
                continue
            path = package.get("path")
            roles = package.get("roles")
            path_ok = repo_relative_file(fixture_dir, path, "package.json")
            roles_ok = isinstance(roles, list) and roles and all(
                isinstance(role, str) for role in roles
            )
            roles_ok = roles_ok and len(roles) == len(set(roles))
            roles_ok = roles_ok and all(role in PACKAGE_ROLES for role in roles)
            roles_ok = roles_ok and roles == sorted(
                roles, key=PACKAGE_ROLE_ORDER.index
            )
            checks.append(check(f"package_{index}_path", path_ok, str(path)))
            checks.append(check(f"package_{index}_roles", roles_ok, str(roles)))

    return checks


def validate_suite(results):
    manifest_path = results / "manifest.json"
    manifest = load(manifest_path)
    if "_parse_error" in manifest:
        return None, [f"manifest.json: {manifest['_parse_error']}"]
    runs = manifest.get("runs_per_fixture")
    selected = manifest.get("selected_fixtures")
    errors = []
    if set(manifest) != MANIFEST_KEYS:
        errors.append(
            f"manifest keys: want={sorted(MANIFEST_KEYS)} got={sorted(manifest)}"
        )
    if not isinstance(runs, int) or runs < 1:
        errors.append(f"invalid runs_per_fixture: {runs}")
    if manifest.get("provider") not in PROVIDERS:
        errors.append(f"invalid provider: {manifest.get('provider')}")
    for key in ("model", "effort"):
        value = manifest.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"invalid {key}: {value}")
    if not isinstance(selected, list) or not selected or len(selected) != len(set(selected)):
        errors.append(f"invalid selected_fixtures: {selected}")
        return None, errors
    actual_dirs = sorted(path.name for path in results.iterdir() if path.is_dir())
    if actual_dirs != sorted(selected):
        errors.append(f"fixture dirs mismatch: want={sorted(selected)} got={actual_dirs}")
    for name in selected:
        if not (FIXTURES / name / "expected.json").is_file():
            errors.append(f"unknown fixture: {name}")
            continue
        if isinstance(runs, int) and runs > 0:
            want = [f"run-{index}.json" for index in range(1, runs + 1)]
            got = {path.name for path in (results / name).glob("run-*.json")}
            if got != set(want):
                errors.append(f"{name}: run files mismatch: want={want} got={sorted(got)}")
    return manifest, errors


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: grade.py <results_dir>")
    results = Path(sys.argv[1])
    if not results.is_dir():
        sys.exit(f"results directory not found: {results}")

    manifest, suite_errors = validate_suite(results)
    if suite_errors:
        for error in suite_errors:
            print(f"XX suite: {error}")
        sys.exit(1)

    failed = []
    for name in manifest["selected_fixtures"]:
        fixture_dir = FIXTURES / name
        expected = load(fixture_dir / "expected.json")
        fixture_pass = True
        lines = []
        for index in range(1, manifest["runs_per_fixture"] + 1):
            run = results / name / f"run-{index}.json"
            checks = grade_run(load(run), expected, fixture_dir)
            for check_name, passed, evidence in checks:
                if not passed:
                    fixture_pass = False
                    lines.append(f"    {run.name}: FAIL {check_name} ({evidence})")
        print(f"{'ok' if fixture_pass else 'XX'} {name}: "
              f"{'PASS' if fixture_pass else 'FAIL'} ({manifest['runs_per_fixture']} runs)")
        for line in lines:
            print(line)
        if not fixture_pass:
            failed.append(name)
            if expected.get("regression_for"):
                print(f"    ^ REGRESSION of: {expected['regression_for']}")

    total = len(manifest["selected_fixtures"])
    print(f"\n{total - len(failed)}/{total} fixtures passed")
    if failed:
        print("failed:", ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()
