#!/usr/bin/env python3
"""Integrity tests for Chronolith Pro: path-bound Merkle, signed baseline drift
detection, and config-filename resolution. These cover the production fixes that
made the guardian actually catch DNA drift (previously the Merkle root was
computed but never compared to a baseline)."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "chronolith_pro" / "chronolith"))

import automation_common as ac  # noqa: E402
import run_chronolith_cycle as rcc  # noqa: E402


class TestMerkleAndSignature(unittest.TestCase):
    def test_path_bound_leaf_binds_filename(self):
        self.assertNotEqual(ac.path_bound_leaf("A.md", "h"), ac.path_bound_leaf("B.md", "h"))

    def test_content_swap_changes_root(self):
        original = ac.build_merkle_tree([ac.path_bound_leaf("A.md", "ha"), ac.path_bound_leaf("B.md", "hb")])
        swapped = ac.build_merkle_tree([ac.path_bound_leaf("A.md", "hb"), ac.path_bound_leaf("B.md", "ha")])
        self.assertNotEqual(original, swapped)

    def test_verify_signature_accepts_valid_rejects_tampered(self):
        state = {"phase": "pro", "merkle_root": "x"}
        state["signature"] = ac.sign_state(state)
        self.assertTrue(ac.verify_signature(state))
        state["merkle_root"] = "y"  # edited after signing
        self.assertFalse(ac.verify_signature(state))

    def test_verify_signature_absent_is_unverifiable_not_rejected(self):
        self.assertTrue(ac.verify_signature({"phase": "pro"}))


class TestConfigFilenameResolution(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_prefers_hyphen(self):
        (self.root / "chronolith.json").write_text("{}", encoding="utf-8")
        (self.root / "chronolith.json").write_text("{}", encoding="utf-8")
        self.assertEqual(ac.resolve_config_file(self.root).name, "chronolith.json")

    def test_falls_back_to_underscore(self):
        (self.root / "chronolith.json").write_text("{}", encoding="utf-8")
        self.assertEqual(ac.resolve_config_file(self.root).name, "chronolith.json")

    def test_default_is_canonical_hyphen(self):
        self.assertEqual(ac.resolve_config_file(self.root).name, "chronolith.json")


class TestDriftDetection(unittest.TestCase):
    def setUp(self):
        # ignore_cleanup_errors: the guardian's logger keeps a FileHandler open on
        # a log inside the temp dir; on Windows that blocks unlink at cleanup.
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = Path(self.tmp.name)
        (self.root / ".chronolith").mkdir()
        (self.root / ".chronolith" / "STATE.json").write_text(
            json.dumps({"phase": "pro", "last_update": "2026-01-01T00:00:00"}), encoding="utf-8"
        )
        (self.root / "DOC.md").write_text("# Canonical content\n", encoding="utf-8")

    def tearDown(self):
        import logging
        logger = logging.getLogger("chronolith_pro")
        for handler in list(logger.handlers):
            handler.close()
            logger.removeHandler(handler)
        self.tmp.cleanup()

    def _run_check(self, accept=False):
        """Run the guardian in non-strict mode (never raises) and return its
        report. accept must be passed explicitly: a typer command called directly
        receives OptionInfo (truthy) for omitted options, not the default."""
        import typer
        try:
            rcc.check(repo_root=self.root, strict=False, scan_source=False, accept=accept)
        except typer.Exit:
            pass
        return json.loads((self.root / ".chronolith" / "pro_report.json").read_text(encoding="utf-8"))

    def test_first_check_baselines_without_drift(self):
        report = self._run_check()
        self.assertFalse(report["dna_drift"])
        # Baseline was crystallized and signed.
        state = json.loads((self.root / ".chronolith" / "STATE.json").read_text(encoding="utf-8"))
        self.assertIn("merkle_root", state)
        self.assertTrue(ac.verify_signature(state))

    def test_content_change_is_detected_as_drift(self):
        self._run_check()  # baseline
        (self.root / "DOC.md").write_text("# Tampered content\n", encoding="utf-8")
        report = self._run_check()
        self.assertTrue(report["dna_drift"], "editing a scanned doc must register as DNA drift")

    def test_tampered_state_signature_is_flagged(self):
        self._run_check()  # baseline (signs STATE)
        state_path = self.root / ".chronolith" / "STATE.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["merkle_root"] = "0" * 64  # hand-edit, leave signature stale
        state_path.write_text(json.dumps(state), encoding="utf-8")
        report = self._run_check()
        self.assertTrue(report["signature_tampered"], "hand-edited STATE must fail signature verification")


class TestMerkleInclusionProofs(unittest.TestCase):
    LEAVES = [f"leaf-{i}" for i in range(7)]  # odd count exercises padding

    def test_proof_roundtrip_every_leaf(self):
        root = ac.build_merkle_tree(self.LEAVES)
        for leaf in self.LEAVES:
            proof = ac.merkle_inclusion_proof(self.LEAVES, leaf)
            self.assertTrue(ac.verify_inclusion_proof(leaf, proof, root), f"proof failed for {leaf}")

    def test_proof_rejects_tampered_leaf(self):
        root = ac.build_merkle_tree(self.LEAVES)
        proof = ac.merkle_inclusion_proof(self.LEAVES, "leaf-3")
        self.assertFalse(ac.verify_inclusion_proof("leaf-3-tampered", proof, root))

    def test_proof_rejects_wrong_root(self):
        proof = ac.merkle_inclusion_proof(self.LEAVES, "leaf-3")
        self.assertFalse(ac.verify_inclusion_proof("leaf-3", proof, "0" * 64))

    def test_single_leaf_has_empty_proof(self):
        root = ac.build_merkle_tree(["only"])
        self.assertTrue(ac.verify_inclusion_proof("only", [], root))

    def test_absent_leaf_raises(self):
        with self.assertRaises(ValueError):
            ac.merkle_inclusion_proof(self.LEAVES, "ghost")


class TestTransparencyChain(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_append_links_and_verifies(self):
        ac.append_chain_entry(self.root, "root-A")
        ac.append_chain_entry(self.root, "root-B")
        self.assertIsNone(ac.append_chain_entry(self.root, "root-B"), "unchanged root must be a no-op")
        entries = ac.read_chain(self.root)
        self.assertEqual([e["seq"] for e in entries], [0, 1])
        self.assertEqual(entries[1]["prev_entry_hash"], entries[0]["entry_hash"])
        ok, issues = ac.verify_chain(self.root)
        self.assertTrue(ok, issues)

    def test_edited_entry_breaks_chain(self):
        ac.append_chain_entry(self.root, "root-A")
        ac.append_chain_entry(self.root, "root-B")
        path = ac.chain_path(self.root)
        lines = path.read_text(encoding="utf-8").splitlines()
        first = json.loads(lines[0])
        first["merkle_root"] = "rewritten-history"  # attacker edits the past
        path.write_text(json.dumps(first, sort_keys=True) + "\n" + lines[1] + "\n", encoding="utf-8")
        ok, issues = ac.verify_chain(self.root)
        self.assertFalse(ok)
        self.assertTrue(any("hash mismatch" in i or "linkage" in i for i in issues), issues)


try:
    import cryptography  # noqa: F401
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


@unittest.skipUnless(HAS_CRYPTO, "cryptography not installed")
class TestSovereignEd25519(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = Path(self.tmp.name)
        ac.generate_sovereign_keys(self.root)
        self.priv, self.pub = ac.load_sovereign_keys(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_signed_state_verifies_and_tamper_fails(self):
        state = {"phase": "pro", "merkle_root": "abc"}
        ac.sovereign_sign_state(state, self.priv, self.pub)
        self.assertTrue(ac.verify_sovereign_state(state, trusted_public=self.pub))
        state["merkle_root"] = "evil"
        self.assertFalse(ac.verify_sovereign_state(state, trusted_public=self.pub))

    def test_attacker_keypair_swap_is_rejected(self):
        # Attacker re-signs the tampered state with THEIR key and embeds their
        # public key; the local trust anchor must still reject it.
        other = Path(self.tmp.name) / "other"
        other.mkdir()
        ac.generate_sovereign_keys(other)
        att_priv, att_pub = ac.load_sovereign_keys(other)
        state = {"phase": "pro", "merkle_root": "evil"}
        ac.sovereign_sign_state(state, att_priv, att_pub)
        self.assertFalse(ac.verify_sovereign_state(state, trusted_public=self.pub))

    def test_unsigned_state_is_checksum_mode(self):
        self.assertIsNone(ac.verify_sovereign_state({"phase": "pro"}, trusted_public=self.pub))

    def test_signed_chain_rejects_unsigned_entries(self):
        ac.append_chain_entry(self.root, "root-A", private_bytes=self.priv)
        ok, issues = ac.verify_chain(self.root, trusted_public=self.pub)
        self.assertTrue(ok, issues)
        ac.append_chain_entry(self.root, "root-B")  # unsigned entry sneaks in
        ok, issues = ac.verify_chain(self.root, trusted_public=self.pub)
        self.assertFalse(ok)


class TestIncrementalHashing(unittest.TestCase):
    def test_cache_hits_and_invalidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = Path(tmp) / "doc.md"
            f.write_text("v1", encoding="utf-8")
            cache: dict = {}
            h1 = ac.calculate_sha256_cached(f, cache)
            self.assertEqual(h1, ac.calculate_sha256(f))
            self.assertEqual(ac.calculate_sha256_cached(f, cache), h1)  # cache hit
            import os, time
            time.sleep(0.01)
            f.write_text("v2-changed", encoding="utf-8")
            os.utime(f)  # ensure mtime moves even on coarse filesystems
            h2 = ac.calculate_sha256_cached(f, cache)
            self.assertNotEqual(h1, h2, "content change must invalidate the cache")
            self.assertEqual(h2, ac.calculate_sha256(f))


if __name__ == "__main__":
    unittest.main()
