# Sovereign Security (Chronolith Pro)

Pro turns the DNA guardian from a *badge* into a **verifiable cryptographic
lineage**. This document covers the sovereign commands, what each one protects
against, and the honest limits of the design.

> **TL;DR** — `sovereign-init` once, then every `check` signs the DNA baseline
> with Ed25519 and appends to an append-only transparency chain. `prove` lets
> anyone verify a single file belongs to the DNA; `attest` records who vouched
> for what; the vault encrypts secrets and protects the key at rest.

---

## The guarantee ladder

| Layer | Command | What it makes impossible |
| :--- | :--- | :--- |
| Content integrity | `check` | An edited document that keeps the same Merkle root (leaves are path-bound). |
| Baseline authenticity | `sovereign-init` + `check` | Forging the baseline: without the private key it cannot be re-signed. A recomputed SHA-256 checksum is rejected by the Ed25519 layer. |
| History integrity | `chain` | Rewriting the past: every crystallization is hash-linked and signed in `.chronolith/dna_chain.jsonl`. |
| Per-file proof | `prove` / `verify-proof` | Claiming a file belongs to the DNA when it doesn't — verified in O(log n) without rehashing the repo. |
| Provenance | `attest` / `verify-attest` | Anonymous or forged authorship: an attestation names the signing key and fails if content changed. |
| Key protection | `sovereign-init --encrypt` | Reading the private key off disk: it is wrapped with scrypt + ChaCha20-Poly1305. |
| Chronolith | `sovereign-rotate` | Losing verifiability after a key change: the old key signs the hand-off to the new one. |
| **External witness** | `anchor` / `verify-anchor` | Trusting the operator: a Bitcoin timestamp over the chain head proves the state existed at a confirmed time to a party who trusts *no one* — and cannot be forged even with a stolen key. |
| Secrecy | `seal_context` (API) | Reading sealed context: real X25519 + ChaCha20-Poly1305 encryption, not obfuscation. |

---

## Quick start

```bash
# 1. Forge the sovereign identity (Ed25519 signing + X25519 encryption keys).
#    Add --encrypt to protect the private keys with CHRONOLITH_PASSPHRASE.
chronolith-pro sovereign-init --encrypt

# 2. Crystallize + sign the baseline (this is your normal guardian run).
chronolith-pro check --strict

# 3. Inspect and verify the transparency chain.
chronolith-pro chain

# 4. Prove one file belongs to the DNA, then verify the proof.
chronolith-pro prove --file README.md --output readme.proof.json
chronolith-pro verify-proof --proof readme.proof.json

# 5. Attest authorship of a document, and verify it later.
chronolith-pro attest --file HANDOFF.md --output handoff.att.json
chronolith-pro verify-attest --attestation handoff.att.json

# 6. Anchor the chain head in Bitcoin (external witness).
#    Needs the OpenTimestamps client: pip install opentimestamps-client
chronolith-pro anchor
chronolith-pro verify-anchor --proof .chronolith/anchors/ANCHOR_<hash>.json.ots

# 7. Third-party verification — one command a skeptic runs. Prints the key
#    fingerprint; pin the one you published out of band to defeat key-swap.
chronolith-pro verify --expect-fingerprint "SHA256:...your published fingerprint..."
```

### Trust bootstrapping (publishing your key fingerprint)

The repo ships `sovereign.pub`, but a verifier needs to know it's really yours
and not one an attacker swapped in on a fork. Run `verify` (or `status`) to read
your **key fingerprint** (`SHA256:...`), publish it somewhere a forger can't
control — your README, profile, a talk — and anyone can then pin it with
`verify --expect-fingerprint`. This is the SSH-host-key / Signal-safety-number
model: no certificate authority, just an out-of-band human check.

The private keys live in `.chronolith/keys/` and are git-ignored (`*.priv`).
Publish `sovereign.pub` so others can verify your signatures.

---

## Key management

- **Non-interactive unlock.** An encrypted vault is opened via the
  `CHRONOLITH_PASSPHRASE` environment variable, so CI and pre-push hooks keep
  working. Without it, the guardian runs in **verify-only** mode: it still
  validates existing signatures but cannot sign, and it *postpones* new chain
  entries rather than poisoning the chain with unsigned ones.
- **Rotation.** `sovereign-rotate` generates a new key and has the **old key
  sign the hand-off** into `.chronolith/keys/rotations.jsonl`. Verification walks
  this log, so baselines and chain entries signed by retired keys still verify —
  and a forged hand-off stops the trust walk cold.
- **Compromise recovery.** If a key leaks: `sovereign-rotate`, then `check` to
  re-sign the baseline with the new key. History remains verifiable; new signing
  power moves to the new key.

---

## Threat model — what it does and does NOT stop

**Stops:** silent document drift, baseline forgery by checksum recomputation,
history rewrites, cross-file content swaps, unauthorized attestations, reading an
at-rest key, and reading sealed context without the recipient key.

**Does not stop (by design / honest limits):**

1. **A live-compromised machine.** If an attacker controls the process *while the
   passphrase is in memory*, they can sign as you. Mitigation: keep the vault
   encrypted, scope `CHRONOLITH_PASSPHRASE` to trusted CI, rotate on suspicion —
   and note that `anchor` gives forward-security here: an attacker with a stolen
   key still cannot forge a *past* Bitcoin timestamp, so anchored history cannot
   be rewritten after the fact.
2. **Post-quantum adversaries.** Ed25519 is not post-quantum. Mitigation:
   crypto-agility — every signed record carries a `sig_alg` tag, so a future
   ML-DSA (Dilithium) signer drops in without a format break; meanwhile the
   SHA-256 Merkle chain and optional Bitcoin anchoring are hash-based and already
   PQ-resistant, giving a second, independent line of integrity evidence.
3. **Trust bootstrapping.** Verifiers must obtain the authentic key fingerprint
   out of band (the usual public-key distribution problem). Mitigated, not
   eliminated, by `verify --expect-fingerprint`: you publish the `SHA256:...`
   fingerprint where a forger can't reach, and a skeptic pins it. There is no
   certificate authority — that is a deliberate scope choice, not an oversight.

---

## Format & crypto-agility

Signed records (STATE, chain entries, attestations) carry `sig_alg` and the
signer's public key **inside the signed payload**, so neither can be swapped
after the fact. The checksum (`signature`) covers content only and excludes all
signature-family fields, so layering Ed25519 on top never trips a false tamper
alarm. This is what lets the algorithm evolve without breaking existing
baselines.
