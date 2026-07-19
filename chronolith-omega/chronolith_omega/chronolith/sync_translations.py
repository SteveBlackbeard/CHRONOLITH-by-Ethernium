from __future__ import annotations
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# CHRONOLITH: Active Universal Translation Sync
# ----------------------------------------------------
# This script manages multilingual documentation across the 4 levels: 
# Root, Pro, Lite, and Omega. It detects drift and can auto-generate READMEs.

LANG_CODES = ["es", "ja", "ru", "zh", "fr", "it", "de", "pt", "ko", "ar", "en"]

# Written into every generated file, and the only way to tell a placeholder
# from a real translation that must not be clobbered.
MARKER = "CHRONOLITH: Global Infrastructure - Generated"

def calculate_md5(path: Path) -> str:
    if not path.exists(): return ""
    return hashlib.md5(path.read_bytes()).hexdigest()

def get_edition_name(root: Path) -> str:
    # Detect which edition we are in
    if (root / "CHRONOLITH Pro").exists(): return "Root Portal"
    if "Pro" in root.name: return "Pro Edition"
    if "Lite" in root.name: return "Lite Edition"
    if "Omega" in root.name: return "Omega Edition"
    return "Universal Core"

def generate_localized_readme(lang, edition_name, source_content):
    # Professional localized templates
    templates = {
        "es": f"# CHRONOLITH: {edition_name}\n\nVersión localizada del framework de continuidad técnica.",
        "ja": f"# CHRONOLITH: {edition_name}\n\nテクニカル・コンティニュイティ・フレームワークのローカライズ版。",
        "ru": f"# CHRONOLITH: {edition_name}\n\nЛокализованная версия фреймворка технической непрерывности.",
        "zh": f"# CHRONOLITH: {edition_name}\n\n技术连续性框架的本地化版本。",
    }
    
    # Generic fallback
    base = templates.get(lang, f"# CHRONOLITH: {edition_name}\n\nLocalized version of the technical continuity framework.")
    
    # Add strategic metadata footer
    footer = f"\n\n---\n*CHRONOLITH: Global Infrastructure - Generated {datetime.utcnow().isoformat()}Z*"
    return base + footer

def sync_all(repo_root: Path, auto_gen: bool):
    edition = get_edition_name(repo_root)
    source_path = repo_root / "README.md"
    
    if not source_path.exists():
        print(f"[!] ERROR: Source README.md not found in {repo_root}")
        return
    
    print(f"[*] SYNC: Analyzing {edition} in {repo_root}...")
    source_hash = calculate_md5(source_path)
    
    lang_dir = repo_root / "OTHER_LANGUAGES"
    lang_dir.mkdir(parents=True, exist_ok=True)
    
    for lang in LANG_CODES:
        target_path = lang_dir / f"README_{lang}.md"
        
        if auto_gen:
            # Fail-closed. The generator emits a two-line stub, not a
            # translation. Overwriting unconditionally meant one run of
            # --auto-generate destroyed every hand-written README in every
            # language and replaced it with a placeholder.
            #
            # A file is only regenerated when it does not exist yet, or when
            # this tool is the one that wrote it — which its own footer marks.
            if target_path.exists():
                existing = target_path.read_text(encoding="utf-8", errors="replace")
                if MARKER not in existing:
                    print(f"    -> SKIP {lang}: hand-written, refusing to overwrite")
                    continue
            print(f"    -> Updating {lang} README...")
            content = generate_localized_readme(lang, edition, source_path.read_text(encoding="utf-8"))
            target_path.write_text(content, encoding="utf-8")
        
    print(f"[✔] SYNC: {edition} is now globally synchronized.")

def main() -> None:
    parser = argparse.ArgumentParser(description="Active Universal Translation Sync.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--auto-generate", action="store_true", help="Automatically generate/update localized files.")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    sync_all(root, args.auto_generate)

if __name__ == "__main__":
    main()
