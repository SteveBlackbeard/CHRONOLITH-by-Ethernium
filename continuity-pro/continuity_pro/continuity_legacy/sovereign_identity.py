import os
import json
import hashlib
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

# ETHERNIUM SOVEREIGN IDENTITY (v1.0.0 - ED25519)
# -----------------------------------------------
# Purpose: Cryptographic signing and verification of Project DNA.

KEY_DIR = Path(".continuity/keys")
PRIV_KEY = KEY_DIR / "sovereign.priv"
PUB_KEY = KEY_DIR / "sovereign.pub"

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
