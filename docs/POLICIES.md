<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau -->
<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

# Policies and stability

## Versioning

Releases follow [AGENTS.md](AGENTS.md) section 3: they start at `0.0.1`
and rise by `0.0.1` each time. A release is a signed tag `v<version>` on
`main`, made from the single `feat/v<version>` pull request.

## Minimum Python

The floor is **Python 3.9**, because the git hooks run `standards-sync`
on whatever `python3` comes first on `PATH`, and on macOS that is the
system `/usr/bin/python3`, which is 3.9.
[ADR 0004](adr/0004-python-3.9-floor.md) records the decision.

| Platform | Default `python3` | Meets the 3.9 floor |
| :--- | :--- | :--- |
| macOS, Command Line Tools | 3.9 | yes |
| RHEL, Rocky and Alma Linux 9 | 3.9 | yes |
| Ubuntu 22.04 LTS | 3.10 | yes |
| Debian 12 | 3.11 | yes |
| Ubuntu 24.04 LTS | 3.12 | yes |
| Debian 13 | 3.13 | yes |

CI runs the test suite on Python 3.10 and on the newest CPython release,
and an end-to-end smoke test (`tests/smoke.py`, standard library only)
on 3.9, all on both Linux and macOS. The full suite cannot run on 3.9:
no pytest release free of GHSA-6w46-j5rx-g56g supports it. The floor rises only when the macOS system
Python does, in a release whose CHANGELOG says so.

## Dependencies

`standards-sync` has no runtime dependencies. The development tools are
held to this provenance policy, which `scripts/check_lock.py` enforces in
`make lint`:

- **One source.** Every package in `uv.lock` comes from PyPI; a git, URL
  or path source fails the check.
- **Hashed.** Every sdist and wheel in `uv.lock` carries its SHA-256, and
  uv verifies it on install.
- **Installed as locked.** Every `uv run` and `uv sync` in the Makefiles
  and workflows is `--frozen` or `--locked`, so nothing is re-resolved.
- **Advisories.** `pip-audit` checks every locked version against OSV in
  `make check`, dependency review checks every pull request, and a
  version with a published advisory is excluded in `pyproject.toml`
  (`constraint-dependencies`) so it cannot resolve.
- **Updates** come from Dependabot, as pull requests that go through the
  same gate.
- **A new dependency** is added in its own commit that says why it is
  needed and who maintains it, and is preferred when it publishes
  attestations from trusted publishing.
- **Everything else is pinned too**: Actions by commit SHA, container
  images by digest (the dev container's base, and the Fedora and Arch
  images that build and test the packages).

## Stability guarantees

For `standards-sync`, these are the public contract. A change to any of
them is a breaking change and is called out in the CHANGELOG:

- **Options**: `--check`, `-q`/`--quiet`, `--push`, `--force`, `--pull`
  and `--install-hooks`, with no option meaning `--push`. Pinned by
  `tests/test_sync.py::test_cli_options_are_stable`.
- **Exit status**: 0 when in sync or done, 1 on drift, a kept edit, an
  earlier published version not pulled, a file or hook that could not be
  written, an existing hook kept, no source, or a `STANDARDS_REPO` that
  does not hold the standards.
- **Status words**: `[OK]`, `[MISSING]`, `[DRIFTED]`, `[COPIED]`, `[KEPT]`,
  `[LINKED]`, `[PULLED]`, `[STALE]` and `[ERROR]`, which scripts may match.
- **Environment**: `STANDARDS_REPO` (when set, the only source) and
  `STANDARDS_TARGETS`.
- **Output stability**: push never overwrites a file edited in place
  without `--force`. A change that would make it do so is breaking even
  if no option changes.
- **Python API**: the public functions of `scripts/sync.py`, checked
  against the last release by `make api`.

A deprecation comes before any removal or change of the contract above.
The deprecated option, status word or behaviour keeps working, with a
warning on standard error, and is listed in
[DEPRECATIONS.md](https://github.com/sebastienrousseau/standards/blob/main/DEPRECATIONS.md)
with what replaces it, the release that deprecated it and a removal date.
That date is at least 90 days after the deprecating release; the change
ships in the first release on or after it, and in a later release than
the one that announced it, never earlier.

For the standards themselves, a release is the unit of change: a
repository that follows `v0.0.3` of the standards follows the files at
that tag. Every rule change is listed in the CHANGELOG.
