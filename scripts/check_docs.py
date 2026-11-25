#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Sebastien Rousseau
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Checks that keep the standards and this repository's documents consistent.

With no argument it checks the repository: the README keeps the heading order
of README-TEMPLATE.md with no unresolved {{TOKEN}} (AGENTS.md section 7.3),
the GitHub PR template is the canonical PR-TEMPLATE.md, the version carriers
agree, and no document asks `gh` for a release `title` field, which it does
not have. With `--site DIR` it checks a built manual instead: every page
carries the author link of AGENTS.md section 7.1.2.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = "standards"
AUTHOR_LINK = '<a href="https://sebastienrousseau.com/" rel="author">Sebastien Rousseau</a>'
HEADING = re.compile(r"^## (.+?)\s*$", re.MULTILINE)
TOKEN = re.compile(r"\{\{[A-Z0-9_]+\}\}")
GH_TITLE_FIELD = re.compile(r"gh release view[^`\n]*--json[^`\n]*\btitle\b")


def _read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def readme_errors() -> list[str]:
    """The README's level-2 headings must be the template's, in order."""
    expected = [h.replace("{{PROJECT_NAME}}", PROJECT) for h in HEADING.findall(_read("README-TEMPLATE.md"))]
    readme = _read("README.md")
    actual = HEADING.findall(readme)
    errors = []
    if actual != expected:
        errors.append(f"README.md headings {actual} differ from README-TEMPLATE.md {expected}")
    errors += [f"README.md: unresolved template token {t}" for t in sorted(set(TOKEN.findall(readme)))]
    return errors


def template_errors() -> list[str]:
    """GitHub's PR template is a copy of the canonical one (make templates)."""
    if _read(".github/pull_request_template.md") != _read("PR-TEMPLATE.md"):
        return [".github/pull_request_template.md differs from PR-TEMPLATE.md; run make templates"]
    return []


def version_errors() -> list[str]:
    """pyproject.toml, CITATION.cff and the newest CHANGELOG section agree."""
    versions = {
        "pyproject.toml": re.search(r'(?m)^version = "([^"]+)"', _read("pyproject.toml")),
        "CITATION.cff": re.search(r"(?m)^version: (\S+)", _read("CITATION.cff")),
        "CHANGELOG.md": re.search(r"(?m)^## \[(\d[^\]]*)\]", _read("CHANGELOG.md")),
    }
    found = {name: m.group(1) if m else None for name, m in versions.items()}
    if len(set(found.values())) != 1:
        return [f"version carriers disagree: {found}"]
    return []


def gh_field_errors() -> list[str]:
    """`gh release view --json` has a `name` field for the title, not `title`."""
    errors = []
    for path in sorted(ROOT.glob("*.md")) + sorted((ROOT / "docs").rglob("*.md")):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if GH_TITLE_FIELD.search(line):
                errors.append(f"{path.relative_to(ROOT)}:{number}: gh has no `title` field; use `name`")
    return errors


def site_errors(site: Path) -> list[str]:
    """Every built page carries the author link."""
    pages = sorted(site.rglob("*.html"))
    if not pages:
        return [f"{site}: no pages built"]
    return [f"{p.relative_to(site)}: no author link" for p in pages if AUTHOR_LINK not in p.read_text(encoding="utf-8")]


def main(argv: list[str] | None = None) -> int:
    """Run the repository checks, or the site check with --site; print each failure."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--site", type=Path, help="check a built manual instead of the repository")
    args = parser.parse_args(argv)
    if args.site:
        errors = site_errors(args.site)
    else:
        errors = readme_errors() + template_errors() + version_errors() + gh_field_errors()
    for error in errors:
        print(error)
    if not errors:
        print("docs: consistent")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
