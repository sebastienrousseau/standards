# SPDX-FileCopyrightText: 2026 Sebastien Rousseau
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""The API breakage check, against a throwaway repository with release tags."""

from __future__ import annotations

import subprocess
from pathlib import Path

import check_api
import pytest
from conftest import GIT, git_commit


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "repo"
    (root / "scripts").mkdir(parents=True)
    (root / "README.md").write_text("x\n")
    subprocess.run([*GIT, "init", "-q", str(root)], check=True)
    git_commit(root, "no sync.py yet")
    subprocess.run([*GIT, "-C", str(root), "update-ref", "refs/tags/v0.0.1", "HEAD"], check=True)
    monkeypatch.setattr(check_api, "ROOT", root)
    return root


def _release(root: Path, tag: str, source: str) -> None:
    (root / "scripts" / "sync.py").write_text(source)
    git_commit(root, tag)
    subprocess.run([*GIT, "-C", str(root), "update-ref", f"refs/tags/{tag}", "HEAD"], check=True)


def test_no_release_with_sync_py(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert check_api.baseline_tag() is None
    assert check_api.main() == 0
    assert "nothing to compare" in capsys.readouterr().out


def test_unchanged_and_broken_api(repo: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _release(repo, "v0.0.2", "def keep(a):\n    return a\n\n\ndef gone():\n    return 1\n")
    assert check_api.baseline_tag() == "v0.0.2"
    assert check_api.main() == 0
    assert "no breaking change since v0.0.2" in capsys.readouterr().out
    (repo / "scripts" / "sync.py").write_text("def keep(a, b):\n    return a\n")
    assert check_api.main() == 1
    out = capsys.readouterr().out
    assert "gone" in out
    assert "keep" in out
