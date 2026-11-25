<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau -->
<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

<p align="center">
  <img src="https://raw.githubusercontent.com/sebastienrousseau/standards/main/.github/logo.svg" alt="standards logo" width="128" />
</p>

<h1 align="center">standards</h1>

<p align="center">
  The rules every repository by Sebastien Rousseau follows, and the command that keeps every copy of them identical.
</p>

<p align="center">
  <a href="https://github.com/sebastienrousseau/standards/actions"><img src="https://img.shields.io/github/actions/workflow/status/sebastienrousseau/standards/ci.yml?style=for-the-badge&logo=github" alt="Build" height="28" /></a>
  <a href="https://github.com/sebastienrousseau/standards/releases"><img src="https://img.shields.io/github/v/release/sebastienrousseau/standards?style=for-the-badge&color=fc8d62&logo=github" alt="Release" height="28" /></a>
  <a href="https://sebastienrousseau.com/standards/"><img src="https://img.shields.io/badge/docs-manual-blue?style=for-the-badge&labelColor=555555&logo=materialformkdocs" alt="Docs" height="28" /></a>
  <a href="https://scorecard.dev/viewer/?uri=github.com/sebastienrousseau/standards"><img src="https://img.shields.io/ossf-scorecard/github.com/sebastienrousseau/standards?style=for-the-badge&label=OpenSSF%20Scorecard&logo=openssf" alt="OpenSSF Scorecard" height="28" /></a>
  <a href="#license"><img src="https://img.shields.io/badge/license-Apache--2.0%20OR%20MIT-blue.svg?style=for-the-badge" alt="License: Apache-2.0 OR MIT" height="28" /></a>
  <a href="https://github.com/sebastienrousseau/standards/blob/main/docs/POLICIES.md"><img src="https://img.shields.io/badge/Python-3.9%2B-93450a.svg?style=for-the-badge&logo=python" alt="Python 3.9 or later" height="28" /></a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/sebastienrousseau/standards/main/.github/demo.gif" alt="standards-sync pushing the five standards to a target, keeping a file edited there instead of overwriting it, and showing the drift with --check" width="100%" />
</p>

---

## Contents

**Getting started**

