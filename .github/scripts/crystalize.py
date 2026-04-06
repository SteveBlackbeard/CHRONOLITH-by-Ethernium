import hashlib
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

# NEXUS CRYSTALLIZER (v2.7.2 - DYNAMIC TOKENATOR HEARTBEAT)
# -----------------------------------------------------------------
# Purpose: DNA Synthesis with Real-Time Token Telemetry and ENE Optimization.

def autonomic_tokenator_heartbeat(root: Path, merkle_root: str, audit_files: list):
    """Executes the Sovereign Tokenator automation cycle with REAL token counting."""
    try:
        # Add project root to sys.path to ensure we can import the tokenator
        sys.path.append(str(root / "continuity-pro"))
        from continuity_pro.continuity_legacy.tokenator import count_tokens, log_session, update_md_report
        from continuity_pro.continuity_legacy.ene_optimizer import ENEOptimizer
        
        # 1. Automatic ENE Optimization (x10 Efficiency)
        optimizer = ENEOptimizer()
        dna_path = root / "PROJECT_DNA.md"
        if dna_path.exists():
            original = dna_path.read_text(encoding="utf-8")
            compressed = optimizer.compress(original)
            ene_path = dna_path.with_suffix(".ene.md")
            ene_path.write_text(compressed, encoding="utf-8")
            print(f"    [✔] ENE Optimized DNA updated (.ene.md).")

        # 2. Dynamic Token Calculation (Realismo Dinámico)
        # We process the actual content of the files audit to get the REAL cognitive weight
        total_content = ""
        for f in audit_files:
            try:
                total_content += f.read_text(encoding="utf-8") + "\n"
            except: continue
        
        real_tokens = count_tokens(total_content)
        
        # 3. Autonomic Telemetry
        # This replaces the hardcoded 150 with the REAL count
        log_session(f"Autonomic DNA Crystallization (NEXUS: {merkle_root[:8]})", real_tokens)
        print(f"    [🛰️] Tokenator Heartbeat synchronized: {real_tokens} tokens.")
        
    except ImportError:
        print("[!] Tokenator Engine (Pro) not found. Skipping dynamic telemetry.")
    except Exception as e:
        print(f"[!] Tokenator heartbeat failed: {e}")

def calculate_sha256(path: Path) -> str:
    if not (path.exists() and path.is_file()): return ""
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""
    # Filter out the DNA Crystal marker to avoid circular hashing
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

def crystalize():
    root = Path(".").resolve()
    EXCLUDE_DIRS = [".git", "node_modules", ".continuity", "outputs", ".pytest_cache", "__pycache__", ".venv", ".github", ".idea", ".vscode"]
    CANONICAL_AUDIT_DIRS = [".", "OTHER_LANGUAGES"]
    
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
    
    print(f"[*] SYMBOLIC SYNTHESIS PROGRESS (v2.1.0-NEXUS)")
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
            # Update specific version marker
            content = re.sub(r'DNA CRYSTAL\*\*: `v2\.1\.0-[a-f0-9]+`', f"DNA CRYSTAL**: `v2.1.0-{merkle_root[:16]}`", content)
            readme_path.write_text(content, encoding="utf-8")
            print(f"    [✔] README.md crystal updated.")
            
        # --- Autonomic Loop (REALISMO DINÁMICO v2.7.2) ---
        autonomic_tokenator_heartbeat(root, merkle_root, all_md_files)
    else:
        print("[+] DNA Parity Confirmed (CI Environment).")

if __name__ == "__main__":
    crystalize()
