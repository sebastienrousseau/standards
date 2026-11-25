#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Sebastien Rousseau
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""End-to-end check of the standards-sync command with the standard library only.

It runs on the minimum Python (3.9), where no pytest release is free of
known advisories, so it needs nothing but python3 and git: push to a
scratch target, check it, edit a file in place, and confirm the next push
keeps the edit and the check reports it.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNC = ROOT / "scripts" / "sync.py"


def sync(env: dict[str, str], *args: str) -> tuple[int, str]:
    """Run standards-sync with `args`; return its exit status and output."""
    result = subprocess.run([sys.executable, str(SYNC), *args], env=env, capture_output=True, text=True, check=False)
    return result.returncode, result.stdout


def expect(condition: bool, message: str) -> None:
    """Stop with `message` unless `condition` holds."""
    if not condition:
        sys.exit(f"smoke: FAIL: {message}")
    print(f"smoke: ok: {message}")


def main() -> int:
    """Push, check, edit in place, push again, check again."""
    with tempfile.TemporaryDirectory() as scratch:
        target = Path(scratch) / "Code"
        env = {**os.environ, "STANDARDS_REPO": str(ROOT), "STANDARDS_TARGETS": str(target)}
        status, _ = sync(env, "--push")
        expect(status == 0 and (target / "AGENTS.md").is_file(), "push copies the standards")
        status, out = sync(env, "--check")
        expect(status == 0 and "All standards are synchronized." in out, "check finds them in sync")
        (target / "AGENTS.md").write_text("an edit made in place\n", encoding="utf-8")
        status, out = sync(env, "--push")
        expect(status == 1 and "[KEPT] AGENTS.md" in out, "push keeps an edit made in place")
        expect((target / "AGENTS.md").read_text(encoding="utf-8") == "an edit made in place\n", "the edit survives")
        status, out = sync(env, "--check")
        expect(status == 1 and "[DRIFTED] AGENTS.md" in out, "check reports the drift")
    print(f"smoke: passed on Python {sys.version.split()[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
