#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Sebastien Rousseau
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Release preflight and release notes, as AGENTS.md section 3 requires.

`preflight TAG` blocks a release unless the tag is annotated, signed by a key
in KEYS.asc, says `standards vX.Y.Z` on its first line, points at a commit on
main, and every version carrier names that version. With `--remote` it also
requires zero open Dependabot alerts and zero open issues, through `gh`; run
it so before pushing the tag.

`notes TAG --sums FILE` prints the release notes: the hand-written Highlights
from .github/releases/TAG.md, then What's Changed, New Contributors, Checksums
and the Full Changelog link.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = "standards"
REPO = "sebastienrousseau/standards"
TAG = re.compile(r"^v(\d+\.\d+\.\d+)$")


class PreflightError(Exception):
    """A release-blocking failure."""


def run(*argv: str) -> str:
    """Run a fixed git or gh command in ROOT; return stdout, or raise on failure."""
    exe = shutil.which(argv[0]) or argv[0]
    # The argv is built from fixed words and the tag, which TAG has validated.
    result = subprocess.run([exe, *argv[1:]], cwd=ROOT, capture_output=True, text=True, check=False)  # noqa: S603
    if result.returncode != 0:
        raise PreflightError(f"{' '.join(argv)}: {result.stderr.strip() or result.stdout.strip()}")
    return result.stdout


def version_of(tag: str) -> str:
    match = TAG.match(tag)
    if not match:
        raise PreflightError(f"{tag}: a release tag is v<major>.<minor>.<patch>")
    return match.group(1)


def check_tag(tag: str) -> None:
    """Annotated, signed by KEYS.asc, message `standards vX.Y.Z`, on main."""
    if run("git", "cat-file", "-t", tag).strip() != "tag":
        raise PreflightError(f"{tag} is a lightweight tag; release tags are annotated")
    run("git", "-c", f"gpg.ssh.allowedSignersFile={ROOT / 'KEYS.asc'}", "tag", "-v", tag)
    subject = run("git", "tag", "-l", "--format=%(contents:subject)", tag).strip()
    if subject != f"{PROJECT} {tag}":
        raise PreflightError(f"{tag} message is {subject!r}; it must be {PROJECT + ' ' + tag!r}")
    run("git", "merge-base", "--is-ancestor", f"{tag}^{{commit}}", "origin/main")


def check_versions(tag: str) -> None:
    """Every version carrier at the tag names the tag's version."""
    version = version_of(tag)
    carriers = {
        "pyproject.toml": rf'(?m)^version = "{re.escape(version)}"$',
        "CITATION.cff": rf"(?m)^version: {re.escape(version)}$",
        "CHANGELOG.md": rf"(?m)^## \[{re.escape(version)}\] - \d{{4}}-\d{{2}}-\d{{2}}$",
        f".github/releases/{tag}.md": r"(?m)^\* \*\*",
    }
    for path, pattern in carriers.items():
        text = run("git", "show", f"{tag}:{path}")
        if not re.search(pattern, text):
            raise PreflightError(f"{path} at {tag} does not match {pattern}")


def check_remote() -> None:
    """Zero open Dependabot alerts and zero open issues (AGENTS.md section 0)."""
    alerts = json.loads(run("gh", "api", f"repos/{REPO}/dependabot/alerts?state=open&per_page=100"))
    issues = json.loads(run("gh", "issue", "list", "--repo", REPO, "--state", "open", "--json", "number"))
    if alerts or issues:
        raise PreflightError(f"{len(alerts)} open Dependabot alert(s) and {len(issues)} open issue(s)")


def previous_tag(tag: str) -> str | None:
    """The release tag before `tag`, if any."""
    tags = run("git", "tag", "--list", "v*", "--sort=-v:refname").split()
    older = tags[tags.index(tag) + 1 :] if tag in tags else []
    return older[0] if older else None


def changes(tag: str, prev: str | None) -> list[dict[str, str]]:
    """Each pull request (or, without one, commit) in the range, oldest first."""
    span = f"{prev}..{tag}" if prev else tag
    seen: dict[str, dict[str, str]] = {}
    for sha in run("git", "rev-list", "--reverse", "--first-parent", span).split():
        pulls = json.loads(run("gh", "api", f"repos/{REPO}/commits/{sha}/pulls"))
        if pulls:
            pr = pulls[0]
            seen.setdefault(
                pr["html_url"], {"title": pr["title"], "author": pr["user"]["login"], "url": pr["html_url"]}
            )
        else:
            commit = json.loads(run("gh", "api", f"repos/{REPO}/commits/{sha}"))
            author = (commit.get("author") or {}).get("login", "unknown")
            subject = commit["commit"]["message"].splitlines()[0]
            seen[sha] = {"title": subject, "author": author, "url": commit["html_url"]}
    return list(seen.values())


def new_contributors(entries: list[dict[str, str]]) -> list[dict[str, str]]:
    """Entries whose author, not the owner, has no merged pull request outside this release."""
    first: list[dict[str, str]] = []
    owner = REPO.split("/", maxsplit=1)[0]
    for author in dict.fromkeys(e["author"] for e in entries if e["author"] != owner):
        query = f"repo:{REPO} is:pr is:merged author:{author}"
        total = json.loads(run("gh", "api", "-X", "GET", "search/issues", "-f", f"q={query}"))["total_count"]
        mine = [e for e in entries if e["author"] == author and "/pull/" in e["url"]]
        if mine and total <= len(mine):
            first.append(mine[0])
    return first


def compose(
    tag: str, highlights: str, entries: list[dict[str, str]], newcomers: list[dict[str, str]], sums: str
) -> str:
    """The release notes, in the section order of AGENTS.md section 3."""
    prev = previous_tag(tag)
    lines = ["## Highlights ⭐️", "", highlights.strip(), "", "## What's Changed", ""]
    lines += [f"* {e['title']} by @{e['author']} in {e['url']}" for e in entries]
    if newcomers:
        lines += ["", "## New Contributors", ""]
        lines += [f"* @{e['author']} made their first contribution in {e['url']}" for e in newcomers]
    lines += ["", "## Checksums", "", "SHA-256 of every asset attached to this release:", "", "```text", sums.strip()]
    full = f"compare/{prev}...{tag}" if prev else f"commits/{tag}"
    lines += ["```", "", f"**Full Changelog**: https://github.com/{REPO}/{full}", ""]
    notes = "\n".join(lines)
    if "—" in notes:
        raise PreflightError("release notes contain an em dash")
    return notes


def main(argv: list[str] | None = None) -> int:
    """Run preflight or print the notes; report a blocking failure on stderr."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    pre = sub.add_parser("preflight")
    pre.add_argument("tag")
    pre.add_argument("--remote", action="store_true", help="also require zero open alerts and issues")
    notes = sub.add_parser("notes")
    notes.add_argument("tag")
    notes.add_argument("--sums", type=Path, required=True, help="the SHA256SUMS file")
    args = parser.parse_args(argv)
    try:
        if args.command == "preflight":
            check_tag(args.tag)
            check_versions(args.tag)
            if args.remote:
                check_remote()
            print(f"preflight: {args.tag} is ready to release")
        else:
            entries = changes(args.tag, previous_tag(args.tag))
            highlights = run("git", "show", f"{args.tag}:.github/releases/{args.tag}.md")
            body = "\n".join(line for line in highlights.splitlines() if line.startswith("* "))
            sums = args.sums.read_text(encoding="utf-8")
            print(compose(args.tag, body, entries, new_contributors(entries), sums), end="")
    except PreflightError as error:
        print(f"release: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
