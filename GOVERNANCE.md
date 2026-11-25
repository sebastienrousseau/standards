<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau -->
<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

# Governance

Sebastien Rousseau maintains this repository and decides what the
standards say. Anyone may propose a change by issue or pull request.

- **Decisions** are made in pull requests. A change to a rule says what
  changed and why in `CHANGELOG.md`, and a decision that will be
  questioned later gets an ADR in `docs/adr/`.
- **Merging** into `main` and tagging a release are the maintainer's
  alone. Agents prepare branches, pull requests and release scripts, and
  never merge or tag ([AGENTS.md](AGENTS.md) section 4).
- **Releases** follow [AGENTS.md](AGENTS.md) section 3.
- **Conduct** is covered by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Roles and responsibilities

| Role | Who | Responsibilities |
| :--- | :--- | :--- |
| Maintainer | Sebastien Rousseau ([@sebastienrousseau](https://github.com/sebastienrousseau)) | Decides what the standards say; reviews and merges pull requests; signs and tags releases; answers issues and security reports ([SECURITY.md](SECURITY.md)); keeps the repository at zero open alerts and issues ([AGENTS.md](AGENTS.md) section 0). |
| Contributor | Anyone | Proposes changes by issue or pull request, following [CONTRIBUTING.md](CONTRIBUTING.md). |
| Agent | AI assistants working for the maintainer | Prepare branches, commits and pull requests under [AGENTS.md](AGENTS.md), attributed with `Assisted-by:`; never merge, tag or publish on their own. |

## Continuity

The project has one maintainer, so its bus factor is 1, and no second
person yet holds the access needed to merge, release or answer reports.
This is a known gap; an arrangement for it will be recorded here when it
exists.

### When a second maintainer joins

The maintainer invites them, and they are given, in one change recorded
in this file:

- the GitHub `maintain` role on this repository and a line in
  `.github/CODEOWNERS`;
- their SSH signing key in `KEYS.asc`, so their tags and commits verify;
- owner on the [PyPI project](https://pypi.org/project/standards-sync/),
  co-maintainer of the [AUR package](https://aur.archlinux.org/packages/standards-sync),
  write access to the [Homebrew tap](https://github.com/sebastienrousseau/homebrew-tap),
  and editor on the [OpenSSF Best Practices entry](https://www.bestpractices.dev/projects/17104);
- the security contact in `SECURITY.md`, alongside the maintainer.

From then on every pull request into `main` needs one approving review
from the maintainer who did not write it, enforced by a branch ruleset.
