<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau -->
<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

# Development

## Setup

You need [uv](https://docs.astral.sh/uv/), Node.js (for markdownlint),
`git` and, for the workflow lint, [actionlint](https://github.com/rhysd/actionlint).
With mise: `mise use uv node actionlint`. Then:

```bash
uv sync --frozen
make help
```

The dev container (`.devcontainer/`) boots with the same tools.

## The gate

`make check` runs every check CI runs, apart from the external link check
(`make linkcheck`, which needs lychee and the network):

| Target | What it checks |
| :--- | :--- |
| `make lint` | ruff lint and format, complexity ceilings, docs consistency, codespell, REUSE, markdownlint, actionlint, em dashes |
| `make test` | the unit tests, with branch coverage at 95 percent or more |
| `make fuzz` | property-based fuzzing and its regression corpus |
| `make docs` | the manual, built strict, and the author link on every page |
| `make api` | no breaking change to `sync.py`'s public API since the last release |
| `make audit` | pip-audit over every locked dependency |
| `make reproducible` | two builds give byte-identical wheel and sdist |

Install hooks run the same checks before each commit:
`uvx pre-commit install` (the config is `.pre-commit-config.yaml`).

## Tests

- `tests/`: behaviour of `scripts/sync.py`, against temporary git
  repositories and a temporary `HOME`; and of the check scripts.
- `fuzz/`: Hypothesis properties. Each `@example` is a corpus entry,
  replayed on every run; add one for every bug a fuzz run finds.

## Complexity

Every function stays within the ceilings of [AGENTS.md](AGENTS.md)
section 0: cyclomatic 10, cognitive 15, Halstead difficulty 30, 60 lines,
and 500 lines per file. `complexity-baseline.json` lists any function
allowed over a ceiling. It is empty, and may only shrink.

## Changing a standard

Edit the file here, on the `feat/v<next-version>` branch, and record the
change in `CHANGELOG.md`. The post-commit hook (`standards-sync
--install-hooks`) copies it to the dotfiles; `~/Code` links here already.
If `README-TEMPLATE.md` gains or loses a `##` heading, this repository's
README must follow: `make lint` fails until it does.

## Releasing

Releases are cut from `main` by pushing a signed tag; see
[CONTRIBUTING.md](CONTRIBUTING.md). The release workflow checks the tag,
builds and attests the assets, and publishes the release. Run it with
`workflow_dispatch` and `dry-run` to see the notes and assets first.
