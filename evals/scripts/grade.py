#!/usr/bin/env python3
"""Grade detection reports against fixture ground truth.

Usage:
    python3 grade.py <results_dir>

<results_dir> layout (produced by run_detection.sh):
    <results_dir>/<fixture>/run-<n>.json     # detection report emitted by the model

Each fixture's ground truth lives at fixtures/<fixture>/expected.json.

Grading is deterministic (no LLM judge needed — detection has objective answers):
  * resolution        exact match, hard fail
  * primary stacks    set of surfaces with role=primary must match exactly, hard fail
  * all surfaces      set of surface stacks must match exactly, hard fail
  * forbidden_stacks  none may appear anywhere in the report, hard fail
  * package_json_role exact match when specified, hard fail (the role vocabulary
    is part of the detection report contract in skills/doc-architect/references/stacks/README.md)

A fixture PASSES only if every run passes (default N=3): detection must be
stable across runs, not just right on average.

Exit code: 0 if all fixtures pass, 1 otherwise.
"""
import json
import sys
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def load(p: Path):
    try:
        return json.loads(p.read_text())
    except Exception as e:  # noqa: BLE001
        return {"_parse_error": str(e)}


def surfaces_by_role(report, roles):
    return sorted(
        s.get("stack", "?")
        for s in report.get("surfaces", [])
        if s.get("role", "primary") in roles
    )


def grade_run(report, expected):
    checks = []  # (name, passed, hard, evidence)

    if "_parse_error" in report:
        return [("valid_json_report", False, True, report["_parse_error"])]
    checks.append(("valid_json_report", True, True, ""))

    got_res, want_res = report.get("resolution"), expected["resolution"]
    checks.append(("resolution", got_res == want_res, True,
                   f"want={want_res} got={got_res}"))

    want_primary = sorted(s["stack"] for s in expected["surfaces"]
                          if s.get("role", "primary") == "primary")
    got_primary = surfaces_by_role(report, {"primary"})
    checks.append(("primary_stacks", got_primary == want_primary, True,
                   f"want={want_primary} got={got_primary}"))

    want_all = sorted(s["stack"] for s in expected["surfaces"])
    got_all = sorted(s.get("stack", "?") for s in report.get("surfaces", []))
    checks.append(("all_surfaces", got_all == want_all, True,
                   f"want={want_all} got={got_all}"))

    forbidden = set(expected.get("forbidden_stacks", []))
    hit = forbidden & set(got_all)
    checks.append(("no_forbidden_stacks", not hit, True,
                   f"forbidden hit: {sorted(hit)}" if hit else ""))

    if "package_json_role" in expected:
        got_role = report.get("package_json_role")
        checks.append(("package_json_role",
                       got_role == expected["package_json_role"], True,
                       f"want={expected['package_json_role']} got={got_role}"))

    return checks


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    results = Path(sys.argv[1])

    total, failed = 0, []
    for fdir in sorted(d for d in results.iterdir() if d.is_dir()):
        expected_path = FIXTURES / fdir.name / "expected.json"
        if not expected_path.exists():
            print(f"?? {fdir.name}: no expected.json, skipping")
            continue
        expected = load(expected_path)
        runs = sorted(fdir.glob("run-*.json"))
        if not runs:
            print(f"?? {fdir.name}: no runs found")
            continue

        total += 1
        fixture_pass = True
        lines = []
        for run in runs:
            checks = grade_run(load(run), expected)
            hard_fails = [c for c in checks if not c[1] and c[2]]
            soft_fails = [c for c in checks if not c[1] and not c[2]]
            if hard_fails:
                fixture_pass = False
                for name, _, _, ev in hard_fails:
                    lines.append(f"    {run.name}: FAIL {name} ({ev})")
            for name, _, _, ev in soft_fails:
                lines.append(f"    {run.name}: warn {name} ({ev})")

        status = "PASS" if fixture_pass else "FAIL"
        marker = "ok" if fixture_pass else "XX"
        print(f"{marker} {fdir.name}: {status} ({len(runs)} runs)")
        for line in lines:
            print(line)
        if not fixture_pass:
            failed.append(fdir.name)
            if expected.get("regression_for"):
                print(f"    ^ REGRESSION of: {expected['regression_for']}")

    print(f"\n{total - len(failed)}/{total} fixtures passed")
    if failed:
        print("failed:", ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()
