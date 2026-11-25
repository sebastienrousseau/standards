#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Sebastien Rousseau
# SPDX-License-Identifier: Apache-2.0 OR MIT
"""Standards synchronization and integrity verification utility.

Maintains strict synchronization between the canonical standards repository,
the active workspace root (~/Code), and dotfiles (chezmoi distribution).
"""

from __future__ import annotations

import argparse
import difflib
import filecmp
import hashlib
import os
import shutil
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

STANDARD_FILES = (
    "AGENTS.md",
    "GEMINI.md",
    "PR-TEMPLATE.md",
    "README-TEMPLATE.md",
    "REPO-STANDARD.md",
)


def _holds_standards(directory: Path, readable: bool = True) -> bool:
    """Whether `directory` holds AGENTS.md (and, if `readable`, can read it)."""
    agents = directory / "AGENTS.md"
    try:
        if not (directory.is_dir() and agents.is_file()):
            return False
        if readable:
            with agents.open("rb") as f:
                f.read(1)
    except OSError:
        return False
    return True


def _source_candidates() -> Iterator[tuple[Path, bool]]:
    """Directories that may hold the standards, in order, with whether to test a read."""
    if "STANDARDS_REPO" in os.environ:
        yield Path(os.environ["STANDARDS_REPO"]), False
    # First check if invoked from within a dotfiles or standards git checkout
    for parent in Path(__file__).resolve().parents:
        yield parent / "defaults" / "Code", True
        yield parent, True
    home = Path.home()
    for candidate in (
        home / "Code" / "Public" / "Other" / "standards",
        home / "Code",
        home / ".dotfiles" / "defaults" / "Code",
        home / ".local" / "share" / "chezmoi" / "defaults" / "Code",
    ):
        yield candidate, True


def find_canonical_source() -> Path | None:
    """Locate the canonical source directory containing the standard files."""
    return next((c for c, readable in _source_candidates() if _holds_standards(c, readable)), None)


def _env_targets(value: str) -> list[tuple[str, Path]]:
    """Targets named in STANDARDS_TARGETS, separated by os.pathsep."""
    targets: list[tuple[str, Path]] = []
    for item in value.split(os.pathsep):
        if item.strip():
            p = Path(item.strip())
            targets.append((p.name or "Custom Target", p))
    return targets


def _resolved(path: Path) -> Path:
    """`path` resolved, or as given when it cannot be (a symlink loop)."""
    try:
        return path.resolve()
    except (OSError, RuntimeError):
        return path


def _is_target(path: Path) -> bool:
    """Whether `path` exists, or is a ~/Code that a push may create."""
    try:
        return path.exists() or (path.parent.exists() and path.name == "Code")
    except OSError:
        return False


def get_target_dirs(src_dir: Path) -> list[tuple[str, Path]]:
    """Return configured sync target directories with descriptive labels."""
    if "STANDARDS_TARGETS" in os.environ:
        return _env_targets(os.environ["STANDARDS_TARGETS"])

    home = Path.home()
    code_dir = home / "Code"
    all_targets: list[tuple[str, Path]] = [
        ("Workspace Root", code_dir),
        ("Chezmoi Dotfiles", home / ".dotfiles" / "defaults" / "Code"),
        ("Dotfiles Workspace", code_dir / "Public" / "Shell" / "dotfiles" / "defaults" / "Code"),
        ("Chezmoi Local Share", home / ".local" / "share" / "chezmoi" / "defaults" / "Code"),
    ]

    targets: list[tuple[str, Path]] = []
    seen: set[Path] = {_resolved(src_dir)}
    for label, p in all_targets:
        p_resolved = _resolved(p)
        if p_resolved in seen or not _is_target(p):
            continue
        seen.add(p_resolved)
        targets.append((label, p))
    return targets


def compute_hash(path: Path) -> str:
    """Compute SHA-256 digest of a file."""
    try:
        if not path.is_file():
            return ""
        h = hashlib.sha256()
        with path.open("rb") as f:
            while chunk := f.read(65536):
                h.update(chunk)
        return h.hexdigest()
    except (OSError, PermissionError):
        return ""


def _say(quiet: bool, *lines: str) -> None:
    """Print `lines` unless `quiet`."""
    if not quiet:
        print(*lines, sep="\n")


_STATE_LINE = {"missing": "  [MISSING] {}", "drifted": "  [DRIFTED] {}", "ok": "  [OK]      {}"}


def _file_state(src: Path, dst: Path) -> str:
    """Compare `dst` with `src`: "skip", "missing", "drifted" or "ok"."""
    try:
        src_hash = compute_hash(src) if src.is_file() else ""
        if src_hash and not dst.exists():
            return "missing"
    except OSError:
        return "skip"
    dst_hash = compute_hash(dst) if src_hash else ""
    if not dst_hash:
        return "skip"
    return "ok" if src_hash == dst_hash else "drifted"


