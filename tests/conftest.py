# SPDX-FileCopyrightText: 2026 Sebastien Rousseau
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Shared fixtures: an isolated home, a standards source and sync targets."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import sync

GIT = ["git", "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null"]


def write_standards(directory: Path, body: str = "v1") -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for name in sync.STANDARD_FILES:
        (directory / name).write_text(f"{name} {body}\n", encoding="utf-8")


def git_commit(repo: Path, message: str) -> None:
    subprocess.run([*GIT, "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(
        [*GIT, "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid", "commit", "-qm", message],
        check=True,
    )


@pytest.fixture
def home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A fresh HOME, with the standards environment variables cleared."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.delenv("STANDARDS_REPO", raising=False)
    monkeypatch.delenv("STANDARDS_TARGETS", raising=False)
    return fake_home


@pytest.fixture
def source(tmp_path: Path) -> Path:
    """A standards git repository with one commit of every standard file."""
    repo = tmp_path / "standards"
    write_standards(repo)
    subprocess.run([*GIT, "init", "-q", str(repo)], check=True)
    git_commit(repo, "v1")
    return repo
