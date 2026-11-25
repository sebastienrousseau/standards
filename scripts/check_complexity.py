#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Sebastien Rousseau
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Hold every Python function to the complexity ceilings of AGENTS.md section 0.

Cyclomatic and Halstead difficulty come from radon, cognitive complexity from
complexipy, and lines from the function's span. A function over a ceiling
passes only if complexity-baseline.json records it at that value or worse, so
the baseline can only shrink: a new offender, a regression, or an entry that
no longer offends (remove it) fails the check.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import complexipy
from radon.complexity import cc_visit
from radon.metrics import h_visit

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "complexity-baseline.json"
SOURCES = ("scripts", "tests", "fuzz")
CEILINGS = {"cyclomatic": 10, "cognitive": 15, "halstead": 30.0, "lines": 60}
FILE_LINES = 500


def _measure(path: Path) -> dict[str, dict[str, float]]:
    """Every function in `path` by name, with its four metrics."""
    code = path.read_text(encoding="utf-8")
    metrics: dict[str, dict[str, float]] = {}
    for block in cc_visit(code):
        name = getattr(block, "fullname", block.name)
        metrics[name] = {"cyclomatic": block.complexity, "lines": block.endline - block.lineno + 1}
    for name, report in h_visit(code).functions:
        for key, entry in metrics.items():
            if key.split(".")[-1] == name:
                entry["halstead"] = round(report.difficulty, 2)
    for func in complexipy.file_complexity(str(path)).functions:
        for key, entry in metrics.items():
            if key.split(".")[-1] == func.name.split("::")[-1]:
                entry["cognitive"] = func.complexity
    return metrics


def _offences(rel: str, metrics: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    """The metrics over a ceiling, keyed by "file::function"."""
    found: dict[str, dict[str, float]] = {}
    for name, values in metrics.items():
        over = {k: v for k, v in values.items() if v > CEILINGS[k]}
        if over:
            found[f"{rel}::{name}"] = over
    return found


def _compare(found: dict[str, dict[str, float]], baseline: dict[str, dict[str, float]]) -> list[str]:
    """Failures: offences beyond the baseline, and baseline entries now cleared."""
    errors = []
    for key, over in found.items():
        for metric, value in over.items():
            allowed = baseline.get(key, {}).get(metric)
            if allowed is None or value > allowed:
                errors.append(f"{key}: {metric} {value} exceeds {CEILINGS[metric]} (baseline {allowed})")
    for key, recorded in baseline.items():
        for metric in recorded:
            if metric not in found.get(key, {}):
                errors.append(f"{key}: {metric} is now within its ceiling; remove it from {BASELINE.name}")
    return errors


def main() -> int:
    """Check every Python file under SOURCES; print each failure."""
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    found: dict[str, dict[str, float]] = {}
    errors: list[str] = []
    for directory in SOURCES:
        for path in sorted((ROOT / directory).rglob("*.py")):
            rel = path.relative_to(ROOT).as_posix()
            if len(path.read_text(encoding="utf-8").splitlines()) > FILE_LINES:
                errors.append(f"{rel}: more than {FILE_LINES} lines")
            found.update(_offences(rel, _measure(path)))
    errors += _compare(found, baseline)
    for error in errors:
        print(error)
    if not errors:
        print(f"complexity: every function within {CEILINGS}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
