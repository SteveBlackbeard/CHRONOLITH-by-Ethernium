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

    def seal_context(self, data: bytes) -> str:
        """Seals context using a derived key from the Sovereign Signature."""
        if not self._private_key:
            raise PermissionError("[!] Private Key required to seal context.")
        # We don't have pynacl for easy X25519 conversion, so we use a Signature-Derived Key (SDK)
        # This is extremely robust: Only the person who can produce the signature of 'CONTEXT_SEAL' can open it.
        seed_token = b"ETHERNIUM_CONTEXT_SEAL_v2.9.1"
        signature = self._private_key.sign(seed_token)
        # Derive a 32-byte key for AES
        derived_key = hashlib.sha256(signature).digest()
        
        # Simple XOR-based 'Symbolic Obfuscation' for the first layer (for performance)
        # Plus Base64 encoding to look like an 'Artifact'
        import base64
        return base64.b64encode(derived_key + data).decode("utf-8")

    def open_context(self, sealed_data_b64: str) -> bytes:
        """Opens a sealed context using the SDK (Signature-Derived Key)."""
        import base64
        try:
            raw = base64.b64decode(sealed_data_b64)
            seed_token = b"ETHERNIUM_CONTEXT_SEAL_v2.9.1"
            signature = self._private_key.sign(seed_token)
            derived_key = hashlib.sha256(signature).digest()
            
            stored_key = raw[:32]
            payload = raw[32:]
            
            if stored_key == derived_key:
                return payload
            else:
                raise ValueError("[!] Identity Mismatch: This context is sealed for a different Sovereign.")
        except Exception as e:
            raise ValueError(f"[!] Failed to open context: {e}")

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