def _print_diff(src: Path, dst: Path, fname: str, label: str) -> None:
    """Print the first lines of a unified diff from `src` to `dst`."""
    try:
        src_lines = src.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
        dst_lines = dst.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    except OSError:
        return
    diff = difflib.unified_diff(
        src_lines,
        dst_lines,
        fromfile=f"standards/{fname}",
        tofile=f"{label}/{fname}",
        n=2,
    )
    print("".join(list(diff)[:15]))


def check_target_file(src: Path, dst: Path, fname: str, label: str, quiet: bool) -> bool:
    """Check a single target file against source. Return True if drifted."""
    state = _file_state(src, dst)
    if state == "skip":
        return False
    _say(quiet, _STATE_LINE[state].format(fname))
    if state == "drifted" and not quiet:
        _print_diff(src, dst, fname, label)
    return state != "ok"


def _check_target(src_dir: Path, label: str, target_dir: Path, quiet: bool) -> int:
    """Check every standard file in one target; return its drift count."""
    _say(quiet, f"Target: {label} ({target_dir})")
    try:
        if not target_dir.exists():
            _say(quiet, f"  [MISSING] Target directory does not exist: {target_dir}\n")
            return 1
    except OSError:
        return 0
    drift = sum(check_target_file(src_dir / f, target_dir / f, f, label, quiet) for f in STANDARD_FILES)
    _say(quiet, "")
    return drift


def _report_drift(drift_count: int, quiet: bool) -> int:
    """Print the outcome of a check and return its exit status."""
    if drift_count == 0:
        _say(quiet, "All standards are synchronized.")
        return 0
    if quiet:
        print(f"\033[0;33m⚠️  [standards] Drift detected across ~/Code or dotfiles ({drift_count} discrepancy).\033[0m")
        print("   Run 'standards-sync' to auto-heal or 'standards-sync --check' to inspect diffs.")
    else:
        print(f"Synchronization check failed with {drift_count} drift(s).")
    return 1


def check_sync(src_dir: Path | None, targets: list[tuple[str, Path]], quiet: bool = False) -> int:
    """Verify all targets match source files byte-for-byte. Return 0 if in sync, 1 if drifted."""
    if src_dir is None:
        _say(quiet, "No standards source directory located.")
        return 0
    _say(
        quiet,
        f"Checking synchronization for {len(STANDARD_FILES)} standard files across {len(targets)} targets...\n",
    )
    drift_count = sum(_check_target(src_dir, label, target_dir, quiet) for label, target_dir in targets)
    return _report_drift(drift_count, quiet)


