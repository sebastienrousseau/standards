#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Sebastien Rousseau
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Generate the distribution packages' inputs from an installed tree.

`make pkg` installs standards-sync into build/pkg/stage/standards-sync-<v>
(the install contract of GNUmakefile, with the licences), then runs this:

- the tree becomes standards-sync-<v>-unix.tar.gz, byte-identical for the
  same SOURCE_DATE_EPOCH;
- every template in pkg/<format>/ is rendered into build/pkg/<format>/ with
  the version, the tarball's URL and its SHA-256 (hex and SRI);
- build/pkg/deb/ gets a package root that `dpkg-deb --build` turns into a
  .deb.

Every template token must resolve; an unknown @TOKEN@ is an error.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import os
import re
import shutil
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = "standards-sync"
RELEASES = "https://github.com/sebastienrousseau/standards/releases/download"
TOKEN = re.compile(r"@[A-Z0-9_]+@")


def project_version(pyproject: Path) -> str:
    """The version in pyproject.toml's [project] table."""
    match = re.search(r'(?m)^version = "([^"]+)"', pyproject.read_text(encoding="utf-8"))
    if not match:
        raise SystemExit(f"{pyproject}: no version")
    return match.group(1)


def _normalised(info: tarfile.TarInfo, mtime: int) -> tarfile.TarInfo:
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    info.mtime = mtime
    info.mode = 0o755 if info.isdir() or info.mode & 0o111 else 0o644
    return info


def write_tarball(tree: Path, out: Path, mtime: int) -> None:
    """Pack `tree` as out, with sorted entries, root ownership and one mtime."""
    paths = [tree, *sorted(tree.rglob("*"))]
    with (
        out.open("wb") as raw,
        gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as gz,
        tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tar,
    ):
        for path in paths:
            info = _normalised(tar.gettarinfo(str(path), path.relative_to(tree.parent).as_posix()), mtime)
            if info.isfile():
                with path.open("rb") as data:
                    tar.addfile(info, data)
            else:
                tar.addfile(info)


def render(text: str, values: dict[str, str]) -> str:
    """Replace each @KEY@ in text; fail on a token with no value."""
    for key, value in values.items():
        text = text.replace(f"@{key}@", value)
    left = sorted(set(TOKEN.findall(text)))
    if left:
        raise SystemExit(f"unresolved template tokens: {', '.join(left)}")
    return text


def render_templates(templates: Path, out: Path, values: dict[str, str]) -> list[Path]:
    """Render every file under templates/<format>/ into out/<format>/."""
    written = []
    for template in sorted(p for p in templates.rglob("*") if p.is_file()):
        target = out / template.relative_to(templates)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(render(template.read_text(encoding="utf-8"), values), encoding="utf-8")
        written.append(target)
    return written


def deb_root(tree: Path, out: Path, version: str) -> Path:
    """A dpkg-deb package root: the tree under /usr, control and copyright."""
    root = out / "deb" / f"{NAME}_{version}-1_all"
    shutil.rmtree(root, ignore_errors=True)
    shutil.copytree(tree, root / "usr")
    shutil.rmtree(root / "usr" / "share" / "licenses")
    (root / "DEBIAN").mkdir()
    shutil.move(str(out / "deb" / "control"), root / "DEBIAN" / "control")
    doc = root / "usr" / "share" / "doc" / NAME
    doc.mkdir(parents=True)
    shutil.move(str(out / "deb" / "copyright"), doc / "copyright")
    return root


def build_parser() -> argparse.ArgumentParser:
    """The command line: the staged tree, the output and the download URL."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--stage", type=Path, required=True, help="directory holding standards-sync-<version>/")
    parser.add_argument("--out", type=Path, required=True, help="where to write the tarball and the recipes")
    parser.add_argument("--templates", type=Path, default=ROOT / "pkg", help="the pkg/ template directory")
    parser.add_argument("--url-base", help=f"where the tarball is served (default: {RELEASES}/v<version>)")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Pack the staged tree, render the recipes and prepare the .deb root."""
    args = build_parser().parse_args(argv)
    version = project_version(ROOT / "pyproject.toml")
    tree = args.stage / f"{NAME}-{version}"
    if not tree.is_dir():
        raise SystemExit(f"{tree}: not found; run make pkg")
    tarball = args.out / f"{NAME}-{version}-unix.tar.gz"
    args.out.mkdir(parents=True, exist_ok=True)
    write_tarball(tree, tarball, int(os.environ.get("SOURCE_DATE_EPOCH", "0")))
    digest = hashlib.sha256(tarball.read_bytes()).digest()
    values = {
        "VERSION": version,
        "TARBALL": tarball.name,
        "URL": f"{args.url_base or f'{RELEASES}/v{version}'}/{tarball.name}",
        "SHA256": digest.hex(),
        "SRI": "sha256-" + base64.b64encode(digest).decode(),
    }
    for path in render_templates(args.templates, args.out, values):
        print(path)
    print(deb_root(tree, args.out, version))
    print(tarball)
    return 0


if __name__ == "__main__":
    sys.exit(main())
