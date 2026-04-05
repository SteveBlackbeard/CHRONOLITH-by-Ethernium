import sys
import argparse
import json
import os
import datetime
from pathlib import Path

# v2.1.0 Evolution: Ensure the current directory is in the path for safe internal imports
# No matter where this script is called from (root, subdir, or hook), it will find its nuclei.
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

# Standardizing internal required manifest
INTERNAL_REQUIRED = [
    "PROJECT_CONTEXT.md",
    "STATE.json",
    "ROADMAP.md",
    ".continuity/CONTEXT_CONTINUITY.md",
    ".continuity/BOOT_SEQUENCE.md",
    ".continuity/LIVE_HANDOFF.md",
    ".continuity/DECISIONS_LOG.md",
    ".continuity/TIMELINE.md",
]

def utc_now_iso() -> str:
    return datetime.datetime.utcnow().isoformat() + "Z"

def check_logical_immunity(repo_root: Path) -> dict:
    context_path = repo_root / "PROJECT_CONTEXT.md"
    decisions_path = repo_root / ".continuity" / "DECISIONS_LOG.md"
    if not context_path.exists() or not decisions_path.exists():
        return {"status": "ok", "reason": "files_missing_for_check"}
    context = context_path.read_text(encoding="utf-8")
    decisions = decisions_path.read_text(encoding="utf-8")
    issues = []
    # Heuristic: Check if 'forbidden' markers in context appear in recent decisions
    for line in context.splitlines():
        if "MUST:" in line or "ALWAYS:" in line:
            parts = line.split(":", 1)
            if len(parts) > 1:
                keyword = parts[1].strip().split()[0]
                if f"REMOVE {keyword}" in decisions.upper() or f"DEPRECATE {keyword}" in decisions.upper():
                    issues.append(f"Potential contradiction: Context requires '{keyword}' but decisions mention its removal.")
    return {"status": "ok" if not issues else "attention_required", "issues": issues}

def crystallize_readme(repo_root: Path, merkle_root: str):
    """v2.1.1: Injects the Merkle Root 'Crystal' into the README.md."""
    readme_path = repo_root / "README.md"
    if not readme_path.exists():
        return
    
    content = readme_path.read_text(encoding="utf-8")
    marker = "<!-- DNA_CRYSTAL -->"
    
    if marker in content:
        import automation_common
        from automation_common import Color, echo
        
        # Hybrid Badge + Text Crystallization
        crystal_text = (
            f"\n> [!IMPORTANT]\n"
            f"> **DNA CRYSTAL**: `v2.1.0-{merkle_root[:16]}`\n"
            f"> [![Merkle Root](https://img.shields.io/badge/DNA--Crystallized-{merkle_root[:8]}-blueviolet)](https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium)\n"
        )
        
        # Simple regex-free replacement to avoid breaking user content
        parts = content.split(marker)
        # We only replace the first occurrence's follower if it was a previous crystal
        # or we just append it after the marker.
        new_content = parts[0] + marker + crystal_text
        
        # If there were more parts, we need to handle them carefully to not duplicate or lose data
        # Check if there's already a crystal block and skip it
        remaining = marker.join(parts[1:])
        if "> **DNA CRYSTAL**:" in remaining:
            # Strip the old block (heuristic: ends at next double newline or next heading)
            import re
            remaining = re.sub(r"\n> \[!IMPORTANT\].*?blueviolet\)\n", "", remaining, flags=re.DOTALL)
        
        new_content += remaining
        readme_path.write_text(new_content, encoding="utf-8")
        echo(f"[✔] README Crystallized: {merkle_root[:8]}", Color.PURPLE)

