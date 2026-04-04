import re
from pathlib import Path

# Absolute banner URLs for the release
LITE_BANNER = "https://raw.githubusercontent.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/main/assets/banners/LEGACYlite.png?raw=true"
PRO_BANNER = "https://raw.githubusercontent.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/main/assets/banners/LEGACYPRO.png?raw=true"
OMEGA_BANNER = "https://raw.githubusercontent.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/main/assets/banners/LEGACYOMEGA.png?raw=true"

# Dictionary of translations
T = {
    'en': {
        'choose': '## 🏢 Choose Your Edition',
        'lite_title': 'Continuity Legacy Lite — Zero-Friction Guardian',
        'lite_desc': 'Minimalist local sync with DNA Synthesis for zero-loss handoffs.',
        'pro_title': 'Continuity Legacy Pro — Tactical Engine',
        'pro_desc': 'Industrial-grade border guard with security audits and global synchronization.',
        'omega_title': 'Continuity Legacy Omega — Enterprise Oracle',
        'omega_desc': 'Advanced RAG, cognitive mapping, and proactive impact analysis.'
    },
    'es': {
        'choose': '## 🏢 Elige tu Edición',
        'lite_title': 'Continuity Legacy Lite — Guardián de Cero Fricción',
        'lite_desc': 'Sincronización local minimalista con Síntesis de ADN para traspasos sin pérdida.',
        'pro_title': 'Continuity Legacy Pro — Motor Táctico',
        'pro_desc': 'Guardia fronterizo de grado industrial con auditorías de seguridad y sincronización global.',
        'omega_title': 'Continuity Legacy Omega — Oráculo Empresarial',
        'omega_desc': 'RAG avanzado, mapas cognitivos y análisis de impacto proactivo.'
    },
    'fr': {
        'choose': '## 🏢 Choisissez votre Édition',
        'lite_title': 'Continuity Legacy Lite — Gardien Zéro Friction',
        'lite_desc': "Synchronisation locale minimaliste avec Synthèse d'ADN pour des transferts sans perte.",
        'pro_title': 'Continuity Legacy Pro — Moteur Tactique',
        'pro_desc': 'Garde-frontière de niveau industriel avec audits de sécurité et synchronisation mondiale.',
        'omega_title': "Continuity Legacy Omega — Oracle d'Entreprise",
        'omega_desc': "RAG avancé, cartographie cognitive et analyse d'impact proactive."
    },
    'de': {
        'choose': '## 🏢 Wählen Sie Ihre Edition',
        'lite_title': 'Continuity Legacy Lite — Reibungsloser Wächter',
        'lite_desc': 'Minimalistische lokale Synchronisation mit DNA-Synthese für verlustfreie Übergaben.',
        'pro_title': 'Continuity Legacy Pro — Taktische Engine',
        'pro_desc': 'Industrieller Grenzschutz mit Sicherheitsaudits und globaler Synchronisation.',
        'omega_title': 'Continuity Legacy Omega — Enterprise-Orakel',
        'omega_desc': 'Erweitertes RAG, kognitives Mapping und proaktive Auswirkungsanalyse.'
    },
    'it': {
        'choose': '## 🏢 Scegli la tua Edizione',
        'lite_title': 'Continuity Legacy Lite — Guardiano a Zero Attrito',
        'lite_desc': 'Sincronizzazione locale minimalista con Sintesi del DNA per passaggi senza perdite.',
        'pro_title': 'Continuity Legacy Pro — Motore Tattico',
        'pro_desc': 'Guardia di confine di livello industriale con controlli di sicurezza e sincronizzazione globale.',
        'omega_title': 'Continuity Legacy Omega — Oracolo Aziendale',
        'omega_desc': "RAG avanzato, mappatura cognitiva e analisi dell'impatto proattiva."
    },
    'pt': {
        'choose': '## 🏢 Escolha sua Edição',
        'lite_title': 'Continuity Legacy Lite — Guardião de Atrito Zero',
        'lite_desc': 'Sincronização local minimalista com Síntese de DNA para transferências sem perdas.',
        'pro_title': 'Continuity Legacy Pro — Motor Tático',
        'pro_desc': 'Guarda de fronteira de nível industrial com auditorias de segurança e sincronização global.',
        'omega_title': 'Continuity Legacy Omega — Oráculo Corporativo',
        'omega_desc': 'RAG avançado, mapeamento cognitivo e análise de impacto proativa.'
    },
    'ru': {
        'choose': '## 🏢 Выберите вашу редакцию',
        'lite_title': 'Continuity Legacy Lite — Хранитель нулевого трения',
        'lite_desc': 'Минималистичная локальная синхронизация с синтезом ДНК для передачи без потерь.',
        'pro_title': 'Continuity Legacy Pro — Тактический двигатель',
        'pro_desc': 'Пограничный контроль промышленного уровня с аудитом безопасности и глобальной синхронизацией.',
        'omega_title': 'Continuity Legacy Omega — Корпоративный оракул',
        'omega_desc': 'Продвинутый RAG, когнитивное картирование и проактивный анализ воздействия.'
    },
    'ja': {
        'choose': '## 🏢 エディションを選択',
        'lite_title': 'Continuity Legacy Lite — ゼロフリクション・ガーディアン',
        'lite_desc': 'ロスゼロのハンドオフのためのDNA合成を備えたミニマリストのローカル同期。',
        'pro_title': 'Continuity Legacy Pro — 戦術エンジン',
        'pro_desc': 'セキュリティ監査とグローバル同期を備えた産業用グレードの国境警備。',
        'omega_title': 'Continuity Legacy Omega — エンタープライズ・オラクル',
        'omega_desc': '高度なRAG、認知マッピング、およびプロアクティブな影響分析。'
    },
    'zh': {
        'choose': '## 🏢 选择您的版本',
        'lite_title': 'Continuity Legacy Lite — 零摩擦守卫',
        'lite_desc': '具有DNA合成功能的极简本地同步，实现无损交接。',
        'pro_title': 'Continuity Legacy Pro — 战术引擎',
        'pro_desc': '具有安全审计和全球同步功能的工业级边界守卫。',
        'omega_title': 'Continuity Legacy Omega — 企业甲骨文',
        'omega_desc': '高级RAG，认知映射和主动影响分析。'
    }
}

