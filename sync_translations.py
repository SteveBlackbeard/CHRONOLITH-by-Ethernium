import re
from pathlib import Path

# Translation Dictionary
T = {
    'en': {
        'title': 'Continuity Legacy v1.3.1: Global Continuity Framework',
        'choose': '## 🏢 Choose Your Edition',
        'lite_desc': 'Minimalist local sync with DNA Synthesis for zero-loss handoffs.',
        'pro_desc': 'Industrial-grade border guard with security audits and global synchronization.',
        'omega_desc': 'Advanced RAG, cognitive mapping, and proactive impact analysis.'
    },
    'es': {
        'title': 'Continuity Legacy v1.3.1: Marco de Continuidad Global',
        'choose': '## 🏢 Elige tu Edición',
        'lite_desc': 'Sincronización local minimalista con Síntesis de ADN para traspasos sin pérdida.',
        'pro_desc': 'Guardia fronterizo de grado industrial con auditorías de seguridad y sincronización.',
        'omega_desc': 'RAG avanzado, mapas cognitivos y análisis de impacto proactivo.'
    },
    'fr': {
        'title': 'Continuity Legacy v1.3.1 : Cadre de Continuité Global',
        'choose': '## 🏢 Choisissez votre Édition',
        'lite_desc': "Synchronisation locale minimaliste con Synthèse d'ADN pour des transferts sans perte.",
        'pro_desc': 'Garde-frontière de niveau industriel con audits de sécurité et sincronización mondiale.',
        'omega_desc': "RAG avancé, cartographie cognitive et analyse d'impact proactive."
    },
    'de': {
        'title': 'Continuity Legacy v1.3.1: Globales Kontinuitäts-Framework',
        'choose': '## 🏢 Wählen Sie Ihre Edition',
        'lite_desc': 'Minimalistische lokale Synchronisation mit DNA-Synthese für verlustfreie Übergaben.',
        'pro_desc': 'Industrieller Grenzschutz mit Sicherheitsaudits und globaler Synchronisation.',
        'omega_desc': 'Erweitertes RAG, kognitives Mapping und proaktive Auswirkungsanalyse.'
    },
    'it': {
        'title': 'Continuity Legacy v1.3.1: Framework di Continuità Globale',
        'choose': '## 🏢 Scegli la tua Edizione',
        'lite_desc': 'Sincronizzazione locale minimalista con Sintesi del DNA per passaggi senza perdite.',
        'pro_desc': 'Guardia di confine di livello industriale con controlli di sicurezza e sincronizzazione globale.',
        'omega_desc': "RAG avanzato, mappatura cognitiva e analisi dell'impatto proattiva."
    },
    'pt': {
        'title': 'Continuity Legacy v1.3.1: Estrutura de Continuidade Global',
        'choose': '## 🏢 Escolha sua Edición',
        'lite_desc': 'Sincronização local minimalista con Síntese de DNA para transferências sem perdas.',
        'pro_desc': 'Guarda de fronteira de nível industrial con auditorias de segurança e sincronização global.',
        'omega_desc': 'RAG avanzado, mapeamento cognitivo e análise de impacto proativa.'
    },
    'ru': {
        'title': 'Continuity Legacy v1.3.1: Глобальный фреймворк непрерывности',
        'choose': '## 🏢 Выберите вашу редакцию',
        'lite_desc': 'Минималистичная локальная синхронизация с синтезом ДНК для передачи без потерь.',
        'pro_desc': 'Пограничный контроль промышленного уровня с аудитом безопасности и глобальной синхронизацией.',
        'omega_desc': 'Продвинутый RAG, когнитивное картирование и проактивный анализ воздействия.'
    },
    'ja': {
        'title': 'Continuity Legacy v1.3.1: グローバル継続性フレームワーク',
        'choose': '## 🏢 エディションを選択',
        'lite_desc': 'ロスゼロのハンドオフのためのDNA合成を備えたミニマリストのローカル同期。',
        'pro_desc': 'セキュリティ監査とグローバル同期を備えた産業用グレードの国境警備。',
        'omega_desc': '高度なRAG、認知マッピング、およびプロアクティブな影響分析。'
    },
    'zh': {
        'title': 'Continuity Legacy v1.3.1: 全球连续性框架',
        'choose': '## 🏢 选择您的版本',
        'lite_desc': '具有DNA合成功能的极简本地同步，实现无损交接。',
        'pro_desc': '具有安全审计和全球同步功能的工业级边界守卫。',
        'omega_desc': '高级RAG，认知映射和主动影响分析。'
    }
}