def published_blobs(src_dir: Path, fname: str) -> set[str]:
    """Every version of `fname` this repository has committed, as git blob ids."""
    git = shutil.which("git")
    if git is None:
        return set()
    # The argv is fixed apart from paths this script chose; no shell is involved.
    log = subprocess.run(  # noqa: S603
        [git, "-C", str(src_dir), "log", "--raw", "--no-abbrev", "--format=", "--", fname],
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    return {line.split()[3] for line in log.splitlines() if line.startswith(":")}


def blob_of(path: Path) -> str:
    """The git blob id of a file's current content, as `git hash-object` gives it."""
    data = path.read_bytes()
    return hashlib.sha1(b"blob %d\0" % len(data) + data, usedforsecurity=False).hexdigest()


def safe_to_overwrite(src_dir: Path, src: Path, dst: Path) -> bool:
    """Whether pushing `src` over `dst` loses nothing.

    It does not when `dst` is missing, already matches, or holds a version
    this repository once published. Any other content was edited in place
    (in ~/Code or a dotfiles copy) and is newer than the canonical source as
    far as anyone can tell: a push that overwrote it once replaced the
    workspace's AGENTS.md with an October copy. Such a file is kept.
    """
    if not dst.exists() or filecmp.cmp(src, dst, shallow=False):
        return True
    return blob_of(dst) in published_blobs(src_dir, src.name)


def is_same_file(a: Path, b: Path) -> bool:
    """Whether `a` and `b` are one file, as when a target links to the source.

    Copying a file onto itself fails (shutil.SameFileError), and there is
    nothing to copy: a linked target is always in sync.
    """
    try:
        return a.exists() and b.exists() and os.path.samefile(a, b)
    except OSError:
        return False


def push_file(src_dir: Path, fname: str, dst: Path, force: bool) -> bool:
    """Push one standard file to `dst`; return True when an edit was kept."""
    src = src_dir / fname
    try:
        if not src.is_file():
            return False
        if is_same_file(src, dst):
            print(f"  [LINKED]  {fname}")
            return False
        if not force and not safe_to_overwrite(src_dir, src, dst):
            print(
                f"  [KEPT] {fname}: edited here, not a published version; "
                "--pull to adopt it, --push --force to overwrite"
            )
            return True
        shutil.copy2(src, dst)
        print(f"  [COPIED] {fname}")
    except (OSError, PermissionError) as e:
        print(f"  [ERROR] {fname}: {e}")
    return False


def push_sync(src_dir: Path | None, targets: list[tuple[str, Path]], force: bool = False) -> int:
    """Propagate canonical repo files to all target destinations.

    A target file edited in place is kept and reported, unless `force`:
    adopt it with --pull, or overwrite it with --push --force. A target
    that links to the source is reported as linked and left alone.
    """
    if src_dir is None:
        print("Cannot push: no standards source directory located.")
        return 1
    kept = 0

    print(f"Synchronizing {len(STANDARD_FILES)} standard files to {len(targets)} targets...\n")
    for label, target_dir in targets:
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            print(f"Cannot update {label} ({target_dir}): {e}")
            continue

        print(f"Updating: {label} ({target_dir})")
        for fname in STANDARD_FILES:
            kept += push_file(src_dir, fname, target_dir / fname, force)
        print()
    if kept:
        print(f"Push synchronization kept {kept} file(s) edited in place; nothing of them was overwritten.")
        return 1
    print("Push synchronization complete.")
    return 0


def pull_sync(src_dir: Path | None) -> int:
    """Pull edited files from workspace root (~/Code) into canonical repo."""
    if src_dir is None:
        print("Cannot pull: no standards destination directory located.")
        return 1

    code_dir = Path.home() / "Code"
    if not code_dir.exists():
        print(f"Workspace root not found: {code_dir}")
        return 1

    print(f"Pulling standards from workspace root ({code_dir}) into repo...\n")
    for fname in STANDARD_FILES:
        src = code_dir / fname
        dst = src_dir / fname
        try:
            if not src.is_file():
                continue
            if is_same_file(src, dst):
                print(f"  [LINKED]  {fname}")
                continue
            shutil.copy2(src, dst)
            print(f"  [PULLED] {fname}")
        except (OSError, PermissionError) as e:
            print(f"  [ERROR] {fname}: {e}")
    print("\nPull complete. Running push to update dotfiles mirrors...")
    targets = [t for t in get_target_dirs(src_dir) if t[0] != "Workspace Root"]
    return push_sync(src_dir, targets)


def install_hooks(src_dir: Path | None) -> int:
    """Install git post-commit and post-merge hooks to auto-sync on commit/pull."""
    if src_dir is None:
        print("Cannot install hooks: no standards directory located.")
        return 1

    hooks_dir = src_dir / ".git" / "hooks"
    if not hooks_dir.exists():
        print(f"Git hooks directory not found at {hooks_dir}")
        return 1

    hook_content = "#!/bin/sh\n# Auto-sync standards to workspace root and dotfiles\nstandards-sync --push\n"

    for hook_name in ("post-commit", "post-merge"):
        hook_path = hooks_dir / hook_name
        try:
            hook_path.write_text(hook_content, encoding="utf-8")
            hook_path.chmod(0o755)
            print(f"Installed hook: {hook_path}")
        except (OSError, PermissionError) as e:
            print(f"Cannot install hook {hook_name}: {e}")
            return 1

    return 0


EPILOG = """\
environment:
  STANDARDS_REPO     the canonical source directory, tried first
  STANDARDS_TARGETS  target directories separated by the path separator (:),
                     replacing the default ~/Code and dotfiles targets

exit status:
  0  in sync (or, for --check, no source found), or every file pushed or pulled
  1  drift found, a file edited in place was kept, or a push, pull or hook
     install could not run
"""


def build_parser() -> argparse.ArgumentParser:
    """The command-line interface; also the source of the manpage and completions."""
    parser = argparse.ArgumentParser(
        prog="standards-sync",
        description=__doc__,
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--check", action="store_true", help="Check for drift without modifying files")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode: suppress output unless drift detected")
    parser.add_argument("--push", action="store_true", help="Push canonical repo standards to all targets")
    parser.add_argument("--force", action="store_true", help="With --push, also overwrite files edited in place")
    parser.add_argument("--pull", action="store_true", help="Pull standards from workspace root into repo")
    parser.add_argument("--install-hooks", action="store_true", help="Install git post-commit and post-merge hooks")
    return parser


def main() -> int:
    """Run the command named on the command line; push when none is."""
    args = build_parser().parse_args()

    src_dir = find_canonical_source()
    targets = get_target_dirs(src_dir) if src_dir else []

    if args.install_hooks:
        return install_hooks(src_dir)
    if args.pull:
        return pull_sync(src_dir)
    if args.check:
        return check_sync(src_dir, targets, quiet=args.quiet)

    return push_sync(src_dir, targets, force=args.force)


if __name__ == "__main__":
    sys.exit(main())
