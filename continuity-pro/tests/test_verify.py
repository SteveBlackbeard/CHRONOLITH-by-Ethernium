#!/usr/bin/env python3
"""Third-party verification: key fingerprint (trust bootstrapping) and the
unified `verify` command driven end to end via the CLI in a temp repo."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "continuity_pro" / "continuity_legacy"))

try:
    import cryptography  # noqa: F401
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

SCRIPT = Path(__file__).parent.parent / "continuity_pro" / "continuity_legacy" / "run_continuity_cycle.py"


@unittest.skipUnless(HAS_CRYPTO, "cryptography not installed")
class TestFingerprint(unittest.TestCase):
    def test_fingerprint_is_stable_and_key_specific(self):
        import automation_common as ac
        import sovereign_vault as sv

        with tempfile.TemporaryDirectory() as tmp:
            ac.generate_sovereign_keys(tmp)
            _priv, pub = ac.load_sovereign_keys(tmp)
            fp1 = sv.key_fingerprint(pub)
            fp2 = sv.key_fingerprint(pub)
            self.assertEqual(fp1, fp2)
            self.assertTrue(fp1.startswith("SHA256:"))
        with tempfile.TemporaryDirectory() as tmp2:
            ac.generate_sovereign_keys(tmp2)
            _p, other = ac.load_sovereign_keys(tmp2)
            self.assertNotEqual(fp1, sv.key_fingerprint(other))


@unittest.skipUnless(HAS_CRYPTO, "cryptography not installed")
class TestVerifyCommand(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = Path(self.tmp.name)
        (self.root / ".continuity").mkdir()
        (self.root / ".continuity" / "STATE.json").write_text('{"phase":"pro"}', encoding="utf-8")
        (self.root / "DOC.md").write_text("# Canonical\n", encoding="utf-8")
        self._run("sovereign-init")
        self._run("check", "--no-scan-source")

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, *args) -> subprocess.CompletedProcess:
        # utf-8/replace: rich prints unicode symbols the Windows default cp1252
        # codec cannot decode when captured (real consoles handle it fine).
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args, "--repo-root", str(self.root)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )

    def _fingerprint(self) -> str:
        import automation_common as ac
        import sovereign_vault as sv
        _p, pub = ac.load_sovereign_keys(self.root)
        return sv.key_fingerprint(pub)

    def test_verify_passes_on_intact_repo(self):
        result = self._run("verify", "--no-scan-source")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("DNA AUTHENTIC", result.stdout)

    def test_verify_detects_content_drift(self):
        (self.root / "DOC.md").write_text("# Tampered\n", encoding="utf-8")
        result = self._run("verify", "--no-scan-source")
        self.assertEqual(result.returncode, 1)
        self.assertIn("DRIFT", result.stdout)

    def test_verify_fingerprint_pin_match_and_mismatch(self):
        good = self._run("verify", "--no-scan-source", "--expect-fingerprint", self._fingerprint())
        self.assertEqual(good.returncode, 0, good.stdout)
        bad = self._run("verify", "--no-scan-source", "--expect-fingerprint", "SHA256:not-the-real-key")
        self.assertEqual(bad.returncode, 1)
        self.assertIn("MISMATCH", bad.stdout)


if __name__ == "__main__":
    unittest.main()
