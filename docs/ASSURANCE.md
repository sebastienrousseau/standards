<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau -->
<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

# Security assurance case

Why the project's security requirements are met: what is protected, from
whom, where the trust boundaries are, and how the design and code counter
the weaknesses that matter here.

## What the project produces

1. **The standards**: five Markdown files that people and AI agents follow
   when they change any repository in the portfolio.
2. **standards-sync**: one Python file (`scripts/sync.py`, standard library
   only) that copies those five files between this repository, `~/Code`
   and the dotfiles copies, and checks them for drift.

## Security requirements

- **R1. Integrity of the rules.** A change to a standard reaches
  `~/Code` or the dotfiles only after review in this repository. Agents
  read these files as instructions, so a tampered rule is a prompt
  injection across every repository.
- **R2. No lost work.** `standards-sync` never silently overwrites a file
  someone edited in place.
- **R3. Contained writes.** `standards-sync` writes only the five standard
  files, into the target directories it lists, and the git hooks of this
  checkout.
- **R4. Authentic releases.** A user can verify that a release came from
  this repository's workflow and the maintainer.

## Threat model

| Threat | Requirement |
| :--- | :--- |
| A malicious or mistaken change to a standard, by a contributor or a compromised dependency of the tooling | R1, R4 |
| A push overwriting a newer edit in `~/Code` or the dotfiles (this happened once; [ADR 0003](adr/0003-keep-edits-made-in-place.md)) | R2 |
| An environment variable or target path that sends writes elsewhere | R3 |
| A tampered release asset or download | R4 |
| A compromised GitHub Action or dev dependency | R1, R4 |

Out of scope: an attacker who already runs code as the user. They can edit
the targets, the hooks and the clone directly.

## Trust boundaries

1. **Pull request to `main`.** Everything outside the repository (a
   contributor's branch, a Dependabot update) crosses into the canonical
   source only through a pull request that passes the full CI gate and
   the maintainer's review. `main` requires the `validate` check, and
   CODEOWNERS names the maintainer for every file.
2. **The user's environment to standards-sync.** `STANDARDS_REPO`,
   `STANDARDS_TARGETS`, the home directory and the files in it are
   controlled by the user running the command and are trusted as such.
3. **Release workflow to the user.** Releases leave through GitHub over
   HTTPS, with checksums, signatures and provenance the user can check
   ([Verifying releases](VERIFYING.md)).

## Secure design principles applied

- **Least privilege.** Workflows run with `contents: read` by default;
  only the jobs that need it get `pages`, `id-token`, `attestations` or
  `contents: write`. Checkouts do not persist credentials.
- **Fail-safe defaults.** A push keeps any target content it does not
  recognise as a published version and exits 1; overwriting it needs
  `--force` (R2). A link to the source is left alone.
- **Economy of mechanism.** One standard-library Python file, no runtime
  dependencies, every function under the complexity ceilings.
- **Complete mediation.** Every change to `main`, including dependency
  updates, goes through the same pull request gate (R1).
- **Open design.** Everything, including the release and signing
  process, is public and documented.

## Common weaknesses countered

| Weakness | How it is countered |
| :--- | :--- |
| Path traversal or writes outside the targets (CWE-22, CWE-73) | File names come only from the fixed `STANDARD_FILES` list, never from input; targets are the directories the user configured. |
| OS command injection (CWE-78) | `git` is the only command run, with a fixed argument list and no shell. |
| Silent loss of an edit made in place | Content is compared with every version this repository committed (git blob ids) before any overwrite. |
| Following a symbolic link (CWE-59) | A target that links to the source is detected and left alone. A target file that links elsewhere is written through, which only someone who can already write the user's files can arrange (trust boundary 2). |
| Unsafe error handling | Errors are caught by type (`OSError`), reported per file, and never silenced; ruff forbids blind `except`. |
| Supply-chain substitution (CWE-494, CWE-829) | Actions pinned by commit SHA; dependencies locked in `uv.lock`, constrained away from advised versions, audited with OSV and dependency review; signed tags, Sigstore-signed checksums and SLSA provenance on releases. |

## Evidence

- Tests of every overwrite decision and error path at 99 percent branch
  coverage; property-based and coverage-guided fuzzing of the inputs
  (`fuzz/`); an end-to-end smoke test on the minimum Python.
- CodeQL and ruff's security rules on every push; OpenSSF Scorecard
  weekly and on every push to `main`.
- [SECURITY.md](https://github.com/sebastienrousseau/standards/blob/main/SECURITY.md)
  for reporting, and [Verifying releases](VERIFYING.md) for checking what
  you download.
