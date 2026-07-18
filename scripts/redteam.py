#!/usr/bin/env python3
"""Adversarial red-team + benchmark for Chronolith Pro.

Each scenario ATTEMPTS to defeat a guarantee; a guarantee HOLDS only if the
system rejects the malicious state (or, for the honest limits, refuses to
overclaim). This is written to be able to print BREAK, not just confirm success
— run it after any change to the crypto/guardian path.

    python scripts/redteam.py            # attacks + benchmark
    python scripts/redteam.py --no-bench # attacks only

Two guarantees are INHERENT LIMITS, documented in SOVEREIGN_SECURITY.md and
asserted here as such, not as defenses:
  * a key-swapped fork passes plain `verify` (needs --expect-fingerprint);
  * a rollback to an older signed state passes plain `verify` (needs an anchor).
`verify` is honest about both, and `verify --strict` rejects them.
"""
from __future__ import annotations

import argparse
import base64
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "chronolith-pro" / "chronolith_pro" / "chronolith" / "run_chronolith_cycle.py"
sys.path.insert(0, str(SCRIPT.parent))
import automation_common as ac  # noqa: E402
import sovereign_vault as sv  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def record(name: str, held: bool, detail: str = "") -> None:
    RESULTS.append((name, held, detail))
    print(f"  [{'HELD' if held else '*** BREAK ***'}] {name}" + (f"  ({detail})" if detail else ""))


def run(*args, env=None, root=None):
    e = dict(os.environ)
    e.update(env or {})
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args, "--repo-root", str(root)],
        capture_output=True, text=True, encoding="utf-8", errors="replace", env=e,
    )


def make_repo(n_docs=3, passphrase=None):
    d = Path(tempfile.mkdtemp())
    (d / ".chronolith").mkdir()
    (d / ".chronolith" / "STATE.json").write_text('{"phase":"pro"}', encoding="utf-8")
    for i in range(n_docs):
        (d / f"DOC{i}.md").write_text(f"# Canonical document {i}\ncontent line\n", encoding="utf-8")
    env = {"CHRONOLITH_PASSPHRASE": passphrase} if passphrase else {}
    run(*(["sovereign-init"] + (["--encrypt"] if passphrase else [])), env=env, root=d)
    run("check", "--no-scan-source", env=env, root=d)
    return d, env


