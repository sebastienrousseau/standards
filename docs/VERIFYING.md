<!-- SPDX-FileCopyrightText: 2026 Sebastien Rousseau -->
<!-- SPDX-License-Identifier: Apache-2.0 OR MIT -->

# Verifying releases

## Signed tags and commits

Tags and commits are signed with SSH keys. `KEYS.asc` lists the keys, in
git's allowed-signers format; they are the signing keys registered on the
`sebastienrousseau` GitHub account.

```bash
git -c gpg.ssh.allowedSignersFile=KEYS.asc tag -v v0.0.3
git -c gpg.ssh.allowedSignersFile=KEYS.asc verify-commit HEAD
```

Both print `Good "git" signature for sebastienrousseau@users.noreply.github.com`.

## Release assets

Every release lists the SHA-256 of each asset in its notes and in
`SHA256SUMS`:

```bash
shasum -a 256 -c SHA256SUMS
```

Each asset also carries a build provenance attestation (SLSA), made by
the release workflow:

```bash
gh attestation verify standards_sync-0.0.3.tar.gz --repo sebastienrousseau/standards
```

The CycloneDX SBOM, `standards-sync.cdx.json`, lists the locked
dependency tree the release was built and tested with.
