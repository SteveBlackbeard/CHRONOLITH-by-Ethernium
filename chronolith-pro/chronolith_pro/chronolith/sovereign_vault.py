"""Sovereign vault: real encryption, protected keys, and key rotation.

Closes the three honest limitations of a bare Ed25519 deployment:

1. *Signing does not encrypt* — `seal`/`open_sealed` implement an authenticated
   sealed box: ephemeral X25519 ECDH -> HKDF-SHA256 -> ChaCha20-Poly1305 (AEAD).
   Only the holder of the recipient's X25519 private key can open it, and any
   tampering with the ciphertext is detected by the AEAD tag.
2. *A private key on disk is the weak point* — `encrypt_private_key` protects
   key material at rest with a passphrase: scrypt (memory-hard KDF, GPU-hostile)
   derives the wrapping key, ChaCha20-Poly1305 seals the seed.
3. *Not post-quantum* — every signature envelope carries `sig_alg` so a future
   ML-DSA (Dilithium) can drop in without a format break (crypto-agility), and
   the SHA-256 Merkle chain plus Bitcoin anchoring already provide a hash-based
   — i.e. post-quantum-resistant — second line of integrity evidence.

All `cryptography` imports are lazy: without the package the guardian still runs
in checksum mode; these features simply report themselves unavailable.
"""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path

SEAL_MAGIC = b"ECNSEAL2"          # versioned format tag for sealed blobs
VAULT_VERSION = "scrypt-chacha20poly1305-v1"
SIG_ALG = "ed25519"               # crypto-agility: consumers must check this tag

_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1


# ── X25519 sealed box (real encryption; replaces the XOR/base64 obfuscation) ──

def generate_x25519_keys(key_dir: str | Path) -> tuple[Path, Path]:
    """Generate the encryption keypair. Kept SEPARATE from the Ed25519 signing
    key — reusing one key for signing and encryption is a classic design smell."""
    from cryptography.hazmat.primitives.asymmetric import x25519
    from cryptography.hazmat.primitives import serialization

    key_dir = Path(key_dir)
    key_dir.mkdir(parents=True, exist_ok=True)
    private = x25519.X25519PrivateKey.generate()
    priv_path = key_dir / "seal.priv"
    pub_path = key_dir / "seal.pub"
    priv_path.write_bytes(private.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    ))
    pub_path.write_bytes(private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    ))
    return priv_path, pub_path


def _derive_seal_key(shared: bytes, ephemeral_pub: bytes, recipient_pub: bytes) -> bytes:
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.hazmat.primitives import hashes

    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"ethernium-sealed-box-v2",
    ).derive(shared + ephemeral_pub + recipient_pub)


def seal(data: bytes, recipient_public: bytes) -> str:
    """Encrypt for the recipient. Anyone may seal (public key), only the
    recipient's private key opens. Output: base64(MAGIC||eph_pub||nonce||ct)."""
    from cryptography.hazmat.primitives.asymmetric import x25519
    from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
    from cryptography.hazmat.primitives import serialization

    ephemeral = x25519.X25519PrivateKey.generate()
    ephemeral_pub = ephemeral.public_key().public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
    )
    shared = ephemeral.exchange(x25519.X25519PublicKey.from_public_bytes(recipient_public))
    key = _derive_seal_key(shared, ephemeral_pub, recipient_public)
    nonce = os.urandom(12)
    ciphertext = ChaCha20Poly1305(key).encrypt(nonce, data, SEAL_MAGIC)
    return base64.b64encode(SEAL_MAGIC + ephemeral_pub + nonce + ciphertext).decode("ascii")


def open_sealed(blob_b64: str, recipient_private: bytes) -> bytes:
    """Open a sealed blob. Raises ValueError on tampering, wrong key, or the
    legacy insecure format (which must not be silently trusted)."""
    from cryptography.hazmat.primitives.asymmetric import x25519
    from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
    from cryptography.hazmat.primitives import serialization
    from cryptography.exceptions import InvalidTag

    raw = base64.b64decode(blob_b64)
    if not raw.startswith(SEAL_MAGIC):
        raise ValueError(
            "not an ECNSEAL2 blob (legacy seal_context output is obfuscation, "
            "not encryption — re-seal the data with the new format)"
        )
    body = raw[len(SEAL_MAGIC):]
    ephemeral_pub, nonce, ciphertext = body[:32], body[32:44], body[44:]
    private = x25519.X25519PrivateKey.from_private_bytes(recipient_private)
    recipient_pub = private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw
    )
    shared = private.exchange(x25519.X25519PublicKey.from_public_bytes(ephemeral_pub))
    key = _derive_seal_key(shared, ephemeral_pub, recipient_pub)
    try:
        return ChaCha20Poly1305(key).decrypt(nonce, ciphertext, SEAL_MAGIC)
    except InvalidTag as exc:
        raise ValueError("sealed context is corrupted or was sealed for a different key") from exc


# ── Passphrase-protected key material at rest ─────────────────────────────────

def encrypt_private_key(raw_key: bytes, passphrase: str) -> dict:
    """Wrap key material with a passphrase. scrypt is memory-hard: brute-forcing
    the passphrase costs RAM as well as CPU, which is what kills GPU farms."""
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

    salt = os.urandom(16)
    kek = Scrypt(salt=salt, length=32, n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P).derive(
        passphrase.encode("utf-8")
    )
    nonce = os.urandom(12)
    return {
        "vault": VAULT_VERSION,
        "salt": salt.hex(),
        "n": _SCRYPT_N, "r": _SCRYPT_R, "p": _SCRYPT_P,
        "nonce": nonce.hex(),
        "ciphertext": ChaCha20Poly1305(kek).encrypt(nonce, raw_key, b"sovereign-key").hex(),
    }