def attacks() -> None:
    print("=== ADVERSARIAL CAMPAIGN: Chronolith Pro ===\n")

    # A1: forge baseline by recomputing the SHA-256 checksum (pre-Ed25519 attack).
    d, env = make_repo()
    st = json.loads((d / ".chronolith" / "STATE.json").read_text())
    st["merkle_root"] = "0" * 64
    st["signature"] = ac.sign_state(st)
    (d / ".chronolith" / "STATE.json").write_text(json.dumps(st))
    record("A1 forge baseline via checksum recompute", run("verify", "--no-scan-source", env=env, root=d).returncode != 0)
    shutil.rmtree(d, ignore_errors=True)

    # A2: silent content edit after baseline.
    d, env = make_repo()
    (d / "DOC0.md").write_text("# EVIL\n", encoding="utf-8")
    record("A2 silent content edit", run("verify", "--no-scan-source", env=env, root=d).returncode != 0)
    shutil.rmtree(d, ignore_errors=True)

    # A3: key-swap on a fork. Plain verify must NOT claim authenticity; the
    # fingerprint pin must reject it.
    d, env = make_repo()
    (d / "DOC0.md").write_text("# Attacker's version\n", encoding="utf-8")
    ac.generate_sovereign_keys(d)
    apriv, apub = ac.load_sovereign_keys(d)
    mds = sorted(Path(p) for p in glob.glob(str(d / "*.md")))
    leaves = [ac.path_bound_leaf(m.name, ac.calculate_sha256(m)) for m in mds]
    root = ac.build_merkle_tree(leaves)
    st = json.loads((d / ".chronolith" / "STATE.json").read_text())
    st.update({"merkle_root": root, "leaf_format": ac.LEAF_FORMAT})
    st["signature"] = ac.sign_state(st)
    ac.sovereign_sign_state(st, apriv, apub)
    (d / ".chronolith" / "STATE.json").write_text(json.dumps(st))
    (d / ".chronolith" / "dna_chain.jsonl").unlink(missing_ok=True)
    ac.append_chain_entry(d, root, private_bytes=apriv)
    out = run("verify", "--no-scan-source", env=env, root=d).stdout
    record("A3a key-swap fork: plain verify refuses to claim AUTHENTIC",
           "DNA AUTHENTIC" not in out and "authenticity" in out.lower(),
           "reports INTEGRITY-only (inherent limit: needs a pinned fingerprint)")
    record("A3b key-swap fork rejected by --expect-fingerprint",
           run("verify", "--no-scan-source", "--expect-fingerprint", "SHA256:VICTIM", env=env, root=d).returncode != 0)
    shutil.rmtree(d, ignore_errors=True)

    # A4: chain grows via --accept, then truncation is detected.
    d, env = make_repo()
    for i in range(3):
        (d / "DOC0.md").write_text(f"# rev {i}\n", encoding="utf-8")
        run("check", "--no-scan-source", "--accept", env=env, root=d)
    chain = d / ".chronolith" / "dna_chain.jsonl"
    lines = chain.read_text().splitlines()
    record("A4a chain grows through accepted changes", len(lines) >= 3, f"length={len(lines)}")
    chain.write_text("\n".join(lines[:-1]) + "\n")
    record("A4b chain truncation detected", run("verify", "--no-scan-source", env=env, root=d).returncode != 0)
    shutil.rmtree(d, ignore_errors=True)

    # A5: rollback to an older signed snapshot. INHERENT LIMIT without an anchor;
    # --strict (which requires a confirmed anchor) rejects it.
    d, env = make_repo()
    d0 = (d / "DOC0.md").read_text()
    snap = Path(tempfile.mkdtemp())
    shutil.copytree(d / ".chronolith", snap / "c")
    (d / "DOC0.md").write_text("# legit later work\n", encoding="utf-8")
    run("check", "--no-scan-source", "--accept", env=env, root=d)
    shutil.rmtree(d / ".chronolith")
    shutil.copytree(snap / "c", d / ".chronolith")
    (d / "DOC0.md").write_text(d0, encoding="utf-8")
    plain = run("verify", "--no-scan-source", env=env, root=d).returncode
    strict = run("verify", "--no-scan-source", "--strict", "--expect-fingerprint",
                 sv.key_fingerprint(ac.load_sovereign_keys(d)[1]), env=env, root=d).returncode
    record("A5a rollback: plain verify (INHERENT LIMIT — undetectable, needs anchor)", plain == 0,
           "documented limit; verify warns")
    record("A5b rollback rejected by --strict (requires anchor)", strict != 0)
    shutil.rmtree(d, ignore_errors=True)
    shutil.rmtree(snap, ignore_errors=True)

    # A6: inclusion-proof forgery for a non-member file.
    leaves = [ac.path_bound_leaf(f"F{i}.md", f"h{i}") for i in range(5)]
    root = ac.build_merkle_tree(leaves)
    ghost = ac.path_bound_leaf("GHOST.md", "evil")
    try:
        proof = ac.merkle_inclusion_proof(leaves + [ghost], ghost)
        forged = ac.verify_inclusion_proof(ghost, proof, root)
    except Exception:
        forged = False
    record("A6 inclusion proof for a non-member file", not forged)

    # A7: sealed box ciphertext tamper (AEAD).
    d = Path(tempfile.mkdtemp())
    sv.generate_x25519_keys(d)
    spriv, spub = (d / "seal.priv").read_bytes(), (d / "seal.pub").read_bytes()
    raw = bytearray(base64.b64decode(sv.seal(b"secret", spub)))
    raw[-1] ^= 0x01
    try:
        sv.open_sealed(base64.b64encode(bytes(raw)).decode(), spriv)
        broke = True
    except ValueError:
        broke = False
    record("A7 tamper sealed ciphertext", not broke)
    shutil.rmtree(d, ignore_errors=True)

    # A8: vault wrong passphrase.
    payload = sv.encrypt_private_key(b"\x01" * 32, "correct")
    try:
        sv.decrypt_private_key(payload, "wrong")
        broke = True
    except ValueError:
        broke = False
    record("A8 vault wrong passphrase", not broke)


def benchmark() -> None:
    print("\n=== BENCHMARK: check latency & incremental cache ===")
    for n in (50, 250, 1000):
        d, env = make_repo(n_docs=0)
        for i in range(n):
            (d / f"F{i}.md").write_text(f"# doc {i}\n" + "lorem ipsum dolor sit amet\n" * 20, encoding="utf-8")
        t0 = time.perf_counter(); run("check", "--no-scan-source", env=env, root=d); t1 = time.perf_counter()
        t2 = time.perf_counter(); run("check", "--no-scan-source", env=env, root=d); t3 = time.perf_counter()
        print(f"  {n:>4} docs | cold {(t1 - t0) * 1000:7.0f} ms | warm (cached) {(t3 - t2) * 1000:7.0f} ms")
        shutil.rmtree(d, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-bench", action="store_true")
    args = parser.parse_args()
    attacks()
    if not args.no_bench:
        benchmark()
    print("\n=== VERDICT ===")
    breaks = [n for n, held, _ in RESULTS if not held]
    for n, held, det in RESULTS:
        if not held:
            print(f"  BREAK: {n} — {det}")
    print(f"\n{len(RESULTS) - len(breaks)}/{len(RESULTS)} guarantees held; {len(breaks)} break(s).")
    return 1 if breaks else 0


if __name__ == "__main__":
    sys.exit(main())
