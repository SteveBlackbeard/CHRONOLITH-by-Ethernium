#!/usr/bin/env python3
"""Third-party verification: key fingerprint (trust bootstrapping) and the
unified `verify` command driven end to end via the CLI in a temp repo."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "chronolith_pro" / "chronolith"))

try:
    import cryptography  # noqa: F401
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False

SCRIPT = Path(__file__).parent.parent / "chronolith_pro" / "chronolith" / "run_chronolith_cycle.py"


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
        (self.root / ".chronolith").mkdir()
        (self.root / ".chronolith" / "STATE.json").write_text('{"phase":"pro"}', encoding="utf-8")
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

    def test_check_fails_closed_on_drift_by_default(self):
        """Plain `check` must exit 1 when a governed file changed.

        The previous logic only halted under --strict or refused to halt under
        permissive; with stock defaults it printed the drift and exited 0. A CI
        job running plain `check` passed on a drifting repository — the exact
        failure this tool exists to catch, and the opposite of its own Law 3.

        Found by an agent running the tool for real, not by reading it.
        """
        (self.root / "DOC.md").write_text("# Canonical\nan unaccepted edit\n", encoding="utf-8")
        result = self._run("check", "--no-scan-source")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("FAIL-CLOSED", result.stdout)

    def test_check_accept_advances_baseline_and_exits_zero(self):
        """--accept is the sanctioned way to record an intentional edit."""
        (self.root / "DOC.md").write_text("# Canonical\nan intentional edit\n", encoding="utf-8")
        accepted = self._run("check", "--no-scan-source", "--accept")
        self.assertEqual(accepted.returncode, 0, accepted.stdout + accepted.stderr)
        # And the baseline actually moved: a plain check is clean afterward.
        after = self._run("check", "--no-scan-source")
        self.assertEqual(after.returncode, 0, after.stdout + after.stderr)

    def test_permissive_mode_is_the_only_escape_hatch(self):
        """CHRONOLITH_MODE=permissive continues past drift; nothing else does."""
        import os
        (self.root / "DOC.md").write_text("# Canonical\ndrift\n", encoding="utf-8")
        env = dict(os.environ, CHRONOLITH_MODE="permissive")
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "check", "--no-scan-source", "--repo-root", str(self.root)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", env=env,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_chain_command_runs(self):
        """`chain` renders the transparency chain without crashing.

        Regression: rich's Table was used at the point of rendering but never
        imported, so the command died with NameError every single time. No test
        invoked it, so only flake8's F821 in CI eventually surfaced it — a
        documented, shipped command that could never once have worked.
        """
        result = self._run("chain")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn("NameError", result.stdout + result.stderr)
        self.assertIn("DNA Transparency Chain", result.stdout)

    def test_verify_without_fingerprint_is_integrity_only_not_authentic(self):
        # Honesty (red-team A3a): without a pinned key, verify proves integrity
        # but must NOT claim authenticity — a key-swapped fork would also pass.
        result = self._run("verify", "--no-scan-source")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("INTEGRITY OK", result.stdout)
        self.assertNotIn("DNA AUTHENTIC", result.stdout)

    def test_verify_with_fingerprint_claims_authentic(self):
        result = self._run("verify", "--no-scan-source", "--expect-fingerprint", self._fingerprint())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("DNA AUTHENTIC", result.stdout)

    def test_verify_strict_requires_fingerprint_and_anchor(self):
        # No anchor present -> --strict must fail even on an intact repo.
        result = self._run("verify", "--no-scan-source", "--strict", "--expect-fingerprint", self._fingerprint())
        self.assertEqual(result.returncode, 1, result.stdout)

    def test_verify_json_is_machine_readable(self):
        result = self._run("verify", "--no-scan-source", "--json")
        self.assertEqual(result.returncode, 0, result.stdout)
        report = json.loads(result.stdout)
        self.assertTrue(report["ok"])
        self.assertEqual(report["verdict"], "integrity-only")
        self.assertTrue(report["checks"]["root_matches_baseline"])
        self.assertIn("authenticity_not_verified", " ".join(report["warnings"]))

    def test_verify_json_reports_drift(self):
        (self.root / "DOC.md").write_text("# tampered\n", encoding="utf-8")
        result = self._run("verify", "--no-scan-source", "--json")
        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertFalse(report["ok"])
        self.assertFalse(report["checks"]["root_matches_baseline"])

    def test_verify_detects_content_drift(self):
        (self.root / "DOC.md").write_text("# Tampered\n", encoding="utf-8")
        result = self._run("verify", "--no-scan-source")
        self.assertEqual(result.returncode, 1)
        self.assertIn("DRIFT", result.stdout)

    def test_accept_advances_baseline_and_grows_chain(self):
        # Red-team A4: without --accept an intentional edit is drift and the chain
        # is stuck; with --accept the baseline advances and the chain grows (the
        # legitimate way the transparency log gains entries).
        chain = self.root / ".chronolith" / "dna_chain.jsonl"
        n0 = len(chain.read_text(encoding="utf-8").splitlines()) if chain.exists() else 0
        (self.root / "DOC.md").write_text("# intentional rev\n", encoding="utf-8")
        drift = self._run("check", "--no-scan-source")  # no --accept: reported as drift
        self.assertIn("DRIFT", drift.stdout)
        accepted = self._run("check", "--no-scan-source", "--accept")
        self.assertEqual(accepted.returncode, 0, accepted.stdout)
        n1 = len(chain.read_text(encoding="utf-8").splitlines())
        self.assertGreater(n1, n0, "the transparency chain must grow when changes are accepted")
        # And the advanced state still verifies.
        self.assertEqual(self._run("verify", "--no-scan-source").returncode, 0)

    def test_verify_detects_chain_truncation(self):
        # Red-team A4b: a chain can be internally valid yet truncated. Grow it,
        # drop the newest entry, and verify must reject via chain-head binding.
        for i in range(2):
            (self.root / "DOC.md").write_text(f"# rev {i}\n", encoding="utf-8")
            self._run("check", "--no-scan-source", "--accept")
        chain = self.root / ".chronolith" / "dna_chain.jsonl"
        lines = chain.read_text(encoding="utf-8").splitlines()
        self.assertGreaterEqual(len(lines), 2)
        chain.write_text("\n".join(lines[:-1]) + "\n", encoding="utf-8")  # drop newest
        result = self._run("verify", "--no-scan-source")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("MISMATCH", result.stdout)

    def test_verify_fingerprint_pin_match_and_mismatch(self):
        good = self._run("verify", "--no-scan-source", "--expect-fingerprint", self._fingerprint())
        self.assertEqual(good.returncode, 0, good.stdout)
        bad = self._run("verify", "--no-scan-source", "--expect-fingerprint", "SHA256:not-the-real-key")
        self.assertEqual(bad.returncode, 1)
        self.assertIn("MISMATCH", bad.stdout)


if __name__ == "__main__":
    unittest.main()


class TestUsabilityFixes(unittest.TestCase):
    """Fixes for defects an agent found using the tool for real (C-4, C-5, C-8)."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = Path(self.tmp.name)
        subprocess.run(["git", "init"], cwd=self.root, capture_output=True)
        (self.root / "DOC.md").write_text("# Canonical\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args, "--repo-root", str(self.root)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )

    def test_init_second_run_says_nothing_was_recreated(self):
        """C-5: a silent no-op second init read as a successful re-crystallization."""
        self._run("init", "--no-hook")
        second = self._run("init", "--no-hook")
        self.assertIn("already present", second.stdout)

    def test_quiet_suppresses_banner_but_not_the_verdict(self):
        """C-8: --quiet gives clean CI output; the status panel still prints."""
        self._run("init", "--no-hook")
        result = self._run("check", "--no-scan-source", "--quiet")
        self.assertNotIn("________", result.stdout)  # no ASCII banner
        self.assertIn("Pro Status:", result.stdout)  # verdict still there

    def test_chronolithignore_excludes_matching_paths(self):
        """C-4: an edit inside an ignored backup tree must not trigger drift."""
        (self.root / "BACKUP").mkdir()
        (self.root / "BACKUP" / "DOC.md").write_text("# dead\n", encoding="utf-8")
        (self.root / ".chronolithignore").write_text("BACKUP\n", encoding="utf-8")
        self._run("init", "--no-hook")
        self._run("check", "--accept", "--quiet")
        (self.root / "BACKUP" / "DOC.md").write_text("# dead edited\n", encoding="utf-8")
        result = self._run("check", "--no-scan-source", "--quiet")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
