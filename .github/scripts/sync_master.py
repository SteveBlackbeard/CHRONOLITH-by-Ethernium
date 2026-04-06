# -*- coding: utf-8 -*-
import re
from pathlib import Path
import sys

# --- Constantes Globales ---
BANNER_HTML = """<p align="center">
  <img src="https://raw.githubusercontent.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/main/banners/ethernium_header.png?raw=true" alt="Ethernium Continuity Legacy Official Header">
</p>"""

ARCH_TREE = """```text
/PROJECT
 â”œâ”€â”€ .continuity/
 â”‚    â”œâ”€â”€ TIMELINE.md
 â”‚    â”œâ”€â”€ DECISIONS_LOG.md
 â”‚    â”œâ”€â”€ LIVE_HANDOFF.md
 â”‚    â”œâ”€â”€ BOOT_SEQUENCE.md
 â”‚    â””â”€â”€ STATE.json
 â”‚
 â”œâ”€â”€ PROJECT_CONTEXT.md
 â”œâ”€â”€ tools/
 â””â”€â”€ assets/
```"""

DEFS = {
    "es": {
        "title": "Marco de Continuidad Global",
        "problem": "## ðŸ§  El Problema vs. La SoluciÃ³n",
        "vision": "Los flujos de trabajo de IA modernos se rompen en un Ã¡rea crÃ­tica: **Reestablecimiento de contexto entre sesiones**.",
        "impact": "## âš¡ â€œLa IA ya no olvida.â€\n\nEstamos orgullosos de anunciar el **Lanzamiento Estable Oficial v1.3.1**. Esta versiÃ³n representa la transiciÃ³n hacia una **infraestructura de grado profesional** diseÃ±ada para la colaboraciÃ³n global IA-Humano.",
        "flow_title": "## ðŸ” Flujo del Sistema (El Bucle de Control)",
        "flow_desc": "Continuity Legacy asegura que no haya pÃ©rdida de contexto a travÃ©s de un bucle de control perpetuo:\n\n```text\nContexto â†’ Estado â†’ Decisiones â†’ CronologÃ­a â†’ Traspaso\n```",
        "arch_title": "## ðŸ—ï¸ Resumen de la Arquitectura del Proyecto"
    },
    "en": {
        "title": "Global Continuity Framework",
        "problem": "## ðŸ§  The Problem vs. The Solution",
        "vision": "Modern AI workflows break in one critical area: **Context resets between sessions**.",
        "impact": "## âš¡ â€œAI doesnâ€™t forget anymore.â€",
        "flow_title": "## ðŸ” System Flow (The Control Loop)",
        "flow_desc": "Continuity Legacy ensures no context loss through a perpetual control loop:\n\n```text\nContext â†’ State â†’ Decisions â†’ Timeline â†’ Handoff\n```",
        "arch_title": "## ðŸ—ï¸ Project Architecture Overview"
    },
    "default": {
        "impact": "## âš¡ â€œAI doesnâ€™t forget anymore.â€",
        "flow_title": "## ðŸ” System Flow (The Control Loop)",
        "flow_desc": "Continuity Legacy ensures no context loss through a perpetual control loop.",
        "arch_title": "## ðŸ—ï¸ Project Architecture Overview"
    }
}

def preserve_images(old_content, new_content):
    """Extrae las imÃ¡genes del contenido antiguo y las inyecta en el nuevo si no existen."""
    images = re.findall(r'(!\[.*?\]\(.*?\)|<img .*?>)', old_content)
    for img in reversed(images):
        if img not in new_content:
            new_content = img + "\n" + new_content
    return new_content

def update_header(content):
    """Asegura que el BANNER_HTML sea el primer elemento del archivo."""
    if BANNER_HTML in content:
        return content
    # Eliminamos cualquier encabezado previo <p align="center">...</p> que contenga imÃ¡genes
    content = re.sub(r'^<p align="center">.*?</p>', '', content, flags=re.DOTALL | re.MULTILINE).strip()
    return f"{BANNER_HTML}\n\n{content}"

def update_badge(content, status="Synchronized", color="green"):
    link = "https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/actions/workflows/global_sync.yml"
    badge_url = f"https://img.shields.io/badge/Global%20Parity-{status}-{color}"
    badge_md = f"[![Global Parity]({badge_url})]({link})"
    
    marker_top_start = "<!-- GOVERNANCE_BADGE_TOP_START -->"
    marker_top_end = "<!-- GOVERNANCE_BADGE_TOP_END -->"
    block_top = f"{marker_top_start}{badge_md}{marker_top_end}"
    
    if marker_top_start in content:
        content = re.sub(rf"{marker_top_start}.*?{marker_top_end}", block_top, content, flags=re.DOTALL)
    
    marker_bot_start = "<!-- GOVERNANCE_BADGE_BOTTOM_START -->"
    marker_bot_end = "<!-- GOVERNANCE_BADGE_BOTTOM_END -->"
    block_bot = f"\n\n---\n{marker_bot_start}\n<p align=\"right\">{badge_md}</p>\n{marker_bot_end}"
    
    if marker_bot_start in content:
        content = re.sub(rf"{marker_bot_start}.*?{marker_bot_end}", block_bot, content, flags=re.DOTALL)
        
    return content

def main():
    action_mode = "--action-mode" in sys.argv
    master_readme_path = Path("README.md")
    master_rel_path = Path("RELEASE_NOTES_MANIFEST.md")
    if not master_readme_path.exists(): return

    status, color = ("Synchronized", "green") if action_mode else ("Out%20of%20Sync", "red")

    for p in [master_readme_path, master_rel_path]:
        if p.exists():
            content = p.read_text(encoding="utf-8")
            content = update_header(content) # APLICAR BANNER
            content = update_badge(content, status, color)
            p.write_text(content, encoding="utf-8")

    if not action_mode: return

    for lang_code in ["es", "fr", "de", "it", "pt", "ru", "ja", "zh"]:
        r_path = Path(f"OTHER_LANGUAGES/README_{lang_code}.md")
        if r_path.exists():
            old_c = r_path.read_text(encoding="utf-8")
            content = update_header(old_c) # PROPAGAR BANNER
            
            # Limpieza de badges si existieran por error
            content = re.sub(r'<!-- GOVERNANCE_BADGE_TOP_.*? -->.*?<!-- GOVERNANCE_BADGE_TOP_.*? -->', '', content, flags=re.DOTALL)
            content = re.sub(r'\[\!\[Global Parity\].*?\-green\)', '', content)
            
            r_path.write_text(content, encoding="utf-8")
        
        rel_path = Path(f"OTHER_LANGUAGES/RELEASE_v1.3.1_{lang_code}.md")
        if rel_path.exists():
            old_rel = rel_path.read_text(encoding="utf-8")
            content = update_header(old_rel) # PROPAGAR BANNER
            
            # Limpieza REL
            content = re.sub(r'\[\!\[Global Parity\].*?\-green\)', '', content)
            
            rel_path.write_text(content, encoding="utf-8")

if __name__ == "__main__":
    main()

