#!/usr/bin/env python3
"""Shared filesystem helpers for end-to-end doc-architect scenarios."""

import hashlib
import json
import os
import sys
from pathlib import Path

IGNORED_DIRS = {".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", "__pycache__"}


def snapshot(root):
    """Return stable fingerprints, excluding Git internals and known tool caches."""
    root = Path(root)
    result = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in IGNORED_DIRS for part in relative.parts):
            continue
        key = relative.as_posix()
        if path.is_symlink():
            result[key] = f"symlink:{os.readlink(path)}"
        elif path.is_file():
            result[key] = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def write_snapshot(root, output):
    Path(output).write_text(json.dumps(snapshot(root), indent=2, sort_keys=True) + "\n")


def main():
    if len(sys.argv) != 4 or sys.argv[1] != "snapshot":
        sys.exit("Usage: scenario_common.py snapshot <repo> <output.json>")
    write_snapshot(sys.argv[2], sys.argv[3])


if __name__ == "__main__":
    main()
