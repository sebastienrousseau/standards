# SPDX-FileCopyrightText: 2026 Sebastien Rousseau
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""The complexity gate: ceilings, and a baseline that may only shrink."""

from __future__ import annotations

import json
from pathlib import Path

import check_complexity as gate
import pytest

COMPLEX = "def f(a):\n" + "".join(f"    if a == {i}:\n        return {i}\n" for i in range(12)) + "    return -1\n"


def test_offences_are_the_metrics_over_a_ceiling(tmp_path: Path) -> None:
    path = tmp_path / "m.py"
    path.write_text(COMPLEX + "\n\ndef g():\n    return 1\n")
    found = gate._offences("m.py", gate._measure(path))
    assert list(found) == ["m.py::f"]
    assert found["m.py::f"]["cyclomatic"] == 13


def test_baseline_allows_recorded_offences_only() -> None:
    found = {"m.py::f": {"cyclomatic": 13}}
    assert gate._compare(found, {"m.py::f": {"cyclomatic": 13}}) == []
    assert "exceeds 10 (baseline 12)" in gate._compare(found, {"m.py::f": {"cyclomatic": 12}})[0]
    assert "(baseline None)" in gate._compare(found, {})[0]


def test_cleared_baseline_entries_must_be_removed() -> None:
    errors = gate._compare({}, {"m.py::f": {"cognitive": 20}})
    assert errors == ["m.py::f: cognitive is now within its ceiling; remove it from complexity-baseline.json"]


def test_main_on_a_tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "m.py").write_text(COMPLEX + "\n" * 500)
    baseline = tmp_path / "complexity-baseline.json"
    baseline.write_text(json.dumps({}))
    monkeypatch.setattr(gate, "ROOT", tmp_path)
    monkeypatch.setattr(gate, "BASELINE", baseline)
    assert gate.main() == 1
    out = capsys.readouterr().out
    assert "scripts/m.py: more than 500 lines" in out
    assert "scripts/m.py::f: cyclomatic 13" in out
    (tmp_path / "scripts" / "m.py").write_text("def g():\n    return 1\n")
    assert gate.main() == 0