def run_continuity_cycle(repo_root: str | Path) -> dict:
    # All modules below are expected to be in the SAME directory
    import automation_common
    import doc_parity_check
    import system_membership_check
    import secret_detector
    
    repo_root = Path(repo_root).resolve()
    config = automation_common.load_config(repo_root)
    
    doc_parity = doc_parity_check.check_doc_parity(str(repo_root))
    membership = system_membership_check.check_system_membership(str(repo_root))
    logical_immunity = check_logical_immunity(repo_root)
    secret_scan = secret_detector.scan_for_secrets(repo_root)

    # v2.1.0 Evolution: Generate Merkle DNA Tree
    # v2.1.1: Optimized Scan - Ignoring heavy directories to prevent freezes.
    print("[*] DNA Nucleotide Scan: Synthesizing architecture...")
    
    md_files = []
    # Targeted walk to avoid node_modules and other monsters
    for root, dirs, files in os.walk(repo_root):
        # In-place modification of dirs to skip these recursively
        dirs[:] = [d for d in dirs if d not in [".git", "node_modules", "venv", ".venv", "outputs", "assets", "banners"]]
        for f in files:
            if f.endswith(".md"):
                md_files.append(Path(root) / f)
    
    md_files = sorted(md_files)
    nucleotides = []
    md_list_for_dna = []
    full_context_text = ""
    
    for md in md_files:
        if "PROJECT_DNA.md" in md.name or "SESSION_LOG.md" in md.name:
            continue
        
        try:
            content = md.read_text(encoding="utf-8", errors="ignore")
            full_context_text += content
            
            import automation_common
            h = automation_common.calculate_sha256(md)
            nucleotides.append(h)
            md_list_for_dna.append((md, n_hash := h))
        except Exception:
            continue
    
    # v2.1.1: Cognitive Volatility Check (Shannon Entropy)
    entropy = automation_common.calculate_context_entropy(full_context_text)
    volatility_alert = False
    if entropy > automation_common.ENTROPY_THRESHOLD:
        volatility_alert = True
    
    merkle_root = automation_common.build_merkle_tree(nucleotides)
    
    # v2.1.1: Crystallization
    crystallize_readme(repo_root, merkle_root)
    
    dna_path = repo_root / "PROJECT_DNA.md"
    dna_lines = [
        "# Project DNA Manifest (Pro Evolution) 🧬\n",
        f"*Synthesized on: {utc_now_iso()}*\n",
        f"*Algorithm: SHA-256 Merkle Tree*\n\n",
        f"> **MERKLE ROOT**: `{merkle_root}`\n\n",
        f"> **COGNITIVE ENTROPY**: `{entropy:.4f}` bits/char\n\n",
        "## 🧬 Enterprise Nucleotides:\n"
    ]
    for md, n_hash in md_list_for_dna:
        dna_lines.append(f"- **{md.name}**: `{n_hash[:16]}...`\n")
    
    dna_path.write_text("".join(dna_lines), encoding="utf-8")

    report = {
        "generated_at": utc_now_iso(),
        "status": "ok" if (doc_parity["status"] == "ok" and membership["status"] == "ok" and not secret_scan["findings"]) else "attention_required",
        "merkle_root": merkle_root,
        "entropy": entropy,
        "volatility_alert": volatility_alert,
        "doc_parity_status": doc_parity["status"],
        "membership_status": membership["status"],
        "security_status": "ok" if not secret_scan["findings"] else "danger",
    }
    
    report_path = automation_common.continuity_report_path(repo_root, config)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report

def main() -> None:
    print('[*] Continuity Engine Pro v2.1.0 Booting...')
    parser = argparse.ArgumentParser(description="Continuity Pro Evolution: DNA Guardian.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--hook", action="store_true")
    args = parser.parse_args()
    
    import automation_common
    from automation_common import Color, echo
    repo_root = Path(args.repo_root).resolve()
    
    if args.hook:
        hook_path = repo_root / ".git" / "hooks" / "pre-push"
        hook_content = f"#!/bin/sh\n# Continuity Pro Evolution Hook\necho '[*] Guarding DNA Lineage...'\npython \"{Path(__file__).resolve()}\" --strict || exit 1\n"
        hook_path.parent.mkdir(parents=True, exist_ok=True)
        hook_path.write_text(hook_content, encoding="utf-8")
        if os.name != "nt": os.chmod(hook_path, 0o755)
        echo(f"[✔] Push Hook (Pro) installed at {hook_path}", Color.GREEN)
        return

    echo("\n[*] CONTINUITY LEGACY Pro - DNA & Parity Validation", Color.CYAN)
    
    # Antifreeze: Interactive prompts only if TTY is present
    if sys.stdin.isatty():
        # Captura de intención opcional
        echo("\n[?] Strategic ideas or intent for this session? (Enter to skip):", Color.CYAN)
        try:
            intent = input("> ").strip()
            if intent:
                log_path = repo_root / ".continuity" / "DECISIONS_LOG.md"
                if log_path.exists():
                    with open(log_path, "a", encoding="utf-8") as f:
                        f.write(f"| {datetime.datetime.utcnow().strftime('%Y-%m-%d')} | Intent: {intent} | Developer Session | Admin |\n")
                    echo(f"[✔] Intent logged.", Color.GREEN)
        except (EOFError, KeyboardInterrupt): pass

    report = run_continuity_cycle(repo_root)
    echo(f"\n[✔] Status: {report['status'].upper()}", Color.GREEN if report['status'] == "ok" else Color.YELLOW)
    echo(f"[*] Merkle Root: {report['merkle_root'][:16]}...", Color.WHITE)
    
    if report["status"] != "ok" and args.strict:
        echo("\n[!] BORDER GUARD: DNA Compromised. Action BLOCKED.", Color.RED)
        sys.exit(1)

    echo("\nCONTINUITY OK: Lineage Protected.", Color.BOLD)

if __name__ == "__main__":
    main()
