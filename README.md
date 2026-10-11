<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau -->
<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

<h1 align="center">Standards</h1>

<p align="center">
  Master code standards, specifications, and repository governance conventions.
</p>

<p align="center">
  <a href="https://github.com/sebastienrousseau/standards/actions"><img src="https://img.shields.io/github/actions/workflow/status/sebastienrousseau/standards/ci.yml?style=for-the-badge&logo=github" alt="Build" height="28" /></a>
  <a href="LICENSE-APACHE"><img src="https://img.shields.io/badge/License-Apache_2.0_OR_MIT-blue.svg?style=for-the-badge" alt="License: Apache-2.0 OR MIT" height="28" /></a>
</p>

---

## Contents

- [Overview](#overview)
- [Standards Catalog](#standards-catalog)
- [Usage Across Workspaces](#usage-across-workspaces)
- [Synchronization Tooling](#synchronization-tooling)
- [Versioning and Branch Lifecycle](#versioning-and-branch-lifecycle)
- [Contributing](#contributing)
- [Security](#security)
- [License](#license)

---

## Overview

`standards` is the central source of truth for repository structure, AI-assisted development standards, pull request specifications, and release governance across all projects maintained by Sebastien Rousseau.

---

## Standards Catalog

| Standard | Purpose | Description |
| :--- | :--- | :--- |
| [`AGENTS.md`](AGENTS.md) | Agent Invariants | Mandatory guidelines and complexity ceilings for AI-assisted engineering. |
| [`GEMINI.md`](GEMINI.md) | Agent Instructions | Global configuration and pointer directives for Gemini and agent sessions. |
| [`PR-TEMPLATE.md`](PR-TEMPLATE.md) | Pull Request Spec | Canonical pull request format with two-line BLUF, highlights, and checksums. |
| [`README-TEMPLATE.md`](README-TEMPLATE.md) | README Standard | Canonical structure, badge row, and section requirements for project READMEs. |
| [`REPO-STANDARD.md`](REPO-STANDARD.md) | Gold Standard | 10/10 repository scorecard, phase recipes, and maturity benchmarks. |

---

## Usage Across Workspaces

These master files are tracked at the root of the local workspace `/Users/seb/Code/` and synchronized with `dotfiles` (via Chezmoi) and this repository.

---

## Synchronization Tooling

Use `standards-sync` (or `python3 scripts/sync.py`) to verify and maintain synchronization between the canonical repository, the active workspace root (`~/Code`), and `dotfiles` (`defaults/Code`):

```bash
# Verify synchronization (exits 0 on match, non-zero on drift)
standards-sync --check

# Push changes from this repository to ~/Code and dotfiles
standards-sync --push

# Pull changes from ~/Code into this repository
standards-sync --pull

# Install automatic post-commit and post-merge git hooks
standards-sync --install-hooks
```

---

## Versioning and Branch Lifecycle

This repository strictly follows the Semantic Versioning sequencing policy:
- Public releases stay on the `0.0.x` line and increment strictly by `0.0.1`.
- All development for the next iteration occurs on `feat/v<next-version>`.
- Exactly one active release pull request targets `main`.

---

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

---

## Security

See [`SECURITY.md`](SECURITY.md) for vulnerability disclosure procedures.

---

## License

Dual-licensed under either:

- Apache License, Version 2.0 ([LICENSE-APACHE](LICENSE-APACHE) or https://www.apache.org/licenses/LICENSE-2.0)
- MIT License ([LICENSE-MIT](LICENSE-MIT) or https://opensource.org/licenses/MIT)

at your option.

Copyright &copy; 2026 <a href="https://sebastienrousseau.com/" rel="author">Sebastien Rousseau</a>.
