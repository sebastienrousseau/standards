# SPDX-FileCopyrightText: 2026 Sebastien Rousseau
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Behaviour of scripts/sync.py: discovery, drift checks, push, pull, hooks."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
import sync
from conftest import git_commit, write_standards

# --- discovery ----------------------------------------------------------------


def test_source_from_environment(home: Path, source: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STANDARDS_REPO", str(source))
    assert sync.find_canonical_source() == source


def test_invalid_environment_source_falls_back_to_checkout(home: Path, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("STANDARDS_REPO", str(tmp_path / "missing"))
    assert sync.find_canonical_source() == Path(sync.__file__).resolve().parents[1]


def test_source_from_home_candidates(home: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    detached = tmp_path / "detached" / "bin" / "standards-sync"
    detached.parent.mkdir(parents=True)
    monkeypatch.setattr(sync, "__file__", str(detached))
    assert sync.find_canonical_source() is None
    write_standards(home / "Code")
    assert sync.find_canonical_source() == home / "Code"


def test_source_from_dotfiles_checkout(home: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    dotfiles = tmp_path / "dotfiles"
    write_standards(dotfiles / "defaults" / "Code")
    script = dotfiles / "bin" / "standards-sync"
    script.parent.mkdir(parents=True)
    monkeypatch.setattr(sync, "__file__", str(script))
    assert sync.find_canonical_source() == dotfiles / "defaults" / "Code"


def test_targets_from_environment(home: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    a, b = tmp_path / "a", tmp_path / "b"
    monkeypatch.setenv("STANDARDS_TARGETS", f"{a}{os.pathsep} {os.pathsep}{b}")
    assert sync.get_target_dirs(tmp_path) == [("a", a), ("b", b)]


def test_default_targets_are_existing_dirs_and_workspace(home: Path, source: Path) -> None:
    (home / ".dotfiles" / "defaults" / "Code").mkdir(parents=True)
    assert sync.get_target_dirs(source) == [
        ("Workspace Root", home / "Code"),
        ("Chezmoi Dotfiles", home / ".dotfiles" / "defaults" / "Code"),
    ]


def test_default_targets_skip_the_source_itself(home: Path) -> None:
    code = home / "Code"
    write_standards(code)
    assert sync.get_target_dirs(code) == []


# --- drift checks -------------------------------------------------------------


def test_compute_hash(tmp_path: Path) -> None:
    f = tmp_path / "f"
    assert sync.compute_hash(f) == ""
    f.write_bytes(b"abc")
    assert sync.compute_hash(f) == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_check_target_file_states(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    src, dst = tmp_path / "src", tmp_path / "dst"
    assert sync.check_target_file(src, dst, "F", "T", quiet=False) is False
    src.write_text("one\n")
    assert sync.check_target_file(src, dst, "F", "T", quiet=False) is True
    dst.write_text("one\n")
    assert sync.check_target_file(src, dst, "F", "T", quiet=False) is False
    out = capsys.readouterr().out
    assert "[MISSING] F" in out
    assert "[OK]      F" in out


def test_check_target_file_prints_a_diff(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    src, dst = tmp_path / "src", tmp_path / "dst"
    src.write_text("one\n")
    dst.write_text("two\n")
    assert sync.check_target_file(src, dst, "F", "T", quiet=False) is True
    out = capsys.readouterr().out
    assert "[DRIFTED] F" in out
    assert "+++ T/F" in out
    assert "-one" in out
    assert "+two" in out


def test_check_target_file_quiet(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    src, dst = tmp_path / "src", tmp_path / "dst"
    src.write_text("one\n")
    dst.write_text("two\n")
    assert sync.check_target_file(src, dst, "F", "T", quiet=True) is True
    assert capsys.readouterr().out == ""


def test_check_sync_without_source(capsys: pytest.CaptureFixture[str]) -> None:
    assert sync.check_sync(None, []) == 0
    assert "No standards source" in capsys.readouterr().out


def test_check_sync_in_sync(source: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = tmp_path / "t"
    write_standards(target)
    assert sync.check_sync(source, [("T", target)]) == 0
    assert "All standards are synchronized." in capsys.readouterr().out


def test_check_sync_reports_drift(source: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    target = tmp_path / "t"
    write_standards(target, body="v2")
    missing = tmp_path / "missing"
    assert sync.check_sync(source, [("T", target), ("M", missing)]) == 1
    out = capsys.readouterr().out
    assert f"Target directory does not exist: {missing}" in out
    assert f"failed with {len(sync.STANDARD_FILES) + 1} drift(s)" in out


def test_check_sync_quiet_drift_warns_once(source: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert sync.check_sync(source, [("M", tmp_path / "missing")], quiet=True) == 1
    out = capsys.readouterr().out
    assert "Drift detected" in out
    assert "(1 discrepancy)" in out
    assert "Checking" not in out


def test_check_sync_quiet_in_sync_prints_nothing(source: Path, tmp_path: Path, capsys) -> None:
    target = tmp_path / "t"
    write_standards(target)
    assert sync.check_sync(source, [("T", target)], quiet=True) == 0
    assert capsys.readouterr().out == ""


# --- push ---------------------------------------------------------------------


def test_push_without_source(capsys: pytest.CaptureFixture[str]) -> None:
    assert sync.push_sync(None, []) == 1
    assert "Cannot push" in capsys.readouterr().out


def test_push_copies_into_missing_target(source: Path, tmp_path: Path) -> None:
    target = tmp_path / "new" / "Code"
    assert sync.push_sync(source, [("T", target)]) == 0
    for name in sync.STANDARD_FILES:
        assert (target / name).read_text() == (source / name).read_text()


def test_push_overwrites_a_published_version(source: Path, tmp_path: Path) -> None:
    target = tmp_path / "t"
    write_standards(target)
    write_standards(source, body="v2")
    git_commit(source, "v2")
    assert sync.push_sync(source, [("T", target)]) == 0
    assert (target / "AGENTS.md").read_text() == "AGENTS.md v2\n"


def test_push_keeps_an_edit_made_in_place(source: Path, tmp_path: Path, capsys) -> None:
    target = tmp_path / "t"
    write_standards(target)
    (target / "AGENTS.md").write_text("edited in place\n")
    assert sync.push_sync(source, [("T", target)]) == 1
    assert (target / "AGENTS.md").read_text() == "edited in place\n"
    out = capsys.readouterr().out
    assert "[KEPT] AGENTS.md" in out
    assert "kept 1 file(s)" in out


def test_push_force_overwrites_an_edit(source: Path, tmp_path: Path) -> None:
    target = tmp_path / "t"
    write_standards(target)
    (target / "AGENTS.md").write_text("edited in place\n")
    assert sync.push_sync(source, [("T", target)], force=True) == 0
    assert (target / "AGENTS.md").read_text() == "AGENTS.md v1\n"


def test_push_leaves_linked_targets_alone(source: Path, tmp_path: Path, capsys) -> None:
    target = tmp_path / "t"
    target.mkdir()
    for name in sync.STANDARD_FILES:
        (target / name).symlink_to(source / name)
    assert sync.push_sync(source, [("T", target)]) == 0
    assert capsys.readouterr().out.count("[LINKED]") == len(sync.STANDARD_FILES)


def test_push_reports_an_unwritable_target(source: Path, tmp_path: Path, capsys) -> None:
    blocker = tmp_path / "file"
    blocker.write_text("not a directory")
    assert sync.push_sync(source, [("T", blocker / "Code")]) == 0
    assert "Cannot update T" in capsys.readouterr().out


def test_push_reports_a_failed_copy(source: Path, tmp_path: Path, capsys) -> None:
    target = tmp_path / "t"
    target.mkdir()
    target.chmod(0o500)
    try:
        sync.push_sync(source, [("T", target)], force=True)
    finally:
        target.chmod(0o700)
    assert "[ERROR] AGENTS.md" in capsys.readouterr().out


def test_push_skips_files_missing_from_source(source: Path, tmp_path: Path) -> None:
    (source / "GEMINI.md").unlink()
    target = tmp_path / "t"
    assert sync.push_sync(source, [("T", target)]) == 0
    assert not (target / "GEMINI.md").exists()


def test_blob_of_matches_git(source: Path) -> None:
    blob = sync.blob_of(source / "AGENTS.md")
    assert blob in sync.published_blobs(source, "AGENTS.md")
    assert len(blob) == 40


# --- pull ---------------------------------------------------------------------


def test_pull_without_source(capsys: pytest.CaptureFixture[str]) -> None:
    assert sync.pull_sync(None) == 1
    assert "Cannot pull" in capsys.readouterr().out


def test_pull_without_workspace(home: Path, source: Path, capsys) -> None:
    assert sync.pull_sync(source) == 1
    assert "Workspace root not found" in capsys.readouterr().out


def test_pull_adopts_workspace_edits_then_pushes(home: Path, source: Path, tmp_path, monkeypatch) -> None:
    write_standards(home / "Code", body="edited")
    (home / "Code" / "GEMINI.md").unlink()
    mirror = tmp_path / "mirror"
    monkeypatch.setenv("STANDARDS_TARGETS", str(mirror))
    assert sync.pull_sync(source) == 0
    assert (source / "AGENTS.md").read_text() == "AGENTS.md edited\n"
    assert (source / "GEMINI.md").read_text() == "GEMINI.md v1\n"
    assert (mirror / "AGENTS.md").read_text() == "AGENTS.md edited\n"


def test_pull_leaves_linked_files_alone(home: Path, source: Path, monkeypatch, capsys) -> None:
    code = home / "Code"
    code.mkdir()
    for name in sync.STANDARD_FILES:
        (code / name).symlink_to(source / name)
    monkeypatch.setenv("STANDARDS_TARGETS", "")
    assert sync.pull_sync(source) == 0
    assert capsys.readouterr().out.count("[LINKED]") == len(sync.STANDARD_FILES)


def test_pull_reports_a_failed_copy(home: Path, source: Path, monkeypatch, capsys) -> None:
    write_standards(home / "Code", body="edited")
    (source / "AGENTS.md").chmod(0o400)
    monkeypatch.setenv("STANDARDS_TARGETS", "")
    try:
        sync.pull_sync(source)
    finally:
        (source / "AGENTS.md").chmod(0o600)
    assert "[ERROR] AGENTS.md" in capsys.readouterr().out


# --- hooks and command line ---------------------------------------------------


def test_install_hooks(source: Path) -> None:
    assert sync.install_hooks(source) == 0
    for name in ("post-commit", "post-merge"):
        hook = source / ".git" / "hooks" / name
        assert hook.read_text().endswith("standards-sync --push\n")
        assert os.access(hook, os.X_OK)


def test_install_hooks_needs_a_git_checkout(tmp_path: Path, capsys) -> None:
    assert sync.install_hooks(None) == 1
    assert sync.install_hooks(tmp_path) == 1
    assert "Git hooks directory not found" in capsys.readouterr().out


def test_install_hooks_reports_a_failed_write(source: Path, capsys) -> None:
    (source / ".git" / "hooks" / "post-commit").mkdir(parents=True)
    assert sync.install_hooks(source) == 1
    assert "Cannot install hook post-commit" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("argv", "called"),
    [
        (["--install-hooks"], "install_hooks"),
        (["--pull"], "pull_sync"),
        (["--check"], "check_sync"),
        (["--push"], "push_sync"),
        ([], "push_sync"),
    ],
)
def test_main_dispatch(argv: list[str], called: str, source: Path, home: Path, monkeypatch) -> None:
    monkeypatch.setenv("STANDARDS_REPO", str(source))
    seen: list[str] = []
    monkeypatch.setattr(sync, called, lambda *a, **k: seen.append(called) or 7)
    monkeypatch.setattr(sys, "argv", ["standards-sync", *argv])
    assert sync.main() == 7
    assert seen == [called]


def test_main_check_end_to_end(source: Path, home: Path, tmp_path: Path, monkeypatch, capsys) -> None:
    target = tmp_path / "t"
    write_standards(target)
    monkeypatch.setenv("STANDARDS_REPO", str(source))
    monkeypatch.setenv("STANDARDS_TARGETS", str(target))
    monkeypatch.setattr(sys, "argv", ["standards-sync", "--check"])
    assert sync.main() == 0
    assert "All standards are synchronized." in capsys.readouterr().out


# --- unreadable paths are skipped, never fatal --------------------------------


def _raise(*_args: object, **_kwargs: object) -> None:
    raise OSError("unreadable")


def test_unreadable_candidates_are_skipped(home: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(Path, "is_dir", _raise)
    assert sync.find_canonical_source() is None


def test_unresolvable_and_unreadable_targets(home: Path, tmp_path: Path, monkeypatch) -> None:
    def loop(_self: Path, *_args: object, **_kwargs: object) -> Path:
        raise RuntimeError("symlink loop")

    monkeypatch.setattr(Path, "resolve", loop)
    monkeypatch.setattr(Path, "exists", _raise)
    assert sync.get_target_dirs(tmp_path) == []


def test_unreadable_files_are_skipped(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    src, dst = tmp_path / "src", tmp_path / "dst"
    src.write_text("one\n")
    dst.write_text("two\n")
    sync._print_diff(src / "missing", dst, "F", "T")
    monkeypatch.setattr(Path, "open", _raise)
    assert sync.compute_hash(src) == ""
    monkeypatch.setattr(Path, "exists", _raise)
    assert sync.check_target_file(src, dst, "F", "T", quiet=False) is False
    assert sync.check_sync(tmp_path, [("T", tmp_path)]) == 0


def test_without_git_nothing_counts_as_published(source: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sync.shutil, "which", lambda _name: None)
    assert sync.published_blobs(source, "AGENTS.md") == set()


def test_same_file_check_tolerates_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "a").write_text("a")
    monkeypatch.setattr(sync.os.path, "samefile", _raise)
    assert sync.is_same_file(tmp_path / "a", tmp_path / "a") is False


# --- the command-line contract (docs/POLICIES.md, stability) ------------------


def test_cli_options_are_stable() -> None:
    options = {o for a in sync.build_parser()._actions for o in a.option_strings}
    assert options == {"-h", "--help", "--check", "-q", "--quiet", "--push", "--force", "--pull", "--install-hooks"}


def test_check_without_source_exits_zero(home: Path, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(sync, "__file__", str(tmp_path / "bin" / "standards-sync"))
    monkeypatch.setattr(sys, "argv", ["standards-sync", "--check"])
    assert sync.main() == 0
    monkeypatch.setattr(sys, "argv", ["standards-sync", "--push"])
    assert sync.main() == 1
