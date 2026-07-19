#!/usr/bin/env python3
"""Sovereign vault tests: real sealed-box encryption, passphrase-protected keys,
key rotation (mini-PKI), attestations, and the checksum/Ed25519 field-exclusion
regression."""

import json
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

import automation_common as ac  # noqa: E402

if HAS_CRYPTO:
    import sovereign_vault as sv  # noqa: E402


@unittest.skipUnless(HAS_CRYPTO, "cryptography not installed")
class TestSealedBox(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        sv.generate_x25519_keys(self.tmp.name)
        self.priv = (Path(self.tmp.name) / "seal.priv").read_bytes()
        self.pub = (Path(self.tmp.name) / "seal.pub").read_bytes()

    def tearDown(self):
        self.tmp.cleanup()

    def test_roundtrip(self):
        secret = "datos confidenciales del proyecto".encode("utf-8")
        self.assertEqual(sv.open_sealed(sv.seal(secret, self.pub), self.priv), secret)

    def test_tampered_ciphertext_rejected(self):
        import base64
        blob = sv.seal(b"secret", self.pub)
        raw = bytearray(base64.b64decode(blob))
        raw[-1] ^= 0xFF  # flip one ciphertext bit
        with self.assertRaises(ValueError):
            sv.open_sealed(base64.b64encode(bytes(raw)).decode(), self.priv)

    def test_wrong_recipient_rejected(self):
        other_dir = Path(self.tmp.name) / "other"
        sv.generate_x25519_keys(other_dir)
        other_priv = (other_dir / "seal.priv").read_bytes()
        with self.assertRaises(ValueError):
            sv.open_sealed(sv.seal(b"secret", self.pub), other_priv)

    def test_legacy_insecure_format_refused(self):
        import base64
        legacy = base64.b64encode(b"\x00" * 32 + b"plaintext-was-never-encrypted").decode()
        with self.assertRaises(ValueError):
            sv.open_sealed(legacy, self.priv)

    def test_nondeterministic_ciphertext(self):
        # Ephemeral keys + random nonce: sealing twice must not leak equality.
        self.assertNotEqual(sv.seal(b"same", self.pub), sv.seal(b"same", self.pub))


@unittest.skipUnless(HAS_CRYPTO, "cryptography not installed")
class TestPassphraseVault(unittest.TestCase):
    def test_roundtrip_and_wrong_passphrase(self):
        raw = b"\x01" * 32
        payload = sv.encrypt_private_key(raw, "correct horse battery staple")
        self.assertEqual(sv.decrypt_private_key(payload, "correct horse battery staple"), raw)
        with self.assertRaises(ValueError):
            sv.decrypt_private_key(payload, "wrong")

    def test_locked_vault_degrades_to_verify_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            key_dir = root / ".chronolith" / "keys"
            ac.generate_sovereign_keys(root)
            priv_path = key_dir / "sovereign.priv"
            payload = sv.encrypt_private_key(priv_path.read_bytes(), "s3cret")
            priv_path.with_suffix(".priv.enc").write_text(json.dumps(payload), encoding="utf-8")
            priv_path.unlink()
            import os
            os.environ.pop("CHRONOLITH_PASSPHRASE", None)
            priv, pub = ac.load_sovereign_keys(root)
            self.assertIsNone(priv, "locked vault must not expose the key")
            self.assertIsNotNone(pub, "public key must remain available for verification")
            os.environ["CHRONOLITH_PASSPHRASE"] = "s3cret"
            try:
                priv2, _ = ac.load_sovereign_keys(root)
                self.assertIsNotNone(priv2, "correct passphrase must unlock the vault")
            finally:
                os.environ.pop("CHRONOLITH_PASSPHRASE", None)


@unittest.skipUnless(HAS_CRYPTO, "cryptography not installed")
class TestKeyRotation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = Path(self.tmp.name)
        self.key_dir = self.root / ".chronolith" / "keys"
        ac.generate_sovereign_keys(self.root)
        self.old_priv, self.old_pub = ac.load_sovereign_keys(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def _rotate(self):
        from cryptography.hazmat.primitives.asymmetric import ed25519
        from cryptography.hazmat.primitives import serialization
        new = ed25519.Ed25519PrivateKey.generate()
        new_priv = new.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())
        new_pub = new.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        sv.record_rotation(self.key_dir, self.old_priv, self.old_pub, new_pub, "2026-07-16T00:00:00")
        (self.key_dir / "sovereign.priv").write_bytes(new_priv)
        (self.key_dir / "sovereign.pub").write_bytes(new_pub)
        return new_priv, new_pub

    def test_history_walk_includes_retired_key(self):
        _new_priv, new_pub = self._rotate()
        keys = sv.historically_valid_pubkeys(self.key_dir, new_pub)
        self.assertEqual(keys[0], new_pub)
        self.assertIn(self.old_pub, keys)

    def test_forged_handoff_stops_the_walk(self):
        _new_priv, new_pub = self._rotate()
        path = self.key_dir / sv.ROTATIONS_FILENAME
        entry = json.loads(path.read_text().splitlines()[0])
        entry["old_pub"] = "ab" * 32  # attacker claims THEIR key was the ancestor
        path.write_text(json.dumps(entry, sort_keys=True) + "\n", encoding="utf-8")
        keys = sv.historically_valid_pubkeys(self.key_dir, new_pub)
        self.assertEqual(keys, [new_pub], "forged hand-off must not extend trust")

    def test_chain_survives_rotation(self):
        ac.append_chain_entry(self.root, "root-A", private_bytes=self.old_priv)
        new_priv, new_pub = self._rotate()
        ac.append_chain_entry(self.root, "root-B", private_bytes=new_priv)
        keys = sv.historically_valid_pubkeys(self.key_dir, new_pub)
        ok, issues = ac.verify_chain(self.root, trusted_public=keys)
        self.assertTrue(ok, issues)
        # Current key alone must NOT validate the pre-rotation entry.
        ok_single, _ = ac.verify_chain(self.root, trusted_public=new_pub)
        self.assertFalse(ok_single)


@unittest.skipUnless(HAS_CRYPTO, "cryptography not installed")
class TestAttestations(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = Path(self.tmp.name)
        ac.generate_sovereign_keys(self.root)
        self.priv, self.pub = ac.load_sovereign_keys(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def test_sign_and_verify(self):
        att = sv.build_attestation("DOC.md", "abc123", self.pub, "2026-07-16T00:00:00")
        sv.sign_attestation(att, self.priv)
        ok, reason = sv.verify_attestation(att, [self.pub])
        self.assertTrue(ok, reason)

    def test_unauthorized_signer_rejected(self):
        att = sv.build_attestation("DOC.md", "abc123", self.pub, "2026-07-16T00:00:00")
        sv.sign_attestation(att, self.priv)
        ok, reason = sv.verify_attestation(att, [])
        self.assertFalse(ok)
        self.assertIn("not an authorized", reason)

    def test_tampered_payload_rejected(self):
        att = sv.build_attestation("DOC.md", "abc123", self.pub, "2026-07-16T00:00:00")
        sv.sign_attestation(att, self.priv)
        att["sha256"] = "evil"
        ok, _ = sv.verify_attestation(att, [self.pub])
        self.assertFalse(ok)


class TestChecksumFieldExclusion(unittest.TestCase):
    """Regression: the checksum must ignore signature-family fields, or adding
    the Ed25519 block after checksumming trips a false tamper alarm."""

    def test_checksum_stable_across_sovereign_fields(self):
        state = {"phase": "pro", "merkle_root": "abc"}
        checksum = ac.sign_state(state)
        state["signature"] = checksum
        state["sovereign_public_key"] = "aa" * 32
        state["sig_alg"] = "ed25519"
        state["sovereign_signature"] = "bb" * 64
        self.assertEqual(ac.sign_state(state), checksum)
        self.assertTrue(ac.verify_signature(state))


if __name__ == "__main__":
    unittest.main()
