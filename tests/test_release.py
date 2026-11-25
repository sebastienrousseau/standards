# SPDX-FileCopyrightText: 2026 Sebastien Rousseau
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Release preflight and notes, with git and gh answered by a fake."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest
import release

GOOD = {
    "pyproject.toml": 'version = "0.0.3"\n',
    "CITATION.cff": "version: 0.0.3\n",
    "CHANGELOG.md": "## [0.0.3] - 2026-11-25\n",
    ".github/releases/v0.0.3.md": "# standards 0.0.3\n\n* **Safe push**: kept edits.\n",
}


def fake(answers: dict[str, str]) -> Callable[..., str]:
    """A `run` that answers by the longest matching command prefix."""

    def run(*argv: str) -> str:
        command = " ".join(argv)
        for prefix in sorted(answers, key=len, reverse=True):
            if command.startswith(prefix):
                answer = answers[prefix]
                if answer == "FAIL":
                    raise release.PreflightError(f"{command}: failed")
                return answer
        raise AssertionError(f"unexpected command: {command}")

    return run


def git_show(files: dict[str, str]) -> dict[str, str]:
    return {f"git show v0.0.3:{path}": text for path, text in files.items()}


@pytest.fixture
def tagged(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    answers = {
        "git cat-file -t v0.0.3": "tag\n",
        "git -c gpg.ssh.allowedSignersFile=": "Good signature\n",
        "git tag -l --format=%(contents:subject) v0.0.3": "standards v0.0.3\n",
        "git merge-base --is-ancestor": "",
        "git tag --list v* --sort=-v:refname": "v0.0.3\nv0.0.2\nv0.0.1\n",
        **git_show(GOOD),
    }
    monkeypatch.setattr(release, "run", fake(answers))
    return answers


def test_version_of() -> None:
    assert release.version_of("v0.0.3") == "0.0.3"
    with pytest.raises(release.PreflightError, match="v<major>"):
        release.version_of("0.0.3")


def test_preflight_passes(tagged: dict[str, str], capsys: pytest.CaptureFixture[str]) -> None:
    assert release.main(["preflight", "v0.0.3"]) == 0
    assert "v0.0.3 is ready to release" in capsys.readouterr().out


@pytest.mark.parametrize(
    "case",
    [
        ("git cat-file -t v0.0.3", "commit\n", "lightweight"),
        ("git -c gpg.ssh.allowedSignersFile=", "FAIL", "allowedSignersFile"),
        ("git tag -l --format=%(contents:subject) v0.0.3", "v0.0.3\n", "message is 'v0.0.3'"),
        ("git merge-base --is-ancestor", "FAIL", "is-ancestor"),
        ("git show v0.0.3:CITATION.cff", "version: 0.0.2\n", "CITATION.cff at v0.0.3"),
        ("git show v0.0.3:CHANGELOG.md", "## [0.0.3] - Unreleased\n", "CHANGELOG.md at v0.0.3"),
        ("git show v0.0.3:.github/releases/v0.0.3.md", "FAIL", ".github/releases/v0.0.3.md"),
    ],
)
def test_preflight_blocks(tagged, monkeypatch, capsys, case: tuple[str, str, str]) -> None:
    key, value, message = case
    monkeypatch.setattr(release, "run", fake({**tagged, key: value}))
    assert release.main(["preflight", "v0.0.3"]) == 1
    assert message in capsys.readouterr().err


def test_preflight_remote_counts(tagged, monkeypatch, capsys) -> None:
    remote = {"gh api repos/sebastienrousseau/standards/dependabot": "[]", "gh issue list": "[]"}
    monkeypatch.setattr(release, "run", fake({**tagged, **remote}))
    assert release.main(["preflight", "v0.0.3", "--remote"]) == 0
    monkeypatch.setattr(release, "run", fake({**tagged, **remote, "gh issue list": '[{"number": 7}]'}))
    assert release.main(["preflight", "v0.0.3", "--remote"]) == 1
    assert "0 open Dependabot alert(s) and 1 open issue(s)" in capsys.readouterr().err


def test_previous_tag(tagged: dict[str, str]) -> None:
    assert release.previous_tag("v0.0.3") == "v0.0.2"
    assert release.previous_tag("v0.0.1") is None
    assert release.previous_tag("v9.9.9") is None


def _pull(number: int, author: str = "sebastienrousseau") -> dict[str, object]:
    url = f"https://github.com/{release.REPO}/pull/{number}"
    return {"title": f"PR {number}", "user": {"login": author}, "html_url": url}


def test_changes_lists_pull_requests_then_bare_commits(monkeypatch: pytest.MonkeyPatch) -> None:
    api = f"gh api repos/{release.REPO}/commits"
    commit = {"author": None, "commit": {"message": "fix: direct\n\nbody"}, "html_url": "https://x/c3"}
    answers = {
        "git rev-list --reverse --first-parent v0.0.2..v0.0.3": "c1\nc2\nc3\n",
        f"{api}/c1/pulls": json.dumps([_pull(4)]),
        f"{api}/c2/pulls": json.dumps([_pull(4)]),
        f"{api}/c3/pulls": "[]",
        f"{api}/c3": json.dumps(commit),
    }
    monkeypatch.setattr(release, "run", fake(answers))
    assert release.changes("v0.0.3", "v0.0.2") == [
        {"title": "PR 4", "author": "sebastienrousseau", "url": f"https://github.com/{release.REPO}/pull/4"},
        {"title": "fix: direct", "author": "unknown", "url": "https://x/c3"},
    ]


def test_new_contributors(monkeypatch: pytest.MonkeyPatch) -> None:
    entries = [
        {"title": "a", "author": "old", "url": "https://x/pull/1"},
        {"title": "b", "author": "new", "url": "https://x/pull/2"},
        {"title": "c", "author": "direct", "url": "https://x/commit/3"},
    ]
    search = "gh api -X GET search/issues -f q=repo:sebastienrousseau/standards is:pr is:merged author:"
    answers = {
        f"{search}old": '{"total_count": 5}',
        f"{search}new": '{"total_count": 1}',
        f"{search}direct": '{"total_count": 0}',
    }
    monkeypatch.setattr(release, "run", fake(answers))
    assert release.new_contributors(entries) == [entries[1]]


def test_notes(tagged, monkeypatch, tmp_path: Path, capsys) -> None:
    entries = [{"title": "feat: v0.0.3", "author": "new", "url": "https://x/pull/5"}]
    monkeypatch.setattr(release, "changes", lambda *_: entries)
    monkeypatch.setattr(release, "new_contributors", lambda e: e)
    sums = tmp_path / "SHA256SUMS"
    sums.write_text("abc  standards_sync-0.0.3.tar.gz\n")
    assert release.main(["notes", "v0.0.3", "--sums", str(sums)]) == 0
    notes = capsys.readouterr().out
    assert notes.startswith("## Highlights ⭐️\n\n* **Safe push**: kept edits.\n\n## What's Changed\n\n")
    assert "* feat: v0.0.3 by @new in https://x/pull/5\n" in notes
    assert "## New Contributors\n\n* @new made their first contribution in https://x/pull/5\n" in notes
    assert "```text\nabc  standards_sync-0.0.3.tar.gz\n```" in notes
    assert notes.endswith(
        "**Full Changelog**: https://github.com/sebastienrousseau/standards/compare/v0.0.2...v0.0.3\n"
    )


def test_notes_for_a_first_release_without_newcomers(tagged) -> None:
    notes = release.compose("v0.0.1", "* **x**: y", [], [], "abc  f")
    assert "New Contributors" not in notes
    assert notes.endswith("**Full Changelog**: https://github.com/sebastienrousseau/standards/commits/v0.0.1\n")


def test_notes_refuse_an_em_dash(tagged) -> None:
    with pytest.raises(release.PreflightError, match="em dash"):
        release.compose("v0.0.3", "* **x**: a — b", [], [], "abc  f")


def test_run_raises_on_failure() -> None:
    assert release.run("git", "--version").startswith("git version")
    with pytest.raises(release.PreflightError, match="git no-such-command"):
        release.run("git", "no-such-command")


def test_the_owner_is_never_a_new_contributor(monkeypatch: pytest.MonkeyPatch) -> None:
    entries = [{"title": "feat: v0.0.2", "author": "sebastienrousseau", "url": "https://x/pull/1"}]
    search = "gh api -X GET search/issues"
    monkeypatch.setattr(release, "run", fake({search: '{"total_count": 1}'}))
    assert release.new_contributors(entries) == []
