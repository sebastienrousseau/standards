<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau -->
<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

# 0005: Zensical builds the manual

**Status**: Accepted, 2026-11-25.

## Context

AGENTS.md section 6 names MkDocs with Material for a Python project's
manual. Material for MkDocs reaches end of life on 5 May 2027, and its
team names Zensical as the successor. Zensical reads `mkdocs.yml`
unchanged, and its `--strict` build fails on a broken link as MkDocs does.

## Decision

The manual is configured in `mkdocs.yml` and built with
`zensical build --strict`. Zensical needs Python 3.11 or later, so it is a
dev dependency only on those versions; the tool itself keeps its 3.9
floor.

## Consequences

No migration when Material stops receiving fixes. Zensical is pre-1.0, so
a release that breaks the build is fixed forward in the same change as the
version bump, and `mkdocs.yml` stays readable by MkDocs as a fallback.
