#!/usr/bin/env python3
"""Bitcoin anchoring tests (external witness for the DNA chain).

The OpenTimestamps client (`ots`) and the Bitcoin network are external, so these
tests cover the local record construction and the client-output parsing without
requiring the client to be installed or the network to be reachable."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "continuity_pro" / "continuity_legacy"))

import anchor as anchor_mod  # noqa: E402


class TestAnchorRecord(unittest.TestCase):
    def test_record_anchors_chain_head_not_just_root(self):
        head = {"seq": 3, "entry_hash": "cafebabe" * 8, "merkle_root": "dead" * 16}
        record = anchor_mod.build_anchor_record(head, "dead" * 16, "aa" * 32)
        self.assertEqual(record["chain_head_hash"], head["entry_hash"])
        self.assertEqual(record["chain_seq"], 3)
        self.assertEqual(record["method"], "opentimestamps")
        self.assertEqual(record["sovereign_public_key"], "aa" * 32)

    def test_record_without_chain_falls_back_to_root(self):
        record = anchor_mod.build_anchor_record(None, "beef" * 16, None)
        self.assertIsNone(record["chain_head_hash"])
        self.assertEqual(record["merkle_root"], "beef" * 16)

    def test_write_anchor_is_deterministic_and_named_by_head(self):
        with tempfile.TemporaryDirectory() as tmp:
            record = anchor_mod.build_anchor_record(
                {"seq": 0, "entry_hash": "abcdef012345" + "0" * 52}, "root", "bb" * 32
            )
            path = anchor_mod.write_anchor(tmp, record)
            self.assertTrue(path.name.startswith("ANCHOR_abcdef012345"))
            reloaded = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(reloaded["chain_head_hash"], record["chain_head_hash"])


class TestOtsParsing(unittest.TestCase):
    """try_ots_verify parses client output; stub _find_ots + subprocess so no
    real client/network is needed."""

    def _patch(self, monkey_binary, stdout="", stderr="", returncode=0):
        anchor_mod._find_ots = lambda: monkey_binary
        import subprocess

        class _Result:
            pass

        def fake_run(cmd, capture_output=True, text=True):
            r = _Result()
            r.returncode = returncode
            r.stdout = stdout
            r.stderr = stderr
            return r

        self._orig_run = subprocess.run
        subprocess.run = fake_run

    def tearDown(self):
        import subprocess
        if hasattr(self, "_orig_run"):
            subprocess.run = self._orig_run

    def test_no_client_is_reported_not_crashed(self):
        anchor_mod._find_ots = lambda: None
        ok, msg = anchor_mod.try_ots_verify("x.ots")
        self.assertFalse(ok)
        self.assertIn("not installed", msg)

    def test_confirmed_proof(self):
        with tempfile.TemporaryDirectory() as tmp:
            proof = Path(tmp) / "a.ots"
            proof.write_bytes(b"stub")
            self._patch("ots", stdout="Success! Bitcoin block 800000 attests existence")
            ok, msg = anchor_mod.try_ots_verify(proof)
            self.assertTrue(ok)
            self.assertIn("Bitcoin", msg)

    def test_pending_proof(self):
        with tempfile.TemporaryDirectory() as tmp:
            proof = Path(tmp) / "a.ots"
            proof.write_bytes(b"stub")
            self._patch("ots", stdout="Pending confirmation in the Bitcoin blockchain")
            ok, msg = anchor_mod.try_ots_verify(proof)
            self.assertFalse(ok)
            self.assertIn("pending", msg.lower())


try:
    import opentimestamps  # noqa: F401
    HAS_OTS = True
except ImportError:
    HAS_OTS = False


@unittest.skipUnless(HAS_OTS, "opentimestamps library not installed")
class TestLibraryAnchor(unittest.TestCase):
    """The friction-free (library) path. The calendar submission needs network
    and is the operator's one verification step; everything else is tested here:
    availability, the .ots serialize/inspect round-trip, and pending detection."""

    def test_library_available(self):
        self.assertTrue(anchor_mod.library_available())

    def _write_pending_ots(self, tmp: Path) -> Path:
        # Build a real .ots with only a calendar (pending) attestation — exactly
        # what stamp_with_library writes before Bitcoin confirmation — without any
        # network, so the serialize/inspect path is verified locally.
        import hashlib
        from opentimestamps.core.op import OpSHA256
        from opentimestamps.core.timestamp import DetachedTimestampFile, Timestamp
        from opentimestamps.core.notary import PendingAttestation
        from opentimestamps.core.serialize import BytesSerializationContext

        digest = hashlib.sha256(b"anchor record").digest()
        ts = Timestamp(digest)
        ts.attestations.add(PendingAttestation("https://example.calendar/submit"))
        ctx = BytesSerializationContext()
        DetachedTimestampFile(OpSHA256(), ts).serialize(ctx)
        p = tmp / "ANCHOR.json.ots"
        p.write_bytes(ctx.getbytes())
        return p

    def test_inspect_reports_pending_for_calendar_only_proof(self):
        with tempfile.TemporaryDirectory() as tmp:
            proof = self._write_pending_ots(Path(tmp))
            confirmed, msg = anchor_mod.inspect_ots_proof(proof)
            self.assertFalse(confirmed)
            self.assertIn("pending", msg.lower())

    def test_inspect_rejects_malformed_proof(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "x.ots"
            bad.write_bytes(b"not a real ots proof")
            ok, msg = anchor_mod.inspect_ots_proof(bad)
            self.assertFalse(ok)
            self.assertIn("malformed", msg.lower())

    def test_upgrade_pending_proof_is_graceful_without_confirmation(self):
        # A freshly-stamped (pending) proof: upgrade finds nothing to fetch and
        # must not raise or crash into python-bitcoinlib's DLL path.
        with tempfile.TemporaryDirectory() as tmp:
            proof = self._write_pending_ots(Path(tmp))
            upgraded, msg = anchor_mod.upgrade_proof(proof, timeout=1)
            self.assertFalse(upgraded)
            self.assertIn("pending", msg.lower())
            # verify_via_library must then report pending, not crash.
            confirmed, vmsg = anchor_mod.verify_via_library(proof)
            self.assertFalse(confirmed)
            self.assertIn("pending", vmsg.lower())

    def test_stamp_with_library_no_calendar_is_graceful(self):
        # Point at an unreachable calendar: must fail cleanly, never raise.
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "ANCHOR.json"
            f.write_text('{"merkle_root":"x"}', encoding="utf-8")
            ok, msg = anchor_mod.stamp_with_library(f, timeout=1, calendars=("https://127.0.0.1:1",))
            self.assertFalse(ok)
            self.assertIn("no OpenTimestamps calendar", msg)


if __name__ == "__main__":
    unittest.main()