def get_base_header(master_file):
    content = Path(master_file).read_text(encoding='utf-8')
    # Extracts the header from start until the first horizontal rule or intro paragraph
    # We want to capture the #### Languages and the center image
    # For README, it goes until the line before "Continuity is now structured..."
    
    match = re.search(r'(#### Languages.*?</p>)', content, flags=re.DOTALL)
    return match.group(1) if match else ""

def build_banners(lang):
    t = T.get(lang, T['en'])
    return f"""{t['choose']}

[![LITE](https://raw.githubusercontent.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/main/assets/banners/LEGACYlite.png?raw=true)](https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/blob/main/continuity-lite/)

_{t['lite_desc']}</sub></p>_

[![PRO](https://raw.githubusercontent.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/main/assets/banners/LEGACYPRO.png?raw=true)](https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/blob/main/continuity-pro/)

_{t['pro_desc']}</sub></p>_

[![OMEGA](https://raw.githubusercontent.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/main/assets/banners/LEGACYOMEGA.png?raw=true)](https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/blob/main/continuity-omega/)

_{t['omega_desc']}</sub></p_
"""

def sync_file(filepath, lang, is_release=False):
    content = Path(filepath).read_text(encoding='utf-8')
    master_file = 'RELEASE_NOTES_MANIFEST.md' if is_release else 'README.md'
    header = get_base_header(master_file)
    
    # 1. Strip everything before the main intro paragraph in the translation
    lines = content.split('\n')
    idx_intro = 0
    intro_keywords = ['**Continuity**', 'Continuity is now structured', '> **', '> "', 'proud to announce', 'orgullecemos de anunciar']
    
    for i, line in enumerate(lines):
        if any(keyword in line for keyword in intro_keywords):
            idx_intro = i
            break
            
    # 2. Extract intro and rest
    full_text = "\n".join(lines[idx_intro:])
    
    # 3. Strip existing old headers/banners from the translation text to avoid duplication
    full_text = re.sub(r'#### Languages.*?</p>\n+', '', full_text, flags=re.DOTALL)
    full_text = re.sub(r'## 🏢 [^\n]+\n+\[\!\[LITE.*?\n+_.*?</sub></p_.*\n+', '', full_text, flags=re.DOTALL)
    full_text = re.sub(r'#### Editions.*?\n+', '', full_text)
    full_text = re.sub(r'^# Continuity Legacy v.*?\n+', '', full_text)
    
    # 4. Construct final file
    title = T.get(lang, T['en'])['title']
    banners = build_banners(lang)
    
    if is_release:
        # Release format starts with Languages, then :zap: header, then intro, then banners
        final = f"{header}\n\n## :zap: \"AI doesn't forget anymore.\"\n\n{full_text.strip()}\n\n---\n\n{banners}"
    else:
        # README format starts with H1 Title, then Languages Header, then Intro, then Banners, then rest
        parts = full_text.split('---', 1)
        intro = parts[0].strip()
        rest = "---" + parts[1] if len(parts) > 1 else ""
        final = f"# {title}\n\n{header}\n\n{intro}\n\n{banners}\n\n{rest}"
        
    # Final cleanup of triple/double newlines
    final = re.sub(r'\n{3,}', '\n\n', final)
    Path(filepath).write_text(final.strip() + "\n", encoding='utf-8')

# Execution
for f in Path('OTHER_LANGUAGES').glob('README_*.md'):
    lang = f.stem.split('_')[-1]
    sync_file(f, lang, is_release=False)
    
for f in Path('OTHER_LANGUAGES').glob('RELEASE_v1.3.1_*.md'):
    lang = f.stem.split('_')[-1]
    sync_file(f, lang, is_release=True)

print("SUCCESS: All translations matched to GitHub Master structural parity.")
