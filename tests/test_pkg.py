# SPDX-FileCopyrightText: 2026 Sebastien Rousseau
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Tests for scripts/pkg.py: the package tarball and the rendered recipes."""

from __future__ import annotations

import base64
import hashlib
import tarfile
from pathlib import Path

import pytest

import pkg

VERSION = pkg.project_version(pkg.ROOT / "pyproject.toml")


def stage(tmp_path: Path) -> Path:
    tree = tmp_path / "stage" / f"standards-sync-{VERSION}"
    (tree / "bin").mkdir(parents=True)
    (tree / "bin" / "standards-sync").write_text("#!/usr/bin/env python3\n", encoding="utf-8")
    (tree / "bin" / "standards-sync").chmod(0o700)
    licences = tree / "share" / "licenses" / "standards-sync"
    licences.mkdir(parents=True)
    (licences / "LICENSE-MIT").write_text("MIT\n", encoding="utf-8")
    return tmp_path / "stage"


def test_project_version_reads_pyproject(tmp_path: Path) -> None:
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('[project]\nname = "x"\nversion = "1.2.3"\n', encoding="utf-8")
    assert pkg.project_version(pyproject) == "1.2.3"
    pyproject.write_text("[project]\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="no version"):
        pkg.project_version(pyproject)


def test_tarball_is_reproducible_and_normalised(tmp_path: Path) -> None:
    tree = stage(tmp_path) / f"standards-sync-{VERSION}"
    first, second = tmp_path / "a.tar.gz", tmp_path / "b.tar.gz"
    pkg.write_tarball(tree, first, 86400)
    (tree / "bin" / "standards-sync").touch()
    pkg.write_tarball(tree, second, 86400)
    assert first.read_bytes() == second.read_bytes()
    with tarfile.open(first) as tar:
        members = {m.name: m for m in tar.getmembers()}
    script = members[f"standards-sync-{VERSION}/bin/standards-sync"]
    assert (script.mode, script.uid, script.uname, script.mtime) == (0o755, 0, "", 86400)
    assert members[f"standards-sync-{VERSION}/share/licenses/standards-sync/LICENSE-MIT"].mode == 0o644
    assert list(members) == sorted(members)


def test_render_fills_tokens_and_rejects_unknown_ones() -> None:
    assert pkg.render("v@VERSION@ @SHA256@", {"VERSION": "1", "SHA256": "ab"}) == "v1 ab"
    with pytest.raises(SystemExit, match="@NOPE@"):
        pkg.render("@VERSION@ @NOPE@", {"VERSION": "1"})


def test_main_renders_every_recipe_against_the_tarball(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "86400")
    out = tmp_path / "out"
    assert pkg.main(["--stage", str(stage(tmp_path)), "--out", str(out), "--url-base", "file:///srv"]) == 0
    tarball = out / f"standards-sync-{VERSION}-unix.tar.gz"
    digest = hashlib.sha256(tarball.read_bytes()).digest()
    brew = (out / "brew" / "standards-sync.rb").read_text(encoding="utf-8")
    assert f'url "file:///srv/{tarball.name}"' in brew
    assert f'sha256 "{digest.hex()}"' in brew
    nix = (out / "nix" / "package.nix").read_text(encoding="utf-8")
    assert f'hash = "sha256-{base64.b64encode(digest).decode()}"' in nix
    assert f'source=("{tarball.name}::file:///srv/{tarball.name}")' in (out / "aur" / "PKGBUILD").read_text()
    assert f"Version:        {VERSION}\n" in (out / "rpm" / "standards-sync.spec").read_text()
    assert str(tarball) in capsys.readouterr().out


def test_main_prepares_the_deb_root(tmp_path: Path) -> None:
    out = tmp_path / "out"
    pkg.main(["--stage", str(stage(tmp_path)), "--out", str(out)])
    root = out / "deb" / f"standards-sync_{VERSION}-1_all"
    assert f"Version: {VERSION}-1\n" in (root / "DEBIAN" / "control").read_text()
    assert (root / "usr" / "share" / "doc" / "standards-sync" / "copyright").is_file()
    assert (root / "usr" / "bin" / "standards-sync").is_file()
    assert not (root / "usr" / "share" / "licenses").exists()


def test_main_defaults_to_the_release_url(tmp_path: Path) -> None:
    out = tmp_path / "out"
    pkg.main(["--stage", str(stage(tmp_path)), "--out", str(out)])
    url = f"{pkg.RELEASES}/v{VERSION}/standards-sync-{VERSION}-unix.tar.gz"
    assert f'url "{url}"' in (out / "brew" / "standards-sync.rb").read_text()


def test_main_needs_the_staged_tree(tmp_path: Path) -> None:
    with pytest.raises(SystemExit, match="run make pkg"):
        pkg.main(["--stage", str(tmp_path), "--out", str(tmp_path / "out")])
