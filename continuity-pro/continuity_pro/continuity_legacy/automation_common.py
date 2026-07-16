from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class Color:
    """Terminal color constants for standardized elite CLI feedback."""
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def echo(text: str, color: str = "") -> None:
    """Prints text to the console with optional color formatting.

    Args:
        text: The string to be printed.
        color: The ANSI color code to apply (e.g., Color.GREEN).
    """
    if color:
        print(f"{color}{text}{Color.END}")
    else:
        print(text)


DEFAULT_CONFIG = {
    "template_name": "CONTINUITY LEGACY",
    "project_name": "YOUR_PROJECT",
    "project_slug": "your_project",
    "context_file": "PROJECT_CONTEXT.md",
    "state_file": "STATE.json",
    "roadmap_file": "ROADMAP.md",
    "continuity_dir": ".continuity",
    "outputs_dir": "outputs/continuity",
    "external_docs": {
        "enabled": False,
        "folder_name": "YOUR_PROJECTDEV",
        "root_override": "",
    },
    "metadata": {
        "generated_by": "Continuity Legacy by Ethernium",
        "tool_version": "5.0.0",
        "creator": "@Steveblackbeard",
        "include_in_reports": True,
    },
}

ALLOWED_MEMBERSHIP_STATUSES = [
    "canonical",
    "bridge",
    "archive_source",
    "external_optional",
]

# v2.1.1 Crystallization: Governance Thresholds
ENTROPY_THRESHOLD = 6.5  # Bits per character (Shannon Entropy)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# Canonical config filename; the underscore spelling is accepted on read for
# backward compatibility with earlier versions that wrote it.
CONFIG_FILENAME = "continuity-legacy.json"
_CONFIG_FILENAME_LEGACY = "continuity_legacy.json"


def resolve_config_file(repo_root: str | Path) -> Path:
    """Return the config file to read: an existing hyphen or legacy underscore
    file if present, else the canonical hyphen path."""
    root = Path(repo_root)
    canonical = root / CONFIG_FILENAME
    if canonical.exists():
        return canonical
    legacy = root / _CONFIG_FILENAME_LEGACY
    if legacy.exists():
        return legacy
    return canonical


def resolve_repo_root(repo_root: str | Path | None, current_file: str | Path) -> Path:
    if repo_root:
        return Path(repo_root).resolve()

    # v2.1.1: Intelligent Upward Discovery to protect hierarchy sovereignty
    start_path = Path(current_file).resolve().parent
    for parent in [start_path] + list(start_path.parents):
        if (parent / CONFIG_FILENAME).exists() or (parent / _CONFIG_FILENAME_LEGACY).exists() or (parent / ".continuity").exists():
            return parent

    # Fallback: walk up at most 3 levels without indexing past the filesystem root.
    parents = start_path.parents
    return parents[min(2, len(parents) - 1)] if len(parents) else start_path


def load_config(repo_root: Path) -> dict:
    """Loads and merges the continuity-legacy.json configuration.

    Args:
        repo_root: The filesystem path to the root of the project.

    Returns:
        A dictionary containing the merged project configuration.
    """
    config_file = resolve_config_file(repo_root)
    payload = {}
    if config_file.exists():
        payload = json.loads(config_file.read_text(encoding="utf-8"))

    return _deep_merge(DEFAULT_CONFIG, payload)


def save_config(repo_root: Path, config: dict) -> None:
    """Saves the continuity-legacy.json configuration to the repository root.

    Args:
        repo_root: The filesystem path to the root of the project.
        config: The configuration dictionary to persist.
    """
    config_file = repo_root / CONFIG_FILENAME
    config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")


def config_path(repo_root: str | Path) -> Path:
    # Return an existing config (hyphen or legacy underscore) or the canonical path.
    return resolve_config_file(repo_root)


