<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau -->
<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

# standards

This repository holds the rules every repository by Sebastien Rousseau
follows, and `standards-sync`, the command that keeps every copy of them
identical.

## The standards

| File | What it governs |
| :--- | :--- |
| [AGENTS.md](AGENTS.md) | How an agent or a person works in a repository: hygiene first, invariants, the definition of done, versioning, commits, compliance tiers. |
| [GEMINI.md](GEMINI.md) | The pointer file Gemini and other agents read first. |
| [Repository gold standard](REPO-STANDARD.md) | The eight-category scorecard and the phases that reach 10 in each. |
| [README template](README-TEMPLATE.md) | The layout of every primary README. |
| [PR template](PR-TEMPLATE.md) | The shape of every pull request description. |

## Where the copies live

The files in this repository are the canonical source. `~/Code` links to
them, and the dotfiles carry copies for machines without a clone. A rule is
changed here, in a pull request, and `standards-sync` carries it to the
copies; see [Architecture](ARCHITECTURE.md).

## standards-sync

```bash
standards-sync --check   # report drift, change nothing
standards-sync --push    # copy this repository's files to every target
standards-sync --pull    # adopt an edit made in ~/Code, then push it on
```

[Policies and stability](POLICIES.md) lists what each release promises,
[Packaging](packaging.md) is for anyone packaging the command, and
[Verifying releases](VERIFYING.md) checks a tag or a download.
