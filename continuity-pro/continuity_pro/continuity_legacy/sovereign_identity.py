import os
import json
import hashlib
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

# ETHERNIUM SOVEREIGN IDENTITY (v2.0.0 - THE_CHOSEN_ONES PROTOCOL)
# ---------------------------------------------------------------
# Purpose: Cryptographic sealing and multi-key authorization.

KEY_DIR = Path(".continuity/keys")
PRIV_KEY = KEY_DIR / "sovereign.priv"
PUB_KEY = KEY_DIR / "sovereign.pub"
CHOSEN_ONES_FILE = KEY_DIR / "chosen_ones.json"

class SovereignIdentity:
    def __init__(self):
        self._private_key = None
        self._public_key = None
        self._load_keys()

    def _load_keys(self):
        if PRIV_KEY.exists():
            raw = PRIV_KEY.read_bytes()
            self._private_key = ed25519.Ed25519PrivateKey.from_private_bytes(raw)
            self._public_key = self._private_key.public_key()
        elif PUB_KEY.exists():
            raw = PUB_KEY.read_bytes()
            self._public_key = ed25519.Ed25519PublicKey.from_public_bytes(raw)
            
    def get_public_bytes(self) -> bytes:
        if not self._public_key: return b""
        return self._public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )

    def _load_seal_keys(self) -> tuple[bytes | None, bytes | None]:
        """X25519 encryption keypair (separate from the Ed25519 signing key)."""
        seal_priv = KEY_DIR / "seal.priv"
        seal_pub = KEY_DIR / "seal.pub"
        return (
            seal_priv.read_bytes() if seal_priv.exists() else None,
            seal_pub.read_bytes() if seal_pub.exists() else None,
        )

    def seal_context(self, data: bytes) -> str:
        """Seals context with REAL encryption: ephemeral X25519 ECDH + HKDF +
        ChaCha20-Poly1305 (authenticated). The previous scheme was base64
        obfuscation — anyone reading the code could open it. Only the holder of
        seal.priv can open the new format, and tampering is detected."""
        try:
            from . import sovereign_vault
        except ImportError:
            import sovereign_vault
        _priv, pub = self._load_seal_keys()
        if pub is None:
            raise PermissionError(
                "[!] Encryption keypair missing. Run `sovereign-init` (v3.1+) to "
                "generate .continuity/keys/seal.pub / seal.priv."
            )
        return sovereign_vault.seal(data, pub)

    def open_context(self, sealed_data_b64: str) -> bytes:
        """Opens an ECNSEAL2 sealed context.

        Raises:
            PermissionError: If the X25519 private key is missing.
            ValueError: On tampering, wrong recipient, or the legacy insecure
                format (which is refused: it was never actually encrypted).
        """
        try:
            from . import sovereign_vault
        except ImportError:
            import sovereign_vault
        priv, _pub = self._load_seal_keys()
        if priv is None:
            raise PermissionError(
                "[!] X25519 private key required to open context. "
                "Ensure .continuity/keys/seal.priv exists."
            )
        return sovereign_vault.open_sealed(sealed_data_b64, priv)

    def authorize_collaborator(self, pub_key_hex: str):
        """Adds a collaborator to THE_CHOSEN_ONES."""
        # Ensure directory exists
        KEY_DIR.mkdir(parents=True, exist_ok=True)
        chosen = []
        if CHOSEN_ONES_FILE.exists():
            chosen = json.loads(CHOSEN_ONES_FILE.read_text())
        if pub_key_hex not in chosen:
            chosen.append(pub_key_hex)
            CHOSEN_ONES_FILE.write_text(json.dumps(chosen, indent=2))

    def is_authorized(self, pub_key_hex: str) -> bool:
        if pub_key_hex == self.get_public_bytes().hex(): return True
        if not CHOSEN_ONES_FILE.exists(): return False
        chosen = json.loads(CHOSEN_ONES_FILE.read_text())
        return pub_key_hex in chosen

    def sign_data(self, data: bytes) -> str:
        if not self._private_key:
            raise PermissionError("[!] Sovereign Private Key missing. Cannot sign.")
        signature = self._private_key.sign(data)
        return signature.hex()

    def verify_data(self, data: bytes, signature_hex: str) -> bool:
        if not self._public_key:
            return False
        try:
            signature = bytes.fromhex(signature_hex)
            self._public_key.verify(signature, data)
            return True
        except Exception:
            return False

    def sign_json(self, payload: dict) -> dict:
        """Signs a JSON payload by hashing and adding a 'signature' field."""
        # We exclude any existing signature to avoid recursion
        clean_payload = {k: v for k, v in payload.items() if k != "signature"}
        serialized = json.dumps(clean_payload, sort_keys=True).encode("utf-8")
        payload["signature"] = self.sign_data(serialized)
        return payload

    def verify_json(self, payload: dict) -> bool:
        """Verifies a signed JSON payload."""
        if "signature" not in payload: return False
        sig = payload["signature"]
        clean_payload = {k: v for k, v in payload.items() if k != "signature"}
        serialized = json.dumps(clean_payload, sort_keys=True).encode("utf-8")
        return self.verify_data(serialized, sig)

def get_identity() -> SovereignIdentity:
    return SovereignIdentity()
