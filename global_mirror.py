import re
from pathlib import Path

# Translation Dictionary for UI/Structural elements
T = {
    'en': {
        'title': 'Continuity Legacy v1.3.1: Global Continuity Framework',
        'choose': '## 🏢 Choose Your Edition',
        'lite_desc': 'Minimalist local sync with DNA Synthesis for zero-loss handoffs.',
        'pro_desc': 'Industrial-grade border guard with security audits and global synchronization.',
        'omega_desc': 'Advanced RAG, cognitive mapping, and proactive impact analysis.',
        'ecosystem': '## :bank: The Triple-Tier Ecosystem',
        'ecosystem_desc': 'Continuity is now structured into three specialized editions:',
        'install': '## 🚀 Quick Installation',
        'usage': '## ⚡ Minimal Usage (5-Line Start)',
        'flow': '## 🔍 The Quality Flow (The Border Guard)',
        'origins': '## 🌌 Origins: The Ethernium Heritage',
        'keywords': '## 🏷️ Keywords',
        'footer': '*Continuity: Protecting the logical lineage of your software.*'
    },
    'es': {
        'title': 'Continuity Legacy v1.3.1: Marco de Continuidad Global',
        'choose': '## 🏢 Elige tu Edición',
        'lite_desc': 'Sincronización local minimalista con Síntesis de ADN para traspasos sin pérdida.',
        'pro_desc': 'Guardia fronterizo de grado industrial con auditorías de seguridad y sincronización.',
        'omega_desc': 'RAG avanzado, mapas cognitivos y análisis de impacto proactivo.',
        'ecosystem': '## :bank: El Ecosistema de Tres Niveles',
        'ecosystem_desc': 'Continuity se estructura ahora en tres ediciones especializadas:',
        'install': '## 🚀 Instalación Rápida',
        'usage': '## ⚡ Uso Mínimo (Inicio en 5 Líneas)',
        'flow': '## 🔍 El Flujo de Calidad (El Guardia Fronterizo)',
        'origins': '## 🌌 Orígenes: La Herencia de Ethernium',
        'keywords': '## 🏷️ Palabras Clave',
        'footer': '*Continuity: Protegiendo el linaje lógico de su software.*'
    },
    'fr': {
        'title': 'Continuity Legacy v1.3.1 : Cadre de Continuité Global',
        'choose': '## 🏢 Choisissez votre Édition',
        'lite_desc': "Synchronisation locale minimaliste avec Synthèse d'ADN pour des transferts sans perte.",
        'pro_desc': 'Garde-frontière de niveau industriel avec audits de sécurité et synchronisation mondiale.',
        'omega_desc': "RAG avancé, cartographie cognitive et analyse d'impact proactive.",
        'ecosystem': '## :bank: L’Écosystème à Trois Niveaux',
        'ecosystem_desc': 'Continuity est désormais structuré en trois éditions spécialisées :',
        'install': '## 🚀 Installation Rapide',
        'usage': '## ⚡ Utilisation Minimale (Démarrage en 5 Lignes)',
        'flow': '## 🔍 Le Flux de Qualité (Le Garde-Frontière)',
        'origins': '## 🌌 Origines : L’Héritage d’Ethernium',
        'keywords': '## 🏷️ Mots-clés',
        'footer': '*Continuity : Protéger la lignée logique de votre logiciel.*'
    },
    'de': {
        'title': 'Continuity Legacy v1.3.1: Globales Kontinuitäts-Framework',
        'choose': '## 🏢 Wählen Sie Ihre Edition',
        'lite_desc': 'Minimalistische lokale Synchronisation mit DNA-Synthese für verlustfreie Übergaben.',
        'pro_desc': 'Industrieller Grenzschutz mit Sicherheitsaudits und globaler Synchronisation.',
        'omega_desc': 'Erweitertes RAG, kognitives Mapping und proaktive Auswirkungsanalyse.',
        'ecosystem': '## :bank: Das Dreistufige Ökosystem',
        'ecosystem_desc': 'Continuity ist jetzt in drei spezialisierte Editionen strukturiert:',
        'install': '## 🚀 Schnellinstallation',
        'usage': '## ⚡ Minimale Nutzung (5-Zeilen-Start)',
        'flow': '## 🔍 Der Qualitätsfluss (Der Grenzwächter)',
        'origins': '## 🌌 Ursprünge: Das Ethernium-Erbe',
        'keywords': '## 🏷️ Schlüsselwörter',
        'footer': '*Continuity: Die logische Abstammung Ihrer Software schützen.*'
    },
    'it': {
        'title': 'Continuity Legacy v1.3.1: Framework di Continuità Globale',
        'choose': '## 🏢 Scegli la tua Edizione',
        'lite_desc': 'Sincronizzazione locale minimalista con Sintesi del DNA per passaggi senza perdite.',
        'pro_desc': 'Guardia di confine di livello industriale con controlli di sicurezza e sincronizzazione globale.',
        'omega_desc': "RAG avanzato, mappatura cognitiva e analisi dell'impatto proattiva.",
        'ecosystem': '## :bank: L’Ecosistema a Tre Livelli',
        'ecosystem_desc': 'Continuity è ora strutturato in tre edizioni specializzate:',
        'install': '## 🚀 Installazione Rapida',
        'usage': '## ⚡ Utilizzo Minimo (Inizio in 5 Linee)',
        'flow': '## 🔍 Il Flusso di Qualità (La Guardia di Confine)',
        'origins': '## 🌌 Origini: L’Eredità di Ethernium',
        'keywords': '## 🏷️ Parole Chiave',
        'footer': '*Continuity: Proteggere la discendenza logica del software.*'
    },
    'pt': {
        'title': 'Continuity Legacy v1.3.1: Estrutura de Continuidade Global',
        'choose': '## 🏢 Escolha sua Edição',
        'lite_desc': 'Sincronização local minimalista com Síntese de DNA para transferências sem perdas.',
        'pro_desc': 'Guarda de fronteira de nível industrial com auditorias de segurança e sincronização global.',
        'omega_desc': 'RAG avanzado, mapeamento cognitivo e análise de impacto proativa.',
        'ecosystem': '## :bank: O Ecossistema de Três Níveis',
        'ecosystem_desc': 'Continuity agora está estruturado em três edições especializadas:',
        'install': '## 🚀 Instalação Rápida',
        'usage': '## ⚡ Uso Mínimo (Início em 5 Linhas)',
        'flow': '## 🔍 O Fluxo de Qualidade (O Guarda de Fronteira)',
        'origins': '## 🌌 Origens: A Herança de Ethernium',
        'keywords': '## 🏷️ Palavras-chave',
        'footer': '*Continuity: Protegendo a linhagem lógica do seu software.*'
    },
    'ru': {
        'title': 'Continuity Legacy v1.3.1: Глобальный фреймворк непрерывности',
        'choose': '## 🏢 Выберите вашу редакцию',
        'lite_desc': 'Минималистичная локальная синхронизация с синтезом ДНК для передачи без потерь.',
        'pro_desc': 'Пограничный контроль промышленного уровня с аудитом безопасности и глобальной синхронизацией.',
        'omega_desc': 'Продвинутый RAG, когнитивное картирование и проактивный анализ воздействия.',
        'ecosystem': '## :bank: Трехуровневая экосистема',
        'ecosystem_desc': 'Continuity теперь структурирована в трех специализированных редакциях:',
        'install': '## 🚀 Быстрая установка',
        'usage': '## ⚡ Минимальное использование (запуск в 5 строк)',
        'flow': '## 🔍 Поток качества (Пограничный контроль)',
        'origins': '## 🌌 Происхождение: Наследие Ethernium',
        'keywords': '## 🏷️ Ключевые слова',
        'footer': '*Continuity: Защита логической преемственности вашего программного обеспечения.*'
    },
    'ja': {
        'title': 'Continuity Legacy v1.3.1: グローバル継続性フレームワーク',
        'choose': '## 🏢 エディションを選択',
        'lite_desc': 'ロスゼロのハンドオフのためのDNA合成を備えたミニマリストのローカル同期。',
        'pro_desc': 'セキュリティ監査とグローバル同期を備えた産業用グレードの国境警備。',
        'omega_desc': '高度なRAG、認知マッピング、およびプロアクティブな影響分析。',
        'ecosystem': '## :bank: 3層エコシステム',
        'ecosystem_desc': 'Continuityは現在、3つの専門的なエディションに分かれています。',
        'install': '## 🚀 クイックインストール',
        'usage': '## ⚡ 最小限の使用（5行スタート）',
        'flow': '## 🔍 品質フロー（ボーダーガード）',
        'origins': '## 🌌 起源：Etherniumの遺産',
        'keywords': '## 🏷️ キーワード',
        'footer': '*Continuity: ソフトウェアの論理的な系譜を保護します。*'
    },
    'zh': {
        'title': 'Continuity Legacy v1.3.1: 全球连续性框架',
        'choose': '## 🏢 选择您的版本',
        'lite_desc': '具有DNA合成功能的极简本地同步，实现无损交接。',
        'pro_desc': '具有安全审计和全球同步功能的工业级边界守卫。',
        'omega_desc': '高级RAG，认知映射和主动影响分析。',
        'ecosystem': '## :bank: 三层生态系统',
        'ecosystem_desc': 'Continuity 现在分为三个专业版本：',
        'install': '## 🚀 快速安装',
        'usage': '## ⚡ 最小化使用（5行启动）',
        'flow': '## 🔍 质量流（边界守卫）',
        'origins': '## 🌌 起源：Ethernium的传承',
        'keywords': '## 🏷️ 关键词',
        'footer': '*Continuity：保护软件的逻辑血统。*'
    }
}