def generate_edition_block(lang):
    t = T.get(lang, T['en'])
    # Se usa la URL absoluta para asegurar que NO SE ROMPAN LOS BANNERS EN LAS VERSIONES como pidió el usuario.
    return f"""
{t['choose']}

[![Continuity Legacy Lite]({LITE_BANNER})](./continuity-lite)
<p align="center"><sub><b>{t['lite_title']}</b>: 

{t['lite_desc']}</sub></p>

[![Continuity Legacy Pro]({PRO_BANNER})](./continuity-pro)
<p align="center"><sub><b>{t['pro_title']}</b>: 

{t['pro_desc']}</sub></p>

[![Continuity Legacy Omega]({OMEGA_BANNER})](./continuity-omega)
<p align="center"><sub><b>{t['omega_title']}</b>: 

{t['omega_desc']}</sub></p>
"""

def update_release_file(filepath, lang):
    content = Path(filepath).read_text(encoding='utf-8')
    
    # Remover el bloque viejo (ya sea los banners solos o los bullet points)
    # Expresión regular para matchear desde Continuity is now structured / Continuity está... hasta antes del siguiente ---
    content = re.sub(r'Continuity [^\n]+ estructur[^\n]+:\n(?:- \*\*\[.*?)\n\n---', '---', content, flags=re.DOTALL)
    content = re.sub(r'Continuity [^\n]+ structured[^\n]+:\n+\[\!\[LITE.*?\n\n---', '---', content, flags=re.DOTALL)
    
    # El usuario incluye "Continuity is now structured..." en su edición directamente antes del bloque, lo mantendremos.
    # Ubicaremos justo después de la línea ## :zap: "AI doesn't forget anymore." y su párrafo
    
    # We will search for the first --- after the :zap: header, and replace the structural block leading up to it.
    # A robust way is to just replace the whole section between the intro paragraph and the System Flow block.
    
    # Reemplazamos la vieja versión horizontal por los banners completos 
    block = generate_edition_block(lang)
    
    # Buscar el texto "Continuity is now structured..." o las descripciones de las ediciones y borrar todo
    content = re.sub(r'\[\!\[LITE.*?continuity-omega/\)\n*', '', content, flags=re.DOTALL)
    content = re.sub(r'- \*\*\[Continuity Legacy Lite.*?impacto proactivo\.\n*', '', content, flags=re.DOTALL)
    content = re.sub(r'- \*\*\[Continuity Legacy Lite.*?proactive impact analysis\.\n*', '', content, flags=re.DOTALL)
    content = re.sub(r'Continuity is now structured.*?:', '', content, flags=re.DOTALL)
    content = re.sub(r'Continuity está ahora estructurado.*?:', '', content, flags=re.DOTALL)
    content = re.sub(r'## 🏢 Choose.*?impact analysis\.</sub></p(?:>|)', '', content, flags=re.DOTALL)

    # Inyectar el nuevo bloque de edición justo antes del primer --- (System flow)
    # Find position of `---` followed by `## :repeat:`
    pos = content.find('\n---\n\n## :repeat:')
    if pos == -1:
         pos = content.find('\n---\n## :repeat:')
    
    if pos != -1:
        content = content[:pos] + "\n" + block + content[pos:]

    # Fix minor glitches as requested
    content = content.replace('- - ', '- ')
    content = content.replace('2. 2. ', '2. ')
    content = content.replace('3. 3. ', '3. ')
    content = content.replace('4. 4. ', '4. ')

    Path(filepath).write_text(content, encoding='utf-8')


# Actualizamos el manifest principal con EN
update_release_file('RELEASE_NOTES_MANIFEST.md', 'en')

# Y las traducciones
for filepath in Path('OTHER_LANGUAGES').glob('RELEASE_v1.3.1_*.md'):
    lang = filepath.stem.split('_')[-1]
    update_release_file(filepath, lang)

print("Todas las versiones han adoptado la nueva estructura de banners preservando el idioma nativo.")
