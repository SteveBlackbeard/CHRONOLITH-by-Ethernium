#!/usr/bin/env python3
"""Integrity tests for Continuity Pro: path-bound Merkle, signed baseline drift
detection, and config-filename resolution. These cover the production fixes that
made the guardian actually catch DNA drift (previously the Merkle root was
computed but never compared to a baseline)."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "continuity_pro" / "continuity_legacy"))

import automation_common as ac  # noqa: E402
import run_continuity_cycle as rcc  # noqa: E402


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
        (self.root / "continuity-legacy.json").write_text("{}", encoding="utf-8")
        (self.root / "continuity_legacy.json").write_text("{}", encoding="utf-8")
        self.assertEqual(ac.resolve_config_file(self.root).name, "continuity-legacy.json")

    def test_falls_back_to_underscore(self):
        (self.root / "continuity_legacy.json").write_text("{}", encoding="utf-8")
        self.assertEqual(ac.resolve_config_file(self.root).name, "continuity_legacy.json")

    def test_default_is_canonical_hyphen(self):
        self.assertEqual(ac.resolve_config_file(self.root).name, "continuity-legacy.json")


class TestDriftDetection(unittest.TestCase):
    def setUp(self):
        # ignore_cleanup_errors: the guardian's logger keeps a FileHandler open on
        # a log inside the temp dir; on Windows that blocks unlink at cleanup.
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = Path(self.tmp.name)
        (self.root / ".continuity").mkdir()
        (self.root / ".continuity" / "STATE.json").write_text(
            json.dumps({"phase": "pro", "last_update": "2026-01-01T00:00:00"}), encoding="utf-8"
        )
        (self.root / "DOC.md").write_text("# Canonical content\n", encoding="utf-8")

    def tearDown(self):
        import logging
        logger = logging.getLogger("continuity_pro")
        for handler in list(logger.handlers):
            handler.close()
            logger.removeHandler(handler)
        self.tmp.cleanup()

    def _run_check(self):
        """Run the guardian in non-strict mode (never raises) and return its report."""
        import typer
        try:
            rcc.check(repo_root=self.root, strict=False, scan_source=False)
        except typer.Exit:
            pass
        return json.loads((self.root / ".continuity" / "pro_report.json").read_text(encoding="utf-8"))

    def test_first_check_baselines_without_drift(self):
        report = self._run_check()
        self.assertFalse(report["dna_drift"])
        # Baseline was crystallized and signed.
        state = json.loads((self.root / ".continuity" / "STATE.json").read_text(encoding="utf-8"))
        self.assertIn("merkle_root", state)
        self.assertTrue(ac.verify_signature(state))

    def test_content_change_is_detected_as_drift(self):
        self._run_check()  # baseline
        (self.root / "DOC.md").write_text("# Tampered content\n", encoding="utf-8")
        report = self._run_check()
        self.assertTrue(report["dna_drift"], "editing a scanned doc must register as DNA drift")

    def test_tampered_state_signature_is_flagged(self):
        self._run_check()  # baseline (signs STATE)
        state_path = self.root / ".continuity" / "STATE.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["merkle_root"] = "0" * 64  # hand-edit, leave signature stale
        state_path.write_text(json.dumps(state), encoding="utf-8")
        report = self._run_check()
        self.assertTrue(report["signature_tampered"], "hand-edited STATE must fail signature verification")


if __name__ == "__main__":
    unittest.main()
