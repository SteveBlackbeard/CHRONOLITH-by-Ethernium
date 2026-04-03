# -*- coding: utf-8 -*-
from pathlib import Path
import re

DEFS = {
    "es": {"impact": "## ⚡ “La IA ya no olvida.”", "flow_title": "## 🔁 Flujo del Sistema (El Bucle de Control)", "arch_title": "## 🏗️ Resumen de la Arquitectura del Proyecto"},
    "en": {"impact": "## ⚡ “AI doesn’t forget anymore.”", "flow_title": "## 🔁 System Flow (The Control Loop)", "arch_title": "## 🏗️ Project Architecture Overview"}
}

def clean_redundancies(content):
    # Remove duplicate "Estamos orgullosos de anunciar..." or similar patterns if they occur consecutively
    lines = content.splitlines()
    new_lines = []
    for i, line in enumerate(lines):
        if i > 0 and line.strip() and line.strip() == lines[i-1].strip():
            continue
        # Specific fix for the Spanish double intro observed
        if "Estamos orgullosos de anunciar el **Lanzamiento Estable Oficial v1.3.1**" in line and i > 0:
            if any("Estamos orgullosos de anunciar" in prev for prev in new_lines[-5:]):
                continue
        new_lines.append(line)
    return "\n".join(new_lines)

def main():
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

    for lang_code in ["es", "fr", "de", "it", "pt", "ru", "ja", "zh"]:
        path = Path(f"OTHER_LANGUAGES/RELEASE_v1.3.1_{lang_code}.md")
        if not path.exists(): continue
        
        content = path.read_text(encoding="utf-8")
        content = clean_redundancies(content)
        
        path.write_text(content, encoding="utf-8")
        print(f"[OK] RELEASE_{lang_code}.md - Pulido completado.")

if __name__ == "__main__":
    main()
