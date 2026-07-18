# Getting Started

Five minutes, one project, no lore. Every command below was run before it was
written here.

## Which edition

| You want | Edition | Install |
| :--- | :--- | :--- |
| Detect when your docs and code drift apart | **Lite** | `pip install chronolith-lite` |
| Cryptographic proof a third party can check | **Pro** | `pip install chronolith-pro` |
| RAG and cognitive mapping over the corpus | **Omega** | `pip install chronolith-omega` |

Start with Lite. It is the whole idea in four commands, and Pro is a superset —
nothing you learn here is thrown away.

Python 3.10+.

## 1. Crystallize a project

From the root of a git repository:

```bash
chronolith-lite init
```

This writes the memory core and installs a push hook. Your documentation now has
a Merkle root: one hash covering every tracked file, keyed by its path.

## 2. Confirm the state is sound

```bash
chronolith-lite check
```

```
┌─────────────────── DNA Guardian ────────────────────┐
│ Parity Confirmed: Merkle Root `9e757152ee2569b4...` │
└─────────────────────────────────────────────────────┘
```

## 3. Break it on purpose

This is the part worth doing. Edit any tracked markdown file — add one line —
and run `check` again:

```
[!] DNA DRIFT DETECTED:
    Current:  929f8c535812d490
    Expected: 9e757152ee2569b4
```

Exit code `1`. Because the leaves are **path-bound**, a rename or swapping the
contents of two files changes the root just as a text edit does.

## 4. Accept a change you meant to make

In a terminal, `check` asks you to confirm, then re-crystallizes the baseline to
the new root. In CI — anywhere without a TTY — it never asks: it aborts with
exit `1`. Fail-closed is the default, so a drifted tree cannot slip through a
pipeline because nobody was watching.

## 5. Prove it to someone who does not trust you (Pro)

```bash
pip install chronolith-pro
chronolith-pro sovereign-init     # Ed25519 signing + X25519 encryption keys
chronolith-pro check              # baseline is now really signed
chronolith-pro verify             # read-only; writes nothing
```

`verify` is the one command a skeptic runs. It recomputes the root, checks it
against the signed baseline, verifies the Ed25519 signature and the whole
append-only transparency chain, and reports the Bitcoin anchor:

```
  merkle root vs baseline: MATCH
  transparency chain: intact
  chain head vs baseline: bound
```

It also tells you what it did **not** prove:

```
  ! authenticity NOT verified: no --expect-fingerprint. This proves internal
    integrity only; a fork that swapped the whole key set would still pass.
```

Pass `--expect-fingerprint` with a fingerprint you obtained out of band to close
that gap. The tool states its own limits rather than letting you assume more
than it checked.

## 6. Anchor to Bitcoin (Pro)

```bash
chronolith-pro anchor
```

Timestamps the transparency-chain head via OpenTimestamps, so a third party can
confirm your DNA existed at a given time without trusting you. A real one is
committed in [`docs/evidence/`](./docs/evidence/) — Bitcoin block 958484.

Anchors confirm asynchronously; `chronolith-pro upgrade-anchors` completes any
that are still pending and is a no-op once confirmed.

## Running the tests

Use the audit runner, not bare `pytest`:

```bash
python scripts/audit_all.py
```

The three editions each vendor a package named `chronolith`, so a single pytest
process serves one edition's code to another edition's tests. `audit_all.py`
runs each in an isolated process, which is what CI does per job.

## Where to go next

- [README.md](./README.md) — full command reference
- [HOW_TO_USE_IT.md](./HOW_TO_USE_IT.md) — the industrial guide
- [chronolith-pro/SOVEREIGN_SECURITY.md](./chronolith-pro/SOVEREIGN_SECURITY.md)
  — the cryptography, and the two limits that are inherent to it
- [CASE_STUDY_DRIFT.md](./CASE_STUDY_DRIFT.md) — why this exists
