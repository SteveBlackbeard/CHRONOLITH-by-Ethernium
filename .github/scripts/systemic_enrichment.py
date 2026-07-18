import os
import re
from pathlib import Path

# THE SYSTEMIC ENRICHMENT ENGINE (v2.4.2 - TONAL SWEEP & REFINEMENT)
# -------------------------------------------------------------------
# 1. Harmonizes the new title "Persistent Cognitive Layer" globally.
# 2. Eliminates deprecated terms: "military", "sovereign", "visceral".
# 3. Ensures badges are correctly linked in all translations.
# 4. Removes redundant legacy files.

NEW_TITLE_EN = "Chronolith: Persistent Cognitive Layer 🧬"
SLOGAN = "\n\n---\n*Chronolith: Protecting the logical lineage of your software.*"

TRANSLATIONS = {
    "es": "Capa Cognitiva Persistente",
    "ja": "持続的認知レイヤー",
    "zh": "持久性认知层",
    "ru": "Постоянный когнитивный слой",
    "fr": "Couche Cognitive Persistante",
    "it": "Livello Cognitivo Persistente",
    "de": "Persistente kognitive Schicht",
    "pt": "Camada Cognitiva Persistente"
}

FORBIDDEN_TERMS = {
    r'\bmilitary-grade\b': 'Enterprise-grade',
    r'\bsovereign\b': 'deterministic',
    r'\bvisceral\b': 'impactful',
    r'\bMilitarized\b': 'Hardened',
    r'\bSovereignty\b': 'Governance'
}

def refine_system():
    root = Path(".")
    count = 0
    
    # 1. Remove redundant legacy files
    legacy_files = ["LIVE_HANDOFF.md"]
    for lf in legacy_files:
        p = root / lf
        if p.exists():
            p.unlink()
            print(f"    [!] DELETED LEGACY: {lf}")

    # 2. Sync READMEs and RELEASES in OTHER_LANGUAGES
    lang_dir = root / "OTHER_LANGUAGES"
    
    # Audit all markdown files for global consistency
    all_md = list(root.glob("*.md")) + list(lang_dir.glob("*.md"))
    
    for f_path in all_md:
        if "PROJECT_DNA" in f_path.name: continue
        
        content = f_path.read_text(encoding="utf-8")
        changed = False
        
        # Tonal Sweep (Lexical Harmonization)
        for pattern, replacement in FORBIDDEN_TERMS.items():
            if re.search(pattern, content, re.IGNORECASE):
                content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                changed = True
        
        # Title Sync (READMEs only)
        if "README" in f_path.name:
            if f_path.parent.name == "OTHER_LANGUAGES":
                lang_code = f_path.name.split("_")[1].split(".")[0]
                title_trans = TRANSLATIONS.get(lang_code, NEW_TITLE_EN)
                content = re.sub(r'# Chronolith: .*', f"# Chronolith: {title_trans} 🧬", content)
            else:
                # Root README title already done, but ensuring here
                content = re.sub(r'# Chronolith: .*', f"# Chronolith: Persistent Cognitive Layer 🧬", content)
            changed = True

        # Ensure slogan
        if slogan_text := "Protecting the logical lineage of your software.":
          if slogan_text not in content:
              content = content.rstrip() + SLOGAN
              changed = True
            
        if changed:
            f_path.write_text(content.strip() + "\n", encoding="utf-8")
            print(f"    [✔] Refined: {f_path.as_posix()}")
            count += 1

    print(f"\n[*] GLOBAL REFINEMENT COMPLETE: {count} files synchronized.")

if __name__ == "__main__":
    refine_system()
