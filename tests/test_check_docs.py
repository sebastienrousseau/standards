# SPDX-FileCopyrightText: 2026 Sebastien Rousseau
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""The documentation consistency checks, on a throwaway copy of the files."""

from __future__ import annotations

import shutil
from pathlib import Path

import check_docs
import pytest

FILES = ("README.md", "README-TEMPLATE.md", "PR-TEMPLATE.md", "pyproject.toml", "CITATION.cff", "CHANGELOG.md")


@pytest.fixture
def repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = Path(check_docs.__file__).resolve().parents[1]
    for name in FILES:
        shutil.copy(root / name, tmp_path / name)
    (tmp_path / ".github").mkdir()
    shutil.copy(root / ".github" / "pull_request_template.md", tmp_path / ".github")
    (tmp_path / "docs").mkdir()
    monkeypatch.setattr(check_docs, "ROOT", tmp_path)
    return tmp_path


def test_the_repository_is_consistent() -> None:
    assert check_docs.main([]) == 0


def test_readme_heading_order_and_tokens(repo: Path) -> None:
    readme = repo / "README.md"
    readme.write_text(readme.read_text().replace("## Install", "## Installing") + "\n{{LOGO_URL}}\n")
    errors = check_docs.readme_errors()
    assert "differ from README-TEMPLATE.md" in errors[0]
    assert errors[1] == "README.md: unresolved template token {{LOGO_URL}}"


def test_pr_template_copy(repo: Path) -> None:
    (repo / ".github" / "pull_request_template.md").write_text("stale\n")
    assert check_docs.template_errors() == [
        ".github/pull_request_template.md differs from PR-TEMPLATE.md; run make templates"
    ]


def test_version_carriers(repo: Path) -> None:
    citation = repo / "CITATION.cff"
    citation.write_text(citation.read_text().replace("version: ", "version: 9"))
    assert "version carriers disagree" in check_docs.version_errors()[0]


def test_gh_title_field(repo: Path) -> None:
    (repo / "docs" / "x.md").write_text(
        "ok `gh release view v1 --json name,body`\nbad `gh release view v1 --json title,body`\n"
    )
    assert check_docs.gh_field_errors() == ["docs/x.md:2: gh has no `title` field; use `name`"]


def test_site_author_link(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert check_docs.site_errors(tmp_path) == [f"{tmp_path}: no pages built"]
    (tmp_path / "a.html").write_text(check_docs.AUTHOR_LINK)
    (tmp_path / "b.html").write_text("no link")
    assert check_docs.main(["--site", str(tmp_path)]) == 1
    assert capsys.readouterr().out == "b.html: no author link\n"
