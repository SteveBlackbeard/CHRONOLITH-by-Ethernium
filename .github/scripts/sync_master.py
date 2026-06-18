# -*- coding: utf-8 -*-
import re
import sys
from pathlib import Path


BANNER_HTML = """<p align="center">
  <img src="https://raw.githubusercontent.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/main/banners/ethernium_header.png?raw=true" alt="Ethernium Continuity Legacy Official Header">
</p>"""

ARCH_TREE = """```text
/PROJECT
 |-- .continuity/
 |   |-- TIMELINE.md
 |   |-- DECISIONS_LOG.md
 |   |-- LIVE_HANDOFF.md
 |   |-- BOOT_SEQUENCE.md
 |   `-- STATE.json
 |
 |-- PROJECT_CONTEXT.md
 |-- tools/
 `-- assets/
```"""

DEFS = {
    "es": {
        "title": "Marco de Continuidad Global",
        "problem": "## El Problema vs. La Solucion",
        "vision": "Los flujos de trabajo de IA modernos se rompen en un area critica: **Reestablecimiento de contexto entre sesiones**.",
        "impact": "## La IA ya no olvida.\n\nEstamos orgullosos de anunciar el **Lanzamiento Estable Oficial v1.3.1**. Esta version representa la transicion hacia una **infraestructura de grado profesional** disenada para la colaboracion global IA-Humano.",
        "flow_title": "## Flujo del Sistema (El Bucle de Control)",
        "flow_desc": "Continuity Legacy asegura que no haya perdida de contexto a traves de un bucle de control perpetuo:\n\n```text\nContexto -> Estado -> Decisiones -> Cronologia -> Traspaso\n```",
        "arch_title": "## Resumen de la Arquitectura del Proyecto",
    },
    "en": {
        "title": "Global Continuity Framework",
        "problem": "## The Problem vs. The Solution",
        "vision": "Modern AI workflows break in one critical area: **Context resets between sessions**.",
        "impact": "## AI does not forget anymore.",
        "flow_title": "## System Flow (The Control Loop)",
        "flow_desc": "Continuity Legacy ensures no context loss through a perpetual control loop:\n\n```text\nContext -> State -> Decisions -> Timeline -> Handoff\n```",
        "arch_title": "## Project Architecture Overview",
    },
    "default": {
        "impact": "## AI does not forget anymore.",
        "flow_title": "## System Flow (The Control Loop)",
        "flow_desc": "Continuity Legacy ensures no context loss through a perpetual control loop.",
        "arch_title": "## Project Architecture Overview",
    },
}


def preserve_images(old_content, new_content):
    """Preserve image references from old content if the new content lacks them."""
    images = re.findall(r"(!\[.*?\]\(.*?\)|<img .*?>)", old_content)
    for img in reversed(images):
        if img not in new_content:
            new_content = img + "\n" + new_content
    return new_content


def update_header(content):
    """Ensure BANNER_HTML is the first file element."""
    if BANNER_HTML in content:
        return content
    content = re.sub(r'^<p align="center">.*?</p>', "", content, flags=re.DOTALL | re.MULTILINE).strip()
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
    block_bot = f'\n\n---\n{marker_bot_start}\n<p align="right">{badge_md}</p>\n{marker_bot_end}'

    if marker_bot_start in content:
        content = re.sub(rf"{marker_bot_start}.*?{marker_bot_end}", block_bot, content, flags=re.DOTALL)

    return content


def main():
    action_mode = "--action-mode" in sys.argv
    master_readme_path = Path("README.md")
    master_rel_path = Path("RELEASE_NOTES_MANIFEST.md")
    if not master_readme_path.exists():
        return

    status, color = ("Synchronized", "green") if action_mode else ("Out%20of%20Sync", "red")

    for path in [master_readme_path, master_rel_path]:
        if path.exists():
            content = path.read_text(encoding="utf-8")
            content = update_header(content)
            content = update_badge(content, status, color)
            path.write_text(content, encoding="utf-8")

    if not action_mode:
        return

    for lang_code in ["es", "fr", "de", "it", "pt", "ru", "ja", "zh"]:
        readme_path = Path(f"OTHER_LANGUAGES/README_{lang_code}.md")
        if readme_path.exists():
            old_content = readme_path.read_text(encoding="utf-8")
            content = update_header(old_content)
            content = re.sub(
                r"<!-- GOVERNANCE_BADGE_TOP_.*? -->.*?<!-- GOVERNANCE_BADGE_TOP_.*? -->",
                "",
                content,
                flags=re.DOTALL,
            )
            content = re.sub(r"\[\!\[Global Parity\].*?\-green\)", "", content)
            readme_path.write_text(content, encoding="utf-8")

        release_path = Path(f"OTHER_LANGUAGES/RELEASE_v1.3.1_{lang_code}.md")
        if release_path.exists():
            old_release = release_path.read_text(encoding="utf-8")
            content = update_header(old_release)
            content = re.sub(r"\[\!\[Global Parity\].*?\-green\)", "", content)
            release_path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    main()
