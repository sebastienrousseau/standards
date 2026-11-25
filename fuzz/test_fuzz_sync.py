# SPDX-FileCopyrightText: 2026 Sebastien Rousseau
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Property-based fuzzing of the parts of sync.py that take outside input.

STANDARDS_TARGETS is parsed from the environment, and blob_of decides
whether a file in the workspace may be overwritten, so it is checked
against git itself. The @example cases are the regression corpus: inputs
that once mattered, replayed on every run.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import sync

GIT = shutil.which("git")
PATH_TEXT = st.text(st.characters(blacklist_categories=("Cs",), blacklist_characters="\x00"), max_size=40)


@given(st.lists(PATH_TEXT, max_size=6).map(os.pathsep.join))
@example("")
@example(os.pathsep)
@example(f" {os.pathsep} ")
@example("/")
@example(f"/  /{os.pathsep} ./ /{os.pathsep}")  # Atheris, PR #12: normalises to Path(" ")
@settings(max_examples=300, deadline=None)
def test_env_targets_never_yield_blank_entries(value: str) -> None:
    targets = sync._env_targets(value)
    assert len(targets) <= value.count(os.pathsep) + 1
    for label, path in targets:
        assert label
        assert str(path).strip()


@pytest.mark.skipif(GIT is None, reason="git is not installed")
@given(st.binary(max_size=4096))
@example(b"")
@example(b"\x00")
@example(b"line\r\n")
@settings(max_examples=60, deadline=None)
def test_blob_of_agrees_with_git(tmp_path_factory: pytest.TempPathFactory, data: bytes) -> None:
    path = tmp_path_factory.mktemp("blob") / "f"
    path.write_bytes(data)
    expected = subprocess.run(
        [GIT, "hash-object", "--no-filters", str(path)], capture_output=True, text=True, check=True
    ).stdout.strip()
    assert sync.blob_of(path) == expected
