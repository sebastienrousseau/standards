<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau -->
<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

# Security Policy

## Reporting a Vulnerability

If you discover a security issue or vulnerability in these specifications, please report it privately:

- Through GitHub Security Advisories: [Report a vulnerability](https://github.com/sebastienrousseau/standards/security/advisories/new)
- Or by email to `sebastian.rousseau@gmail.com`

Please do not disclose security issues publicly until they have been evaluated and addressed.

You will get an acknowledgement within 7 days, and an assessment with a
plan or a fix within 30 days. The advisory credits you unless you ask
otherwise.

## Supported versions

Only the latest release is supported; a fix ships as the next `0.0.x`.

## Scope

`standards-sync` writes the five standard files into `~/Code` and the
dotfiles, and git hooks into this checkout. In scope: anything that makes
it write outside those paths, overwrite a file edited in place without
`--force`, or run code it was not asked to. A rule in the standards that
leads an agent to an unsafe action (leaking a secret, publishing without
review) is in scope too.

## How the repository is protected

- Commits and release tags are SSH-signed; the keys are in `KEYS.asc`.
- Every GitHub Action is pinned by commit SHA and updated by Dependabot.
- Dependencies are locked in `uv.lock` and audited with pip-audit on every
  push; CodeQL, secret scanning with push protection, and the OpenSSF
  Scorecard run on `main`.
- Release assets carry SHA-256 sums, an SBOM and build provenance
  ([docs/VERIFYING.md](docs/VERIFYING.md)).
