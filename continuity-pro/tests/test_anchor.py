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


if __name__ == "__main__":
    unittest.main()
