import hashlib
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

# ENTERPRISE CRYSTALLIZER (v2.5.0 - AUTONOMIC SENTINEL INTEGRATION)
# -----------------------------------------------------------------
# Purpose: DNA Synthesis with automatic ENE Optimization and Token Telemetry.

# Industrial Note: We attempt to load the Sentinel and Optimizer from the local environment.
try:
    from continuity_pro.continuity_legacy.token_sentinel import count_tokens, update_md_report
    from continuity_pro.continuity_legacy.ene_optimizer import ENEOptimizer
    SENTINEL_ACTIVE = True
except ImportError:
    SENTINEL_ACTIVE = False

EXCLUDE_DIRS = [".git", "node_modules", ".continuity", "outputs", ".pytest_cache", "__pycache__", ".venv", ".github", ".idea", ".vscode"]
CANONICAL_AUDIT_DIRS = [".", "OTHER_LANGUAGES"]

def calculate_sha256(path: Path) -> str:
    if not (path.exists() and path.is_file()): return ""
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""
    lines = [l.rstrip() for l in content.splitlines() if "DNA CRYSTAL" not in l and "img.shields.io/badge/DNA--Crystallized" not in l]
    return hashlib.sha256("\n".join(lines).strip().encode("utf-8")).hexdigest()

def build_merkle_root(hashes: list[str]) -> str:
    if not hashes: return "0" * 64
    current_level = [hashlib.sha256(b"\x00" + h.encode("utf-8")).hexdigest() for h in sorted(hashes)]
    while len(current_level) > 1:
        next_level = []
        if len(current_level) % 2 != 0: current_level.append(current_level[-1])
        for i in range(0, len(current_level), 2):
            combined = b"\x01" + (current_level[i] + current_level[i+1]).encode("utf-8")
            next_level.append(hashlib.sha256(combined).hexdigest())
        current_level = next_level
    return current_level[0]

def autonomic_sentinel_cycle(root: Path, merkle_root: str):
    """Automatically performs ENE optimization and Token logging."""
    if not SENTINEL_ACTIVE: return
    
    optimizer = ENEOptimizer()
    dna_path = root / "PROJECT_DNA.md"
    
    # 1. Automatic ENE Optimization (x10 Efficiency)
    if dna_path.exists():
        original = dna_path.read_text(encoding="utf-8")
        compressed = optimizer.compress(original)
        ene_path = dna_path.with_suffix(".ene.md")
        ene_path.write_text(compressed, encoding="utf-8")
        print(f"    [✔] ENE Optimized DNA updated (.ene.md).")
        
    # 2. Token Telemetry (Tachometer)
    # We estimate the cost of the current change relative to the Merkle Drift
    # or just record the current total project status.
    total_tokens = count_tokens("\n".join([f.read_text(encoding="utf-8") for f in root.glob("*.md") if f.is_file()]))
    update_md_report(f"Autonomic DNA Sync ({merkle_root[:8]})", total_tokens)
    print(f"    [✔] Token Tachometer synchronized: {total_tokens} tokens.")

def crystalize():
    root = Path(".").resolve()
    # Add project root to sys.path to ensure we can import the sentinel
    sys.path.append(str(root / "continuity-pro"))
    
    all_md_files = []
    for audit_dir in CANONICAL_AUDIT_DIRS:
        a_path = root / audit_dir
        if not a_path.exists(): continue
        if audit_dir == ".":
            for f in a_path.glob("*.md"):
                if "PROJECT_DNA" not in f.name: all_md_files.append(f)
        else:
            for f in a_path.rglob("*.md"):
                if "PROJECT_DNA" not in f.name: all_md_files.append(f)
    
    nucleotides = [calculate_sha256(md) for md in sorted(all_md_files)]
    merkle_root = build_merkle_root(nucleotides)
    
    print(f"[*] SYMBOLIC SYNTHESIS COMPLETE.")
    print(f"[*] CANONICAL MERKLE ROOT: {merkle_root}")
    
    is_ci = os.environ.get("CI") == "true"
    state_path = root / "STATE.json"
    
    if not is_ci:
        # Update State & Readme
        if state_path.exists():
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["merkle_root"] = merkle_root
            state["last_check"] = datetime.now().isoformat()
            serialized = json.dumps({k: v for k, v in state.items() if k != "signature"}, sort_keys=True)
            state["signature"] = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
            state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
            print(f"    [✔] STATE.json crystallized.")
            
        readme_path = root / "README.md"
        if readme_path.exists():
            content = readme_path.read_text(encoding="utf-8")
            content = re.sub(r'DNA CRYSTAL\*\*: `v2\.1\.0-[a-f0-9]+`', f"DNA CRYSTAL**: `v2.1.0-{merkle_root[:16]}`", content)
            readme_path.write_text(content, encoding="utf-8")
            print(f"    [✔] README.md crystal updated.")
            
        # [NEW] Autonomic Sentinel Cycle
        autonomic_sentinel_cycle(root, merkle_root)

if __name__ == "__main__":
    crystalize()
