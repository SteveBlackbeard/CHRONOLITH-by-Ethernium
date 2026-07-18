# Evidence

Measured results and a verifiable artifact, so the claims in this repository can
be checked rather than believed. Everything here is reproducible.

## 1. A real Bitcoin-anchored DNA state (verifiable by anyone)

`ANCHOR_3647dd737ee8.json` is a sovereign anchor record for a Continuity Pro
project; `ANCHOR_3647dd737ee8.json.ots` is its OpenTimestamps proof.

**Confirmed in Bitcoin block 958484.**

Verify it yourself — you do not need to trust this repository, its author, or
GitHub. You need only the two files and access to Bitcoin:

```bash
pip install "ethernium-continuity-pro[anchor]"
continuity-pro verify-anchor --proof docs/evidence/ANCHOR_3647dd737ee8.json.ots
# -> [✔] ANCHOR CONFIRMED on Bitcoin: confirmed in Bitcoin block 958484
```

Or with the reference client, independently of this project:

```bash
ots verify docs/evidence/ANCHOR_3647dd737ee8.json.ots
```

### What this proves — and what it does not

| Proves | Does not prove |
| :--- | :--- |
| The anchored data existed **before** that block was mined. | **Who** created it (the Ed25519 signature covers that). |
| Any single-byte change breaks the proof (integrity). | That the content is correct, original, or true. |
| The timestamp cannot be forged backwards without rewriting Bitcoin. | That it was created *at* that moment (it may be older). |

Its role here is specific: the DNA transparency chain is signed, so a holder of
the private key could otherwise roll the project back to an older
internally-consistent state and re-sign it. They cannot produce a Bitcoin
timestamp for a state they deleted. **The anchor is what closes the rollback
gap** — see [SECURITY.md](../../continuity-pro/SECURITY.md).

## 2. Guardian performance (`check`)

Cold run versus a warm run using the mtime+size incremental hash cache:

| Documents | Cold | Warm (cached) |
| ---: | ---: | ---: |
| 50 | ~0.6 s | ~0.5 s |
| 250 | ~1.4 s | ~0.6 s |
| 1000 | ~3.5 s | ~0.9 s |

The cache is worth 2.5–4× on repeat runs, which is what keeps a pre-push hook
tolerable on a large repository. Reproduce with `python scripts/redteam.py`.

## 3. Adversarial results

`scripts/redteam.py` attempts to defeat each guarantee and reports **BREAK** when
an attack succeeds. Current status: **11/11 guarantees hold**, covering baseline
forgery by checksum recomputation, silent content edits, key-swapped forks,
chain truncation, rollback, inclusion-proof forgery for a non-member file,
sealed-ciphertext tampering, and wrong-passphrase vault access.

Two results are reported as **inherent limits**, not defenses: a key-swapped fork
and a rollback both pass a plain `verify`. They are mitigated by
`verify --expect-fingerprint` and `verify --strict` (which requires a confirmed
anchor), and `verify` says so on screen rather than overclaiming.

## 4. What running it for real caught

The anchor above was produced by a person on an ordinary Windows machine, and
that single real run surfaced two defects that 63 unit tests and the 11-attack
red-team had missed:

1. `verify-anchor` crashed into the `ots` CLI (broken on Windows by a
   python-bitcoinlib/OpenSSL issue) because the fallback only triggered on
   "not installed", never on a runtime crash.
2. The ASCII banner had dropped letters and a hard-coded stale version.

Both are fixed. This is recorded because it is the honest argument for the
"one external user" rule in [BUILD_DISCIPLINE.md](../../BUILD_DISCIPLINE.md):
tests prove what you thought to ask; a real run proves what you forgot.
