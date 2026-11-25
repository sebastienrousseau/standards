# SPDX-FileCopyrightText: 2026 Sebastien Rousseau
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Tests for scripts/check_lock.py: the dependency provenance policy."""

from __future__ import annotations

from pathlib import Path

import check_lock

HASH = "sha256:" + "a" * 64
GOOD = f"""version = 1

[[package]]
name = "ruff"
version = "1.0"
source = {{ registry = "https://pypi.org/simple" }}
sdist = {{ url = "https://files.pythonhosted.org/r.tar.gz", hash = "{HASH}", size = 1 }}
wheels = [
    {{ url = "https://files.pythonhosted.org/r.whl", hash = "{HASH}", size = 1 }},
]

[[package]]
name = "standards-sync"
version = "0.0.1"
source = {{ editable = "." }}
"""


def test_a_hashed_pypi_lock_passes() -> None:
    assert check_lock.lock_errors(GOOD) == []


def test_a_git_source_fails() -> None:
    lock = GOOD.replace('{ registry = "https://pypi.org/simple" }', '{ git = "https://example.com/r" }')
    error = 'uv.lock: ruff: source is not PyPI: source = { git = "https://example.com/r" }'
    assert check_lock.lock_errors(lock) == [error]


def test_a_package_with_no_source_fails() -> None:
    lock = GOOD.replace('source = { editable = "." }\n', "")
    assert check_lock.lock_errors(lock) == ["uv.lock: standards-sync: source is not PyPI: none"]


def test_an_unhashed_artifact_fails() -> None:
    lock = GOOD.replace(f'r.whl", hash = "{HASH}"', 'r.whl"')
    assert check_lock.lock_errors(lock) == ["uv.lock: ruff: no SHA-256 for https://files.pythonhosted.org/r.whl"]


def test_uv_calls_must_use_the_lock() -> None:
    text = "a:\n\tuv run --frozen x\n\tuv sync\n\t$(UV) run y\n\tuv run --locked z\n\tuv build\n"
    assert check_lock.unfrozen_calls(Path("Makefile"), text) == [
        "Makefile:3: uv call without --frozen or --locked: uv sync",
        "Makefile:4: uv call without --frozen or --locked: $(UV) run y",
    ]


def test_main_checks_the_repository(tmp_path: Path, capsys) -> None:
    assert check_lock.main() == 0
    (tmp_path / ".github" / "workflows").mkdir(parents=True)
    (tmp_path / "uv.lock").write_text(GOOD, encoding="utf-8")
    (tmp_path / "Makefile").write_text("x:\n\tuv sync\n", encoding="utf-8")
    (tmp_path / "GNUmakefile").write_text("", encoding="utf-8")
    (tmp_path / ".github" / "workflows" / "ci.yml").write_text("run: uv run --frozen pytest\n", encoding="utf-8")
    assert check_lock.main(tmp_path) == 1
    assert "Makefile:2" in capsys.readouterr().out
