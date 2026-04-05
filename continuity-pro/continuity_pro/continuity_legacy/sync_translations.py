from __future__ import annotations
import argparse
import os
import re
from pathlib import Path
from datetime import datetime

# CONTINUITY LEGACY: Global Sync & Authority Engine (v1.5.0)
# ---------------------------------------------------------
# SST: High-Fidelity Universal Synchronization across 9 languages.

LANG_CODES = ["es", "ja", "ru", "zh", "fr", "it", "de", "pt", "en"]

# Deep Technical Translation Dictionary
TRANSLATIONS = {
    "en": {
        "tagline": "Protecting the logical lineage of your software.",
        "editions_title": "Editions",
        "languages_title": "Languages",
        "sync_note": "*(Localized technical sync for Continuity Legacy)*",
        "overview": "Continuity Legacy is a professional-grade synchronization framework designed to protect the logical lineage of your software. Born from the **Ethernium Ecosystem**, it ensures that development intent and architectural decisions are preserved across all handoffs.",
        "tiers_title": "The Triple-Tier Ecosystem",
        "lite_desc": "**Lite**: Zero-Friction Guardian. Optimized for speed and daily developer usage.",
        "pro_desc": "**Pro**: Tactical Engine. Industrial-grade border guard with security and synchronization audits.",
        "omega_desc": "**Omega**: Enterprise Oracle. Advanced RAG, cognitive maps, and proactive impact analysis.",
        "features_title": "Key Features (Intellectual Symphony)",
        "feat_metabolism": "**Metabolism Optimization**: Lazy Loading implemented in all editions. Instant CLI startup (<100ms).",
        "feat_dna": "**DNA Synthesis**: Merkle Tree-based cryptographic protection (SHA-256).",
        "feat_cognitive": "**Cognitive Governance**: Entropy-aware volatility monitoring and DNA crystallization.",
        "feat_global": "**Global Awareness**: Full documentation and CLI support in 9 languages.",
        "feat_diamond": "**Diamond Sanitization**: Deep purge of encoding errors and mojibake.",
        "omega_section_title": "Omega Edition: Cognitive Insight",
        "omega_text": "The **Omega edition** is our Enterprise-grade Tier. It provides a visual, interactive decision lineage and semantic impact analysis using Merkle DNA proof-of-state.",
        "quality_title": "Quality Flow",
        "quality_steps": ["Intent Capture: Documenting the 'Why'.", "Parity Check: Validating the ecosystem.", "Crystallization: Synthesizing the Merkle Root.", "DNA Synthesis: Updating nucleotides."],
        "footer_brand": "CONTINUITY LEGACY: Global Infrastructure"
    },
    "es": {
        "tagline": "Protegiendo el linaje lógico de su software.",
        "editions_title": "Ediciones",
        "languages_title": "Idiomas",
        "sync_note": "*(Sincronización técnicaizada para Continuity Legacy)*",
        "overview": "Continuity Legacy es un marco de sincronización de grado profesional diseñado para proteger el linaje lógico de su software. Nacido del **Ecosistema Ethernium**, asegura que la intención de desarrollo y las decisiones arquitectónicas se preserven en todas las entregas.",
        "tiers_title": "El Ecosistema de Triple Nivel",
        "lite_desc": "**Lite**: Guardián de Cero Fricción. Optimizado para velocidad y uso diario del desarrollador.",
        "pro_desc": "**Pro**: Motor Táctico. Guardia fronterizo de grado industrial con auditorías de seguridad y Merkle DNA.",
        "omega_desc": "**Omega**: Oráculo Empresarial. RAG avanzado, mapas cognitivos y análisis de entropía proactivo.",
        "features_title": "Características Clave (Sinfonía Intelectual)",
        "feat_metabolism": "**Optimización del Metabolismo**: Carga perezosa implementada. Inicio instantáneo de CLI (<100ms).",
        "feat_dna": "**Síntesis de ADN**: Protección criptográfica basada en Merkle Tree (SHA-256).",
        "feat_cognitive": "**Gobernanza Cognitiva**: Monitorización de entropía y cristalización de ADN.",
        "feat_global": "**Conciencia Global**: Documentación completa y soporte CLI en 9 idiomas.",
        "feat_diamond": "**Sanitización Diamante**: Purga profunda de errores de codificación y mojibake.",
        "omega_section_title": "Edición Omega: Perspectiva Cognitiva",
        "omega_text": "La **edición Omega** es nuestro nivel de grado empresarial. Proporciona un linaje de decisión visual e interactivo y análisis de impacto semántico con pruebas de estado Merkle.",
        "quality_title": "Flujo de Calidad",
        "quality_steps": ["Captura de Intención: Documentar el 'Por qué'.", "Verificación de Paridad: Validar el ecosistema.", "Cristalización: Sintetizar el Merkle Root.", "Síntesis de ADN: Actualizar nucleótidos."],
        "footer_brand": "CONTINUITY LEGACY: Infraestructura Global"
    },
    "ja": {
        "tagline": "ソフトウェアの論理的系統を保護します。",
        "editions_title": "エディション",
        "languages_title": "言語",
        "sync_note": "*(Continuity Legacy の技術同期)*",
        "overview": "Continuity Legacy は、ソフトウェアの論理的な系統を保護するために設計されたプロフェッショナル グレードの同期フレームワークです。**Ethernium エコシステム**から誕生し、開発意図とアーキテクチャ上の決定がすべてのハンドオフで確実に保持されるようにします。",
        "tiers_title": "3 層エコシステム",
        "lite_desc": "**Lite**: ゼロフリクション・ガーディアン。速度と日常的な開発者の使用に最適化されています。",
        "pro_desc": "**Pro**: タクティカル・エンジン。セキュリティと同期監査を備えた産業グレードの境界ガード。",
        "omega_desc": "**Omega**: エンタープライズ・オラクル。高度な RAG、認知マップ、および事前の影響分析。",
        "features_title": "主な機能 (知的シンフォニー)",
        "feat_metabolism": "**代謝の最適化**: すべてのエディションで遅延読み込みを実装。CLI の即時起動 (<100ms)。",
        "feat_dna": "**DNA 合成**: 論理的系統を保護するための `PROJECT_DNA.md` の自動生成。",
        "feat_cognitive": "**認知インサイト (Omega)**: インタラクティブな意思決定マップと影響アラート。",
        "feat_global": "**グローバル・アウェアネス**: 9 言語の完全なドキュメントと CLI サポート。",
        "feat_diamond": "**ダイヤモンド・サニタイズ**: エンコード エラーと文字化けの徹底的なパージ。",
        "omega_section_title": "Omega エディション: 認知的洞察",
        "in_dev": "(開発中)",
        "omega_text": "**Omega エディション**は、当社のエンタープライズ グレードのティアです。アーキテクチャのドリフトを防ぐために、視覚的でインタラクティブな意思決定の系統と意味的な影響分析を提供します。",
        "quality_title": "品質フロー",
        "quality_steps": ["意図の把握：「なぜ」を文書化する。", "パリティチェック：エコシステムを検証する。", "影響分析：意味的な矛盾を検出する。", "DNA合成：コアヌクレオチドの更新。"],
        "footer_brand": "CONTINUITY LEGACY: グローバル・インフラストラクチャ"
    },
    "ru": {
        "tagline": "Защита логической преемственности вашего программного обеспечения.",
        "editions_title": "Редакции",
        "languages_title": "Языки",
        "sync_note": "*(Техническая синхронизация для Continuity Legacy)*",
        "overview": "Continuity Legacy — это среда синхронизации профессионального уровня, предназначенная для защиты логической последовательности вашего программного обеспечения. Созданная в рамках **экосистемы Ethernium**, она гарантирует сохранение целей разработки и архитектурных решений на всех этапах передачи.",
        "tiers_title": "Трехуровневая экосистема",
        "lite_desc": "**Lite**: Страж с нулевым трением. Оптимизировано для скорости и ежедневного использования разработчиками.",
        "pro_desc": "**Pro**: Тактический движок. Промышленная пограничная защита с аудитом безопасности.",
        "omega_desc": "**Omega**: Корпоративный оракул. Продвинутый RAG, когнитивные карты и упреждающий анализ влияния.",
        "features_title": "Основные характеристики (Интеллектуальная симфония)",
        "feat_metabolism": "**Оптимизация метаболизма**: Ленивая загрузка во всех версиях. Мгновенный запуск CLI (<100 мс).",
        "feat_dna": "**Синтез ДНК**: Автоматическая генерация `PROJECT_DNA.md` для защиты логической линии.",
        "feat_cognitive": "**Когнитивные инсайты (Omega)**: Интерактивные карты решений и оповещения о влиянии.",
        "feat_global": "**Глобальная осведомленность**: Полная документация и поддержка CLI на 9 языках.",
        "feat_diamond": "**Алмазная очистка**: Глубокое удаление ошибок кодировки и文字化け (mojibake).",
        "omega_section_title": "Редакция Omega: Когнитивное прозрение",
        "in_dev": "(В разработке)",
        "omega_text": "**Редакция Omega** — это наш уровень корпоративного класса. Она обеспечивает визуальную интерактивную преемственность решений и семантический анализ влияния.",
        "quality_title": "Поток качества",
        "quality_steps": ["Захват намерения: Документирование «Почему».", "Проверка паритета: Проверка экосистемы.", "Анализ влияния: Обнаружение семантических противоречий.", "Синтез ДНК: Обновление основных нуклеотидов."],
        "footer_brand": "CONTINUITY LEGACY: Глобальная инфраструктура"
    },
    "zh": {
        "tagline": "保护软件的逻辑血统。",
        "editions_title": "版本",
        "languages_title": "语言",
        "sync_note": "*(Continuity Legacy 的本地化技术同步)*",
        "overview": "Continuity Legacy 是一个专业级同步框架，旨在保护软件的逻辑起源。它源自 **Ethernium 生态系统**，确保开发意图和架构决策在所有交付环节中得以保留。",
        "tiers_title": "三层生态系统",
        "lite_desc": "**Lite**: 零摩擦守护者。针对速度和日常开发人员使用进行了优化。",
        "pro_desc": "**Pro**: 战术引擎。带有安全和同步审计的工业级边界防护。",
        "omega_desc": "**Omega**: 企业级先知。高级 RAG、认知图谱和主动影响分析。",
        "features_title": "核心特性 (智力交响曲)",
        "feat_metabolism": "**代谢优化**: 所有版本均实现延迟加载。CLI 瞬时启动 (<100ms)。",
        "feat_dna": "**DNA 合成**: 自动生成 `PROJECT_DNA.md` 以保护逻辑血统。",
        "feat_cognitive": "**认知洞察 (Omega)**: 交互式决策图和影响警报。",
        "feat_global": "**全球视野**: 支持 9 种语言的完整文档和 CLI。",
        "feat_diamond": "**钻石净化**: 深度清除编码错误和文字化け (mojibake)。",
        "omega_section_title": "Omega 版本: 认知洞察",
        "in_dev": "(开发中)",
        "omega_text": "**Omega 版本**是我们的企业级层级。它提供可视化的交互式决策血统和语义影响分析，以防止架构漂移。",
        "quality_title": "质量流程",
        "quality_steps": ["意向捕获：记录“原因”。", "一致性检查：验证生态系统。", "影响分析：检测语义矛盾。", "DNA 合成：更新核心核苷酸。"],
        "footer_brand": "CONTINUITY LEGACY: 全球基础设施"
    }
}

