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

`SHA256SUMS` is signed. From 0.0.5, the release workflow signs it with
Sigstore (keyless, tied to the workflow run) as `SHA256SUMS.sigstore.json`:

```bash
cosign verify-blob SHA256SUMS --bundle SHA256SUMS.sigstore.json \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  --certificate-identity-regexp '^https://github.com/sebastienrousseau/standards/\.github/workflows/release\.yml@refs/tags/v'
```

Releases 0.0.1 to 0.0.4 carry `SHA256SUMS.sig` instead, signed afterwards
with the maintainer's SSH key from `KEYS.asc`:

```bash
ssh-keygen -Y verify -f KEYS.asc -I sebastienrousseau@users.noreply.github.com \
  -n file -s SHA256SUMS.sig < SHA256SUMS
```

Each asset of 0.0.3 and later also carries a build provenance
attestation (SLSA), made by the release workflow. The Sigstore bundle is
attached as `standards-sync-<version>.intoto.jsonl`, and GitHub serves it
too:

```bash
gh attestation verify standards_sync-0.0.3.tar.gz --repo sebastienrousseau/standards
gh attestation verify standards_sync-0.0.3.tar.gz --repo sebastienrousseau/standards \
  --bundle standards-sync-0.0.3.intoto.jsonl
```

The CycloneDX SBOM, `standards-sync.cdx.json`, lists the locked
dependency tree the release was built and tested with.
