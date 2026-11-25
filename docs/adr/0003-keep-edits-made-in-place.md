<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau -->
<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

# 0003: A push keeps a file edited in place

**Status**: Accepted, 2026-11-24 (shipped in 0.0.3).

## Context

The post-merge hook ran `standards-sync --push`, which copied this
repository's October files over newer copies in `~/Code` and both
dotfiles copies, replacing the workspace's `AGENTS.md` with an older one.
Nothing warned, and the loss surfaced only later.

## Decision

A push overwrites a target file only when it is missing, already matches,
or holds a version this repository has committed (its git blob id appears
in the file's history). Any other content was edited in place: the push
keeps it, names it `[KEPT]` and exits 1. `--pull` adopts the edit and
`--push --force` overwrites it on purpose.

## Consequences

A push can no longer destroy work silently. It can fail where it used to
succeed, which is the point: the person deciding is told which file and
given both ways out.