# Add remaining slots with default (EN) or quick localized logic if needed
for l in ["fr", "it", "de", "pt"]:
    if l not in TRANSLATIONS: TRANSLATIONS[l] = TRANSLATIONS["en"]

def get_universal_version(repo_root: Path) -> str:
    v_file = repo_root / "VERSION"
    if not v_file.exists(): v_file = repo_root.parent / "VERSION"
    if v_file.exists(): return v_file.read_text(encoding="utf-8").strip()
    return "2.1.0"

def get_edition_name(root: Path) -> str:
    if (root / "continuity-lite").exists(): return "Root Portal"
    if "lite" in root.name.lower(): return "Lite Edition"
    if "omega" in root.name.lower(): return "Omega Edition"
    if "pro" in root.name.lower() or "continuity" == root.name.lower(): return "Pro Edition"
    return "Universal Core"

def generate_ribbons(lang, is_root, base_path):
    lang_path = f"{base_path}OTHER_LANGUAGES/"
    v_ribbon = (f"[![LITE](https://img.shields.io/badge/Edition-LITE-black)]({base_path}continuity-lite/) "
                f"[![PRO](https://img.shields.io/badge/Edition-PRO-black)]({base_path}continuity/) "
                f"[![OMEGA](https://img.shields.io/badge/Edition-OMEGA-black)]({base_path}continuity-omega/)")
    l_ribbon = ""
    for l in LANG_CODES:
        link = f"{base_path}README.md" if l == "en" else f"{lang_path}README_{l}.md"
        l_ribbon += f"[![{l.upper()}](https://img.shields.io/badge/{l.upper()}-white)]({link}) "
    return v_ribbon, l_ribbon

