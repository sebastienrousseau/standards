<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau -->
<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

# Deprecations

What `standards-sync` still accepts but will stop accepting, under the
policy in [docs/POLICIES.md](docs/POLICIES.md): each entry keeps working,
with a warning on standard error, until its removal date, and changes in
the first release on or after that date.

| Deprecated | Replacement | Deprecated in | Removal no earlier than |
| :--- | :--- | :--- | :--- |
| Two commands at once (`--check --push`, `--pull --install-hooks`): the first in `--install-hooks`, `--pull`, `--check`, `--push` order runs | Name one command | 0.0.14 (2026-11-25) | 2027-02-23: an error, exit 2 |
| `--force` with a command other than `--push` or `--pull`: ignored | Use `--force` only with `--push` or `--pull` | 0.0.14 (2026-11-25) | 2027-02-23: an error, exit 2 |
