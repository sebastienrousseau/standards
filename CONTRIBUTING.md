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

[DEVELOPMENT.md](DEVELOPMENT.md) sets up the tools and explains `make check`.

## Commit Guidelines

- Format: `<type>: <subject>` (maximum 50 characters, imperative mood).
- Commit message body wrapped strictly at 72 characters.
- Signed commits (`commit.gpgsign = true`) and a `Signed-off-by:` trailer (`git commit -s`).
- Agent attributions in trailers: `Assisted-by: <agent>:<model> [<analysis tools>]`.

## Pull Request Process

1. Work on the release branch `feat/v<next-version>`, where the version is
   one `0.0.1` above the latest release. From a fork, branch from it.
2. Run `make check` and fix what it reports.
3. Open the pull request against `main`, following [PR-TEMPLATE.md](PR-TEMPLATE.md).
   There is only ever one open pull request into `main`: the release
   branch's. Other work reaches it as commits on that branch.

## Releases

The maintainer merges the release pull request and pushes a signed,
annotated tag `v<version>` whose message is `standards v<version>`. The
release workflow does the rest: it checks the tag, builds and attests the
assets, and publishes a release titled `standards <version>`.
