# Build Discipline

How this ecosystem decides what to build. This exists because building with AI
removes the friction that used to force prioritization: the assistant will
competently build almost anything you ask, so the discipline has to be explicit.
This is drift-prevention applied to the roadmap, not just the code.

## The thesis test (apply to every proposed feature)

> Does this reinforce the product thesis, or betray it?

The thesis is: **sovereign, local-first, verifiable without trusting anyone.**

- A Bitcoin anchor *reinforces* it (external witness, no trusted party) → build.
- A certificate authority *betrays* it (a central party you must trust) → do not
  build, no matter how much it would "solve" the fork problem.

"Is it overengineering?" is the wrong question. "Does it serve the thesis?" is
the right one.

## Definition of done: verifiable = done

A change is not done until a test, a command, or a benchmark backs its claim.
Concretely, the gates are:

- unit tests green;
- `install_audit` / `audit_all` green (it installs clean and runs);
- for anything security-relevant, `redteam` green.

Corollary: **if it cannot be verified here, it is not built here.** Unverifiable
crypto or features are recorded as a TODO with the exact approach, not shipped
blind. (Example: the frictionless anchor below.)

## One external user before new features

The largest unknown is not technical — it is whether anyone but the author needs
this. Prefer putting the current build in one external person's hands over adding
a feature. That single user surfaces assumptions neither the author nor the AI
can see from inside.

## Deliberately NOT built (and why) — the anti-scope-creep ledger

Recorded so these are not re-litigated every session:

| Not built | Why |
| :--- | :--- |
| Certificate authority / keyless (Fulcio) identity | Betrays the no-trusted-party thesis; heavy infrastructure. |
| Mandatory-anchor enforcement | Kept optional; the mitigation (`verify --strict`) is enough. |
| Post-quantum (ML-DSA) signer | Premature; `sig_alg` agility tags already reserve the slot. |
| HSM / hardware-key support | Disproportionate to the scale. |
| Verification / analytics dashboard | Roadmap defers dashboards; a CLI `verify --json` covers CI. |
| Shared base package across the three editions | Would break standalone PyPI publishing; parity test governs the vendoring instead. |

## Done — with the verification handoff completed

- **Frictionless Bitcoin anchor — built and VERIFIED end to end.** The `ots` CLI
  hits a python-bitcoinlib / OpenSSL DLL issue on Windows, so `anchor` prefers
  the `opentimestamps` Python library (optional `[anchor]` extra) and falls back
  to the CLI, then to a local record. Everything except the live calendar
  submission is unit-tested; that one step was isolated and handed to the
  operator rather than shipped as a silent claim.

  **The handoff was executed and passed** on a networked Windows machine:
  `anchor` stamped via the library (one calendar reached), and hours later
  `verify-anchor` reported **`confirmed in Bitcoin block 958484`**. The external
  witness is therefore not a design claim — it is a checked fact, and the
  rollback limitation it mitigates is closed in practice, not only on paper.

  Two real defects surfaced only because a human ran it for real: `verify-anchor`
  crashed into the broken CLI (the fallback only triggered on "not installed",
  not on a runtime crash), and the ASCII banner had dropped letters. Both fixed.
  This is the strongest argument for the "one external user" rule above.
