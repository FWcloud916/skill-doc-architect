#!/usr/bin/env python3
"""Normalize and validate independent Fresh Session Test JSON."""

import json
import re
import sys
from pathlib import Path

QUESTIONS = [
    "What is this system?",
    "How is it organized?",
    "How do I run it?",
    "How do I verify my work?",
    "What work state, if any, does this repository track?",
    "What does the core project terminology mean, and which synonyms are avoided?",
]
ANSWER_KEYS = {"q", "question", "answer", "citation"}
MARKDOWN_PATH = re.compile(r"(?:^|[\s(`])((?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.md)")


def parse_report(raw):
    text = raw
    try:
        envelope = json.loads(raw)
        if isinstance(envelope, dict) and "result" in envelope:
            if envelope.get("is_error"):
                raise ValueError("provider returned an error envelope")
            text = envelope["result"]
        elif isinstance(envelope, dict) and "answers" in envelope:
            return envelope
    except json.JSONDecodeError:
        pass
    if not isinstance(text, str):
        raise ValueError("provider result must be text or an answers object")
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("no JSON object in provider output")
    return json.loads(match.group(0))


def cited_path(citation):
    match = MARKDOWN_PATH.search(citation)
    return match.group(1) if match else None


def validate_report(report, target):
    target = Path(target).resolve()
    errors = []
    if not isinstance(report, dict) or set(report) != {"answers"}:
        return ["report must contain only the answers field"]
    answers = report.get("answers")
    expected_n = 6 if (target / "CONTEXT.md").is_file() else 5
    if not isinstance(answers, list) or len(answers) != expected_n:
        return [f"answers must contain exactly {expected_n} items"
                " (6 requires CONTEXT.md at the repository root)"]
    expected_qs = list(range(1, expected_n + 1))
    if [item.get("q") for item in answers if isinstance(item, dict)] != expected_qs:
        errors.append(f"answers must be ordered q=1..{expected_n}")

    for index, item in enumerate(answers, start=1):
        if not isinstance(item, dict) or set(item) != ANSWER_KEYS:
            errors.append(f"q{index}: invalid answer shape")
            continue
        if item.get("question") != QUESTIONS[index - 1]:
            errors.append(f"q{index}: question text drift")
        if not all(isinstance(item.get(key), str) and item[key].strip()
                   for key in ("question", "answer", "citation")):
            errors.append(f"q{index}: question/answer/citation must be non-empty strings")
            continue

        if index == 6 and cited_path(item["citation"]) != "CONTEXT.md":
            errors.append("q6: citation must cite CONTEXT.md itself")
            continue
        if index == 5 and not (target / "PROGRESS.md").exists():
            answer = item["answer"]
            citation = item["citation"]
            if "N/A" not in answer or "not agent-tracked" not in answer:
                errors.append("q5: absent PROGRESS.md requires the N/A not-agent-tracked answer")
            if "PROGRESS.md" not in citation or "absent" not in citation.lower():
                errors.append("q5: absent PROGRESS.md requires an absence citation")
            continue

        relative = cited_path(item["citation"])
        if relative is None:
            errors.append(f"q{index}: citation has no Markdown file path")
            continue
        path = Path(relative)
        if path.is_absolute() or ".." in path.parts:
            errors.append(f"q{index}: citation escapes repository: {relative}")
            continue
        if not (target / path).is_file():
            errors.append(f"q{index}: cited file does not exist: {relative}")
    return errors


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: validate_fresh_session.py <target_repo>")
    raw = sys.stdin.read()
    try:
        report = parse_report(raw)
        errors = validate_report(report, sys.argv[1])
        if errors:
            raise ValueError("; ".join(errors))
        print(json.dumps(report, indent=2))
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"_parse_error": str(exc), "_raw": raw[:2000]}))
        sys.exit(1)


if __name__ == "__main__":
    main()
