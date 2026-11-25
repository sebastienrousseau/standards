<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau -->
<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

# Packaging

For anyone packaging `standards-sync`.

- **Licence**: `Apache-2.0 OR MIT`, at the user's option. Both texts ship
  as `LICENSE-APACHE` and `LICENSE-MIT`; every file's licence is
  machine-readable ([REUSE](https://reuse.software/) 3.3, checked in CI).
- **Toolchain**: Python 3.9 or later and `git`. No runtime dependencies.
  See [Policies](POLICIES.md) for when the floor may rise.
- **Build**: `uv build` or `python3 -m build` (hatchling) produces the
  wheel and sdist. With `SOURCE_DATE_EPOCH` set, two builds are
  byte-identical; CI builds twice and compares (`make reproducible`).
- **Install**: `make DESTDIR=<stage> PREFIX=/usr install` installs the
  command, its manpage and bash, zsh and fish completions under FHS
  paths. The manpage and completions are generated from the argument
  parser at build time; none is committed.
- **Tests**: `python3 -m pytest tests` needs only `pytest` and `git`, and
  no network.
- **Source**: from 0.0.8 the wheel and sdist of each release are also on
  [PyPI](https://pypi.org/project/standards-sync/), uploaded by the
  release workflow with trusted publishing; they are the same files as
  the GitHub release assets.
- **Verification**: tags are SSH-signed with the keys in `KEYS.asc`;
  release assets carry SHA-256 sums and build provenance. See
  [Verifying releases](VERIFYING.md).

## What is not provided

There are no distribution packages, container images or standalone
binaries. The default targets are one person's workspace layout, so the
command is useful to that workspace and to anyone adopting the same
standards with `STANDARDS_TARGETS`; a distribution package would add
nothing a `make install` does not. A container would need the home
directory mounted to do anything. The command is a single Python file
that runs on the system `python3`, so a frozen binary would only add
size. This will be revisited if someone outside the workspace asks to
package it.