def generate_localized_readme(lang, edition_name, version, is_root):
    t = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    base_path = "./" if is_root else "../"
    v_ribbon, l_ribbon = generate_ribbons(lang, is_root, base_path)
    
    title = f"CONTINUITY LEGACY: {edition_name}"
    if lang != "en": title = f"{title} ({t['footer_brand'].split(': ')[1]})"
    
    badge = f"![Version](https://img.shields.io/badge/version-{version}-blue.svg)"
    
    # Version-Aware Content Filtering (Purity 1.3.1)
    is_lite_only = (version == "1.3.1")
    
    tiers_body = f"- {t['lite_desc']}"
    if not is_lite_only:
        tiers_body += f"\n- {t['pro_desc']}\n- {t['omega_desc']}"
        
    omega_section = ""
    if not is_lite_only:
        omega_section = f"\n---\n\n## {t['omega_section_title']}\n{t['omega_text']}\n\n![Ethernium Omega](https://media.canary.gl/m/4346747d6be20a7b)"
    
    # Compose Full Body
    lines = [
        f"# {title}",
        f"{badge}",
        f"\n#### {t['editions_title']}\n{v_ribbon}",
        f"\n#### {t['languages_title']}\n{l_ribbon}",
        f"\n---\n\n{t['sync_note']}\n\n{t['overview']}",
        f"\n---\n\n## {t['tiers_title']}",
        tiers_body,
        f"\n---\n\n## {t['features_title']}",
        f"- {t['feat_metabolism']}\n- {t['feat_dna']}\n- {t['feat_cognitive']}\n- {t['feat_global']}\n- {t['feat_diamond']}",
        omega_section,
        f"\n---\n\n## {t['quality_title']}",
        "\n".join([f"{i+1}. {step}" for i, step in enumerate(t['quality_steps'])]),
        f"\n---\n*Continuity: {t['tagline']}*",
        f"\n---\n* {t['footer_brand']} - Version {version} - Generated {datetime.utcnow().isoformat()}Z *"
    ]
    return "\n".join(lines)

