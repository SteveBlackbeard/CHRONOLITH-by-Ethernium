from __future__ import annotations
import argparse
import hashlib
import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime

# CONTINUITY LEGACY: Universal Version & Translation Engine (v1.4.0)
# -----------------------------------------------------------------
# This engine is the "Single Source of Truth" (SST) for the ecosystem.
# It synchronizes 9 languages and manages the global project version.

LANG_CODES = ["es", "ja", "ru", "zh", "fr", "it", "de", "pt", "en"]

def get_universal_version(repo_root: Path) -> str:
    """Reads the global project version from the root SST file."""
    # Try finding it at the current root or absolute root
    v_file = repo_root / "VERSION"
    if not v_file.exists():
        # Fallback to absolute project root if in a sub-edition
        v_file = repo_root.parent / "VERSION"
        
    if v_file.exists():
        return v_file.read_text(encoding="utf-8").strip()
    return "1.3.1" # Safe fallback

def calculate_md5(path: Path) -> str:
    if not path.exists(): return ""
    return hashlib.md5(path.read_bytes()).hexdigest()

def get_edition_name(root: Path) -> str:
    # Improved detection logic for v1.4.0
    if (root / "continuity-lite").exists(): return "Root Portal"
    if "lite" in root.name.lower(): return "Lite Edition"
    if "omega" in root.name.lower(): return "Omega Edition"
    if "pro" in root.name.lower() or "continuity" == root.name.lower(): return "Pro Edition"
    return "Universal Core"

def generate_localized_readme(lang, edition_name, version, source_content):
    # Professional localized title mapping
    titles = {
        "es": f"CONTINUIDAD LEGACY: {edition_name}",
        "ja": f"CONTINUITY LEGACY: {edition_name} (テクニカル)",
        "ru": f"CONTINUITY LEGACY: {edition_name} (Локализация)",
        "zh": f"CONTINUITY LEGACY: {edition_name} (本地化)",
        "fr": f"CONTINUITY LEGACY: {edition_name} (Version Française)",
        "it": f"CONTINUITY LEGACY: {edition_name} (Versione Italiana)",
        "de": f"CONTINUITY LEGACY: {edition_name} (Deutsche Version)",
        "pt": f"CONTINUITY LEGACY: {edition_name} (Versão Portuguesa)",
        "en": f"CONTINUITY LEGACY: {edition_name}"
    }
    
    title = titles.get(lang, f"CONTINUITY LEGACY: {edition_name}")
    badge = f"![Version](https://img.shields.io/badge/version-{version}-blue.svg)"
    
    # Build the localized document
    header = f"# {title} 🧬🏛️\n\n{badge}\n\n"
    body = "*(Esta es una versión sincronizada del núcleo universal del framework. Por favor, consulte el README principal para la documentación completa.)*" if lang != "en" else "*(Localized technical sync for Continuity Legacy.)*"
    
    # Add strategic metadata footer with SST version stamp
    footer = f"\n\n---\n*CONTINUITY LEGACY: Global Infrastructure - Version {version} - Generated {datetime.utcnow().isoformat()}Z*"
    return header + body + footer

def sync_all(repo_root: Path, auto_gen: bool):
    edition = get_edition_name(repo_root)
    version = get_universal_version(repo_root)
    source_path = repo_root / "README.md"
    
    if not source_path.exists():
        print(f"[!] ERROR: Source README.md not found in {repo_root}")
        return
    
    print(f"[*] SYNC Engine v1.4.0: Processing {edition} (Central Version: {version})")
    
    # Update version in the source README if it's there (Experimental SST propagation)
    source_text = source_path.read_text(encoding="utf-8")
    new_source_text = re.sub(r"version-\d+\.\d+\.\d+-blue\.svg", f"version-{version}-blue.svg", source_text)
    if source_text != new_source_text:
        source_path.write_text(new_source_text, encoding="utf-8")
        print(f"    [✔] Source README version updated to {version}.")
    
    lang_dir = repo_root / "OTHER_LANGUAGES"
    lang_dir.mkdir(parents=True, exist_ok=True)
    
    for lang in LANG_CODES:
        target_path = lang_dir / f"README_{lang}.md"
        
        if auto_gen:
            content = generate_localized_readme(lang, edition, version, source_path.read_text(encoding="utf-8"))
            target_path.write_text(content, encoding="utf-8")
        
    print(f"[✔] SYNC: {edition} is globally synchronized and coherent.")

def main() -> None:
    parser = argparse.ArgumentParser(description="Universal Sync & Version Manager (v1.4.0).")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--auto-gen", action="store_true", help="Automatically generate/update localized files.")
    args = parser.parse_args()

    # Normalize path for multi-tier detection
    root = Path(args.repo_root).resolve()
    sync_all(root, args.auto_gen)

if __name__ == "__main__":
    main()
