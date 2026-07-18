# Security Policy — Chronolith Pro

Chronolith Pro is a cryptographic integrity layer for a project's canonical
documents. This policy states honestly what it protects, what it does not, and
how to report issues. The full design is in
[SOVEREIGN_SECURITY.md](./SOVEREIGN_SECURITY.md).

## Supported versions

The latest `3.x` release receives security fixes. Chronolith Pro is pre-1.0 in
API-stability terms despite the `3.x` line; the on-disk formats carry a
`sig_alg` / `leaf_format` tag so they can evolve without silent breakage.

## Reporting a vulnerability

Report privately via a GitHub security advisory on the repository, or contact
**@Steveblackbeard**. Please do not open a public issue for an unfixed
vulnerability. Include a description and reproduction steps. There is no
bug-bounty program.

## What is protected

- **Baseline forgery** — the Ed25519 signature cannot be recomputed without the
  private key; a recomputed SHA-256 checksum is rejected.
- **Silent content drift** — path-bound Merkle leaves detect edits, renames, and
  cross-file content swaps; `check` fails closed against a signed baseline.
- **History rewrite / truncation** — the transparency chain is hash-linked and
  signed, and the chain head is bound to the baseline, so dropped entries are
  detected.
- **Sealed context** — X25519 + ChaCha20-Poly1305; tampering and wrong-recipient
  are detected.
- **Key at rest** — optional scrypt + ChaCha20-Poly1305 vault.

## What is NOT protected (inherent limits, by design)

These are documented limits, not bugs. `verify` reports them rather than
overclaiming, and `verify --strict` refuses to pass without their mitigations.

1. **A key-swapped fork.** Plain `verify` proves internal integrity, not
   authenticity: a fork that replaces the whole key set and re-signs will pass.
   *Mitigation:* publish your key fingerprint out of band and have verifiers pin
   it with `verify --expect-fingerprint`.
2. **Rollback to an older signed state.** Without an external witness, reverting
   to an earlier internally-consistent baseline+chain passes `verify`.
   *Mitigation:* `anchor` timestamps the chain head into Bitcoin; `verify
   --strict` requires a confirmed anchor. **Verified in practice:** a real anchor
   was confirmed as `confirmed in Bitcoin block 958484`, so this mitigation is a
   checked fact, not a design claim.
3. **A live-compromised machine.** An attacker controlling the process while the
   passphrase is in memory can sign as the sovereign. *Mitigation:* keep the
   vault encrypted, scope `CHRONOLITH_PASSPHRASE`, rotate on suspicion. Anchored
   history still cannot be rewritten after the fact.
4. **Post-quantum adversaries.** Ed25519 is not post-quantum. *Mitigation:*
   `sig_alg` crypto-agility for a future ML-DSA signer; the SHA-256 Merkle chain
   and Bitcoin anchor are hash-based and already PQ-resistant.
5. **Trust bootstrapping.** There is no certificate authority; obtaining the
   authentic fingerprint is an out-of-band step. Deliberate scope choice.

## Assurance

The guarantees above are exercised by an adversarial test suite
(`scripts/redteam.py`) and per-guarantee unit tests. No custom cryptographic
primitives are implemented — only standard constructions from the `cryptography`
library. An independent security review has **not** been performed; treat
"enterprise crypto" as a design goal, not a certification.
