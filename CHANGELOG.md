<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau -->
<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

# Changelog

All notable changes to Standards are recorded here, in the form of
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions follow
[AGENTS.md](AGENTS.md) section 3.

## [0.0.12] - 2026-11-25

### Added

- `standards-sync` is published in the Homebrew tap
  (`brew install sebastienrousseau/tap/standards-sync`) and on the AUR
  (`standards-sync`), from the 0.0.10 recipes; the README and
  `docs/packaging.md` show how to install from each.

## [0.0.11] - 2026-11-25

### Changed

- Dependencies: the dev container's base image moves from Python 3.13 to
  3.15 (Dependabot #16), and `cachix/install-nix-action`, which builds the
  Nix package in CI, from 31.11.3 to 32.0.0 (Dependabot #17).

## [0.0.10] - 2026-11-25

### Added

- Distribution packages. `make pkg` packs the installed tree as a
  reproducible `standards-sync-<version>-unix.tar.gz` and renders the
  recipes in `pkg/` against it: a Debian package root, an RPM spec, an
  AUR `PKGBUILD` and `.SRCINFO`, a Homebrew formula and a Nix expression.
  CI builds and installs each one (apt on Ubuntu, dnf on Fedora 44,
  pacman on Arch, brew on macOS, nix-build on nixpkgs 26.05), and every
  release attaches the `.deb`, the `.rpm` and the recipes.
- A dependency provenance policy (`docs/POLICIES.md`), enforced by
  `scripts/check_lock.py` in `make lint`: every locked package from PyPI
  with a SHA-256 for every file, and every `uv` call in the Makefiles and
  workflows frozen to the lock.

### Changed

- The dev container's base image is pinned by digest, in
  `.devcontainer/Dockerfile`, which Dependabot now updates.

## [0.0.9] - 2026-11-25

### Changed

- The README installs `standards-sync` from PyPI, where 0.0.8 is the
  first release, and its registry badge shows the PyPI version.
- `docs/VERIFYING.md` shows how to verify a PyPI file's attestation.

## [0.0.8] - 2026-11-25

### Added

- The release workflow uploads the wheel and sdist to PyPI as
  `standards-sync`, by trusted publishing (OpenID Connect, no stored
  token), after the GitHub release is published.
- CI tests on Python 3.16, the next release, while it is a pre-release.
  The job warns without blocking a merge.

## [0.0.7] - 2026-11-25

### Added

- The README and the assurance case link the project's OpenSSF Best
  Practices passing badge, where every criterion's evidence is recorded.

### Fixed

- A `STANDARDS_TARGETS` entry that is blank only once `Path` normalises
  it, such as `./ /` (a directory named by one space), is now ignored
  like any other blank entry instead of becoming a target. Found by the
  Atheris fuzzer on pull request #12; the input joins the corpus and
  the Hypothesis examples.

## [0.0.6] - 2026-11-25

### Added

- `ROADMAP.md`: what the project plans, and does not plan, through 2027.
- `docs/ASSURANCE.md`: the security assurance case (requirements, threat
  model, trust boundaries, secure design, common weaknesses countered).
- `CONTRIBUTING.md` names the coding standards, requires tests for new
  functionality and a regression test for each fix, and sets out what a
  review checks.
- `GOVERNANCE.md` lists the roles and their responsibilities, and states
  the continuity gap: one maintainer, bus factor 1.

## [0.0.5] - 2026-11-25

### Added

- Every release carries its signature and provenance as assets, where the
  OpenSSF Scorecard's Signed-Releases check looks for them: the workflow
  attaches the build provenance bundle as
  `standards-sync-<version>.intoto.jsonl` and signs `SHA256SUMS` with
  Sigstore (`SHA256SUMS.sigstore.json`). Releases 0.0.1 to 0.0.4 gained
  `SHA256SUMS.sig`, signed with the maintainer's SSH key, and 0.0.3 and
  0.0.4 their original provenance bundles. `docs/VERIFYING.md` shows how
  to check each.

### Changed

- `KEYS.asc` allows its keys in the `file` namespace as well as `git`,
  so `ssh-keygen -Y verify` accepts the release checksum signatures.

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

[0.0.12]: https://github.com/sebastienrousseau/standards/compare/v0.0.11...v0.0.12
[0.0.11]: https://github.com/sebastienrousseau/standards/compare/v0.0.10...v0.0.11
[0.0.10]: https://github.com/sebastienrousseau/standards/compare/v0.0.9...v0.0.10
[0.0.9]: https://github.com/sebastienrousseau/standards/compare/v0.0.8...v0.0.9
[0.0.8]: https://github.com/sebastienrousseau/standards/compare/v0.0.7...v0.0.8
[0.0.7]: https://github.com/sebastienrousseau/standards/compare/v0.0.6...v0.0.7
[0.0.6]: https://github.com/sebastienrousseau/standards/compare/v0.0.5...v0.0.6
[0.0.5]: https://github.com/sebastienrousseau/standards/compare/v0.0.4...v0.0.5
[0.0.4]: https://github.com/sebastienrousseau/standards/compare/v0.0.3...v0.0.4
[0.0.3]: https://github.com/sebastienrousseau/standards/compare/v0.0.2...v0.0.3
[0.0.2]: https://github.com/sebastienrousseau/standards/compare/v0.0.1...v0.0.2
[0.0.1]: https://github.com/sebastienrousseau/standards/releases/tag/v0.0.1
