#!/usr/bin/env python3
"""Secret detector tests, with emphasis on private key material.

Regression origin: `.chronolith/keys/sovereign.priv` — 32 raw bytes of an
Ed25519 seed — sat tracked in this repository for three months while this
scanner reported the tree clean. Two independent reasons:

1. The extension filter skipped every file whose suffix was not a known text
   type, so a `.priv` file was never read at all.
2. Every pattern was a text regex, and raw key bytes match none of them.

The detector had no tests. That is why nobody noticed it was blind.
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "chronolith_pro" / "chronolith"))

import secret_detector as sd  # noqa: E402


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, capture_output=True, check=False)


class TestPrivateKeyDetection(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.repo = Path(self.tmp.name)
        _git(self.repo, "init")
        (self.repo / ".chronolith" / "keys").mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def _find(self, report: dict, name: str) -> dict | None:
        return next((f for f in report["findings"] if Path(f["file"]).name == name), None)

    def test_tracked_unencrypted_key_is_danger(self):
        """The exact incident: a raw key that git is following."""
        key = self.repo / ".chronolith" / "keys" / "sovereign.priv"
        key.write_bytes(os.urandom(32))
        _git(self.repo, "add", "--force", str(key.relative_to(self.repo)))
        _git(self.repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "k")

        report = sd.scan_for_secrets(self.repo)
        finding = self._find(report, "sovereign.priv")
        self.assertIsNotNone(finding, "a tracked private key must be reported")
        self.assertEqual(finding["status"], "danger")
        self.assertTrue(finding["tracked"])
        self.assertEqual(report["status"], "danger")

    def test_untracked_local_key_is_only_a_warning(self):
        """Keys live on the machine that owns them; that is not an incident.

        If a local key failed the scan, every developer would learn to run it
        with the check disabled — which is worse than not having it.
        """
        (self.repo / "local.priv").write_bytes(os.urandom(32))
        report = sd.scan_for_secrets(self.repo)
        finding = self._find(report, "local.priv")
        self.assertIsNotNone(finding)
        self.assertEqual(finding["status"], "warning")
        self.assertFalse(finding["tracked"])
        self.assertNotEqual(report["status"], "danger")

    def test_public_key_is_not_flagged(self):
        (self.repo / ".chronolith" / "keys" / "sovereign.pub").write_bytes(os.urandom(32))
        report = sd.scan_for_secrets(self.repo)
        self.assertIsNone(self._find(report, "sovereign.pub"))

    def test_ca_bundle_is_not_flagged(self):
        """certifi ships a ~270KB cacert.pem of public certificates.

        Flagging it is not a harmless false positive: a scanner that cries wolf
        on every venv gets ignored, and then it misses the real key.
        """
        bundle = self.repo / "cacert.pem"
        bundle.write_bytes(b"-----BEGIN CERTIFICATE-----\n" + b"A" * 300000 +
                           b"\n-----END CERTIFICATE-----\n")
        report = sd.scan_for_secrets(self.repo)
        self.assertIsNone(self._find(report, "cacert.pem"))

    def test_pem_private_key_is_flagged(self):
        pem = self.repo / "server.pem"
        pem.write_bytes(b"-----BEGIN PRIVATE KEY-----\nMIIB\n-----END PRIVATE KEY-----\n")
        report = sd.scan_for_secrets(self.repo)
        self.assertIsNotNone(self._find(report, "server.pem"))

    def test_passphrase_protected_key_is_not_danger(self):
        """An encrypted key is the correct way to store one. Report, do not fail."""
        enc = self.repo / "vault.priv"
        enc.write_bytes(b'{"kdf": "scrypt", "salt": "aaaa", "nonce": "bbbb", "ct": "cccc"}')
        _git(self.repo, "add", "--force", "vault.priv")
        _git(self.repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-m", "v")

        report = sd.scan_for_secrets(self.repo)
        finding = self._find(report, "vault.priv")
        self.assertIsNotNone(finding)
        self.assertEqual(finding["status"], "warning")


class TestTextSecrets(unittest.TestCase):
    """The original regex patterns must keep working."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.repo = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_aws_access_key_still_detected(self):
        (self.repo / "config.yml").write_text("key: AKIAIOSFODNN7EXAMPLE\n", encoding="utf-8")
        report = sd.scan_for_secrets(self.repo)
        self.assertEqual(report["status"], "danger")

    def test_clean_repository_is_ok(self):
        (self.repo / "README.md").write_text("# Nothing secret here\n", encoding="utf-8")
        report = sd.scan_for_secrets(self.repo)
        self.assertEqual(report["status"], "ok")
        self.assertEqual(report["findings"], [])


if __name__ == "__main__":
    unittest.main()
