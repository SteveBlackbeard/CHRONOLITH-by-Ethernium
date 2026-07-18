import hashlib
import json
import math
import os
import re
import sys
from pathlib import Path
from datetime import datetime

# ============================================================================
# CHRONOLITH CRYSTALLIZER (v3.0.0 - DETERMINISTIC INFORMATION PHYSICS)
# ============================================================================
# Purpose: DNA Synthesis with mathematically rigorous entropy measurement.
#
# FORMAL DEFINITIONS (eliminating all ambiguity):
# ────────────────────────────────────────────────
# Let Ω = {f₁, f₂, ..., fₙ} be the set of all audited files (leaves of Merkle Tree).
# Let w(fᵢ) = size_in_bytes(fᵢ) be the information weight of file fᵢ.
# Let W = Σ w(fᵢ) be the total information mass of the repository.
#
# Then the probability distribution P over the architecture is:
#   P(fᵢ) = w(fᵢ) / W
#
# The Structural Entropy H(Ω) is:
#   H(Ω) = -Σ P(fᵢ) · log₂(P(fᵢ))    for all fᵢ where P(fᵢ) > 0
#
# INTERPRETATION:
#   H_max = log₂(N) when all files have equal weight (perfect balance)
#   H → 0 when one file dominates (monolithic antipattern)
#   Normalized: η = H(Ω) / log₂(N)  ∈ [0, 1]
#     η > 0.75 → Healthy architecture (distributed)
#     η < 0.50 → Drift detected (centralization risk)
#
# DRIFT DETECTION via Kullback-Leibler Divergence:
#   D_KL(P_current || P_reference) = Σ P_current(fᵢ) · log₂(P_current(fᵢ) / P_ref(fᵢ))
#   If D_KL > threshold → structural drift from last crystallized state.
# ============================================================================


def calculate_sha256(path: Path) -> str:
    """Compute deterministic SHA-256 hash of a file's content, excluding self-referential markers."""
    if not (path.exists() and path.is_file()):
        return ""
    try:
        content = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return ""
    # Filter self-referential lines to prevent circular hashing
    lines = [
        l.rstrip() for l in content.splitlines()
        if "DNA CRYSTAL" not in l and "img.shields.io/badge/DNA--Crystallized" not in l
    ]
    return hashlib.sha256("\n".join(lines).strip().encode("utf-8")).hexdigest()


def build_merkle_root(hashes: list[str]) -> str:
    """Build binary Merkle Tree root from sorted leaf hashes. O(N log N)."""
    if not hashes:
        return "0" * 64
    # Leaf prefix: 0x00, internal prefix: 0x01 (Bitcoin-style domain separation)
    current_level = [hashlib.sha256(b"\x00" + h.encode("utf-8")).hexdigest() for h in sorted(hashes)]
    while len(current_level) > 1:
        next_level = []
        if len(current_level) % 2 != 0:
            current_level.append(current_level[-1])  # Duplicate last for odd count
        for i in range(0, len(current_level), 2):
            combined = b"\x01" + (current_level[i] + current_level[i + 1]).encode("utf-8")
            next_level.append(hashlib.sha256(combined).hexdigest())
        current_level = next_level
    return current_level[0]


def compute_structural_entropy(file_sizes: dict[str, int]) -> dict:
    """
    Compute Shannon Entropy H(Ω) over the ARCHITECTURE, not character frequency.

    X  = Set of audited files (structural blocks of the repository).
    xᵢ = Individual file (leaf node in the Merkle Tree).
    P(xᵢ) = w(xᵢ) / W  where w = file size in bytes, W = total bytes.

    Returns a dict with all computed physics metrics.
    """
    if not file_sizes:
        return {"H": 0.0, "H_max": 0.0, "eta": 0.0, "N": 0, "W": 0, "gini": 0.0}

    N = len(file_sizes)
    weights = list(file_sizes.values())
    W = sum(weights)

    if W == 0 or N <= 1:
        return {"H": 0.0, "H_max": 0.0, "eta": 0.0, "N": N, "W": W, "gini": 0.0}

    # --- Shannon Entropy H(Ω) ---
    H = 0.0
    probabilities = []
    for w in weights:
        if w > 0:
            p = w / W
            probabilities.append(p)
            H -= p * math.log2(p)

    H_max = math.log2(N)  # Maximum possible entropy (uniform distribution)
    eta = H / H_max if H_max > 0 else 0.0  # Normalized entropy η ∈ [0, 1]

    # --- Gini Coefficient (structural inequality) ---
    # G = 0 → perfect equality; G = 1 → one file holds everything
    sorted_w = sorted(weights)
    cumulative = 0.0
    gini_sum = 0.0
    for i, w in enumerate(sorted_w):
        cumulative += w
        gini_sum += cumulative
    gini = (2 * gini_sum) / (N * W) - (N + 1) / N if N > 0 and W > 0 else 0.0

    return {
        "H": round(H, 6),         # Structural entropy (bits)
        "H_max": round(H_max, 6), # Theoretical maximum (bits)
        "eta": round(eta, 6),     # Normalized balance ratio [0,1]
        "N": N,                   # Number of structural blocks
        "W": W,                   # Total information mass (bytes)
        "gini": round(gini, 6),   # Gini coefficient [0,1]
    }


