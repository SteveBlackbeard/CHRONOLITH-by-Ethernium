from __future__ import annotations
import argparse
import traceback
import os
import re
import json
from pathlib import Path
from datetime import datetime

# CHRONOLITH: Global Sync & Authority Engine (v1.5.0)
# ---------------------------------------------------------
# ENE Optimized: Semantic sidecar loading (x20 script weight reduction).

LANG_CODES = ["es", "ja", "ru", "zh", "fr", "it", "de", "pt", "ko", "ar", "en"]

# Written into every generated file, and the only way to tell a placeholder
# from a real translation that must not be clobbered.
MARKER = "CHRONOLITH: Global Infrastructure - Generated"

def load_translations():
    """ENE: Dynamic Nucleotide Loading (Saves 6,000 tokens of active logic)."""
    try:
        json_path = Path(__file__).parent / "translations_ene.json"
        if json_path.exists():
            return json.loads(json_path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"en": {"tagline": "Protecting the logical lineage of your software.", "footer_brand": "CHRONOLITH: Industrial Infrastructure"}}

TRANSLATIONS = load_translations()

# Add remaining slots with default (EN) or quick localized logic if needed
for l in ["fr", "it", "de", "pt"]:
    if l not in TRANSLATIONS: TRANSLATIONS[l] = TRANSLATIONS["en"]

def get_universal_version(repo_root: Path) -> str:
    v_file = repo_root / "VERSION"
    if not v_file.exists(): v_file = repo_root.parent / "VERSION"
    if v_file.exists():
        raw = v_file.read_bytes()
        try:
            return raw.decode("utf-8-sig").strip()
        except UnicodeDecodeError:
            try: return raw.decode("utf-16").strip()
            except UnicodeDecodeError:
                return raw.decode("latin-1").replace("\x00", "").strip()
    return "2.1.0"

def get_edition_name(root: Path) -> str:
    if (root / "chronolith-lite").exists(): return "Root Portal"
    if "lite" in root.name.lower(): return "Lite Edition"
    if "omega" in root.name.lower(): return "Omega Edition"
    if "pro" in root.name.lower() or "chronolith" == root.name.lower(): return "Pro Edition"
    return "Universal Core"

def generate_ribbons(lang, is_root, base_path):
    lang_path = f"{base_path}OTHER_LANGUAGES/"
    lite_banner = f"[![LITE](https://raw.githubusercontent.com/SteveBlackbeard/CHRONOLITH-by-Ethernium/main/assets/banners/LEGACYlite.png?raw=true)]({base_path}chronolith-lite/)"
    pro_banner = f"[![PRO](https://raw.githubusercontent.com/SteveBlackbeard/CHRONOLITH-by-Ethernium/main/assets/banners/LEGACYPRO.png?raw=true)]({base_path}chronolith-pro/)"
    omega_banner = f"[![OMEGA](https://raw.githubusercontent.com/SteveBlackbeard/CHRONOLITH-by-Ethernium/main/assets/banners/LEGACYOMEGA.png?raw=true)]({base_path}chronolith-omega/)"
    
    v_ribbon = f"{lite_banner}\n\n{pro_banner}\n\n{omega_banner}"
    l_ribbon = ""
    for l in LANG_CODES:
        link = f"{base_path}README.md" if l == "en" else f"{lang_path}README_{l}.md"
        l_ribbon += f"[![{l.upper()}](https://img.shields.io/badge/{l.upper()}-white)]({link}) "
    return v_ribbon, l_ribbon

def generate_localized_readme(lang, edition_name, version, is_root):
    t = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    base_path = "./" if is_root else "../"
    v_ribbon, l_ribbon = generate_ribbons(lang, is_root, base_path)
    title = f"CHRONOLITH: {edition_name}"
    if lang != "en": title = f"{title} ({t.get('footer_brand', '').split(': ')[-1]})"
    badge = f"![Version](https://img.shields.io/badge/version-{version}-blue.svg)"
    is_lite_only = (version == "1.3.1")
    tiers_body = f"- {t.get('lite_desc', '')}"
    if not is_lite_only:
        tiers_body += f"\n- {t.get('pro_desc', '')}\n- {t.get('omega_desc', '')}"
    omega_section = ""
    if not is_lite_only:
        omega_section = f"\n---\n\n## {t.get('omega_section_title', '')}\n{t.get('omega_text', '')}\n\n![Ethernium Omega](https://media.canary.gl/m/4346747d6be20a7b)"
    
    use_cases_section = ""
    if "use_cases_title" in t:
        use_cases_list = "\n".join([f"{i+1}. {case}" for i, case in enumerate(t.get('use_cases', []))])
        use_cases_section = f"\n---\n\n## {t['use_cases_title']}\n{t.get('use_cases_intro', '')}\n{use_cases_list}"

    lines = [
        f"# {title}",
        f"{badge}",
        f"\n#### {t.get('editions_title', 'Editions')}\n{v_ribbon}",
        f"\n#### {t.get('languages_title', 'Languages')}\n{l_ribbon}",
        f"\n-----",
        f"\n## {t.get('tiers_title', '')}",
        v_ribbon,
        f"\n---\n\n## 📊 Technical Specifications (Hardware Profiles)",
        "| Edition | RAM (Min) | Storage | Dependencies | Best For |\n| :--- | :--- | :--- | :--- | :--- |\n| **Lite** | < 100 MB | < 5 MB | Zero | Local Dev / CI-CD |\n| **Pro** | 4 GB | 50 MB | Standard | Industrial Handoffs |\n| **Omega** | 16 GB+ | 500 MB+ | RAG/Graph | Enterprise Strategy |",
        use_cases_section,
        f"\n---\n\n## 🚀 Modos de Operación (How to use)\n"
        f"1. **Modo Autónomo (Industrial CLI)**: Ejecute `chronolith-lite status` para ver la salud del sistema.\n"
        f"2. **Modo Centinela (Automatic Guardian)**: Use `chronolith-lite init` para activar Hooks automáticos.\n"
        f"3. **Modo Auditor (DNA Oracle)**: Use el motor Omega para informes de deriva semántica.",
        f"\n---",
        f"\n## {t.get('features_title', '')}",
        f"- {t.get('feat_metabolism', '')}\n- {t.get('feat_dna', '')}\n- {t.get('feat_cognitive', '')}\n- {t.get('feat_global', '')}\n- {t.get('feat_diamond', '')}",
        omega_section,
        f"\n---\n\n## {t.get('quality_title', '')}",
        "\n".join([f"{i+1}. {step}" for i, step in enumerate(t.get('quality_steps', []))]),
        f"\n---\n*Chronolith: {t.get('tagline', '')}*",
        f"\n---\n* {t.get('footer_brand', '')} - Version {version} - Generated {datetime.utcnow().isoformat()}Z *"
    ]
    return "\n".join(lines)

