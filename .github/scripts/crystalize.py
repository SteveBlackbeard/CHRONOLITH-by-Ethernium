import hashlib
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

# SOVEREIGN CRYSTALLIZER (v2.4.1 - ROBUST ROOT AUDIT)
# --------------------------------------------------
# Purpose: Finalize the DNA Synthesis (Cross-Platform, Metabolically Hardened).
# FIX: Robustness in file collection and scope.

EXCLUDE_DIRS = [".git", "node_modules", ".continuity", "outputs", ".pytest_cache", "__pycache__", ".venv", ".github", ".idea", ".vscode"]
CANONICAL_AUDIT_DIRS = [".", "OTHER_LANGUAGES"]

def calculate_sha256(path: Path) -> str:
    if not (path.exists() and path.is_file()): return ""
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""
        
    lines = content.splitlines()
    filtered = []
    for l in lines:
        if "DNA CRYSTAL" in l or "img.shields.io/badge/DNA--Crystallized" in l:
            continue
        filtered.append(l.rstrip())
    
    return hashlib.sha256("\n".join(filtered).strip().encode("utf-8")).hexdigest()

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
    all_md_files = []
    
    # Radical Strategy: Search only in Root and OTHER_LANGUAGES
    for audit_dir in CANONICAL_AUDIT_DIRS:
        a_path = root / audit_dir
        if not a_path.exists(): continue
        
        if audit_dir == ".":
            # Just root md files
            for f in a_path.glob("*.md"):
                if "PROJECT_DNA" not in f.name:
                    all_md_files.append(f)
        else:
            # Languages md files (recursive)
            for f in a_path.rglob("*.md"):
                if "PROJECT_DNA" not in f.name:
                    all_md_files.append(f)
    
    nucleotides = [calculate_sha256(md) for md in sorted(all_md_files)]
    merkle_root = build_merkle_root(nucleotides)
    
    print(f"[*] SYMBOLIC SYNTHESIS COMPLETE.")
    print(f"[*] CANONICAL MERKLE ROOT: {merkle_root}")
    
    is_ci = os.environ.get("CI") == "true"
    state_path = root / "STATE.json"
    
    if is_ci:
        # CI MODE: Verify only, never mutate
        if state_path.exists():
            state = json.loads(state_path.read_text(encoding="utf-8"))
            expected = state.get("merkle_root", "")
            if expected and expected != merkle_root:
                print(f"[!] DNA DRIFT DETECTED:")
                print(f"    Computed: {merkle_root[:16]}")
                print(f"    Expected: {expected[:16]}")
                sys.exit(1)
        print(f"[✔] CI PARITY CONFIRMED: {merkle_root[:16]}")
    else:
        # LOCAL MODE: Update STATE.json and README badge
        if state_path.exists():
            try:
                state = json.loads(state_path.read_text(encoding="utf-8"))
                state["merkle_root"] = merkle_root
                state["last_check"] = datetime.utcnow().isoformat()
                serialized = json.dumps({k: v for k, v in state.items() if k != "signature"}, sort_keys=True)
                state["signature"] = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
                state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
                print(f"    [✔] STATE.json crystallized.")
            except Exception as e:
                print(f"    [!] STATE.json Error: {e}")

        readme_path = root / "README.md"
        if readme_path.exists():
            content = readme_path.read_text(encoding="utf-8")
            short_hash = merkle_root[:8]
            long_hash16 = merkle_root[:16]
            content = re.sub(r'DNA CRYSTAL\*\*: `v2\.1\.0-[a-f0-9]+`', f"DNA CRYSTAL**: `v2.1.0-{long_hash16}`", content)
            content = re.sub(r'\[!\[Merkle Root\].*DNA--Crystallized-[a-f0-9]+-blueviolet', 
                             f"[![Merkle Root](https://img.shields.io/badge/DNA--Crystallized-{short_hash}-blueviolet)", 
                             content)
            readme_path.write_text(content, encoding="utf-8")
            print(f"    [✔] README.md crystal updated.")

if __name__ == "__main__":
    crystalize()