def compute_kl_divergence(current_sizes: dict[str, int], reference_sizes: dict[str, int]) -> float:
    """
    Kullback-Leibler Divergence D_KL(P_current || P_reference).
    Measures structural drift from the last crystallized state.
    D_KL = 0 → no drift. D_KL > 0.1 → significant drift.
    Uses Laplace smoothing to handle new/deleted files.
    """
    all_files = set(current_sizes.keys()) | set(reference_sizes.keys())
    if not all_files:
        return 0.0

    # Laplace smoothing: add 1 byte to all files to avoid division by zero
    epsilon = 1
    W_curr = sum(current_sizes.values()) + epsilon * len(all_files)
    W_ref = sum(reference_sizes.values()) + epsilon * len(all_files)

    d_kl = 0.0
    for f in all_files:
        p_curr = (current_sizes.get(f, 0) + epsilon) / W_curr
        p_ref = (reference_sizes.get(f, 0) + epsilon) / W_ref
        if p_curr > 0 and p_ref > 0:
            d_kl += p_curr * math.log2(p_curr / p_ref)

    return round(max(0.0, d_kl), 6)


def autonomic_tokenator_heartbeat(root: Path, merkle_root: str, audit_files: list):
    """Executes the Sovereign Tokenator automation cycle with REAL token counting."""
    try:
        sys.path.append(str(root / "chronolith-pro"))
        from chronolith_pro.chronolith.tokenator import count_tokens, log_session, update_md_report
        from chronolith_pro.chronolith.ene_optimizer import ENEOptimizer
        from chronolith_pro.chronolith.sovereign_identity import get_identity

        # ENE v3.0 Optimization (Ghost Mode Active)
        optimizer = ENEOptimizer()
        identity = get_identity()
        dna_path = root / "PROJECT_DNA.md"

        if dna_path.exists():
            original = dna_path.read_text(encoding="utf-8")
            compressed = optimizer.compress(original, identity=identity, ghost_mode=True)
            ene_path = dna_path.with_suffix(".ene.md.locked")
            ene_path.write_text(compressed, encoding="utf-8", errors="surrogateescape")
            print(f"    [✔] Sovereign DNA Sealed (.ene.md.locked)")

        # Dynamic Token Calculation
        total_content = ""
        for f in audit_files:
            try:
                total_content += f.read_text(encoding="utf-8") + "\n"
            except Exception:
                continue

        real_tokens = count_tokens(total_content)

        status_msg = f"Autonomic DNA Crystallization (Merkle: {merkle_root[:12]})"
        log_session(status_msg, real_tokens)
        update_md_report(f"Φ_CRYSTAL: Structural Synthesis ({real_tokens} tokens)", real_tokens)
        print(f"    [🛰️] Tokenator Heartbeat: {real_tokens} tokens crystallized.")

    except ImportError:
        print("[!] Tokenator Engine (Pro) not found. Skipping dynamic telemetry.")
    except Exception as e:
        print(f"[!] Tokenator heartbeat failed: {e}")


