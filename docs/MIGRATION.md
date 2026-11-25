<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau -->
<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

# Migrating

## From copies in ~/Code to links

Older dotfiles installed plain copies of the standards in `~/Code`, and
an edit there could be overwritten by the next push. With a clone at
`~/Code/Public/Other/standards`, `chezmoi apply` from the current dotfiles
replaces each copy with a link into the clone. A copy edited in place is kept and named
instead; adopt it first:

```bash
standards-sync --pull     # copy the edited file into the clone
chezmoi apply             # then link it
standards-sync --check    # every target [OK] or linked
```

## From the vendored script to an installed command

The dotfiles install `scripts/sync.py` as `~/.local/bin/standards-sync`.
To install it from this repository instead, with its manpage and
completions:

```bash
make PREFIX="$HOME/.local" install
```

or as a Python tool:

```bash
uv tool install git+https://github.com/sebastienrousseau/standards
```

With both installed, the first `standards-sync` on `PATH` runs;
`command -v standards-sync` shows which one.

## The release title field

Earlier copies of `REPO-STANDARD.md` told agents to read the release
title from a `title` field of `gh release view --json`. `gh` has no such
field; the release title is `name`. Use `gh release view <tag> --json name,body`.
