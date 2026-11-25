<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau -->
<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

# Roadmap

What the project intends to do, and not do, through the end of 2027.
Releases follow [AGENTS.md](AGENTS.md) section 3: small `0.0.x` steps,
one release pull request at a time.

## Planned

- **Keep the standards current.** Rules change here first, in a pull
  request, and reach `~/Code` and the dotfiles through `standards-sync`.
- **Keep the repository at its own bar.** Zero open alerts and issues,
  every gate in `make check` green, dependencies current.
- **Reach the OpenSSF Best Practices Silver badge**, and work towards an
  OpenSSF Scorecard of 9 or more.
- **Follow the manual's generator.** Zensical is pre-1.0; each release
  that changes its output is adopted in the same change as the bump
  ([ADR 0005](docs/adr/0005-zensical-for-the-manual.md)).

## Not planned

- A general-purpose file synchroniser: `standards-sync` manages exactly
  the five standard files.
- Distribution packages, container images or frozen binaries
  ([docs/packaging.md](docs/packaging.md) explains why).
- Windows support.