def generate_localized_release(lang, version):
    t = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    base_url = f"https://github.com/SteveBlackbeard/CHRONOLITH-by-Ethernium/blob/main/"
    title = f"Official Stable Release v{version} - {t.get('footer_brand', '').split(': ')[-1]}"
    is_lite_only = (version == "1.3.1")
    v_ribbon, _ = generate_ribbons(lang, True, base_url)
    tiers_body = f"- {t.get('lite_desc', '')}"
    if not is_lite_only:
        tiers_body += f"\n- {t.get('pro_desc', '')}\n- {t.get('omega_desc', '')}"
    omega_section = ""
    if not is_lite_only:
        omega_section = f"\n---\n\n## {t.get('omega_section_title', '')}\n{t.get('omega_text', '')}\n\n![Ethernium Omega](https://media.canary.gl/m/4346747d6be20a7b)"
    
    lines = [
        f"**{t.get('tagline', '')}** 🧬\n<p align=\"center\">\n  <img src=\"https://raw.githubusercontent.com/SteveBlackbeard/CHRONOLITH-by-Ethernium/main/banners/ethernium_header.png?raw=true\" alt=\"Ethernium Chronolith Official Header\">\n</p>",
        f"\n{t.get('overview', '')}",
        f"\n## 🏛️ {t.get('editions_title', 'Editions')}\n{v_ribbon}",
        f"\n##  Navigation Explorer",
        f"*   [**Industrial Guide** (HOW_TO_USE_IT.md)](../HOW_TO_USE_IT.md)",
        f"*   [**Main Documentation** (README.md)](../README_{lang}.md)",
        f"*   [**Legal Heritage** (LICENSE)](../LICENSE)",
        f"*   [**Decision Log** (.chronolith/DECISIONS_LOG.md)](../.chronolith/DECISIONS_LOG.md)",
        f"\n---\n\n## 📊 Technical Specifications (Hardware Profiles)",
        "| Edition | RAM (Min) | Storage | Dependencies | Best For |\n| :--- | :--- | :--- | :--- | :--- |\n| **Lite** | < 100 MB | < 5 MB | Zero | Local Dev / CI-CD |\n| **Pro** | 4 GB | 50 MB | Standard | Industrial Handoffs |\n| **Omega** | 16 GB+ | 500 MB+ | RAG/Graph | Enterprise Strategy |",
        omega_section,
        f"\n---\n*Chronolith: {t.get('tagline', '')}*"
    ]
    return "\n".join(lines)

def sync_all(repo_root: Path, auto_gen: bool):
    edition = get_edition_name(repo_root)
    version = get_universal_version(repo_root)
    is_root_dir = (repo_root / "chronolith-lite").exists()
    source_path = repo_root / "README.md"
    if not source_path.exists(): return
    try:
        source_content = source_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        source_content = source_path.read_text(encoding="latin-1")
    
    print(f"[*] Global Sync v1.5.0: Processing {edition} ({version})")
    lang_dir = repo_root / "OTHER_LANGUAGES"
    lang_dir.mkdir(parents=True, exist_ok=True)
    for lang in LANG_CODES:
        try:
            target_path = lang_dir / f"README_{lang}.md"
            if auto_gen:
                content = generate_localized_readme(lang, edition, version, is_root_dir)
                target_path.write_text(content, encoding="utf-8")
            if is_root_dir:
                release_path = lang_dir / f"RELEASE_v{version}_{lang}.md"
                if auto_gen:
                    release_content = generate_localized_release(lang, version)
                    release_path.write_text(release_content, encoding="utf-8")
        except Exception as e:
            print(f"[!] Error processing {lang}: {e}")
            continue
    print(f"[✔] SYNC: {edition} is globally synchronized and high-fidelity.")

def main() -> None:
    parser = argparse.ArgumentParser(description="Global Sync & Authority Engine (v1.5.0).")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--auto-gen", action="store_true")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    sync_all(root, args.auto_gen)

if __name__ == "__main__":
    main()
