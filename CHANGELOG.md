<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau -->
<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

# Changelog

All notable changes to Standards are recorded here, in the form of
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions follow
[AGENTS.md](AGENTS.md) section 3.

## [0.0.4] - 2026-11-25

### Added

- Coverage-guided fuzzing with Atheris (`fuzz/fuzz_atheris.py`, seeded
  from `fuzz/corpus/`), run in CI's new `fuzz` job and by
  `make fuzz-atheris` on Linux x86-64. It checks the STANDARDS_TARGETS
  parser, `blob_of` and the drift check against a byte comparison. The
  OpenSSF Scorecard recognises Atheris, not Hypothesis, so its first run
  on `main` reported the project as not fuzzed.

### Changed

- The dev tools declare their own floor, Python 3.10
  (`[tool.uv.dependency-groups]`), so `uv.lock` no longer resolves them for
  3.9. Dependabot's `uv` update had failed there: griffe 2.3 needs 3.10.
  `standards-sync` keeps its 3.9 floor, checked by `tests/smoke.py`.
- Dependencies: `astral-sh/setup-uv` 10.3.3 to 10.4.0, `ossf/scorecard-action`
  to its latest release, and the dev container's Node feature 1.7.1 to
  2.1.2 (Dependabot #6 and #7); `uv lock --upgrade` for the dev tools.

## [0.0.3] - 2026-11-25

### Added

- `standards-sync` installs as a command: `uv tool install` from the
  repository, or `make install` (with `PREFIX` and `DESTDIR`), which also
  installs a manpage and bash, zsh and fish completions generated from the
  argument parser. `--help` now documents the environment variables and
  the exit status.
- One gate, `make check`: ruff lint and format, the complexity ceilings of
  `AGENTS.md` section 0 for every function (`scripts/check_complexity.py`,
  with an empty baseline that may only shrink), codespell, REUSE 3.3,
  markdownlint, actionlint, tests at 95 percent branch coverage or more
  (99 now), property-based fuzzing with a regression corpus, a strict
  manual build, an API breakage check against the last release,
  pip-audit, and a byte-for-byte reproducible build.
- `scripts/check_docs.py` holds this README to `README-TEMPLATE.md`'s
  heading order with no unresolved tokens, the GitHub PR template to
  `PR-TEMPLATE.md`, the version carriers to one version, every document
  to `gh`'s real `name` field, and every manual page to the author link.
- CI on Linux and macOS with Python 3.10 and 3.15 and a 3.9 smoke test, plus the README Quick
  Start run as written, a staged install, the dev container, a link
  check, dependency review, and a `validate` job that requires them all.
- A manual built with Zensical and deployed to GitHub Pages by Actions,
  with architecture, policies, migration, packaging and verification
  pages, five decision records, and an API reference generated from the
  docstrings by mkdocstrings; ruff's D1 rules require a docstring on
  every public function.
- A release workflow: blocking preflight (signed annotated tag, message,
  on `main`, versions), assets with SHA-256 sums, a CycloneDX SBOM and
  SLSA provenance, notes in the section order of `AGENTS.md` section 3,
  and an audit of the published release. `workflow_dispatch` runs it dry.
- `KEYS.asc` (the SSH signing keys), `DEVELOPMENT.md`, `GOVERNANCE.md`,
  `SUPPORT.md`, issue and PR templates, `CODEOWNERS`, Dependabot for
  Actions, uv and the dev container, the OpenSSF Scorecard,
  `.editorconfig`, a pre-commit config, a dev container, a VHS demo and a
  logo.

### Changed

- `AGENTS.md`, `GEMINI.md`, `PR-TEMPLATE.md` and `REPO-STANDARD.md` catch up
  with the workspace. They had been edited in `~/Code` and in the dotfiles
  copy since October (the zero-open rule, GitHub Pages by Actions, the latest
  ssg, the release-title field), so this repository, the canonical source,
  was the oldest copy. `AGENTS.md` section 8 also names the audit tool's
  real path, `Public/Python/code-portfolio-compliance`.
- The README follows `README-TEMPLATE.md`.
- `CONTRIBUTING.md` sends work to the `feat/v<next-version>` branch, as
  `AGENTS.md` section 3 requires, instead of a branch from `main`.
- `SECURITY.md` states response times, the supported version and the scope.
- The `sync.py` functions over the complexity ceilings (`check_sync`,
  `find_canonical_source`, `get_target_dirs`, `check_target_file`) are
  split into private helpers, with no change in behaviour. The usage line
  names the installed command, `standards-sync`.

### Fixed

- `REPO-STANDARD.md` told agents to run `gh release view --json` with a
  `title` field, which `gh` does not have; it is `name`, as `AGENTS.md`
  already said.
- `sync.py` passes ruff: three blind `except Exception` and a silent
  `try`/`except`/`pass` now catch the errors they mean.
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
- The dev tools can no longer resolve a `filelock` affected by
  GHSA-v4x8-3wr5-3wq8 and the other advisories fixed in 4.2.1: a uv
  constraint requires `filelock>=4.2.1` in every environment, and
  `pip-audit`, which pulls it in, installs only on Python 3.11 or later,
  as no fixed release supports older versions. pip-audit now queries OSV.
- Likewise `pytest>=9.0.3` (GHSA-6w46-j5rx-g56g). The fixed pytest needs
  Python 3.10, so the suite runs on 3.10 and 3.15, and the 3.9 floor is
  checked end to end by `tests/smoke.py`, which needs only the standard
  library. An OSV query over every version in `uv.lock` finds nothing else.
- Markdown lint findings across the standards: list spacing, a fenced
  block without a language, a table style, a code span with a trailing
  space.

## [0.0.2] - 2026-10-11

### Added

- Multi-target synchronization utility (`scripts/sync.py`) for workspace root
  and chezmoi dotfiles distribution.
- Git hooks installer for automated post-commit and post-merge synchronization.

### Changed

- Advanced version carriers for the 0.0.2 release iteration cycle.

## [0.0.1] - 2026-10-11

### Added

- Initial release of the global code standards and specifications repository.
- Master Code Repositories Standard (`AGENTS.md`).
- Global Standard and Conventions (`GEMINI.md`).
- Pull Request Specification (`PR-TEMPLATE.md`).
- Canonical README Standard (`README-TEMPLATE.md`).
- Repository Gold Standard (`REPO-STANDARD.md`).

[0.0.4]: https://github.com/sebastienrousseau/standards/compare/v0.0.3...v0.0.4
[0.0.3]: https://github.com/sebastienrousseau/standards/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/sebastienrousseau/standards/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/sebastienrousseau/standards/releases/tag/v0.0.1
