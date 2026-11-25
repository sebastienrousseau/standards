<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau -->
<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

# 0001: Record architecture decisions

**Status**: Accepted, 2026-11-25.

## Context

The standards bind every repository, and `standards-sync` writes into the
workspace and the dotfiles. Why a rule or a behaviour is the way it is gets
lost between sessions, human or agent.

## Decision

Decisions that will be questioned later are recorded in `docs/adr/`, one
file each, with context, decision and consequences.

## Consequences

A change that reverses a decision adds a superseding record instead of
editing history.
