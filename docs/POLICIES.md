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

## Stability guarantees

For `standards-sync`, these are the public contract. A change to any of
them is a breaking change and is called out in the CHANGELOG:

- **Options**: `--check`, `-q`/`--quiet`, `--push`, `--force`, `--pull`
  and `--install-hooks`, with no option meaning `--push`. Pinned by
  `tests/test_sync.py::test_cli_options_are_stable`.
- **Exit status**: 0 when in sync or done, 1 on drift, a kept edit, or a
  push, pull or hook install that could not run.
- **Status words**: `[OK]`, `[MISSING]`, `[DRIFTED]`, `[COPIED]`, `[KEPT]`,
  `[LINKED]`, `[PULLED]` and `[ERROR]`, which scripts may match.
- **Environment**: `STANDARDS_REPO` and `STANDARDS_TARGETS`.
- **Output stability**: push never overwrites a file edited in place
  without `--force`. A change that would make it do so is breaking even
  if no option changes.
- **Python API**: the public functions of `scripts/sync.py`, checked
  against the last release by `make api`.

An option or status word to be removed keeps working, with a warning on
standard error, for at least one release before it goes.

For the standards themselves, a release is the unit of change: a
repository that follows `v0.0.3` of the standards follows the files at
that tag. Every rule change is listed in the CHANGELOG.
