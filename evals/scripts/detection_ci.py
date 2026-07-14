#!/usr/bin/env python3
"""Prepare detection-eval CI matrices and provider-specific manifests."""

import argparse
import json
from pathlib import Path


PROVIDERS = {"anthropic", "openai", "both"}
MANIFEST_PROVIDERS = {"anthropic", "openai"}
OPENAI_EFFORTS = {"low", "medium", "high"}
MAX_GITHUB_MATRIX_JOBS = 256


def parse_runs(value):
    try:
        runs = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"runs must be a positive integer: {value}") from exc
    if runs < 1:
        raise ValueError(f"runs must be a positive integer: {value}")
    return runs


def select_fixtures(fixtures_dir, filter_text=""):
    root = Path(fixtures_dir)
    selected = sorted(
        path.name for path in root.iterdir()
        if path.is_dir() and (not filter_text or filter_text in path.name)
    )
    if not selected:
        raise ValueError(f"fixture filter matched nothing: {filter_text or '<all>'}")
    return selected


def validate_request(provider, anthropic_model, openai_model, openai_effort):
    if provider not in PROVIDERS:
        raise ValueError(f"invalid provider: {provider}")
    if provider in {"anthropic", "both"} and not anthropic_model.strip():
        raise ValueError("anthropic_model must not be blank")
    if provider in {"openai", "both"}:
        if not openai_model.strip():
            raise ValueError("openai_model must not be blank")
        if openai_effort not in OPENAI_EFFORTS:
            raise ValueError(f"invalid openai_effort: {openai_effort}")


def build_matrix(selected, runs):
    size = len(selected) * runs
    if size > MAX_GITHUB_MATRIX_JOBS:
        raise ValueError(
            f"OpenAI matrix has {size} jobs; GitHub Actions limit is "
            f"{MAX_GITHUB_MATRIX_JOBS}"
        )
    return {
        "include": [
            {"fixture": fixture, "run": run}
            for fixture in selected
            for run in range(1, runs + 1)
        ]
    }


def manifest_data(selected, runs, provider, model, effort):
    if provider not in MANIFEST_PROVIDERS:
        raise ValueError(f"manifest provider must be anthropic or openai: {provider}")
    if not model.strip() or not effort.strip():
        raise ValueError("manifest model and effort must not be blank")
    return {
        "runs_per_fixture": runs,
        "selected_fixtures": selected,
        "provider": provider,
        "model": model,
        "effort": effort,
    }


def write_github_output(path, matrix, selected):
    with Path(path).open("a") as output:
        output.write(f"matrix={json.dumps(matrix, separators=(',', ':'))}\n")
        output.write(f"selected={json.dumps(selected, separators=(',', ':'))}\n")


def add_common_selection_args(parser):
    parser.add_argument("--fixtures", required=True)
    parser.add_argument("--runs", required=True)
    parser.add_argument("--filter", default="")


def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)

    prepare = commands.add_parser("prepare")
    add_common_selection_args(prepare)
    prepare.add_argument("--provider", required=True)
    prepare.add_argument("--anthropic-model", default="")
    prepare.add_argument("--openai-model", default="")
    prepare.add_argument("--openai-effort", default="medium")
    prepare.add_argument("--github-output", required=True)

    manifest = commands.add_parser("manifest")
    add_common_selection_args(manifest)
    manifest.add_argument("--provider", required=True)
    manifest.add_argument("--model", required=True)
    manifest.add_argument("--effort", required=True)
    manifest.add_argument("--results", required=True)

    args = parser.parse_args()
    try:
        runs = parse_runs(args.runs)
        selected = select_fixtures(args.fixtures, args.filter)
        if args.command == "prepare":
            validate_request(
                args.provider, args.anthropic_model, args.openai_model,
                args.openai_effort,
            )
            write_github_output(
                args.github_output, build_matrix(selected, runs), selected
            )
        else:
            data = manifest_data(
                selected, runs, args.provider, args.model, args.effort
            )
            results = Path(args.results)
            results.mkdir(parents=True, exist_ok=True)
            (results / "manifest.json").write_text(json.dumps(data, indent=2) + "\n")
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
