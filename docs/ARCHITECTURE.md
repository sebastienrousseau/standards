<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau -->
<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

# Architecture

`standards-sync` is one Python file, `scripts/sync.py`, with no
dependencies beyond the standard library and `git`. The dotfiles vendor it
byte for byte as `~/.local/bin/standards-sync`, so it stays a single file
([ADR 0002](adr/0002-one-canonical-source.md)).

## The files it manages

`STANDARD_FILES`: `AGENTS.md`, `GEMINI.md`, `PR-TEMPLATE.md`,
`README-TEMPLATE.md` and `REPO-STANDARD.md`. Nothing else is read or
written, apart from the git hooks that `--install-hooks` installs.

## Finding the source

`find_canonical_source` returns the first directory holding a readable
`AGENTS.md`, trying in order:

1. `$STANDARDS_REPO`.
2. The directories above the running script, each first as
   `<dir>/defaults/Code` (a dotfiles checkout) and then as `<dir>` (this
   repository).
3. `~/Code/Public/Other/standards`, `~/Code`, `~/.dotfiles/defaults/Code`
   and `~/.local/share/chezmoi/defaults/Code`.

## Finding the targets

`get_target_dirs` uses `$STANDARDS_TARGETS` when it is set (directories
separated by `:`). Otherwise the targets are `~/Code`,
`~/.dotfiles/defaults/Code`, `~/Code/Public/Shell/dotfiles/defaults/Code`
and `~/.local/share/chezmoi/defaults/Code`, keeping only those that exist
(`~/Code` is kept whenever the home directory exists, so a push can create
it). The source itself, and a second path to a directory already listed,
are dropped by comparing resolved paths.

## The three operations

**Check** (`--check`) compares SHA-256 digests. Each file is `[OK]`,
`[MISSING]` or `[DRIFTED]`, with the first lines of a unified diff for a
drifted one. It changes nothing and exits 1 on any drift. With `-q` it
prints one warning line, or nothing.

**Push** (`--push`, the default) copies each file to each target, with two
exceptions:

- A target that is a link to the source file is `[LINKED]` and left alone:
  it is always in sync, and copying a file onto itself fails.
- A target file whose content is neither the source's nor any version
  this repository has committed was edited in place. It is `[KEPT]`, and
  the push exits 1 ([ADR 0003](adr/0003-keep-edits-made-in-place.md)).
  `--pull` adopts the edit; `--push --force` overwrites it.

"Any version this repository has committed" is the set of git blob ids in
`git log --raw` for that file. `blob_of` computes a file's blob id the way
`git hash-object` does, and the fuzz suite checks the two agree.

**Pull** (`--pull`) copies the five files from `~/Code` into the source,
then pushes to every target except `~/Code`.

## Git hooks

`--install-hooks` writes `post-commit` and `post-merge` hooks into the
source checkout that run `standards-sync --push`, so a commit or a pull
here reaches the copies at once.

## How ~/Code links to this repository

The dotfiles (`install/migrate/link-standards.sh`) make each file in
`~/Code` a symbolic link into this clone when the clone exists. An edit in
`~/Code` is then an edit here, visible to `git status`, and push and pull
both leave the link alone.