- [Install](#install): `uv tool install`, `make install`, or the dotfiles
- [Requirements](#requirements): toolchain floor, platforms
- [Quick Start](#quick-start): push the standards to a scratch directory and check them

**The standards ecosystem**

- [The standards ecosystem](#the-standards-ecosystem): the five standards, standards-sync, the dotfiles, the compliance audit

**Library reference**

- [Capabilities at a glance](#capabilities-at-a-glance): the current surface by theme
- [Ecosystem comparison](#ecosystem-comparison): why there is none
- [Benchmarks](#benchmarks): why there are none
- [Features](#features): what each part does
- [Configuration](#configuration): environment variables
- [Examples](#examples): common tasks

**Operational**

- [When not to use standards](#when-not-to-use-standards): limitations
- [Development](#development): make targets, fuzzing, CI
- [Security](#security): guarantees and compliance
- [Documentation](#documentation): all reference docs
- [Stability guarantees](#stability-guarantees): SemVer axis, output stability, minimum toolchain discipline
- [License](#license)

---

## Install

### As a Python library

```bash
uv tool install git+https://github.com/sebastienrousseau/standards
```

This installs the `standards-sync` command; its functions are importable
as `standards_sync`.

From a clone, with the manpage and bash, zsh and fish completions:

```bash
make PREFIX="$HOME/.local" install
```

The [dotfiles](https://github.com/sebastienrousseau/dotfiles) also install
it as `~/.local/bin/standards-sync`, and link `~/Code`'s standards to a
clone of this repository.

---

## Requirements

| Requirement | Version | Why |
| :--- | :--- | :--- |
| Python | 3.9 or later | the minimum toolchain is the macOS system `python3`; see the policy in [docs/POLICIES.md](docs/POLICIES.md) |
| git | any | to tell a published version of a file from an edit |
| OS | macOS, Linux | tested on both in CI |

---

## Quick Start

```bash
make PREFIX="$HOME/.local" install
export PATH="$HOME/.local/bin:$PATH"
export STANDARDS_REPO="$PWD" STANDARDS_TARGETS="$PWD/build/quickstart"
standards-sync --push     # copy the five standards to the scratch directory
standards-sync --check    # every file [OK]
```

Run from a clone, this installs the command and tries it on a scratch
directory, leaving `~/Code` and the dotfiles alone. Unset
`STANDARDS_TARGETS` to work on the real targets. CI runs this block as
written.

---

## The standards ecosystem

The standards are edited here, carried to every machine by the dotfiles,
and measured across the portfolio by the compliance audit.

| Component | Purpose | Use case |
| :--- | :--- | :--- |
| [`AGENTS.md`](AGENTS.md) | Invariants for AI-assisted and human work | Read before changing any repository |
| [`GEMINI.md`](GEMINI.md) | Pointer file for Gemini and other agents | Loaded at the start of an agent session |
| [`REPO-STANDARD.md`](REPO-STANDARD.md) | The eight-category scorecard and its phases | Rating and raising a repository |
| [`README-TEMPLATE.md`](README-TEMPLATE.md) | The layout of every primary README | Writing or checking a README |
| [`PR-TEMPLATE.md`](PR-TEMPLATE.md) | The shape of every pull request description | Opening a pull request |
| `standards-sync` | Keeps every copy identical without losing an edit | `~/Code` and dotfiles upkeep |
| [dotfiles](https://github.com/sebastienrousseau/dotfiles) | Installs the command, links `~/Code` here | A new machine |

---

## Capabilities at a glance

| Area | Capability | Status |
| :--- | :--- | :--- |
| Standards | Five canonical files, released together | Stable |
| Sync | Drift check with diffs | Stable |
| Sync | Push that keeps edits made in place | Stable |
| Sync | Pull that adopts a `~/Code` edit | Stable |
| Sync | Git hooks that push on commit and merge | Stable |
| Tooling | Manpage and completions from the parser | Stable |

---

## Ecosystem comparison

This section does not apply: the repository is one portfolio's
governance, not a product with alternatives, and no comparison is claimed.

---

## Benchmarks

This section does not apply: `standards-sync` hashes and copies five
small text files, and no performance claim is made.

---

## Features

- **One source.** A rule changes here, in a pull request, and nowhere else.
- **Safe push.** A target file is overwritten only if it is missing,
  identical, or a version this repository committed. An edit made in
  place is kept and named, and the push exits 1.
- **Links respected.** A target that links to the source is left alone.
- **Pull.** An edit made in `~/Code` is adopted, then pushed to the
  dotfiles copies.
- **Checks that bind this repository too.** CI holds the README to
  `README-TEMPLATE.md`, the GitHub PR template to `PR-TEMPLATE.md`, and
  every function to the complexity ceilings of `AGENTS.md`.

---

## Configuration

| Variable | Effect |
| :--- | :--- |
| `STANDARDS_REPO` | The source directory, tried before any other |
| `STANDARDS_TARGETS` | Target directories, separated by `:`, replacing the defaults |

Without them, the source is found from the script's location or under
`~/Code`, and the targets are `~/Code` and the dotfiles copies that exist.
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) lists the exact order.

---

## Examples

```bash
standards-sync --check          # what differs, with diffs; changes nothing
standards-sync --check -q       # one warning line, or silence
standards-sync --push           # bring every copy up to date
standards-sync --push --force   # also overwrite files edited in place
standards-sync --pull           # adopt an edit made in ~/Code
standards-sync --install-hooks  # push after every commit and merge here
```

---

## When not to use standards

- The default targets are one workspace's layout (`~/Code`, chezmoi
  dotfiles). Elsewhere, set `STANDARDS_TARGETS`.
- It syncs exactly five files. It is not a general file synchroniser.
- The rules are opinionated (`0.0.x` versioning, one release pull
  request, signed-off commits). Adopt them knowingly.
- Windows is not tested.

---

## Development

```bash
uv sync --frozen
make check        # every gate CI runs
make help         # every task
```

`make check` runs ruff, the complexity ceilings, codespell, REUSE,
markdownlint, actionlint, the tests at 95 percent branch coverage, the
property-based fuzz corpus, the strict manual build, the API breakage
check, pip-audit and a reproducible-build comparison. See
[DEVELOPMENT.md](DEVELOPMENT.md).

---

## Security

`standards-sync` writes only the five standard files, into the targets it
lists, and git hooks into this checkout. Commits and tags are signed
(`KEYS.asc`), every Action is pinned by SHA, dependencies are locked and
audited on every push, and releases carry checksums, an SBOM and build
provenance. CodeQL, secret scanning and the OpenSSF Scorecard run on
`main`.

Report vulnerabilities according to [`SECURITY.md`](SECURITY.md).

---

## Documentation

- [User manual](https://sebastienrousseau.com/standards/): the standards and `standards-sync`
- `man standards-sync`, after `make install`
- [DEVELOPMENT.md](DEVELOPMENT.md): tools, the gate, tests, releases
- [ROADMAP.md](ROADMAP.md) and [GOVERNANCE.md](GOVERNANCE.md): plans, roles and decisions
- [docs/ASSURANCE.md](docs/ASSURANCE.md): the security assurance case
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and the [decision records](docs/adr/index.md)
- [CHANGELOG.md](CHANGELOG.md)

---

## Stability guarantees

Versions rise by `0.0.1` per release ([`AGENTS.md`](AGENTS.md) section 3).
For `standards-sync`, the options, exit status, status words and
environment variables are the contract, and a push never overwrites an
edit made in place without `--force`: changing any of these is breaking,
even with no option renamed. The public Python API is checked against the
last release in CI. The minimum toolchain is Python 3.9 and rises only
with the macOS system Python. Details in
[docs/POLICIES.md](docs/POLICIES.md).

---

## License

Dual-licensed under either:

- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or <https://www.apache.org/licenses/LICENSE-2.0>)
- MIT License ([LICENSE-MIT](LICENSE-MIT) or <https://opensource.org/licenses/MIT>)

at your option.

Copyright &copy; 2026 <a href="https://sebastienrousseau.com/" rel="author">Sebastien Rousseau</a>.
