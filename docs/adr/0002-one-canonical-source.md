<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau -->
<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

# 0002: One canonical source, synced by a single-file script

**Status**: Accepted, 2026-11-25 (recording the design shipped in 0.0.2);
amended by [0006](0006-a-package-when-sync-grows.md).

## Context

The standards are read from `~/Code` by agents, shipped in the dotfiles for
new machines, and reviewed here. Three hand-maintained copies drifted: in
November 2026 this repository was found to hold the oldest copy of all.

## Decision

This repository is the only place a standard is edited, through a pull
request. `~/Code` links to its files; the dotfiles hold copies that
`standards-sync` refreshes. The script is one standard-library Python
file, `scripts/sync.py`, because the dotfiles vendor it byte for byte and
it must run before any dependency could be installed.

## Consequences

A change reaches every copy through one reviewed path. The script cannot
use third-party packages, and any helper it needs lives in the same file.