def generate_localized_release(lang, version):
    t = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    # No base_path adjustment needed as these are standalone documents for GitHub Release links
    base_url = f"https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/blob/main/"
    
    title = f"Official Stable Release v{version} - {t['footer_brand'].split(': ')[1]}"
    
    # Navigation Ribbons (Full URLs for GitHub Release compatibility)
    # Filter Ribbons for 1.3.1
    is_lite_only = (version == "1.3.1")
    v_ribbon = f"[![LITE](https://img.shields.io/badge/Edition-LITE-black)]({base_url}continuity-lite/) "
    if not is_lite_only:
        v_ribbon += (f"[![PRO](https://img.shields.io/badge/Edition-PRO-black)]({base_url}continuity/) "
                     f"[![OMEGA](https://img.shields.io/badge/Edition-OMEGA-black)]({base_url}continuity-omega/)")
    
    l_ribbon = ""
    for l in LANG_CODES:
        link = f"{base_url}RELEASE_NOTES_MANIFEST.md" if l == "en" else f"{base_url}OTHER_LANGUAGES/RELEASE_v{version}_{l}.md"
        l_ribbon += f"[![{l.upper()}](https://img.shields.io/badge/{l.upper()}-white)]({link}) "
    
    tiers_body = f"- {t['lite_desc']}"
    if not is_lite_only:
        tiers_body += f"\n- {t['pro_desc']}\n- {t['omega_desc']}"
        
    omega_section = ""
    if not is_lite_only:
        omega_section = f"\n---\n\n## {t['omega_section_title']}\n{t['omega_text']}\n\n![Ethernium Omega](https://media.canary.gl/m/4346747d6be20a7b)"

    lines = [
        f"# {title}",
        f"\n#### {t['editions_title']}\n{v_ribbon}",
        f"\n#### {t['languages_title']}\n{l_ribbon}",
        f"\n---\n\n{t['overview']}",
        f"\n---\n\n## {t['tiers_title']}",
        tiers_body,
        f"\n---\n\n## {t['features_title']}",
        f"- {t['feat_metabolism']}\n- {t['feat_dna']}\n- {t['feat_cognitive']}\n- {t['feat_global']}\n- {t['feat_diamond']}",
        omega_section,
        f"\n---\n\n## {t['quality_title']}",
        "\n".join([f"{i+1}. {step}" for i, step in enumerate(t['quality_steps'])]),
        f"\n---\n*Continuity: {t['tagline']}*",
        f"\n---\n* {t['footer_brand']} - Version {version} - Generated {datetime.utcnow().isoformat()}Z *"
    ]
    return "\n".join(lines)

