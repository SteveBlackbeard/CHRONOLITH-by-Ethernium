# -*- coding: utf-8 -*-
from pathlib import Path
import re

# Traducciones y Estructura
DEFS = {
    "es": {"title": "Marco de Continuidad Global", "problem": "## 🧠 El Problema vs. La Solución", "vision": "Los flujos de trabajo de IA modernos se rompen en un área crítica: **Reestablecimiento de contexto entre sesiones**.", "impact": "## ⚡ “La IA ya no olvida.”\n\nEstamos orgullosos de anunciar el **Lanzamiento Estable Oficial v1.3.1**. Esta versión representa la transición hacia una **infraestructura de grado profesional** diseñada para la colaboración global IA-Humano.", "flow_title": "## 🔁 Flujo del Sistema (El Bucle de Control)", "flow_desc": "Continuity Legacy asegura que no haya pérdida de contexto a través de un bucle de control perpetuo:\n\n```text\nContexto → Estado → Decisiones → Cronología → Traspaso\n```", "arch_title": "## 🏗️ Resumen de la Arquitectura del Proyecto"},
    "en": {"title": "Global Continuity Framework", "problem": "## 🧠 The Problem vs. The Solution", "vision": "Modern AI workflows break in one critical area: **Context resets between sessions**.", "impact": "## ⚡ “AI doesn’t forget anymore.”", "flow_title": "## 🔁 System Flow (The Control Loop)", "flow_desc": "Continuity Legacy ensures no context loss through a perpetual control loop:\n\n```text\nContext → State → Decisions → Timeline → Handoff\n```", "arch_title": "## 🏗️ Project Architecture Overview"}
}

def clean_readme(content):
    content = re.sub(r'(#### Languages\n.*?)\n\n#### Languages\n.*?\n', r'\1\n', content, flags=re.DOTALL)
    content = "\n".join([line for line in content.splitlines() if '<p align="center"><sub>' not in line])
    return content

def sync_all():
    arch_tree = """```text
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

    for lang, t in DEFS.items():
        if lang == "en": continue
        
        # 1. Sync README_lang.md (Additive)
        r_path = Path(f"OTHER_LANGUAGES/README_{lang}.md")
        if r_path.exists():
            content = clean_readme(r_path.read_text(encoding="utf-8"))
            if "## 🧠" not in content:
                vision_block = f"\n{t['problem']}\n\n{t['vision']}\n\n```text\nContext → State → Decisions → Timeline → Handoff\n```\n"
                content = content.replace("## 🏢", vision_block + "\n## 🏢")
            
            # Sub injection
            content = content.replace("LEGACYlite.png)](../continuity-lite)", "LEGACYlite.png)](../continuity-lite)\n<p align=\"center\"><sub><b>Continuity Legacy Lite</b>: Sincronización mínima local con síntesis de ADN.</sub></p>")
            content = content.replace("LEGACYPRO.png)](../continuity)", "LEGACYPRO.png)](../continuity)\n<p align=\"center\"><sub><b>Continuity Legacy Pro</b>: Guardia fronterizo de grado industrial.</sub></p>")
            content = content.replace("LEGACYOMEGA.png)](../continuity-omega)", "LEGACYOMEGA.png)](../continuity-omega)\n<p align=\"center\"><sub><b>Continuity Legacy Omega</b>: RAG avanzado y análisis de impacto proactivo.</sub></p>")
            
            r_path.write_text(content, encoding="utf-8")
            print(f"[OK] README_{lang}.md synced.")

        # 2. Sync RELEASE_v1.3.1_lang.md (Additive)
        rel_path = Path(f"OTHER_LANGUAGES/RELEASE_v1.3.1_{lang}.md")
        if rel_path.exists():
            rel_content = rel_path.read_text(encoding="utf-8")
            t_rel = DEFS.get(lang, DEFS["en"])
            
            if "## ⚡" not in rel_content:
                rel_content = rel_content.replace("---", "---\n\n" + t_rel["impact"], 1)
            if "## 🔁" not in rel_content:
                flow_block = f"\n{t_rel['flow_title']}\n\n{t_rel['flow_desc']}\n\n---\n"
                rel_content = rel_content.replace("## ✨", flow_block + "## ✨")
            if "## 🏗️" not in rel_content:
                arch_block = f"\n{t_rel['arch_title']}\n\n{arch_tree}\n\n---\n"
                rel_content = rel_content.replace("## 🔍", arch_block + "## 🔍")
                
            rel_path.write_text(rel_content, encoding="utf-8")
            print(f"[OK] RELEASE_{lang}.md synced.")

if __name__ == "__main__":
    sync_all()
