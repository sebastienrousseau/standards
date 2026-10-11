<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau -->
<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

# Contributing to Standards

Thank you for your interest in contributing to the master specifications and standards repository.

## Standards and Guidelines

All contributions to this repository must adhere to:
- [AGENTS.md](AGENTS.md): Code Repositories Standard and agent invariants
- [PR-TEMPLATE.md](PR-TEMPLATE.md): Pull Request specification
- [README-TEMPLATE.md](README-TEMPLATE.md): Canonical README standard
- [REPO-STANDARD.md](REPO-STANDARD.md): Repository gold standard

## Commit Guidelines

- Format: `<type>: <subject>` (maximum 50 characters, imperative mood).
- Commit message body wrapped strictly at 72 characters.
- Signed commits (`commit.gpgsign = true`) and format signoffs (`format.signoff = true`).
- Agent attributions in trailers: `Assisted-by: <agent>:<model> [<analysis tools>]`.

## Pull Request Process

1. Fork or branch from `main`.
2. Work on iteration branches `feat/v<next-version>`.
3. Submit a PR following the format defined in [PR-TEMPLATE.md](PR-TEMPLATE.md).