def get_shared_header():
    # Use github_readme_de.md to extract the fixed language badges and main image block
    content = Path('github_readme_de.md').read_text(encoding='utf-8')
    match = re.search(r'(#### Languages.*?</p>)', content, flags=re.DOTALL)
    return match.group(1) if match else ""

def generate_banners(lang):
    t = T.get(lang, T['en'])
    header = t['choose']
    return f"""{header}

[![Continuity Legacy Lite](https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/blob/main/assets/banners/LEGACYlite.png?raw=true)](https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/tree/main/continuity-lite)
<p align="center"><sub><b>Continuity Legacy Lite — {'Reibungsloser Wächter' if lang == 'de' else t['lite_desc'].split(' — ')[0]}</b>: {t['lite_desc'].split(': ')[-1]}</sub></p>

[![Continuity Legacy Pro](https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/blob/main/assets/banners/LEGACYPRO.png?raw=true)](https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/tree/main/continuity-pro)
<p align="center"><sub><b>Continuity Legacy Pro — {'Taktische Engine' if lang == 'de' else t['pro_desc'].split(' — ')[0]}</b>: {t['pro_desc'].split(': ')[-1]}</sub></p>

[![Continuity Legacy Omega](https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/blob/main/assets/banners/LEGACYOMEGA.png?raw=true)](https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/tree/main/continuity-omega)
<p align="center"><sub><b>Continuity Legacy Omega — {'Enterprise-Orakel' if lang == 'de' else t['omega_desc'].split(' — ')[0]}</b>: {t['omega_desc'].split(': ')[-1]}</sub></p>"""

