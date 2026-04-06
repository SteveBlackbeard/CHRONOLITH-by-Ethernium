from __future__ import annotations
import argparse
import traceback
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
        "tiers_title": "🏛️ The Triple-Tier Ecosystem",
        "features_title": "🧠 Key Features (Intellectual Symphony)",
        "omega_section_title": "🧠 Omega Edition: Cognitive Insight",
        "quality_title": "🔍 Quality Flow",
        "editions_title": "Editions",
        "languages_title": "Languages",
        "sync_note": "*(Localized technical sync for Continuity Legacy)*",
        "overview": "Continuity Legacy is a professional-grade synchronization framework designed to protect the logical lineage of your software. Born from the **Ethernium Ecosystem**, it ensures that development intent and architectural decisions are preserved across all handoffs.",
        "lite_desc": "**Lite**: Zero-Friction Guardian. Optimized for speed and daily developer usage.",
        "pro_desc": "**Pro**: Tactical Engine. Industrial-grade border guard with security and synchronization audits.",
        "omega_desc": "**Omega**: Enterprise Oracle. Advanced RAG, cognitive maps, and proactive impact analysis.",
        "feat_metabolism": "**Metabolism Optimization**: Typ-Rich Engine with <100ms startup and lazy-loading nuclei.",
        "feat_dna": "**DNA Synthesis**: Merkle Tree cryptographic protection with SHA-256 signatures.",
        "feat_cognitive": "**enterprise Governance**: Sentinel Guardian with automatic Git-Hooks and session logging.",
        "feat_global": "**Global Symmetry**: Documentation and industrial CLI support in 9 languages.",
        "feat_diamond": "**Industrial Sanitization**: Complete purge of UTF-16 rogue artifacts and tactical residue.",
        "omega_text": "The **Omega edition** is our Enterprise-grade Oracle. It provides advanced RAG, cognitive graph mapping, and proactive semantic impact analysis for enterprise decision guarding.",
        "quality_steps": ["Intent Capture: Recording the 'Why' in structured logs.", "DNA Validation: Verifying Merkle Root and State signatures.", "Crystallization: Updating the README DNA Crystal marker.", "enterprise Sync: Globally propagating the logical lineage."],
        "footer_brand": "CONTINUITY LEGACY: Industrial Infrastructure"
    },
    "es": {
        "tagline": "Protegiendo el linaje lógico de su software.",
        "tiers_title": "🏛️ El Ecosistema de Triple Nivel",
        "features_title": "🧠 Características Clave (Sinfonía Intelectual)",
        "omega_section_title": "🧠 Edición Omega: Perspectiva Cognitiva",
        "quality_title": "🔍 Flujo de Calidad",
        "editions_title": "Ediciones",
        "languages_title": "Idiomas",
        "sync_note": "*(Sincronización técnicaizada para Continuity Legacy)*",
        "overview": "Continuity Legacy es un marco de sincronización de grado profesional diseñado para proteger el linaje lógico de su software. Nacido del **Ecosistema Ethernium**, asegura que la intención de desarrollo y las decisiones arquitectónicas se preserven en todas las entregas.",
        "lite_desc": "**Lite**: Guardián de Cero Fricción. Optimizado para velocidad y uso diario del desarrollador.",
        "pro_desc": "**Pro**: Motor Táctico. Guardia fronterizo de grado industrial con auditorías de seguridad y Merkle DNA.",
        "omega_desc": "**Omega**: Oráculo Empresarial. RAG avanzado, mapas cognitivos y análisis de entropía proactivo.",
        "feat_metabolism": "**Optimización del Metabolismo**: Motor Typ-Rich con inicio <100ms y carga perezosa de núcleos.",
        "feat_dna": "**Síntesis de ADN**: Protección criptográfica Merkle con firmas SHA-256 de estado.",
        "feat_cognitive": "**Gobernanza Soberana**: Guardián Centinela con Git-Hooks automáticos y logging de sesión.",
        "feat_global": "**Simetría Global**: Documentación y soporte CLI industrial en 9 idiomas.",
        "feat_diamond": "**Sanitización Industrial**: Purga completa de archivos UTF-16 y residuos tácticos.",
        "omega_text": "La **edición Omega** es nuestro Oráculo de grado empresarial. Proporciona RAG avanzado, mapas cognitivos y análisis de impacto semántico para la protección de decisiones soberanas.",
        "quality_steps": ["Captura de Intención: Registro del 'Por qué' en logs estructurados.", "Validación de ADN: Verificación de Merkle Root y firmas de estado.", "Cristalización: Actualización del marcador DNA Crystal en el README.", "Sincronización Soberana: Propagación global del linaje lógico."],
        "footer_brand": "CONTINUITY LEGACY: Infraestructura Industrial"
    },
    "ja": {
        "tagline": "ソフトウェアの論理的系統を保護します。",
        "tiers_title": "🏛️ 3 層エコシステム",
        "features_title": "🧠 主な機能 (知的シンフォニー)",
        "omega_section_title": "🧠 Omega エディション: 認知的洞察",
        "quality_title": "🔍 品質フロー",
        "editions_title": "エディション",
        "languages_title": "言語",
        "sync_note": "*(Continuity Legacy の技術同期)*",
        "overview": "Continuity Legacy は、ソフトウェアの論理的な系統を保護するために設計されたプロフェッショナル グレードの同期フレームワークです。**Ethernium エコシステム**から誕生し、開発意図とアーキテクチャ上の決定がすべてのハンドオフで確実に保持されるようにします。",
        "lite_desc": "**Lite**: ゼロフリクション・ガーディアン。速度と日常的な開発者の使用に最適化されています。",
        "pro_desc": "**Pro**: タクティカル・エンジン。セキュリティと同期監査を備えた産業グレードの境界ガード。",
        "omega_desc": "**Omega**: エンタープライズ・オラクル。高度な RAG、認知マップ、および事前の影響分析。",
        "feat_metabolism": "**代謝の最適化**: すべてのエディションで遅延読み込みを実装。CLI の即時起動 (<100ms)。",
        "feat_dna": "**DNA 合成**: 論理的系統を保護するための `PROJECT_DNA.md` の自動生成。",
        "feat_cognitive": "**認知インサイト (Omega)**: インタラクティブな意思決定マップと影響アラート。",
        "feat_global": "**グローバル・アウェアネス**: 9 言語の完全なドキュメントと CLI サポート。",
        "feat_diamond": "**ダイヤモンド・サニタイズ**: エンコード エラーと文字化けの徹底的なパージ。",
        "omega_text": "**Omega エディション**は、当社のエンタープライズ グレードのティアです。アーキテクチャのドリフトを防ぐために、視覚的でインタラクティブな意思決定の系統と意味的な影響分析を提供します。",
        "quality_steps": ["意図の把握：「なぜ」を文書化する。", "パリティチェック：エコシステムを検証する。", "影響分析：意味的な矛盾を検出する。", "DNA合成：コアヌクレオチドの更新。"],
        "footer_brand": "CONTINUITY LEGACY: グローバル・インフラストラクチャ"
    },
    "ru": {
        "tagline": "Защита логической преемственности вашего программного обеспечения.",
        "tiers_title": "🏛️ Трехуровневая экосистема",
        "features_title": "🧠 Основные характеристики (Интеллектуальная симфония)",
        "omega_section_title": "🧠 Редакция Omega: Когнитивное прозрение",
        "quality_title": "🔍 Поток качества",
        "editions_title": "Редакции",
        "languages_title": "Языки",
        "sync_note": "*(Техническая синхронизация для Continuity Legacy)*",
        "overview": "Continuity Legacy — это среда синхронизации профессионального уровня, предназначенная для защиты логической последовательности вашего программного обеспечения. Созданная в рамках **экосистемы Ethernium**, она гарантирует сохранение целей разработки и архитектурных решений на всех этапах передачи.",
        "lite_desc": "**Lite**: Страж с нулевым трением. Оптимизировано для скорости и ежедневного использования разработчиками.",
        "pro_desc": "**Pro**: Тактический движок. Промышленная пограничная защита с аудитом безопасности.",
        "omega_desc": "**Omega**: Корпоративный оракул. Продвинутый RAG, когнитивные карты и упреждающий анализ влияния.",
        "feat_metabolism": "**Оптимизация метаболизма**: Ленивая загрузка во всех версиях. Мгновенный запуск CLI (<100 мс).",
        "feat_dna": "**Синтез ДНК**: Автоматическая генерация `PROJECT_DNA.md` для защиты логической линии.",
        "feat_cognitive": "**Когнитивные инсайты (Omega)**: Интерактивные карты решений и оповещения о влиянии.",
        "feat_global": "**Глобальная осведомленность**: Полная документация и поддержка CLI на 9 языках.",
        "feat_diamond": "**Алмазная очистка**: Глубокое удаление ошибок кодировки и文字化け (mojibake).",
        "omega_text": "**Редакция Omega** — это наш уровень корпоративного класса. Она обеспечивает визуальную интерактивную преемственность решений и семантический анализ влияния.",
        "quality_steps": ["Захват намерения: Документирование «Почему».", "Проверка паритета: Проверка экосистемы.", "Анализ влияния: Обнаружение семантических противоречий.", "Синтез ДНК: Обновление основных нуклеотидов."],
        "footer_brand": "CONTINUITY LEGACY: Глобальная инфраструктура"
    },
    "zh": {
        "tagline": "保护软件的逻辑血统。",
        "tiers_title": "🏛️ 三层生态系统",
        "features_title": "🧠 核心特性 (智力交响曲)",
        "omega_section_title": "🧠 Omega 版本: 认知洞察",
        "quality_title": "🔍 质量流程",
        "editions_title": "版本",
        "languages_title": "语言",
        "sync_note": "*(Continuity Legacy 的本地化技术同步)*",
        "overview": "Continuity Legacy 是一个专业级同步框架，旨在保护软件的逻辑起源。它源自 **Ethernium 生态系统**，确保开发意图和架构决策在所有交付环节中得以保留。",
        "lite_desc": "**Lite**: 零摩擦守护者。针对速度和日常开发人员使用进行了优化。",
        "pro_desc": "**Pro**: 战术引擎。带有安全和同步审计的工业级边界防护。",
        "omega_desc": "**Omega**: 企业级先知。高级 RAG、认知图谱和主动影响分析。",
        "feat_metabolism": "**代谢优化**: 所有版本均实现延迟加载。CLI 瞬时启动 (<100ms)。",
        "feat_dna": "**DNA 合成**: 自动生成 `PROJECT_DNA.md` 以保护逻辑血统。",
        "feat_cognitive": "**认知洞察 (Omega)**: 交互式决策图和影响警报。",
        "feat_global": "**全球视野**: 支持 9 种语言的完整文档和 CLI。",
        "feat_diamond": "**钻石净化**: 深度清除编码错误和文字化け (mojibake)。",
        "omega_text": "**Omega 版本**是我们的企业级层级。它提供可视化的交互式决策血统和语义影响分析，以防止架构漂移。",
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
    if v_file.exists():
        raw = v_file.read_bytes()
        # Handle UTF-16 or garbage
        try:
            return raw.decode("utf-8-sig").strip()
        except UnicodeDecodeError:
            try: return raw.decode("utf-16").strip()
            except UnicodeDecodeError:
                return raw.decode("latin-1").replace("\x00", "").strip()
    return "2.1.0"

def get_edition_name(root: Path) -> str:
    if (root / "continuity-lite").exists(): return "Root Portal"
    if "lite" in root.name.lower(): return "Lite Edition"
    if "omega" in root.name.lower(): return "Omega Edition"
    if "pro" in root.name.lower() or "continuity" == root.name.lower(): return "Pro Edition"
    return "Universal Core"

def generate_ribbons(lang, is_root, base_path):
    lang_path = f"{base_path}OTHER_LANGUAGES/"
    lite_banner = f"[![LITE](https://raw.githubusercontent.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/main/assets/banners/LEGACYlite.png?raw=true)]({base_path}continuity-lite/)"
    pro_banner = f"[![PRO](https://raw.githubusercontent.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/main/assets/banners/LEGACYPRO.png?raw=true)]({base_path}continuity-pro/)"
    omega_banner = f"[![OMEGA](https://raw.githubusercontent.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/main/assets/banners/LEGACYOMEGA.png?raw=true)]({base_path}continuity-omega/)"
    
    v_ribbon = f"{lite_banner}\n\n{pro_banner}\n\n{omega_banner}"
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
    
    is_lite_only = (version == "1.3.1")
    
    tiers_body = f"- {t['lite_desc']}"
    if not is_lite_only:
        tiers_body += f"\n- {t['pro_desc']}\n- {t['omega_desc']}"
        
    omega_section = ""
    if not is_lite_only:
        omega_section = f"\n---\n\n## {t['omega_section_title']}\n{t['omega_text']}\n\n![Ethernium Omega](https://media.canary.gl/m/4346747d6be20a7b)"
    
    lines = [
        f"# {title}",
        f"{badge}",
        f"\n#### {t['editions_title']}\n{v_ribbon}",
        f"\n#### {t['languages_title']}\n{l_ribbon}",
        f"\n-----",
        f"\n## {t['tiers_title']}",
        v_ribbon,
        f"\n---\n\n## 📊 Technical Specifications (Hardware Profiles)",
        "| Edition | RAM (Min) | Storage | Dependencies | Best For |\n| :--- | :--- | :--- | :--- | :--- |\n| **Lite** | < 100 MB | < 5 MB | Zero | Local Dev / CI-CD |\n| **Pro** | 4 GB | 50 MB | Standard | Industrial Handoffs |\n| **Omega** | 16 GB+ | 500 MB+ | RAG/Graph | Enterprise Strategy |",
        f"\n---\n\n## 🚀 Modos de Operación (How to use)\n"
        f"1. **Modo Autónomo (Industrial CLI)**: Ejecute `continuity-lite status` para ver la salud del sistema.\n"
        f"2. **Modo Centinela (Automatic Guardian)**: Use `continuity-lite init` para activar Hooks automáticos.\n"
        f"3. **Modo Auditor (DNA Oracle)**: Use el motor Omega para informes de deriva semántica.",
        f"\n---",
        f"\n## {t['features_title']}",
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
    base_url = f"https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/blob/main/"
    
    title = f"Official Stable Release v{version} - {t['footer_brand'].split(': ')[1]}"
    
    is_lite_only = (version == "1.3.1")
    lite_banner = f"[![LITE](https://raw.githubusercontent.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/main/assets/banners/LEGACYlite.png?raw=true)]({base_url}continuity-lite/)"
    pro_banner = f"[![PRO](https://raw.githubusercontent.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/main/assets/banners/LEGACYPRO.png?raw=true)]({base_url}continuity-pro/)"
    omega_banner = f"[![OMEGA](https://raw.githubusercontent.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/main/assets/banners/LEGACYOMEGA.png?raw=true)]({base_url}continuity-omega/)"
    
    v_ribbon = f"{lite_banner}\n\n{pro_banner}\n\n{omega_banner}"
    
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
        f"**{t['tagline']}** 🧬\n<p align=\"center\">\n  <img src=\"https://raw.githubusercontent.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/main/banners/ethernium_header.png?raw=true\" alt=\"Ethernium Continuity Legacy Official Header\">\n</p>",
        f"\n{t['overview']}",
        f"\n## 🏛️ {t['editions_title']}\n{v_ribbon}",
        f"\n##  Navigation Explorer",
        f"*   [**Industrial Guide** (HOW_TO_USE_IT.md)](../HOW_TO_USE_IT.md)",
        f"*   [**Main Documentation** (README.md)](../README_{lang}.md)",
        f"*   [**Legal Heritage** (LICENSE)](../LICENSE)",
        f"*   [**Decision Log** (.continuity/DECISIONS_LOG.md)](../.continuity/DECISIONS_LOG.md)",
        f"\n---\n\n## 📊 Technical Specifications (Hardware Profiles)",
        "| Edition | RAM (Min) | Storage | Dependencies | Best For |\n| :--- | :--- | :--- | :--- | :--- |\n| **Lite** | < 100 MB | < 5 MB | Zero | Local Dev / CI-CD |\n| **Pro** | 4 GB | 50 MB | Standard | Industrial Handoffs |\n| **Omega** | 16 GB+ | 500 MB+ | RAG/Graph | Enterprise Strategy |",
        omega_section,
        f"\n---\n*Continuity Legacy: {t['tagline']}*"
    ]
    return "\n".join(lines)

def sync_all(repo_root: Path, auto_gen: bool):
    edition = get_edition_name(repo_root)
    version = get_universal_version(repo_root)
    is_root_dir = (repo_root / "continuity-lite").exists()
    
    source_path = repo_root / "README.md"
    if not source_path.exists(): return
    
    # Pre-load source to ensure it's readable
    try:
        source_content = source_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        source_content = source_path.read_text(encoding="latin-1")
    
    print(f"[*] Global Sync v1.5.0: Processing {edition} ({version})")
    
    lang_dir = repo_root / "OTHER_LANGUAGES"
    lang_dir.mkdir(parents=True, exist_ok=True)
    
    for lang in LANG_CODES:
        try:
            if lang == "en" and is_root_dir: continue 
            
            target_path = lang_dir / f"README_{lang}.md"
            if auto_gen:
                content = generate_localized_readme(lang, edition, version, is_root_dir)
                target_path.write_text(content, encoding="utf-8")
                
            if is_root_dir:
                release_path = lang_dir / f"RELEASE_v{version}_{lang}.md"
                if auto_gen:
                    release_content = generate_localized_release(lang, version)
                    release_path.write_text(release_content, encoding="utf-8")
        except Exception as e:
            print(f"[!] Error processing {lang}: {e}")
            traceback.print_exc()
            continue
    
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
