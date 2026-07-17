import hashlib
import pytest
from pathlib import Path
import sys

# CONTINUITY LEGACY: Logic Audit Tests (v2.1.1 - RFC 6962 Hardened)
# ------------------------------------------------------------------

sys.path.append(str(Path(__file__).parent.parent / 'continuity_lite' / 'continuity_legacy'))

from run_continuity_lite import (
    build_merkle_root,
    calculate_sha256,
    sign_state,
    verify_signature,
    leaf_hash,
)

# --- SHA-256 Tests ---

def test_calculate_sha256(tmp_path):
    test_file = tmp_path / "test.txt"
    content = b"Ethernium Continuity Legacy"
    test_file.write_bytes(content)
    expected = hashlib.sha256(content).hexdigest()
    assert calculate_sha256(test_file) == expected

def test_calculate_sha256_missing():
    assert calculate_sha256(Path("non_existent_phantom.txt")) == ""

def test_calculate_sha256_accepts_str_path(tmp_path):
    # API parity with Pro/Omega: accept a plain string, not only a Path.
    f = tmp_path / "x.txt"
    f.write_bytes(b"content")
    assert calculate_sha256(str(f)) == calculate_sha256(f)

# --- Merkle Tree Tests (RFC 6962 compliant) ---

def test_build_merkle_root_empty():
    assert build_merkle_root([]) == "0" * 64

def test_build_merkle_root_single():
    h1 = "abc123"
    # Single node: leaf hash = H(0x00 || "abc123")
    expected = hashlib.sha256(b"\x00" + b"abc123").hexdigest()
    assert build_merkle_root([h1]) == expected

def test_build_merkle_root_even():
    # 2 nodes: sorted ["a", "b"]
    # Leaf: L0 = H(0x00 || "a"), L1 = H(0x00 || "b")
    # Root: H(0x01 || L0 || L1)
    L0 = hashlib.sha256(b"\x00a").hexdigest()
    L1 = hashlib.sha256(b"\x00b").hexdigest()
    expected = hashlib.sha256(b"\x01" + (L0 + L1).encode("utf-8")).hexdigest()
    assert build_merkle_root(["b", "a"]) == expected

def test_build_merkle_root_odd():
    # 3 nodes sorted: ["a", "b", "c"]
    # Leaves: L0=H(0x00||"a"), L1=H(0x00||"b"), L2=H(0x00||"c")
    # Padded: L3 = L2 (duplicate)
    # Level 1: N0=H(0x01||L0||L1), N1=H(0x01||L2||L3)
    # Root: H(0x01||N0||N1)
    L0 = hashlib.sha256(b"\x00a").hexdigest()
    L1 = hashlib.sha256(b"\x00b").hexdigest()
    L2 = hashlib.sha256(b"\x00c").hexdigest()
    N0 = hashlib.sha256(b"\x01" + (L0 + L1).encode("utf-8")).hexdigest()
    N1 = hashlib.sha256(b"\x01" + (L2 + L2).encode("utf-8")).hexdigest()
    expected = hashlib.sha256(b"\x01" + (N0 + N1).encode("utf-8")).hexdigest()
    assert build_merkle_root(["c", "b", "a"]) == expected

def test_merkle_deterministic_order():
    """Tree must be order-independent (sorted internally)."""
    assert build_merkle_root(["z", "a", "m"]) == build_merkle_root(["a", "m", "z"])

# --- State Signature Tests (Expert #1: Cybersecurity) ---

def test_sign_state_deterministic():
    data = {"phase": "stable", "last_update": "2026-01-01T00:00:00"}
    sig1 = sign_state(data)
    sig2 = sign_state(data)
    assert sig1 == sig2
    assert len(sig1) == 64  # SHA-256 hex digest

def test_sign_state_excludes_signature_field():
    data = {"phase": "stable", "signature": "old_sig"}
    sig = sign_state(data)
    # Changing the signature field should NOT change the hash
    data2 = {"phase": "stable", "signature": "different_sig"}
    assert sign_state(data2) == sig

def test_sign_state_detects_tampering():
    data = {"phase": "stable", "last_update": "2026-01-01T00:00:00"}
    sig = sign_state(data)
    data["phase"] = "compromised"
    assert sign_state(data) != sig

# --- Signature Verification (closes the write-only-signature gap) ---

def test_verify_signature_accepts_valid():
    data = {"phase": "stable", "last_update": "2026-01-01T00:00:00"}
    data["signature"] = sign_state(data)
    assert verify_signature(data) is True

def test_verify_signature_rejects_tampered_state():
    data = {"phase": "stable", "last_update": "2026-01-01T00:00:00"}
    data["signature"] = sign_state(data)
    data["merkle_root"] = "deadbeef" * 8  # edited after signing
    assert verify_signature(data) is False

def test_verify_signature_absent_is_unverifiable_not_rejected():
    assert verify_signature({"phase": "stable"}) is True

# --- Path-Bound Merkle Leaves (root reacts to renames / content swaps) ---

def test_leaf_hash_binds_filename():
    content_h = calculate_sha256(Path("non_existent_phantom.txt")) or "abc"
    assert leaf_hash("A.md", content_h) != leaf_hash("B.md", content_h)

def test_leaf_hash_content_swap_changes_root():
    # Two files swapping content must change the root when leaves are path-bound.
    ha, hb = "hash_a", "hash_b"
    original = build_merkle_root([leaf_hash("A.md", ha), leaf_hash("B.md", hb)])
    swapped = build_merkle_root([leaf_hash("A.md", hb), leaf_hash("B.md", ha)])
    assert original != swapped


