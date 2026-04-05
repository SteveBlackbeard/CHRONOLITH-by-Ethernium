import sys
import hashlib
import os
from pathlib import Path
from datetime import datetime

# CONTINUITY LEGACY Lite (v2.1.0) - Evolution DNA Guardian
# -------------------------------------------------------------
# [!] v2.1.0: Evolution Parity, Multi-Nucleotide DNA, Hook Entry Points.

def calculate_sha256(path: Path) -> str:
    """Calculates the SHA-256 hash of a file for high-fidelity DNA synthesis."""
    if not path.exists(): return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()

def ensure_file(path: Path, template: str, description: str):
    if not path.exists():
        print(f"[?] Missing Nucleotide: {description}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(template, encoding="utf-8")
        print(f"    [✔] Re-synthesized: {path.name}")
        return True
    return False

def install_hooks(repo_root: Path):
    hook_path = repo_root / ".git" / "hooks" / "pre-push"
    if not (repo_root / ".git").exists():
        print("[!] ERROR: Not a git repository. Cannot install hooks.")
        return
    
    # Updated hook content for v2.1.0 Evolution
    hook_content = f"#!/bin/sh\n# Continuity Lite Evolution Hook\necho '[*] Guarding DNA Lineage...'\npython '{Path(__file__).resolve()}' || exit 1\n"
    hook_path.parent.mkdir(parents=True, exist_ok=True)
    hook_path.write_text(hook_content, encoding="utf-8")
    
    if os.name != "nt": os.chmod(hook_path, 0o755)
    print(f"[✔] Push Hook (v2.1.0) installed at {hook_path}")

def build_merkle_root(hashes: list[str]) -> str:
    """Computes a deterministic Merkle Root from a list of nucleotide hashes."""
    if not hashes: return ""
    current_level = sorted(hashes)
    while len(current_level) > 1:
        next_level = []
        if len(current_level) % 2 != 0:
            current_level.append(current_level[-1])
        for i in range(0, len(current_level), 2):
            combined = current_level[i] + current_level[i+1]
            next_level.append(hashlib.sha256(combined.encode("utf-8")).hexdigest())
        current_level = next_level
    return current_level[0]

def crystallize_readme(repo_root: Path, merkle_root: str):
    """v2.1.1: Injects the Merkle Root 'Crystal' into the README.md."""
    readme_path = repo_root / "README.md"
    if not readme_path.exists(): return
    content = readme_path.read_text(encoding="utf-8")
    marker = "<!-- DNA_CRYSTAL -->"
    if marker in content:
        crystal_text = (
            f"\n> [!IMPORTANT]\n"
            f"> **DNA CRYSTAL**: `v2.1.1-{merkle_root[:16]}`\n"
            f"> [![Merkle Root](https://img.shields.io/badge/DNA--Crystallized-{merkle_root[:8]}-blueviolet)](https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium)\n"
        )
        parts = content.split(marker)
        new_content = parts[0] + marker + crystal_text
        remaining = marker.join(parts[1:])
        if "> **DNA CRYSTAL**:" in remaining:
            import re
            remaining = re.sub(r"\n> \[!IMPORTANT\].*?blueviolet\)\n", "", remaining, flags=re.DOTALL)
        new_content += remaining
        readme_path.write_text(new_content, encoding="utf-8")
        print(f"    [✔] README Crystallized: {merkle_root[:8]}")

def generate_minimal_dna(repo_root: Path):
    """v2.1.0 Evolution DNA Synthesis: Hierarchical Merkle Tree protection."""
    print("[*] LITE: DNA Nucleotide Scan...")
    
    md_files = []
    # Targeted walk to skip heavy folders
    import os
    for root, dirs, files in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in [".git", "node_modules", "venv", ".venv", "outputs", "assets", "banners"]]
        for f in files:
            if f.endswith(".md"):
                md_files.append(Path(root) / f)
    
    dna_path = repo_root / "PROJECT_DNA.md"
    nucleotides = []
    dna_lines = [
        "# Project DNA Manifest (Lite) 🧬\n",
        f"*Synthesized on: {datetime.now().isoformat()}*\n",
        f"*Algorithm: SHA-256 Merkle Tree*\n\n"
    ]
    
    dna_lines.append("## 🧬 Nucleotide Integrity Check:\n")
    for md in sorted(md_files): # Deterministic order
        if "PROJECT_DNA" in md.name:
            continue
        n_hash = calculate_sha256(md)
        nucleotides.append(n_hash)
        dna_lines.append(f"- **{md.name}**: `{n_hash[:16]}...`\n")
        
    merkle_root = build_merkle_root(nucleotides)
    dna_lines.insert(4, f"> **MERKLE ROOT**: `{merkle_root}`\n\n")
    
    dna_path.write_text("".join(dna_lines), encoding="utf-8")
    crystallize_readme(repo_root, merkle_root) # v2.1.1
    print(f"[✔] LITE: Merkle Root generated: {merkle_root[:16]}...")
    print(f"[✔] LITE: Project DNA synthesized at {dna_path.name}")

def log_session(repo_root: Path):
    """v2.1.0 Evolution: Non-interactive session logging."""
    intent = ""
    if sys.stdin.isatty():
        print("\n[*] [OPTIONAL] Session intent capture")
        try:
            intent = input("    -> What did you achieve in this session? (Enter to skip): ").strip()
        except (EOFError, KeyboardInterrupt):
            pass
    
    if intent:
        log_path = repo_root / "SESSION_LOG.md"
        if not log_path.exists():
            log_path.write_text("# Continuity Session Log\n\n", encoding="utf-8")
        
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"- [{datetime.utcnow().isoformat()}Z] {intent}\n")
        print("    [✔] Intent logged.")

def main() -> None:
    print('[*] Continuity Engine Lite v2.1.0 Booting...')
    # MOVE argparse inside to ensure instant help command
    import argparse
    parser = argparse.ArgumentParser(description="Continuity Lite: DNA Guardian.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--hook", action="store_true", help="Install pre-push hook.")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    if args.hook:
        install_hooks(root)
        return

    print("\n[*] CONTINUITY LEGACY Lite - DNA Validation")
    files = {
        "PROJECT_CONTEXT.md": "# Project Context\n\n- Define your project core here.",
        "STATE.json": '{"phase": "stable", "last_update": "' + datetime.utcnow().isoformat() + '"}',
        "LIVE_HANDOFF.md": "# Live Handoff\n\n- No handoff pending."
    }
    
    for filename, template in files.items():
        ensure_file(root / filename, template, filename)

    generate_minimal_dna(root)
    log_session(root)
    print("\n[✔] Continuity Cycle Complete. Lineage Protected.")

if __name__ == "__main__":
    main()
