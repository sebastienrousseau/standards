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

## Packages and recipes

`pkg/` holds one recipe per format. `make pkg` installs the command into
a staging tree (the `install` contract above, plus the licences), packs
it as `standards-sync-<version>-unix.tar.gz`, byte-identical for the same
`SOURCE_DATE_EPOCH`, and renders each recipe against that tarball's URL
and SHA-256 into `build/pkg/`. Nothing generated is committed.

| Format | Recipe | Built and installed in CI on | Attached to each release |
| :--- | :--- | :--- | :--- |
| Debian, Ubuntu | `pkg/deb/control`, `copyright` | Ubuntu, with `apt` | `standards-sync_<version>-1_all.deb` |
| Fedora, RHEL | `pkg/rpm/standards-sync.spec` | Fedora 44, with `rpmbuild` and `dnf` | the `.noarch.rpm` and the spec |
| Arch (AUR) | `pkg/aur/PKGBUILD`, `.SRCINFO` | Arch, with `makepkg` and `pacman`; `.SRCINFO` must match `makepkg --printsrcinfo` | `PKGBUILD`, `SRCINFO` |
| Homebrew | `pkg/brew/standards-sync.rb` | macOS, `brew install` and `brew test` | `standards-sync.rb` |
| Nix | `pkg/nix/package.nix` | nixpkgs 26.05, `nix-build` | `standards-sync.nix` |

The rendered recipes point at the release's own tarball, so a packager
can take them from the release page as they are.

## What is not provided

There is no container image: the command edits files in the user's home
directory and their workspace, so a container would need the home
directory mounted to do anything, and would add nothing a package does
not. There is no frozen binary either: the command is a single Python
file that runs on the system `python3`.