def update_file(path, lang, is_release=False):
    t = T.get(lang, T['en'])
    header = get_shared_header()
    banners = generate_banners(lang)
    
    # Read existing content to preserve unique translations
    orig = Path(path).read_text(encoding='utf-8')
    
    # Extract unique parts (paragraphs after intro)
    # This is tricky because the files are very messy.
    # I will look for standard headings to capture blocks.
    
    def get_block(heading_key):
        # Look for the section and capture until next section or end
        # We need to handle variations in translations of headings
        regex = rf"(?:## |### )[^\n]*{t[heading_key].split(' ')[-1]}[^\n]*\n+(.*?)(?=\n+(?:## |### |---|\Z))"
        match = re.search(regex, orig, flags=re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""

    install_block = get_block('install')
    usage_block = get_block('usage')
    origins_block = get_block('origins')
    
    # Extract intro paragraph
    # It's usually the first paragraph that isn't a badge or header
    intro_match = re.search(r'(?:\*\*Continuity\*\*[^\n]+|Continuity ist ein[^\n]+|Continuity is a[^\n]+|Continuity es un[^\n]+)(.*?)(?=\n\n|\n---|\n#)', orig, flags=re.DOTALL)
    intro_p = intro_match.group(0).strip() if intro_match else ""
    
    if is_release:
        # Use German Release structural model
        # # Title -> Header -> (Empty) -> Choose Edition -> Banners -> Ecosystem -> System Flow -> Features -> Tech Specs -> Architecture -> Quality Flow -> Omega -> Footer
        # Since I don't have all sections correctly translated in T for every language, I will use English for non-translated headers if missing.
        
        # Actually, let's just make everything follow the README DE structure but adjust if it's release
        pass

    # RECONSTRUCTING EXACTLY LIKE README_DE
    final_text = f"# {t['title']}\n\n"
    final_text += f"{header}\n\n"
    final_text += f"{intro_p}\n\n"
    final_text += "---\n\n"
    final_text += f"{banners}\n\n"
    final_text += "---\n\n"
    final_text += f"{t['install']}\n\n```bash\n{install_block.split('```bash')[-1].split('```')[0].strip() if '```bash' in install_block else ''}\n```\n\n"
    final_text += "---\n\n"
    final_text += f"{t['usage']}\n\n```python\n{usage_block.split('```python')[-1].split('```')[0].strip() if '```python' in usage_block else ''}\n```\n\n"
    final_text += "---\n\n"
    final_text += f"{t['flow']}\n\n"
    final_text += "```mermaid\ngraph TD\n    A[Dev Intent] --> B{Parity Check}\n    B -- Fail --> C[Self-Healing / Fix]\n    B -- Pass --> D{Impact Analysis}\n    D -- Alert --> E[Reconcile / Override]\n    D -- Safe --> F[DNA Synthesis]\n    E --> F\n    F --> G[Final Sync & Push]\n```\n\n"
    final_text += "---\n\n"
    final_text += f"### 🧠 {t['omega_desc'].split(' — ')[0]} *(In development)*\n"
    final_text += "The **Omega edition** is our Enterprise-grade Tier. It provides a visual, interactive decision lineage and semantic impact analysis to prevent architectural drift.\n\n"
    final_text += "*OMEGA DASHBOARD VISUALIZATION (In Development)*\n\n"
    final_text += "---\n\n"
    final_text += f"{t['origins']}\n\n{origins_block}\n\n"
    final_text += "---\n\n"
    final_text += f"{t['keywords']}\n"
    final_text += "`context-management`, `ai-memory`, `rag-framework`, `project-continuity`, `decision-logging`, `software-governance`\n\n"
    final_text += "---\n"
    final_text += f"{t['footer']}\n"
    
    # Save
    Path(path).write_text(final_text, encoding='utf-8')

# Run mirror for ALL languages
langs = ['en', 'es', 'fr', 'it', 'ja', 'pt', 'ru', 'zh']
for l in langs:
    readme_path = Path(f'OTHER_LANGUAGES/README_{l}.md')
    if readme_path.exists():
        print(f"Mirroring README_{l}")
        update_file(readme_path, l)
    
    release_path = Path(f'OTHER_LANGUAGES/RELEASE_v1.3.1_{l}.md')
    if release_path.exists():
        print(f"Mirroring RELEASE_{l}")
        update_file(release_path, l, is_release=True)

print("GLOBAL MIRROR COMPLETED.")