def decrypt_private_key(payload: dict, passphrase: str) -> bytes:
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
    from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
    from cryptography.exceptions import InvalidTag

    kek = Scrypt(
        salt=bytes.fromhex(payload["salt"]), length=32,
        n=int(payload["n"]), r=int(payload["r"]), p=int(payload["p"]),
    ).derive(passphrase.encode("utf-8"))
    try:
        return ChaCha20Poly1305(kek).decrypt(
            bytes.fromhex(payload["nonce"]), bytes.fromhex(payload["ciphertext"]), b"sovereign-key"
        )
    except InvalidTag as exc:
        raise ValueError("wrong passphrase or corrupted key vault") from exc


# ── Key rotation (mini-PKI: the old key blesses the new one) ─────────────────

ROTATIONS_FILENAME = "rotations.jsonl"


def _rotation_payload(old_pub_hex: str, new_pub_hex: str, timestamp: str) -> bytes:
    return json.dumps(
        {"type": "key-rotation", "old": old_pub_hex, "new": new_pub_hex, "ts": timestamp},
        sort_keys=True,
    ).encode("utf-8")


def record_rotation(key_dir: str | Path, old_priv: bytes, old_pub: bytes, new_pub: bytes, timestamp: str) -> dict:
    """Sign 'old key -> new key' with the OLD key: identity chronolith is
    provable, so history signed by retired keys still verifies."""
    from cryptography.hazmat.primitives.asymmetric import ed25519

    payload = _rotation_payload(old_pub.hex(), new_pub.hex(), timestamp)
    entry = {
        "type": "key-rotation",
        "old_pub": old_pub.hex(),
        "new_pub": new_pub.hex(),
        "ts": timestamp,
        "sig_alg": SIG_ALG,
        "signature": ed25519.Ed25519PrivateKey.from_private_bytes(old_priv).sign(payload).hex(),
    }
    path = Path(key_dir) / ROTATIONS_FILENAME
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")
    return entry


def historically_valid_pubkeys(key_dir: str | Path, current_pub: bytes | None) -> list[bytes]:
    """Walk the rotation log backwards from the current key, verifying each
    hand-off signature. Returns every public key that was legitimately the
    sovereign at some point (current first)."""
    from cryptography.hazmat.primitives.asymmetric import ed25519

    if current_pub is None:
        return []
    rotations_path = Path(key_dir) / ROTATIONS_FILENAME
    valid = [current_pub]
    if not rotations_path.exists():
        return valid
    entries = [json.loads(line) for line in rotations_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    cursor = current_pub.hex()
    for entry in reversed(entries):
        if entry.get("new_pub") != cursor:
            continue
        old_pub = bytes.fromhex(entry["old_pub"])
        payload = _rotation_payload(entry["old_pub"], entry["new_pub"], entry["ts"])
        try:
            ed25519.Ed25519PublicKey.from_public_bytes(old_pub).verify(
                bytes.fromhex(entry["signature"]), payload
            )
        except Exception:
            break  # forged hand-off: refuse to extend trust past it
        valid.append(old_pub)
        cursor = entry["old_pub"]
    return valid


# ── Attestations (multi-agent provenance over THE_CHOSEN_ONES) ───────────────

def key_fingerprint(public_bytes: bytes) -> str:
    """Human-verifiable fingerprint of a public key (SSH-style SHA256:<base64>).

    This is the missing piece of trust bootstrapping: the repository already ships
    `sovereign.pub`, but a verifier has no way to know that key is really yours
    and not one an attacker swapped in on a fork. You publish this fingerprint
    OUT OF BAND (README, profile, a talk), and a skeptic pins it with
    `verify --expect-fingerprint` — exactly how SSH host keys and Signal safety
    numbers work."""
    import base64
    import hashlib

    digest = hashlib.sha256(public_bytes).digest()
    return "SHA256:" + base64.b64encode(digest).decode("ascii").rstrip("=")


def build_attestation(rel_path: str, content_sha256: str, signer_pub: bytes, timestamp: str) -> dict:
    return {
        "type": "attestation",
        "file": rel_path,
        "sha256": content_sha256,
        "ts": timestamp,
        "signer_pub": signer_pub.hex(),
        "sig_alg": SIG_ALG,
    }


def attestation_payload(att: dict) -> bytes:
    clean = {k: v for k, v in att.items() if k != "signature"}
    return json.dumps(clean, sort_keys=True).encode("utf-8")


def sign_attestation(att: dict, private_bytes: bytes) -> dict:
    from cryptography.hazmat.primitives.asymmetric import ed25519

    att["signature"] = ed25519.Ed25519PrivateKey.from_private_bytes(private_bytes).sign(
        attestation_payload(att)
    ).hex()
    return att


def verify_attestation(att: dict, authorized_pubkeys: list[bytes]) -> tuple[bool, str]:
    """Signature must verify AND the signer must be an authorized identity
    (current sovereign, a rotated-out sovereign, or one of THE_CHOSEN_ONES)."""
    from cryptography.hazmat.primitives.asymmetric import ed25519

    signature = att.get("signature", "")
    signer_hex = att.get("signer_pub", "")
    if not signature or not signer_hex:
        return False, "attestation is unsigned"
    if signer_hex not in {p.hex() for p in authorized_pubkeys}:
        return False, "signer is not an authorized identity"
    try:
        ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(signer_hex)).verify(
            bytes.fromhex(signature), attestation_payload(att)
        )
        return True, "attestation verified"
    except Exception:
        return False, "signature does not match the attestation payload"
