<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau -->
<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

# Changelog

All notable changes to Standards are recorded here.

## Unreleased

## 0.0.3 - Unreleased

### Changed

- `AGENTS.md`, `GEMINI.md`, `PR-TEMPLATE.md` and `REPO-STANDARD.md` catch up
  with the workspace. They had been edited in `~/Code` and in the dotfiles
  copy since October (the zero-open rule, GitHub Pages by Actions, the latest
  ssg, the release-title field), so this repository, the canonical source,
  was the oldest copy. `AGENTS.md` section 8 also names the audit tool's
  real path, `Public/Python/code-portfolio-compliance`.

### Fixed

- `sync.py --push` no longer overwrites a file edited in place. The post-merge
  hook pushed this repository's October files over newer copies in `~/Code`
  and both dotfiles copies. A target is now overwritten only when it matches
  the source or holds a version this repository once committed; any other is
  kept and reported, and `--push --force` overwrites it on purpose.
- `sync.py --push` and `--pull` leave a target that links to the source
  alone and report it `[LINKED]`. Copying a file onto itself failed with
  `[ERROR] ... are the same file` for every file, so `~/Code` could not
  link its standards to this repository. The per-file step of `--push`
  moves to `push_file`, which brings `push_sync` under the complexity
  ceilings (cyclomatic 10 to 6, cognitive 17 to 7).

## 0.0.2 - 2026-10-11

### Added

- Multi-target synchronization utility (`scripts/sync.py`) for workspace root
  and chezmoi dotfiles distribution.
- Git hooks installer for automated post-commit and post-merge synchronization.

### Changed

- Advanced version carriers for the 0.0.2 release iteration cycle.

## 0.0.1 - 2026-10-11

### Added

- Initial release of the global code standards and specifications repository.
- Master Code Repositories Standard (`AGENTS.md`).
- Global Standard and Conventions (`GEMINI.md`).
- Pull Request Specification (`PR-TEMPLATE.md`).
- Canonical README Standard (`README-TEMPLATE.md`).
- Repository Gold Standard (`REPO-STANDARD.md`).
