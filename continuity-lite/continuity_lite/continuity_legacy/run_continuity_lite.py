import sys
import hashlib
import os
from pathlib import Path
from datetime import datetime

# CONTINUITY LEGACY Lite (v1.3.1) - Zero-Friction DNA Guardian
# -------------------------------------------------------------
# [!] v1.3.1: Global Parity, Multi-Nucleotide DNA, Hook Automation.

def calculate_md5(path: Path) -> str:
    if not path.exists(): return ""
    return hashlib.md5(path.read_bytes()).hexdigest()

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
    
    hook_content = f"#!/bin/sh\n# Continuity Lite Auto-Hook\npython {Path(__file__).resolve()} || exit 1\n"
    hook_path.parent.mkdir(parents=True, exist_ok=True)
    hook_path.write_text(hook_content, encoding="utf-8")
    
    if os.name != "nt": os.chmod(hook_path, 0o755)
    print(f"[✔] Push Hook (v1.3) installed at {hook_path}")

def generate_minimal_dna(repo_root: Path):
    """Zero-dependency DNA Synthesis: Distills core project identity from Markdown files."""
    print("[*] LITE: Synthesizing Project DNA...")
    md_files = list(repo_root.rglob("*.md"))
    dna_path = repo_root / "PROJECT_DNA.md"
    
    dna_lines = ["# Project DNA Manifest (Lite) 🧬\n", f"*Synthesized on: {datetime.now().isoformat()}*\n\n"]
    dna_lines.append("## 🧬 Core Nucleotides Found:\n")
    
    for md in md_files:
        if ".git" in str(md) or "PROJECT_DNA" in md.name: continue
        dna_lines.append(f"- **{md.name}** (Integrity: {calculate_md5(md)[:8]})\n")
        
    dna_path.write_text("".join(dna_lines), encoding="utf-8")
    print(f"[✔] LITE: Project DNA synthesized at {dna_path.name}")

def log_session(repo_root: Path):
    print("\n[*] [OPTIONAL] Session intent capture")
    intent = input("    -> What did you achieve in this session? (Enter to skip): ").strip()
    
    if intent:
        log_path = repo_root / "SESSION_LOG.md"
        if not log_path.exists():
            log_path.write_text("# Continuity Session Log\n\n", encoding="utf-8")
        
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"- [{datetime.utcnow().isoformat()}Z] {intent}\n")
        print("    [✔] Intent logged.")

def main() -> None:
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
