"""Bitcoin anchoring for the DNA transparency chain (external witness).

The signed chain proves lineage *to anyone who trusts the sovereign key*. That is
the honest limit: a party who controls both the repo and the key can rebuild a
consistent chain. OpenTimestamps closes that gap — it stamps the chain head into
the Bitcoin blockchain, so a **skeptical third party** can verify that this exact
DNA state existed at a given time without trusting the operator at all. And
because a past Bitcoin timestamp cannot be forged even with a stolen key, the
anchor also gives forward-security against history rewrites after a key
compromise.

Design (matching the Ethernium Frugal anchor): anchoring is optional
infrastructure, never a blocker. If the `ots` client is installed it produces a
real `.ots` proof; if not, a local sovereign record is still written and install
instructions are printed. No hard dependency, no network call from this module
itself — the `ots` client owns the calendar/network interaction.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ANCHOR_DIRNAME = "anchors"
_OTS_CANDIDATES = ("ots", "ots.exe")
# Public OpenTimestamps aggregator calendars (same set the ots client uses).
_CALENDARS = (
    "https://alice.btc.calendar.opentimestamps.org",
    "https://bob.btc.calendar.opentimestamps.org",
    "https://finney.calendar.eternitywall.com",
)


def library_available() -> bool:
    try:
        import opentimestamps  # noqa: F401
        return True
    except ImportError:
        return False


def stamp_with_library(anchor_path: str | Path, *, timeout: int = 10, calendars=_CALENDARS) -> tuple[bool, str]:
    """Stamp a file via the opentimestamps Python library — the friction-free
    path when the `ots` CLI is broken (its python-bitcoinlib/OpenSSL DLL issue on
    Windows). This is a thin wrapper: the library owns the calendar protocol and
    .ots serialization; we only submit the file's SHA-256 to the aggregator
    calendars and write the returned proof. Requires network to the calendars.
    Never raises."""
    import hashlib

    try:
        from opentimestamps.calendar import RemoteCalendar
        from opentimestamps.core.op import OpSHA256
        from opentimestamps.core.timestamp import DetachedTimestampFile, Timestamp
        from opentimestamps.core.serialize import BytesSerializationContext
    except ImportError:
        return False, "opentimestamps library not installed (pip install continuity-pro[anchor])"

    path = Path(anchor_path)
    digest = hashlib.sha256(path.read_bytes()).digest()
    timestamp = Timestamp(digest)
    reached = []
    for url in calendars:
        try:
            timestamp.merge(RemoteCalendar(url).submit(digest, timeout=timeout))
            reached.append(url)
        except Exception:
            continue  # try the next calendar; one is enough
    if not reached:
        return False, "no OpenTimestamps calendar was reachable"
    ctx = BytesSerializationContext()
    DetachedTimestampFile(OpSHA256(), timestamp).serialize(ctx)
    ots_path = path.with_suffix(path.suffix + ".ots")
    ots_path.write_bytes(ctx.getbytes())
    return True, f"{ots_path} (via {len(reached)} calendar(s))"


def anchor_dir(repo_root: str | Path) -> Path:
    return Path(repo_root) / ".continuity" / ANCHOR_DIRNAME


def build_anchor_record(
    chain_head: dict | None,
    merkle_root: str,
    sovereign_pub_hex: str | None,
) -> dict:
    """The record that gets timestamped. Anchoring `chain_head['entry_hash']`
    (which hash-links the entire history) timestamps the whole lineage, not just
    the current root."""
    return {
        "project": "Continuity Legacy (Pro)",
        "anchored_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "method": "opentimestamps",
        "merkle_root": merkle_root,
        "chain_seq": chain_head.get("seq") if chain_head else None,
        "chain_head_hash": chain_head.get("entry_hash") if chain_head else None,
        "sovereign_public_key": sovereign_pub_hex,
        "note": (
            "The chain head hash links the full DNA lineage; a Bitcoin timestamp "
            "over this file proves that exact state existed at the confirmed time, "
            "verifiable by anyone with the .ots proof — no trust in the operator."
        ),
    }


def write_anchor(repo_root: str | Path, record: dict) -> Path:
    directory = anchor_dir(repo_root)
    directory.mkdir(parents=True, exist_ok=True)
    tag = (record.get("chain_head_hash") or record.get("merkle_root") or "state")[:12]
    path = directory / f"ANCHOR_{tag}.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _find_ots() -> str | None:
    for binary in _OTS_CANDIDATES:
        try:
            probe = subprocess.run([binary, "--version"], capture_output=True, text=True)
        except (OSError, FileNotFoundError):
            continue
        if probe.returncode == 0 or probe.stdout or probe.stderr:
            return binary
    return None


def try_ots_stamp(anchor_path: str | Path) -> tuple[bool, str]:
    """Create a `.ots` proof via the OpenTimestamps client, if installed.
    Returns (stamped, message). Never raises — anchoring must not block a run."""
    binary = _find_ots()
    if not binary:
        return False, "ots client not installed"
    try:
        result = subprocess.run([binary, "stamp", str(anchor_path)], capture_output=True, text=True)
    except OSError as exc:
        return False, f"ots stamp failed: {exc}"
    if result.returncode == 0:
        return True, f"{anchor_path}.ots"
    return False, (result.stderr or result.stdout or "ots stamp returned non-zero").strip()


def inspect_ots_proof(ots_path: str | Path) -> tuple[bool, str]:
    """Local structural check of a .ots proof (no network): confirmed if it
    already carries a Bitcoin attestation, otherwise pending on the calendars.
    Full blockchain confirmation still needs `ots verify` or a Bitcoin node."""
    try:
        from opentimestamps.core.serialize import BytesDeserializationContext
        from opentimestamps.core.timestamp import DetachedTimestampFile
        from opentimestamps.core.notary import BitcoinBlockHeaderAttestation
    except ImportError:
        return False, "opentimestamps library not installed"
    path = Path(ots_path)
    if not path.exists():
        return False, f"proof not found: {path}"
    try:
        ctx = BytesDeserializationContext(path.read_bytes())
        dtf = DetachedTimestampFile.deserialize(ctx)
    except Exception as exc:
        return False, f"malformed .ots proof: {exc}"
    for _msg, attestation in dtf.timestamp.all_attestations():
        if isinstance(attestation, BitcoinBlockHeaderAttestation):
            return True, f"confirmed in Bitcoin block {attestation.height}"
    return False, "pending: calendar attestation present, not yet confirmed on Bitcoin (upgrade later)"


def _walk_timestamps(ts):
    """Yield a timestamp and all of its sub-timestamps (the proof tree)."""
    yield ts
    for _op, sub in ts.ops.items():
        yield from _walk_timestamps(sub)


def upgrade_proof(ots_path: str | Path, *, timeout: int = 10) -> tuple[bool, str]:
    """Fetch Bitcoin attestations from the calendars for a pending proof and
    rewrite the .ots. Returns (upgraded, message). Best-effort and DLL-safe: the
    calendar fetch and attestation reads do NOT import python-bitcoinlib's
    OpenSSL-dependent key module, so this works where the `ots` CLI crashes on
    Windows. Right after stamping the calendar has nothing yet (pending); it
    succeeds a few hours later once Bitcoin confirms."""
    try:
        from opentimestamps.calendar import RemoteCalendar
        from opentimestamps.core.timestamp import DetachedTimestampFile
        from opentimestamps.core.notary import PendingAttestation
        from opentimestamps.core.serialize import (
            BytesDeserializationContext, BytesSerializationContext,
        )
    except ImportError:
        return False, "opentimestamps library not installed"
    path = Path(ots_path)
    try:
        dtf = DetachedTimestampFile.deserialize(BytesDeserializationContext(path.read_bytes()))
    except Exception as exc:
        return False, f"malformed .ots proof: {exc}"
    upgraded = False
    for sub in _walk_timestamps(dtf.timestamp):
        for att in list(sub.attestations):
            if isinstance(att, PendingAttestation):
                uri = att.uri.decode() if isinstance(att.uri, bytes) else att.uri
                try:
                    sub.merge(RemoteCalendar(uri).get_timestamp(sub.msg, timeout=timeout))
                    upgraded = True
                except Exception:
                    continue  # not confirmed yet, or calendar unreachable
    if upgraded:
        ctx = BytesSerializationContext()
        dtf.serialize(ctx)
        path.write_bytes(ctx.getbytes())
    return upgraded, "upgraded from calendar" if upgraded else "no upgrade available yet (still pending)"


def verify_via_library(ots_path: str | Path) -> tuple[bool, str]:
    """Full-as-possible verification via the library (no broken CLI): upgrade the
    proof from the calendars, then report whether it now carries a Bitcoin
    attestation. Confirmed = the timestamp is anchored in a Bitcoin block."""
    upgrade_proof(ots_path)
    return inspect_ots_proof(ots_path)


def try_ots_verify(ots_path: str | Path) -> tuple[bool, str]:
    """Verify a `.ots` proof against the Bitcoin blockchain via the client.
    Returns (verified, message)."""
    binary = _find_ots()
    if not binary:
        return False, "ots client not installed (cannot verify the blockchain proof)"
    path = Path(ots_path)
    if not path.exists():
        return False, f"proof not found: {path}"
    try:
        result = subprocess.run([binary, "verify", str(path)], capture_output=True, text=True)
    except OSError as exc:
        return False, f"ots verify failed: {exc}"
    output = (result.stdout + result.stderr).strip()
    # `ots verify` prints "Success! Bitcoin block ..." on a confirmed proof and a
    # "Pending" notice while the calendar attestation awaits confirmation. Check
    # pending FIRST — the pending message also mentions "Bitcoin".
    if "pending" in output.lower():
        return False, "pending: calendar attestation not yet confirmed on Bitcoin (retry in a few hours)"
    if result.returncode == 0 and ("Success" in output or "Bitcoin block" in output):
        return True, output
    return False, output or "verification failed"
