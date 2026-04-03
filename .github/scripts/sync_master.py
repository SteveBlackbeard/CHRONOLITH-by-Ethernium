# -*- coding: utf-8 -*-
import re
from pathlib import Path
import sys

# --- Constantes Globales ---
ARCH_TREE = """```text
/PROJECT
 ├── .continuity/
 │    ├── TIMELINE.md
 │    ├── DECISIONS_LOG.md
 │    ├── LIVE_HANDOFF.md
 │    ├── BOOT_SEQUENCE.md
 │    └── STATE.json
 │
 ├── PROJECT_CONTEXT.md
 ├── tools/
 └── assets/
```"""

DEFS = {
    "es": {
        "title": "Marco de Continuidad Global",
        "problem": "## 🧠 El Problema vs. La Solución",
        "vision": "Los flujos de trabajo de IA modernos se rompen en un área crítica: **Reestablecimiento de contexto entre sesiones**.",
        "impact": "## ⚡ “La IA ya no olvida.”\n\nEstamos orgullosos de anunciar el **Lanzamiento Estable Oficial v1.3.1**. Esta versión representa la transición hacia una **infraestructura de grado profesional** diseñada para la colaboración global IA-Humano.",
        "flow_title": "## 🔁 Flujo del Sistema (El Bucle de Control)",
        "flow_desc": "Continuity Legacy asegura que no haya pérdida de contexto a través de un bucle de control perpetuo:\n\n```text\nContexto → Estado → Decisiones → Cronología → Traspaso\n```",
        "arch_title": "## 🏗️ Resumen de la Arquitectura del Proyecto"
    },
    "en": {
        "title": "Global Continuity Framework",
        "problem": "## 🧠 The Problem vs. The Solution",
        "vision": "Modern AI workflows break in one critical area: **Context resets between sessions**.",
        "impact": "## ⚡ “AI doesn’t forget anymore.”",
        "flow_title": "## 🔁 System Flow (The Control Loop)",
        "flow_desc": "Continuity Legacy ensures no context loss through a perpetual control loop:\n\n```text\nContext → State → Decisions → Timeline → Handoff\n```",
        "arch_title": "## 🏗️ Project Architecture Overview"
    },
    "default": {
        "impact": "## ⚡ “AI doesn’t forget anymore.”",
        "flow_title": "## 🔁 System Flow (The Control Loop)",
        "flow_desc": "Continuity Legacy ensures no context loss through a perpetual control loop.",
        "arch_title": "## 🏗️ Project Architecture Overview"
    }
}

def update_badge(content, status="Synchronized", color="green"):
    link = "https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/actions/workflows/global_sync.yml"
    badge_url = f"https://img.shields.io/badge/Global%20Parity-{status}-{color}"
    badge_md = f"[![Global Parity]({badge_url})]({link})"
    
    # 🏛️ ZONAS DE EXCLUSIÓN v2.1 (SEGURIDAD ATÓMICA)
    # 1. Inyección TOP
    marker_top_start = "<!-- GOVERNANCE_BADGE_TOP_START -->"
    marker_top_end = "<!-- GOVERNANCE_BADGE_TOP_END -->"
    block_top = f"{marker_top_start}\n{badge_md}\n{marker_top_end}"
    
    if marker_top_start in content:
        content = re.sub(rf"{marker_top_start}.*?{marker_top_end}", block_top, content, flags=re.DOTALL)
    else:
        # Si no hay marcadores, los creamos en puntos seguros
        if "[![Stars]" in content:
            content = content.replace("[![Stars]", block_top + "\n[![Stars]", 1)
        elif 'alt="Omega Edition">' in content:
            content = re.sub(r'(alt="Omega Edition"></a>)', r'\1\n<br>\n' + block_top, content)
        else:
            content = re.sub(r'(# .*?\n)', r'\1' + block_top + r'\n', content, 1)

    # 2. Inyección BOTTOM
    marker_bot_start = "<!-- GOVERNANCE_BADGE_BOTTOM_START -->"
    marker_bot_end = "<!-- GOVERNANCE_BADGE_BOTTOM_END -->"
    block_bot = f"\n\n---\n{marker_bot_start}\n<p align=\"right\">{badge_md}</p>\n{marker_bot_end}"
    
    if marker_bot_start in content:
        content = re.sub(rf"{marker_bot_start}.*?{marker_bot_end}", block_bot, content, flags=re.DOTALL)
    else:
        content += block_bot
        
    return content

def clean_readme(content):
    content = re.sub(r'(#### Languages\n.*?)\n\n#### Languages\n.*?\n', r'\1\n', content, flags=re.DOTALL)
    content = "\n".join([line for line in content.splitlines() if '<p align="center"><sub>' not in line])
    return content

def main():
    action_mode = "--action-mode" in sys.argv
    check_mode = "--check" in sys.argv

    master_readme_path = Path("README.md")
    master_rel_path = Path("RELEASE_NOTES_MANIFEST.md")
    
    if not master_readme_path.exists(): return

    drift_detected = False
    master_txt = master_readme_path.read_text(encoding="utf-8")
    
    if check_mode:
        es_path = Path("OTHER_LANGUAGES/README_es.md")
        if es_path.exists():
            es_txt = es_path.read_text(encoding="utf-8")
            for marker in ["continuity-pro", ".jpg", ".png"]:
                if marker in master_txt and marker not in es_txt:
                    drift_detected = True; break

    if check_mode:
        if drift_detected:
            status, color = "Out%20of%20Sync", "red"
        else:
            return

    if action_mode:
        status, color = "Synchronized", "green"

    for p in [master_readme_path, master_rel_path]:
        if p.exists():
            content = p.read_text(encoding="utf-8")
            content = update_badge(content, status, color)
            p.write_text(content, encoding="utf-8")

    if not action_mode: return

    for lang_code in ["es", "fr", "de", "it", "pt", "ru", "ja", "zh"]:
        r_path = Path(f"OTHER_LANGUAGES/README_{lang_code}.md")
        if r_path.exists():
            content = clean_readme(r_path.read_text(encoding="utf-8"))
            t = DEFS.get(lang_code, DEFS["default"])
            if "## 🧠" not in content:
                vision_block = f"\n{t.get('problem', DEFS['en']['problem'])}\n\n{t.get('vision', DEFS['en']['vision'])}\n\n```text\nContext → State → Decisions → Timeline → Handoff\n```\n"
                content = content.replace("## 🏢", vision_block + "\n## 🏢")
            r_path.write_text(content, encoding="utf-8")
        
        rel_path = Path(f"OTHER_LANGUAGES/RELEASE_v1.3.1_{lang_code}.md")
        if rel_path.exists():
            rel_content = rel_path.read_text(encoding="utf-8")
            t_rel = DEFS.get(lang_code, DEFS["default"])
            if "## ⚡" not in rel_content:
                rel_content = rel_content.replace("---", "---\n\n" + t_rel.get('impact', DEFS['en']['impact']), 1)
            if "## 🔁" not in rel_content:
                flow_block = f"\n{t_rel.get('flow_title', DEFS['en']['flow_title'])}\n\n{t_rel.get('flow_desc', DEFS['en']['flow_desc'])}\n\n---\n"
                rel_content = rel_content.replace("## ✨", flow_block + "## ✨")
            if "## 🏗️" not in rel_content:
                arch_block = f"\n{t_rel.get('arch_title', DEFS['en']['arch_title'])}\n\n{ARCH_TREE}\n\n---\n"
                rel_content = rel_content.replace("## 🔍", arch_block + "## 🔍")
            rel_path.write_text(rel_content, encoding="utf-8")

if __name__ == "__main__":
    main()
