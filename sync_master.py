# -*- coding: utf-8 -*-
import os
import re
from pathlib import Path

# Metadata Master
DEFS = {
    "es": {"title": "Marco de Continuidad Global", "impact": "“La IA ya no olvida.”"},
    "fr": {"title": "Cadre de Continuité Globale", "impact": "“L'IA n'oublie plus.”"},
    "de": {"title": "Globaler Kontinuitätsrahmen", "impact": "“Die KI vergisst nicht mehr.”"},
    "it": {"title": "Quadro di Continuità Globale", "impact": "“L'IA non dimentica più.”"},
    "pt": {"title": "Estrutura de Continuidade Global", "impact": "“A IA não esquece mais.”"},
    "ru": {"title": "Глобальная Система Преемственности", "impact": "“ИИ больше не забывает.”"},
    "ja": {"title": "グローバル・コンティニュイティ・フレームワーク", "impact": "“AIはもう忘れません。”"},
    "zh": {"title": "全球连续性框架", "impact": "“AI 不再遗忘。”"}
}

def sync_readmes():
    master = Path("README.md").read_text(encoding="utf-8")
    # Identify the sections to propagate
    # Vision, Problem/Solution, Infrastructure, Positioning
    vision_sec = re.search(r'## 🧠 The Problem vs. The Solution.*?(?=## 🏢)', master, re.DOTALL).group(0)
    infra_sec = re.search(r'## 🧩 Core Infrastructure.*?(\n\n---|\n#)', master, re.DOTALL).group(0)
    pos_sec = re.search(r'## 🧬 Positioning.*?(\n\n---|\n#)', master, re.DOTALL).group(0)
    
    for lang in DEFS:
        path = Path(f"OTHER_LANGUAGES/README_{lang}.md")
        if not path.exists(): continue
        content = path.read_text(encoding="utf-8")
        
        # We need to adapt the sections or just replace with translated markers?
        # For now, we ensure structure parity.
        content = re.sub(r'## 🏢 .*?\n.*?(?=## 🚀)', re.search(r'## 🏢 .*?\n.*?(?=## 🚀)', master, re.DOTALL).group(0).replace("./assets", "../assets").replace("./continuity", "../continuity"), content, flags=re.DOTALL)
        
        path.write_text(content, encoding="utf-8")
        print(f"[OK] README_{lang}.md sync complete.")

def sync_releases():
    master_rel = Path("RELEASE_NOTES_MANIFEST.md").read_text(encoding="utf-8")
    # Extract structural blocks
    arch_tree = re.search(r'## 🏗️ Project Architecture Overview.*?(\n\n---|\n#)', master_rel, re.DOTALL).group(0)
    system_flow = re.search(r'## 🔁 System Flow.*?(\n\n---|\n#)', master_rel, re.DOTALL).group(0)
    
    for lang in DEFS:
        path = Path(f"OTHER_LANGUAGES/RELEASE_v1.3.1_{lang}.md")
        if not path.exists(): continue
        content = path.read_text(encoding="utf-8")
        
        # Inject Architecture and Flow
        if "## 🏗️" not in content:
            content = content.replace("## 🔍 Quality Flow", arch_tree + "\n\n## 🔍 Quality Flow")
        if "## 🔁" not in content:
            content = content.replace("## ✨ Key Features", system_flow + "\n\n## ✨ Key Features")
            
        path.write_text(content, encoding="utf-8")
        print(f"[OK] RELEASE_{lang}.md sync complete.")

if __name__ == "__main__":
    sync_readmes()
    sync_releases()
