<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau -->
<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

# 0004: Python 3.9 is the floor

**Status**: Accepted, 2026-11-25.

## Context

The git hooks run `standards-sync` with `#!/usr/bin/env python3`. On macOS
that is often `/usr/bin/python3` from the Command Line Tools, which is 3.9;
RHEL 9 also ships 3.9. Python 3.9 itself is past its upstream end of life.

## Decision

`requires-python = ">=3.9"`. The code uses nothing newer than 3.9
offers. CI proves the floor by running the command end to end on 3.9
with `tests/smoke.py`, which needs only the standard library: since
GHSA-6w46-j5rx-g56g, fixed in pytest 9.0.3, no safe pytest supports 3.9,
so the full suite runs on 3.10 and the newest CPython. The dev tools
declare that floor themselves (`[tool.uv.dependency-groups]`), so the
lockfile never resolves them for 3.9.

## Consequences

The hooks work on a fresh Mac with no Python installed. The floor rises
when the macOS system Python does, recorded in a new ADR and the CHANGELOG.
