<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau -->
<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

# 0006: standards-sync becomes a package when it next grows

**Status**: Accepted, 2026-11-25. Amends [0002](0002-one-canonical-source.md).

## Context

`scripts/sync.py` reached 500 lines in 0.0.14, the per-file ceiling of
AGENTS.md section 0, so the next feature cannot go into it. It was kept
to one file because the dotfiles copied it byte for byte as
`~/.local/bin/standards-sync`; the dotfiles' 0.2.554 iteration installs it
from PyPI with mise instead, so that reason goes with it. What still needs one file
is `make install`, the release's `standards-sync` asset and the
distribution packages, which install a single executable.

## Decision

The first change that adds to `sync.py` first splits it, in its own
commit with no change in behaviour, into the package `standards_sync`
(source discovery, check, push and pull, hooks, command line), whose
`__init__` keeps today's public names so `make api` holds. A zipapp built
from the package with fixed timestamps replaces the single-file
executable, so `make install`, the release asset and the packages keep
installing one file. Until such a change, the file stays as it is.

## Consequences

No refactor is made without a feature that needs it, and the split is
reviewed on its own before any behaviour changes. The tests, the fuzz
targets, `check_api.py`, the manual's API page and the recipes in `pkg/`
move to the package import path in the split commit.
