# Chronolith: 지속적 거버넌스 계층

![Version](https://img.shields.io/badge/version-3.2.1-blue.svg)

#### 에디션

[![LITE](https://img.shields.io/badge/Edition-LITE-black)](../../chronolith-lite/) [![PRO](https://img.shields.io/badge/Edition-PRO-black)](../../chronolith-pro/) [![OMEGA](https://img.shields.io/badge/Edition-OMEGA-black)](../../chronolith-omega/)

#### 언어

[![ES](https://img.shields.io/badge/ES-white)](../OTHER_LANGUAGES/README_es.md) [![JA](https://img.shields.io/badge/JA-white)](../OTHER_LANGUAGES/README_ja.md) [![RU](https://img.shields.io/badge/RU-white)](../OTHER_LANGUAGES/README_ru.md) [![ZH](https://img.shields.io/badge/ZH-white)](../OTHER_LANGUAGES/README_zh.md) [![FR](https://img.shields.io/badge/FR-white)](../OTHER_LANGUAGES/README_fr.md) [![IT](https://img.shields.io/badge/IT-white)](../OTHER_LANGUAGES/README_it.md) [![DE](https://img.shields.io/badge/DE-white)](../OTHER_LANGUAGES/README_de.md) [![PT](https://img.shields.io/badge/PT-white)](../OTHER_LANGUAGES/README_pt.md) [![KO](https://img.shields.io/badge/KO-white)](../OTHER_LANGUAGES/README_ko.md) [![AR](https://img.shields.io/badge/AR-white)](../OTHER_LANGUAGES/README_ar.md) [![EN](https://img.shields.io/badge/EN-white)](../README.md)

---

*(Chronolith 기술 동기화)*

Chronolith는 소프트웨어의 논리적 계보를 보호하기 위해 설계된 전문가급 동기화 프레임워크입니다. **Ethernium 생태계**에서 태어났으며, 개발 의도와 아키텍처 결정이 모든 인계 과정에서 확실히 보존되도록 합니다.

---

## 2분 만에 시작하기

```bash
pip install chronolith-lite
chronolith-lite init
chronolith-lite check
```

그런 다음 추적 중인 파일을 아무거나 수정하고 `check`를 다시 실행하십시오. 루트 해시가 바뀌는 것을 확인할 수 있습니다. 이것이 전부입니다.

리프(leaf)가 경로에 결속되어 있기 때문에, 파일 이름 변경이나 두 파일의 내용 교환도 텍스트 수정과 마찬가지로 루트를 변경합니다.

---

## 3계층 생태계

- **Lite**: 마찰 없는 수호자. 속도와 일상적인 개발 사용에 최적화되어 있습니다.

- **Pro**: 전술 엔진. 보안 및 동기화 감사를 갖춘 산업 등급의 경계 수호자.

- **Omega**: 엔터프라이즈 오라클. 고급 RAG, 인지 지도, 사전 영향 분석.

---

## 주요 기능

- **대사 최적화**: 모든 에디션에 지연 로딩을 구현. CLI 즉시 시작 (<100ms).

- **DNA 합성**: 논리적 계보를 보호하기 위한 `PROJECT_DNA.md` 자동 생성.

- **인지적 통찰 (Omega)**: 대화형 의사결정 지도와 영향 알림.

- **글로벌 인식**: 11개 언어의 완전한 문서 및 CLI 지원.

- **다이아몬드 정화**: 인코딩 오류와 문자 깨짐의 철저한 제거.

---

## 실패 시 닫힘 (Fail-closed)

터미널에서 `check`는 드리프트를 감지하면 확인을 요청하고, 승인하면 기준선을 새 루트로 재결정화합니다. CI에서는, 즉 TTY가 없는 환경에서는 절대 묻지 않고 종료 코드 `1`로 중단합니다.

기본값이 실패 시 닫힘이므로, 아무도 보고 있지 않다는 이유로 드리프트된 트리가 파이프라인을 통과하는 일은 없습니다.

---

## 품질 흐름

1. 의도 포착: '왜'를 문서화한다.

2. 패리티 검사: 생태계를 검증한다.

3. 영향 분석: 의미적 모순을 탐지한다.

4. DNA 합성: 핵심 뉴클레오타이드를 갱신한다.

---

| 안내서 | 링크 |
| :--- | :--- |
| [**빠른 시작**](../../GETTING_STARTED.md) | [GETTING_STARTED.md](../../GETTING_STARTED.md) |
| [**산업용 가이드**](../../HOW_TO_USE_IT.md) | [HOW_TO_USE_IT.md](../../HOW_TO_USE_IT.md) |
| [**릴리스 매니페스트**](../../RELEASE_NOTES_MANIFEST.md) | [RELEASE_NOTES_MANIFEST.md](../../RELEASE_NOTES_MANIFEST.md) |

---

*Chronolith: 소프트웨어의 논리적 계보를 보호합니다.*