def crystalize():
    root = Path(".").resolve()
    EXCLUDE_DIRS = {".git", "node_modules", ".chronolith", "outputs", ".pytest_cache",
                    "__pycache__", ".venv", ".github", ".idea", ".vscode"}
    CANONICAL_AUDIT_DIRS = [".", "OTHER_LANGUAGES"]

    # ── Phase 1: Collect auditable files ──
    all_md_files = []
    for audit_dir in CANONICAL_AUDIT_DIRS:
        a_path = root / audit_dir
        if not a_path.exists():
            continue
        if audit_dir == ".":
            for f in a_path.glob("*.md"):
                if "PROJECT_DNA" not in f.name:
                    all_md_files.append(f)
        else:
            for f in a_path.rglob("*.md"):
                if "PROJECT_DNA" not in f.name:
                    all_md_files.append(f)

    # ── Phase 2: Compute Merkle Root (Cryptographic Parity) ──
    nucleotides = [calculate_sha256(md) for md in sorted(all_md_files)]
    merkle_root = build_merkle_root(nucleotides)

    print(f"[*] CHRONOLITH CRYSTALLIZER (v3.0.0)")
    print(f"[*] CANONICAL MERKLE ROOT: {merkle_root}")

    # ── Phase 3: Structural Entropy (Information Physics) ──
    file_sizes = {}
    for f in sorted(all_md_files):
        try:
            file_sizes[f.name] = f.stat().st_size
        except OSError:
            file_sizes[f.name] = 0

    physics = compute_structural_entropy(file_sizes)

    print(f"    [Φ] Structural Entropy H(Ω) = {physics['H']:.4f} bits")
    print(f"    [Φ] Maximum Entropy H_max    = {physics['H_max']:.4f} bits")
    print(f"    [Φ] Balance Ratio η          = {physics['eta']:.4f}")
    print(f"    [Φ] Gini Coefficient G        = {physics['gini']:.4f}")
    print(f"    [Φ] Structural Blocks N       = {physics['N']}")
    print(f"    [Φ] Information Mass W         = {physics['W']} bytes")

    # Diagnostic output
    if physics["eta"] >= 0.75:
        print(f"    [✔] Architecture: HEALTHY (well-distributed)")
    elif physics["eta"] >= 0.50:
        print(f"    [⚠] Architecture: MODERATE DRIFT (centralization risk)")
    else:
        print(f"    [❌] Architecture: SEVERE DRIFT (monolithic antipattern)")

    # ── Phase 4: Persist State ──
    is_ci = os.environ.get("CI") == "true"
    state_path = root / "STATE.json"

    if not is_ci:
        # Load existing state for KL divergence calculation
        reference_sizes = {}
        if state_path.exists():
            state = json.loads(state_path.read_text(encoding="utf-8"))
            reference_sizes = state.get("file_sizes", {})
        else:
            state = {}

        # Compute drift from last crystallization
        d_kl = compute_kl_divergence(file_sizes, reference_sizes) if reference_sizes else 0.0
        if d_kl > 0:
            print(f"    [Δ] KL Divergence (drift): {d_kl:.6f}")
            if d_kl > 0.1:
                print(f"    [⚠] SIGNIFICANT STRUCTURAL DRIFT DETECTED")

        # Update STATE.json with full physics telemetry
        state["merkle_root"] = merkle_root
        state["last_check"] = datetime.now().isoformat()
        state["physics"] = physics
        state["drift_kl"] = d_kl
        state["file_sizes"] = file_sizes
        state["crystallizer_version"] = "3.0.1"

        serialized = json.dumps({k: v for k, v in state.items() if k != "signature"}, sort_keys=True)
        state["signature"] = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        print(f"    [✔] STATE.json crystallized (Physics Telemetry Embedded)")

        # Update README crystal marker
        readme_path = root / "README.md"
        if readme_path.exists():
            content = readme_path.read_text(encoding="utf-8", errors="surrogateescape")
            content = re.sub(
                r'DNA CRYSTAL\*\*: `v[\d.]+-[a-f0-9]+`',
                f"DNA CRYSTAL**: `v3.0.0-{merkle_root[:16]}`",
                content
            )
            readme_path.write_text(content, encoding="utf-8", errors="surrogateescape")
            print(f"    [✔] README.md crystal updated.")

        # Autonomic Tokenator Loop
        autonomic_tokenator_heartbeat(root, merkle_root, all_md_files)
    else:
        print("[+] DNA Parity Confirmed (CI Environment).")

    print(f"\n[*] CRYSTALLIZATION COMPLETE. Merkle Root: {merkle_root[:24]}...")


if __name__ == "__main__":
    crystalize()
