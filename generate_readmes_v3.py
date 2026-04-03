# -*- coding: utf-8 -*-
import re
from pathlib import Path

REPO_URL = "https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium"
BASE_URL = "https://github.com/SteveBlackbeard/CONTINUITY-LEGACY-by-Ethernium/blob/main/"

DEFS = {
    "es": {
        "lite": "Continuity Legacy Lite — Guardián de Cero Fricción: Sincronización mínima local con síntesis de ADN para traspasos sin pérdida de contexto.",
        "pro": "Continuity Legacy Pro — Motor Táctico: Guardia fronterizo de grado industrial con auditorías de seguridad y sincronización global.",
        "omega": "Continuity Legacy Omega — Oráculo Empresarial: RAG avanzado, mapas cognitivos y análisis de impacto proactivo."
    },
    "fr": {
        "lite": "Continuity Legacy Lite — Gardien Zéro-Friction : Synchronisation locale minimale avec synthèse ADN pour des transferts sans perte de contexte.",
        "pro": "Continuity Legacy Pro — Moteur Tactique : Garde-frontière de qualité industrielle avec audits de sécurité et synchronisation globale.",
        "omega": "Continuity Legacy Omega — Oracle Entreprise : RAG avancé, cartographie cognitive et analyse d'impact proactive."
    },
    "de": {
        "lite": "Continuity Legacy Lite — Null-Reibung Wächter: Minimale lokale Synchronisation mit DNA-Synthese für verlustfreien Kontexttransfer.",
        "pro": "Continuity Legacy Pro — Taktischer Motor: Industrieller Grenzwächter mit Sicherheitsaudits und globaler Synchronisation.",
        "omega": "Continuity Legacy Omega — Enterprise-Orakel: Fortgeschrittenes RAG, kognitive Kartierung und proaktive Wirkungsanalyse."
    },
    "it": {
        "lite": "Continuity Legacy Lite — Guardiano Zero-Frizione: Sincronizzazione locale minima con sintesi DNA per passaggi senza perdita di contesto.",
        "pro": "Continuity Legacy Pro — Motore Tattico: Guardia di frontiera industriale con audit di sicurezza e sincronizzazione globale.",
        "omega": "Continuity Legacy Omega — Oracolo Enterprise: RAG avanzato, mappatura cognitiva e analisi d'impatto proattiva."
    },
    "pt": {
        "lite": "Continuity Legacy Lite — Guardião Zero-Fricção: Sincronização local mínima com síntese de ADN para transferências sem perda de contexto.",
        "pro": "Continuity Legacy Pro — Motor Tático: Guarda de fronteira industrial com auditorias de segurança e sincronização global.",
        "omega": "Continuity Legacy Omega — Oráculo Enterprise: RAG avançado, mapeamento cognitivo e análise de impacto proativa."
    },
    "ru": {
        "lite": "Continuity Legacy Lite — Страж Нулевого Трения: Минимальная локальная синхронизация с синтезом ДНК для бесшовной передачи контекста.",
        "pro": "Continuity Legacy Pro — Тактический Двигатель: Промышленный пограничный контроль с аудитами безопасности и глобальной синхронизацией.",
        "omega": "Continuity Legacy Omega — Корпоративный Оракул: Продвинутый RAG, когнитивное картирование и проактивный анализ воздействия."
    },
    "ja": {
        "lite": "Continuity Legacy Lite — ゼロフリクション・ガーディアン：コンテキスト損失ゼロのハンドオフのためのDNA合成を備えた最小限のローカル同期。",
        "pro": "Continuity Legacy Pro — タクティカル・エンジン：セキュリティ監査とグローバル同期を備えた産業グレードのボーダーガード。",
        "omega": "Continuity Legacy Omega — エンタープライズ・オラクル：高度なRAG、認知的マッピング、およびプロアクティブな影響分析。"
    },
    "zh": {
        "lite": "Continuity Legacy Lite — 零摩擦守护者：具有 DNA 合成的极简本地同步，确保交接过程中上下文零流失。",
        "pro": "Continuity Legacy Pro — 战术引擎：具有安全审计和全球同步功能的工业级边境守卫。",
        "omega": "Continuity Legacy Omega — 企业级神谕：高级 RAG、认知地图和主动影响分析。"
    }
}

def generate_ribbons():
    editions = (
        "[![LITE](https://img.shields.io/badge/Continuity%20Legacy-LITE-black)]"
        f"({BASE_URL}continuity-lite/) "
        "[![PRO](https://img.shields.io/badge/Continuity%20Legacy-PRO-black)]"
        f"({BASE_URL}continuity/) "
        "[![OMEGA](https://img.shields.io/badge/Continuity%20Legacy-OMEGA-black)]"
        f"({BASE_URL}continuity-omega/)"
    )
    lang_codes = ["es", "en", "ja", "zh", "ru", "fr", "it", "de", "pt"]
    lang_badges = []
    for lc in lang_codes:
        link = f"{BASE_URL}README.md" if lc == "en" else f"{BASE_URL}OTHER_LANGUAGES/README_{lc}.md"
        lang_badges.append(f"[![{lc.upper()}](https://img.shields.io/badge/{lc.upper()}-white)]({link})")
    
    return f"#### Editions\n{editions}\n\n#### Languages\n{' '.join(lang_badges)}\n"

def main():
    ribbons = generate_ribbons()
    for lang, t in DEFS.items():
        filepath = Path(f"OTHER_LANGUAGES/README_{lang}.md")
        if not filepath.exists(): continue
        
        content = filepath.read_text(encoding="utf-8")
        
        # 1. Update Ribbons at top (after first H1)
        if "#### Editions" not in content:
            content = re.sub(r'(^# .*?\n)', r'\1\n' + ribbons + '\n', content)
        else:
            content = re.sub(r'#### Editions.*?(\n\n|$)', ribbons + "\n", content, flags=re.DOTALL)

        # 2. Update Choose Your Edition Section (detecting icon 🏢)
        lite_p = f'<p align="center"><sub><b>{t["lite"].split(" — ")[0]}</b>: {t["lite"].split(": ")[1]}</sub></p>'
        pro_p = f'<p align="center"><sub><b>{t["pro"].split(" — ")[0]}</b>: {t["pro"].split(": ")[1]}</sub></p>'
        omega_p = f'<p align="center"><sub><b>{t["omega"].split(" — ")[0]}</b>: {t["omega"].split(": ")[1]}</sub></p>'
        
        new_section = (
            '\n[![Continuity Legacy Lite](../assets/banners/LEGACYlite.png)](../continuity-lite)\n' + lite_p + '\n\n' +
            '[![Continuity Legacy Pro](../assets/banners/LEGACYPRO.png)](../continuity)\n' + pro_p + '\n\n' +
            '[![Continuity Legacy Omega](../assets/banners/LEGACYOMEGA.png)](../continuity-omega)\n' + omega_p + '\n'
        )
        
        content = re.sub(r'## 🏢 .*?\n.*?(?=### 🧠)', r'## 🏢 Choose Your Edition\n' + new_section + "\n", content, flags=re.DOTALL)
        
        filepath.write_text(content, encoding="utf-8")
        print(f"[OK] README_{lang}.md fully synchronized")

if __name__ == "__main__": main()