def read_text(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8", errors="ignore")


def write_text(path: str | Path, content: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content.rstrip() + "\n", encoding="utf-8")


def read_json(path: str | Path, default: Any | None = None) -> Any:
    file_path = Path(path)
    if not file_path.exists():
        return deepcopy(default)
    return json.loads(file_path.read_text(encoding="utf-8"))


def write_json(path: str | Path, payload: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def build_context_snapshot(repo_root: Path, external_root_override: Path | None = None) -> dict:
    """Builds a comprehensive snapshot of the project context from multiple sources.

    Args:
        repo_root: The root directory of the project.
        external_root_override: Optional path to an external documentation root.

    Returns:
        A dictionary containing the aggregated 'truth' of the project.
    """
    config = load_config(repo_root)
    state = read_json(state_path(repo_root, config), {})
    context_text = read_text(context_path(repo_root, config))
    roadmap_text = read_text(roadmap_path(repo_root, config))

    return {
        "project_name": config.get("project_name"),
        "project_slug": config.get("project_slug"),
        "phase": state.get("status", "unknown"),
        "next_actions": state.get("next_actions", []),
        "context_summary": context_text[:2000],
        "roadmap_summary": roadmap_text[:2000],
        "last_decision": state.get("last_decision", "none"),
        "timestamp": utc_now_iso(),
    }


def context_path(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    config = config or load_config(repo_root)
    return Path(repo_root) / config["context_file"]


def state_path(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    config = config or load_config(repo_root)
    return Path(repo_root) / config["state_file"]


def roadmap_path(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    config = config or load_config(repo_root)
    return Path(repo_root) / config["roadmap_file"]


def continuity_dir(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    config = config or load_config(repo_root)
    return Path(repo_root) / config["continuity_dir"]


def continuity_doc_path(repo_root: str | Path, name: str, config: dict[str, Any] | None = None) -> Path:
    return continuity_dir(repo_root, config) / name


def outputs_dir(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    config = config or load_config(repo_root)
    return Path(repo_root) / config["outputs_dir"]


def bootstrap_output_path(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    return outputs_dir(repo_root, config) / "context_bootstrap_summary.json"


def continuity_report_path(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    return outputs_dir(repo_root, config) / "continuity_cycle_report.json"


def dependency_map_path(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    return continuity_dir(repo_root, config) / "registry" / "document_dependency_map.json"


def membership_registry_path(repo_root: str | Path, config: dict[str, Any] | None = None) -> Path:
    return continuity_dir(repo_root, config) / "registry" / "system_membership_registry.json"


def load_dependency_map(repo_root: str | Path, config: dict[str, Any] | None = None) -> dict[str, Any]:
    return read_json(dependency_map_path(repo_root, config), {"version": "1.0", "documents": []}) or {
        "version": "1.0",
        "documents": [],
    }


def load_membership_registry(repo_root: str | Path, config: dict[str, Any] | None = None) -> dict[str, Any]:
    return read_json(
        membership_registry_path(repo_root, config),
        {
            "version": "1.0",
            "allowed_statuses": ALLOWED_MEMBERSHIP_STATUSES,
            "entries": [],
        },
    ) or {
        "version": "1.0",
        "allowed_statuses": ALLOWED_MEMBERSHIP_STATUSES,
        "entries": [],
    }


def is_ignored(repo_root: str | Path, rel_path: str) -> bool:
    ignore_file = Path(repo_root) / ".continuityignore"
    if not ignore_file.exists():
        return False
    
    import fnmatch
    patterns = [line.strip() for line in ignore_file.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
    for pattern in patterns:
        if fnmatch.fnmatch(rel_path, pattern):
            return True
    return False


def external_root(
    repo_root: str | Path,
    config: dict[str, Any] | None = None,
    override: str | Path | None = None,
) -> Path | None:
    config = config or load_config(repo_root)
    external_cfg = config.get("external_docs", {})
    if override:
        return Path(override).resolve()
    root_override = str(external_cfg.get("root_override") or "").strip()
    if root_override:
        return Path(root_override).resolve()
    if not external_cfg.get("enabled"):
        return None
    return Path(repo_root).resolve().parent / str(external_cfg.get("folder_name") or "PROJECTDEV")


def calculate_sha256(path: str | Path) -> str:
    """Calculates the SHA-256 hash of a file for high-fidelity DNA synthesis."""
    import hashlib
    p = Path(path)
    if not p.exists():
        return ""
    return hashlib.sha256(p.read_bytes()).hexdigest()


# Merkle leaf format tag; bumped when leaf derivation changes so an upgrade
# re-baselines once instead of raising a false drift alarm.
LEAF_FORMAT = "path-bound-v1"


def path_bound_leaf(rel_path: str, content_hash: str) -> str:
    """Bind the file path into the Merkle leaf.

    Content-only leaves make the root blind to structure: a rename or a content
    swap between two files leaves the root unchanged (build_merkle_tree also sorts
    leaves, discarding order). Hashing the path with the content makes both
    mutations alter the root."""
    import hashlib
    return hashlib.sha256(f"{rel_path}\n{content_hash}".encode("utf-8")).hexdigest()


def sign_state(data: dict) -> str:
    """Deterministic SHA-256 signature over the state record (excluding the
    signature field itself)."""
    import hashlib
    serialized = json.dumps({k: v for k, v in data.items() if k != "signature"}, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def verify_signature(state: dict) -> bool:
    """Recompute and compare the state signature.

    A missing signature is unverifiable (returns True so pre-signature states are
    not falsely rejected); a present-but-mismatched signature means the record was
    tampered with (returns False)."""
    stored = state.get("signature")
    if not stored:
        return True
    return sign_state(state) == stored


# ── Sovereign Ed25519 signatures ─────────────────────────────────────────────
# The SHA-256 "signature" above is honestly a checksum: it detects accidental or
# naive edits, but an informed attacker simply recomputes it. Ed25519 closes that
# hole — without the private key the baseline cannot be re-signed. Lazy imports
# keep `cryptography` an optional dependency (no key material -> checksum mode).

_SIGNED_FIELDS_EXCLUDED = ("signature", "sovereign_signature")


def state_payload_bytes(state: dict) -> bytes:
    """Canonical byte serialization of a state record for signing/verification."""
    clean = {k: v for k, v in state.items() if k not in _SIGNED_FIELDS_EXCLUDED}
    return json.dumps(clean, sort_keys=True).encode("utf-8")


def load_sovereign_keys(repo_root: str | Path) -> tuple[bytes | None, bytes | None]:
    """Load raw Ed25519 key material from <root>/.continuity/keys (repo-rooted,
    unlike SovereignIdentity which resolves relative to the process CWD)."""
    key_dir = Path(repo_root) / ".continuity" / "keys"
    priv = key_dir / "sovereign.priv"
    pub = key_dir / "sovereign.pub"
    return (
        priv.read_bytes() if priv.exists() else None,
        pub.read_bytes() if pub.exists() else None,
    )


def generate_sovereign_keys(repo_root: str | Path) -> tuple[Path, Path]:
    """Generate and persist a raw Ed25519 keypair for this repository."""
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.hazmat.primitives import serialization

    key_dir = Path(repo_root) / ".continuity" / "keys"
    key_dir.mkdir(parents=True, exist_ok=True)
    private_key = ed25519.Ed25519PrivateKey.generate()
    priv_path = key_dir / "sovereign.priv"
    pub_path = key_dir / "sovereign.pub"
    priv_path.write_bytes(
        private_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )
    pub_path.write_bytes(
        private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
    )
    return priv_path, pub_path


def ed25519_sign(private_bytes: bytes, data: bytes) -> str:
    from cryptography.hazmat.primitives.asymmetric import ed25519

    return ed25519.Ed25519PrivateKey.from_private_bytes(private_bytes).sign(data).hex()


def ed25519_verify(public_bytes: bytes, data: bytes, signature_hex: str) -> bool:
    try:
        from cryptography.hazmat.primitives.asymmetric import ed25519

        ed25519.Ed25519PublicKey.from_public_bytes(public_bytes).verify(
            bytes.fromhex(signature_hex), data
        )
        return True
    except Exception:
        return False


def sovereign_sign_state(state: dict, private_bytes: bytes, public_bytes: bytes) -> dict:
    """Attach a real Ed25519 signature (and the signer's public key) to a state."""
    state["sovereign_public_key"] = public_bytes.hex()
    state["sovereign_signature"] = ed25519_sign(private_bytes, state_payload_bytes(state))
    return state


def verify_sovereign_state(state: dict, trusted_public: bytes | None = None) -> bool | None:
    """Verify the Ed25519 state signature.

    Returns None when no sovereign signature is present (checksum mode). The
    trust anchor is the LOCAL public key when available — verifying only against
    the embedded key would let an attacker swap in their own keypair."""
    signature = state.get("sovereign_signature")
    if not signature:
        return None
    embedded = state.get("sovereign_public_key", "")
    public = trusted_public or (bytes.fromhex(embedded) if embedded else None)
    if public is None:
        return False
    if trusted_public and embedded and embedded != trusted_public.hex():
        return False
    return ed25519_verify(public, state_payload_bytes(state), signature)


# ── DNA transparency chain ───────────────────────────────────────────────────
# A single stored merkle_root only proves the LATEST state; every re-crystallize
# overwrites history. The chain is an append-only log (Certificate-Transparency
# style): each entry hash-links to the previous one, so the full lineage of the
# project DNA is verifiable and history rewrites are detectable.

CHAIN_FILENAME = "dna_chain.jsonl"


def chain_path(repo_root: str | Path) -> Path:
    return Path(repo_root) / ".continuity" / CHAIN_FILENAME


def _chain_entry_hash(entry: dict) -> str:
    import hashlib

    clean = {k: v for k, v in entry.items() if k not in ("entry_hash", "sovereign_signature")}
    return hashlib.sha256(json.dumps(clean, sort_keys=True).encode("utf-8")).hexdigest()


def read_chain(repo_root: str | Path) -> list[dict]:
    path = chain_path(repo_root)
    if not path.exists():
        return []
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            entries.append(json.loads(line))
    return entries


def append_chain_entry(
    repo_root: str | Path,
    merkle_root: str,
    *,
    private_bytes: bytes | None = None,
) -> dict | None:
    """Append a crystallization event. No-op when the root is unchanged."""
    entries = read_chain(repo_root)
    prev = entries[-1] if entries else None
    if prev and prev.get("merkle_root") == merkle_root:
        return None
    entry = {
        "seq": (prev["seq"] + 1) if prev else 0,
        "timestamp": utc_now_iso(),
        "merkle_root": merkle_root,
        "leaf_format": LEAF_FORMAT,
        "prev_entry_hash": prev["entry_hash"] if prev else "0" * 64,
    }
    entry["entry_hash"] = _chain_entry_hash(entry)
    if private_bytes:
        entry["sovereign_signature"] = ed25519_sign(private_bytes, entry["entry_hash"].encode("utf-8"))
    path = chain_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")
    return entry


def verify_chain(repo_root: str | Path, trusted_public: bytes | None = None) -> tuple[bool, list[str]]:
    """Verify linkage, per-entry hashes, sequence monotonicity, and (when a
    trusted public key exists) the Ed25519 signature of every entry."""
    issues: list[str] = []
    prev_hash = "0" * 64
    prev_seq = -1
    for entry in read_chain(repo_root):
        seq = entry.get("seq")
        if seq != prev_seq + 1:
            issues.append(f"seq {seq}: non-monotonic (expected {prev_seq + 1})")
        if entry.get("prev_entry_hash") != prev_hash:
            issues.append(f"seq {seq}: broken linkage to previous entry")
        if _chain_entry_hash(entry) != entry.get("entry_hash"):
            issues.append(f"seq {seq}: entry hash mismatch (entry edited)")
        if trusted_public is not None:
            signature = entry.get("sovereign_signature", "")
            if not signature or not ed25519_verify(
                trusted_public, str(entry.get("entry_hash", "")).encode("utf-8"), signature
            ):
                issues.append(f"seq {seq}: invalid or missing sovereign signature")
        prev_hash = entry.get("entry_hash", prev_hash)
        prev_seq = seq if isinstance(seq, int) else prev_seq + 1
    return (not issues, issues)


# ── Merkle inclusion proofs ──────────────────────────────────────────────────
# A Merkle tree used only to publish its root is just an expensive flat hash.
# Inclusion proofs are the point: verify that ONE document belongs to the DNA in
# O(log n) hashes, without rehashing the repository.


def merkle_levels(leaf_values: list[str]) -> list[list[str]]:
    """All tree levels (leaves first), replicating build_merkle_tree exactly:
    sorted leaves, H(0x00||leaf), odd levels padded by duplicating the last node,
    internal nodes H(0x01||left+right). Each stored level includes its padding so
    sibling lookup is index^1."""
    import hashlib

    if not leaf_values:
        return [[]]
    current = [hashlib.sha256(b"\x00" + v.encode("utf-8")).hexdigest() for v in sorted(leaf_values)]
    levels = []
    while True:
        if len(current) > 1 and len(current) % 2 != 0:
            current = current + [current[-1]]
        levels.append(current)
        if len(current) == 1:
            return levels
        current = [
            hashlib.sha256(b"\x01" + (current[i] + current[i + 1]).encode("utf-8")).hexdigest()
            for i in range(0, len(current), 2)
        ]


def merkle_inclusion_proof(leaf_values: list[str], target_leaf: str) -> list[dict]:
    """Audit path for target_leaf: [{'hash': sibling, 'position': 'left'|'right'}, ...]."""
    import hashlib

    sorted_leaves = sorted(leaf_values)
    if target_leaf not in sorted_leaves:
        raise ValueError("leaf not present in the tree")
    levels = merkle_levels(leaf_values)
    index = sorted_leaves.index(target_leaf)
    proof: list[dict] = []
    for level in levels[:-1]:
        sibling = index ^ 1
        proof.append({
            "hash": level[sibling],
            "position": "left" if sibling < index else "right",
        })
        index //= 2
    return proof


def verify_inclusion_proof(leaf_value: str, proof: list[dict], root: str) -> bool:
    import hashlib

    node = hashlib.sha256(b"\x00" + leaf_value.encode("utf-8")).hexdigest()
    for step in proof:
        sibling = str(step.get("hash", ""))
        if step.get("position") == "left":
            combined = sibling + node
        else:
            combined = node + sibling
        node = hashlib.sha256(b"\x01" + combined.encode("utf-8")).hexdigest()
    return node == root


# ── Incremental hashing ──────────────────────────────────────────────────────
# Rehashing every file on every check is the guardian's real bottleneck (and the
# #1 reason users disable pre-push hooks). mtime+size gate the rehash.

HASH_CACHE_FILENAME = "hash_cache.json"


def load_hash_cache(repo_root: str | Path) -> dict:
    return read_json(Path(repo_root) / ".continuity" / HASH_CACHE_FILENAME, {}) or {}


def save_hash_cache(repo_root: str | Path, cache: dict) -> None:
    write_json(Path(repo_root) / ".continuity" / HASH_CACHE_FILENAME, cache)


def calculate_sha256_cached(path: str | Path, cache: dict) -> str:
    import os

    p = Path(path)
    if not p.exists():
        return ""
    stat = os.stat(p)
    token = f"{stat.st_mtime_ns}:{stat.st_size}"
    key = str(p)
    cached = cache.get(key)
    if cached and cached.get("token") == token:
        return cached["sha256"]
    digest = calculate_sha256(p)
    cache[key] = {"token": token, "sha256": digest}
    return digest


def build_merkle_tree(hashes: list[str]) -> str:
    """RFC 6962 compliant Merkle Tree with leaf/node prefix hardening.
    
    Uses deterministic sorting and prefixed hashing:
    - Leaf nodes: H(0x00 || data)  
    - Internal nodes: H(0x01 || left || right)
    
    This prevents second-preimage attacks where an attacker crafts
    a different input set that produces the same root hash.
    """
    import hashlib
    if not hashes:
        return "0" * 64
    
    # Leaf nodes: H(0x00 || data)
    current_level = [hashlib.sha256(b"\x00" + h.encode("utf-8")).hexdigest() for h in sorted(hashes)]
    
    while len(current_level) > 1:
        next_level = []
        if len(current_level) % 2 != 0:
            current_level.append(current_level[-1])
            
        for i in range(0, len(current_level), 2):
            # Internal nodes: H(0x01 || left || right)
            combined = b"\x01" + (current_level[i] + current_level[i+1]).encode("utf-8")
            next_level.append(hashlib.sha256(combined).hexdigest())
        current_level = next_level
        
    return current_level[0]

# Alias for backward compatibility
build_merkle_root = build_merkle_tree


def calculate_context_entropy(text: str) -> float:
    """Calculates the Shannon Entropy of a text block to measure context volatility."""
    import math
    if not text:
        return 0.0
    
    # Calculate frequencies
    freqs = {}
    for char in text:
        freqs[char] = freqs.get(char, 0) + 1
    
    # Shannon Entropy formula
    length = len(text)
    entropy = 0.0
    for count in freqs.values():
        p = count / length
        entropy -= p * math.log2(p)
        
    return entropy
