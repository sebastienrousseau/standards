#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Sebastien Rousseau
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Fail on a breaking change to sync.py's public Python API since the last release.

The baseline is the newest release tag that contains scripts/sync.py. With no
such tag yet there is nothing to compare against, and the check says so and
passes. The command-line contract is pinned separately, by
tests/test_sync.py::test_cli_options_are_stable.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import griffe

ROOT = Path(__file__).resolve().parents[1]


def _git(*args: str) -> str:
    git = shutil.which("git") or "git"
    # A fixed git argv on this repository; no shell is involved.
    result = subprocess.run([git, "-C", str(ROOT), *args], capture_output=True, text=True, check=False)  # noqa: S603
    return result.stdout if result.returncode == 0 else ""


def baseline_tag() -> str | None:
    """The newest v* tag whose tree holds scripts/sync.py."""
    for tag in _git("tag", "--list", "v*", "--sort=-v:refname").split():
        if _git("ls-tree", "--name-only", tag, "scripts/sync.py").strip():
            return tag
    return None


def main() -> int:
    """Compare the working tree's sync module with the baseline release."""
    tag = baseline_tag()
    if tag is None:
        print("api: no release contains scripts/sync.py yet; nothing to compare")
        return 0
    old = griffe.load_git("sync", ref=tag, repo=ROOT, search_paths=["scripts"])
    new = griffe.load("sync", search_paths=[str(ROOT / "scripts")])
    breakages = list(griffe.find_breaking_changes(old, new))
    for breakage in breakages:
        print(f"api: {breakage.explain()}")
    if not breakages:
        print(f"api: no breaking change since {tag}")
    return 1 if breakages else 0


if __name__ == "__main__":
    sys.exit(main())
