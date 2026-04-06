# Continuity Legacy: Persistent Governance Layer 



`CONTINUITY LEGACY` — это независимый стартовый набор для создания проектов с устойчивой непрерывностью, канонической памятью и повторяемой передачей дел (handoff) между людьми и ИИ-операторами.



Этот инструментарий ставит непрерывность на первое место: он предоставляет многоразовую дисциплину для сохранения контекста, проверки соответствия документов и управляемой передачи дел без зависимости от каких-либо внешних фреймворков.



## Что сюда входит

- минимальная каноническая область памяти

- снимок загрузки непрерывности (bootstrap snapshot)

- проверки соответствия документов (parity checks)

- проверки членства в системе

- опциональный внешний уровень разработки (например, `PROJECTDEV/`)

- команда строгого завершения цикла непрерывности

- загрузчик (bootstrapper) для персонализации шаблона под новый проект



## Быстрый старт



### 1. Профессиональный способ (CLI) — РЕКОМЕНДУЕТСЯ

Установите глобальный CLI, чтобы инициализировать проекты одним шагом:



```powershell

pip install continuity-legacy

continuity-legacy init "My Project"

```



### 2. Ручное управление (Копирование/Вставка)

1. Скопируйте эту папку в корень вашего нового проекта.

2. Запустите загрузчик:



```powershell

python tools/continuity_legacy/bootstrap_project.py --repo-root . --project-name "My Project" --project-slug my_project

```



3. Если вам нужен внешний уровень непрерывности:



```powershell

python tools/continuity_legacy/bootstrap_project.py --repo-root . --project-name "My Project" --project-slug my_project --enable-external-docs

```



## Автоматическая защита (Continuity Guard)

Чтобы проект оставался целостным без ручных усилий, в комплект включены два уровня безопасности:



1. **Локальная защита (`pre-commit`)**: Устанавливается по умолчанию. Использует мягкий режим (Soft Mode) для предупреждения о дрейфе или отсутствии маркеров во время работы, не блокируя творческий поток.

2. **Пограничная защита (`pre-push`)**: Устанавливается по умолчанию. Использует строгий режим (Strict Mode) для блокировки отправки (push) в GitHub, если цикл непрерывности не на 100% валиден.



## Основные файлы

- `PROJECT_CONTEXT.md`

- `STATE.json`

- `ROADMAP.md`

- `.continuity/LIVE_HANDOFF.md`

- `AGENT_START.md` (Что передать новому ИИ-агенту)



---

**Для получения более подробной информации см. «Варианты использования» и «Руководство по устранению неполадок» в корневом каталоге.**

---

| Guide | Link |
| :--- | :--- |
| [**Industrial Guide**](../../../docs/HOW_TO_USE_IT.md) | [HOW_TO_USE_IT.md](../../../docs/HOW_TO_USE_IT.md) |
| [**Release Manifest**](../../../RELEASE_NOTES_MANIFEST.md) | [RELEASE_NOTES_MANIFEST.md](../../../RELEASE_NOTES_MANIFEST.md) |

---

---
*Continuity Legacy: Protecting the logical lineage of your software.*
