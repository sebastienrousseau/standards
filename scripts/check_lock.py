#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Sebastien Rousseau
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hold the dependency provenance policy of docs/POLICIES.md.

- Every package in uv.lock comes from PyPI, apart from this project itself:
  no git, URL or path source.
- Every sdist and wheel in uv.lock carries a SHA-256, which uv checks on
  install.
- Every `uv run` and `uv sync` in the Makefiles and workflows is `--frozen`
  or `--locked`, so CI installs exactly the locked, hashed set.

uv.lock is read line by line, not with tomllib, so this runs on every
Python the dev tools support (3.10 has no tomllib).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYPI = 'source = { registry = "https://pypi.org/simple" }'
SELF = 'source = { editable = "." }'
ARTIFACT = re.compile(r'\burl = "([^"]+)"')
HASH = re.compile(r'\bhash = "sha256:[0-9a-f]{64}"')
UV_CALL = re.compile(r"(?:\buv|\$\(UV\))\s+(?:run|sync)\b[^\n]*")
FROZEN = re.compile(r"--(?:frozen|locked)\b")


def _packages(lock: str) -> list[str]:
    return lock.split("\n[[package]]\n")[1:]


def lock_errors(lock: str) -> list[str]:
    """Sources other than PyPI, and artifacts without a SHA-256."""
    errors = []
    for block in _packages(lock):
        name = re.search(r'(?m)^name = "([^"]+)"', block)
        label = name.group(1) if name else "?"
        source = re.search(r"(?m)^source = .*$", block)
        if not source or source.group(0) not in (PYPI, SELF):
            errors.append(f"uv.lock: {label}: source is not PyPI: {source.group(0) if source else 'none'}")
        for line in block.splitlines():
            url = ARTIFACT.search(line)
            if url and not HASH.search(line):
                errors.append(f"uv.lock: {label}: no SHA-256 for {url.group(1)}")
    return errors


def unfrozen_calls(path: Path, text: str) -> list[str]:
    """`uv run` or `uv sync` calls that may re-resolve instead of using the lock."""
    errors = []
    for number, line in enumerate(text.splitlines(), 1):
        for call in UV_CALL.findall(line):
            if not FROZEN.search(call):
                errors.append(f"{path}:{number}: uv call without --frozen or --locked: {call.strip()}")
    return errors


def main(root: Path = ROOT) -> int:
    """Check uv.lock and every uv call; print each failure."""
    errors = lock_errors((root / "uv.lock").read_text(encoding="utf-8"))
    files = [root / "Makefile", root / "GNUmakefile", *sorted((root / ".github" / "workflows").glob("*.yml"))]
    for path in files:
        errors += unfrozen_calls(path.relative_to(root), path.read_text(encoding="utf-8"))
    for error in errors:
        print(error)
    if not errors:
        print("lock: every dependency from PyPI, hashed, installed frozen")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
