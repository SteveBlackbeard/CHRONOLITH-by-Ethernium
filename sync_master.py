# -*- coding: utf-8 -*-
import re
from pathlib import Path

DEFS = {
    "es": {"title": "Marco de Continuidad Global", "problem": "## 🧠 El Problema vs. La Solución", "vision": "Los flujos de trabajo de IA modernos se rompen en un área crítica: **Reestablecimiento de contexto entre sesiones**."},
    "fr": {"title": "Cadre de Continuité Globale", "problem": "## 🧠 Le Problème vs. La Solution", "vision": "Les flux de travail d'IA modernes se brisent dans un domaine critique : **Réinitialisation du contexte entre les sessions**."},
    "de": {"title": "Globaler Kontinuitätsrahmen", "problem": "## 🧠 Das Problem vs. Die Lösung", "vision": "Moderne KI-Workflows brechen in einem kritischen Bereich: **Kontext-Resets zwischen den Sitzungen**."},
    "it": {"title": "Quadro di Continuità Globale", "problem": "## 🧠 Il Problema vs. La Soluzione", "vision": "I moderni flussi di lavoro dell'IA si interrompono in un'area critica: **Reset del contesto tra le sessioni**."},
    "pt": {"title": "Estrutura de Continuidade Global", "problem": "## 🧠 O Problema vs. A Solução", "vision": "Os fluxos de trabalho de IA modernos quebram em uma área crítica: **Resets de contexto entre sessões**."},
    "ru": {"title": "Глобальная Система Преемственности", "problem": "## 🧠 Проблема vs. Решение", "vision": "Современные рабочие процессы ИИ прерываются в критической области: **Сброс контекста между сессиями**."},
    "ja": {"title": "グローバル・コンティニュイティ・フレームワーク", "problem": "## 🧠 問題点 vs. 解決策", "vision": "現代のAIワークフローは、ある重要な領域で中断されます：**セッション間のコンテキストのリセット**。"},
    "zh": {"title": "全球连续性框架", "problem": "## 🧠 问题 vs. 解决方案", "vision": "现代 AI 工作流程在一个关键领域断裂：**会话之间的上下文重置**。"}
}

def clean_content(content):
    # Remove duplicate language ribbons
    content = re.sub(r'(#### Languages\n.*?)\n\n#### Languages\n.*?\n', r'\1\n', content, flags=re.DOTALL)
    # Remove any existing sub paragraphs to prevent triplication
    content = [line for line in content.splitlines() if '<p align="center"><sub>' not in line]
    return "\n".join(content)

def main():
    master = Path("README.md").read_text(encoding="utf-8")
    for lang, t in DEFS.items():
        path = Path(f"OTHER_LANGUAGES/README_{lang}.md")
        if not path.exists(): continue
        
        content = clean_content(path.read_text(encoding="utf-8"))
        
        # Inject Vision Section before Editions
        if "## 🧠" not in content:
            vision_block = f"\n{t['problem']}\n\n{t['vision']}\n\n```text\nContext → State → Decisions → Timeline → Handoff\n```\n"
            content = content.replace("## 🏢", vision_block + "\n## 🏢")
            
        # Ensure correct banner formatting with <sub>
        # This is a bit manual but safer
        lite_desc = f'<p align="center"><sub><b>Continuity Legacy Lite</b>: Sincronización mínima local con síntesis de ADN.</sub></p>'
        pro_desc = f'<p align="center"><sub><b>Continuity Legacy Pro</b>: Guardia fronterizo de grado industrial.</sub></p>'
        omega_desc = f'<p align="center"><sub><b>Continuity Legacy Omega</b>: RAG avanzado y análisis de impacto proactivo.</sub></p>'
        
        content = content.replace("LEGACYlite.png)](../continuity-lite)", f"LEGACYlite.png)](../continuity-lite)\n{lite_desc}")
        content = content.replace("LEGACYPRO.png)](../continuity)", f"LEGACYPRO.png)](../continuity)\n{pro_desc}")
        content = content.replace("LEGACYOMEGA.png)](../continuity-omega)", f"LEGACYOMEGA.png)](../continuity-omega)\n{omega_desc}")
        
        path.write_text(content, encoding="utf-8")
        print(f"[OK] README_{lang}.md polished and synced.")

if __name__ == "__main__":
    main()