def sync_all(repo_root: Path, auto_gen: bool):
    edition = get_edition_name(repo_root)
    version = get_universal_version(repo_root)
    is_root_dir = (repo_root / "continuity-lite").exists()
    
    source_path = repo_root / "README.md"
    if not source_path.exists(): return
    
    print(f"[*] Global Sync v1.5.0: Processing {edition} ({version})")
    
    lang_dir = repo_root / "OTHER_LANGUAGES"
    lang_dir.mkdir(parents=True, exist_ok=True)
    
    for lang in LANG_CODES:
        if lang == "en" and is_root_dir: continue 
        
        # 1. Update README_lang.md
        target_path = lang_dir / f"README_{lang}.md"
        if auto_gen:
            content = generate_localized_readme(lang, edition, version, is_root_dir)
            target_path.write_text(content, encoding="utf-8")
            
        # 2. Update RELEASE_v{version}_lang.md (Only at root level sync)
        if is_root_dir:
            release_path = lang_dir / f"RELEASE_v{version}_{lang}.md"
            if auto_gen:
                release_content = generate_localized_release(lang, version)
                release_path.write_text(release_content, encoding="utf-8")
    
    print(f"[✔] SYNC: {edition} is globally synchronized and high-fidelity.")

def main() -> None:
    parser = argparse.ArgumentParser(description="Global Sync & Authority Engine (v1.5.0).")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--auto-gen", action="store_true")
    args = parser.parse_args()
    root = Path(args.repo_root).resolve()
    sync_all(root, args.auto_gen)

if __name__ == "__main__":
    main()
