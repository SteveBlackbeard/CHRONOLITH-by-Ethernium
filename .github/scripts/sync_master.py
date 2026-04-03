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
    
    # PULREZA TOTAL: Limpiamos CUALQUIER rastro previo de este badge
    content = re.sub(r'\[\!\[Global Parity\].*?\)(\]\(https://github.com/.*?/actions/workflows/global_sync.yml\))*', '', content, flags=re.DOTALL)
    
    # Inyección Limpia 1: Top (bajo la lista de badges)
    content = content.replace("[![Stars]", badge_md + "\n[![Stars]", 1)
    
    # Inyección Limpia 2: Bottom
    # Remove old footer marker if exists to avoid recursion
    content = content.split("\n\n---\n<p align=\"right\">")[0]
    content += f"\n\n---\n<p align=\"right\">{badge_md}</p>\n"
    
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
        print("[!] Performing structural check for drift...")
        es_path = Path("OTHER_LANGUAGES/README_es.md")
        if es_path.exists():
            es_txt = es_path.read_text(encoding="utf-8")
            for marker in ["continuity-pro", ".jpg", ".png", "LITE", "OMEGA"]:
                if marker in master_txt and marker not in es_txt:
                    drift_detected = True; break
            if len(master_txt) > len(es_txt) + 200:
                drift_detected = True

    if check_mode:
        if drift_detected:
            print("[!] DRIFT DETECTED! Setting badge to RED.")
            status, color = "Out%20of%20Sync", "red"
        else:
            print("[OK] Parity confirmed. System state is Green.")
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
            content = content.replace("LEGACYlite.png)](../continuity-lite)", "LEGACYlite.png)](../continuity-lite)\n<p align=\"center\"><sub><b>Continuity Legacy Lite</b>: Minimal local sync.</sub></p>")
            content = content.replace("LEGACYPRO.png)](../continuity-pro)", "LEGACYPRO.png)](../continuity-pro)\n<p align=\"center\"><sub><b>Continuity Legacy Pro</b>: Industrial grade guard.</sub></p>")
            content = content.replace("LEGACYOMEGA.png)](../continuity-omega)", "LEGACYOMEGA.png)](../continuity-omega)\n<p align=\"center\"><sub><b>Continuity Legacy Omega</b>: Enterprise RAG oracle.</sub></p>")
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
