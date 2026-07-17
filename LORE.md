# The Ethernium Lore

> **This document is narrative, not specification.** It is the story and the
> metaphors behind the names you'll see in the code — "DNA", "nucleotides",
> "sovereign", "the chosen ones", "Project Soul". None of it is a technical
> claim. For what the software actually does and guarantees, read the
> [README](./README.md) and [continuity-pro/SOVEREIGN_SECURITY.md](./continuity-pro/SOVEREIGN_SECURITY.md).
> The lore is kept here, deliberately apart, so the engineering docs can stay
> plain and honest.

---

## Why the mythology exists

Ethernium began as a personal project about a simple frustration: an AI
assistant that forgets everything between sessions, and a codebase whose intent
quietly erodes as different models and different people touch it. The mythology
is a memory aid, not a marketing skin — giving the moving parts vivid names made
them easier to reason about and to keep faithful to over long stretches of work.

So the lore is a lens. Underneath every poetic term is an ordinary engineering
idea.

## The metaphor map

| Lore term | What it actually is |
| :--- | :--- |
| **DNA / Genome** | The set of tracked files whose hashes form a Merkle tree. |
| **Nucleotide** | One tracked file (a Merkle leaf). |
| **Crystallization** | Computing the Merkle root and recording it as the baseline. |
| **DNA drift** | The current Merkle root no longer matches the recorded baseline. |
| **Sovereign** | The holder of the Ed25519 signing key for this repository. |
| **The Chosen Ones** | Additional public keys authorized to sign attestations. |
| **Socratic Firewall** | The fail-closed check that halts on drift, secrets, or a bad signature. |
| **Project Soul** | The canonical context documents (`PROJECT_CONTEXT.md`, the state, the roadmap). |
| **Transparency chain** | An append-only, hash-linked log of every crystallization. |
| **External witness** | A Bitcoin (OpenTimestamps) timestamp over the chain head. |

## The three editions, as characters

- **Lite** — the scribe. Minimal, fast, keeps an honest signed record of the
  lineage for handoffs.
- **Pro** — the guardian. The full border control: signed baselines, the
  transparency chain, inclusion proofs, encryption, key rotation, and the
  Bitcoin anchor.
- **Omega** — the cartographer. Builds a searchable cognitive map (RAG) of the
  project's meaning, not just its hashes.

## A note on tone

You will find grand language in older documents and banners. Treat it as
flavor. The project's actual promises are deliberately modest and testable, and
they live in the engineering docs — where a claim is only made if a test or a
command can back it up. If the lore and the spec ever disagree, the spec wins.
