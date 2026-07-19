# Chronolith Omega: 엔터프라이즈 오라클

![Version](https://img.shields.io/badge/version-3.2.1-blue.svg)

#### 에디션

[![LITE](https://img.shields.io/badge/Edition-LITE-black)](../../chronolith-lite/) [![PRO](https://img.shields.io/badge/Edition-PRO-black)](../../chronolith-pro/) [![OMEGA](https://img.shields.io/badge/Edition-OMEGA-black)](../../chronolith-omega/)

#### 언어

[![ES](https://img.shields.io/badge/ES-white)](../OTHER_LANGUAGES/README_es.md) [![JA](https://img.shields.io/badge/JA-white)](../OTHER_LANGUAGES/README_ja.md) [![RU](https://img.shields.io/badge/RU-white)](../OTHER_LANGUAGES/README_ru.md) [![ZH](https://img.shields.io/badge/ZH-white)](../OTHER_LANGUAGES/README_zh.md) [![FR](https://img.shields.io/badge/FR-white)](../OTHER_LANGUAGES/README_fr.md) [![IT](https://img.shields.io/badge/IT-white)](../OTHER_LANGUAGES/README_it.md) [![DE](https://img.shields.io/badge/DE-white)](../OTHER_LANGUAGES/README_de.md) [![PT](https://img.shields.io/badge/PT-white)](../OTHER_LANGUAGES/README_pt.md) [![KO](https://img.shields.io/badge/KO-white)](../OTHER_LANGUAGES/README_ko.md) [![AR](https://img.shields.io/badge/AR-white)](../OTHER_LANGUAGES/README_ar.md) [![EN](https://img.shields.io/badge/EN-white)](../README.md)

---

Lite와 Pro는 *"이것이 변경되었는가?"*에 답합니다. **Omega**는 *"우리는 왜 이렇게 결정했는가?"*에 답합니다. 통제된 코퍼스에 대한 의미 검색이며, 전부 로컬에서 동작합니다.

```bash
pip install chronolith-omega

chronolith-omega init      # 메모리 코어 + 자동 색인 훅
chronolith-omega index     # 로컬 벡터 저장소 구축
chronolith-omega query "왜 서명에 Ed25519를 선택했는가?"
```

---

## 의미 기반 검색

`query`는 키워드가 아니라 의미로 코퍼스를 순위화합니다. 따라서 결정 기록에 "왜"라는 단어가 한 번도 등장하지 않아도 그 질문에 해당하는 항목을 찾아냅니다.

임베딩이 다국어이므로 언어의 경계도 넘습니다. 영어로 던진 질문이, 공통 단어가 하나도 없는 스페인어 결정 기록을 첫 번째 결과로 반환합니다.

색인과 질의는 완전히 로컬에서 이루어집니다. 코퍼스의 어떤 내용도 기기 밖으로 나가지 않습니다.

---

## 결정 계보 지도

```bash
chronolith-omega map       # -> outputs/chronolith/cognitive_map.html
```

기록된 각 결정을 노드로 삼아, 채택된 순서대로 연결한 계층적 대화형 그래프를 생성합니다.

> **참고**: 생성된 지도는 CDN에서 `vis-network`를 불러오므로 그 HTML 파일 하나는 렌더링에 네트워크 접근이 필요합니다. 색인과 질의는 전적으로 로컬입니다.

---

## 주요 기능

- **고급 RAG**: 통제된 코퍼스 위에서 동작하는 로컬 검색.

- **인지 지도**: 결정의 계보를 시각화.

- **영향 분석**: 의미적 모순의 탐지.

- **글로벌 인식**: 11개 언어의 문서 및 CLI 지원.

---

| 안내서 | 링크 |
| :--- | :--- |
| [**빠른 시작**](../../GETTING_STARTED.md) | [GETTING_STARTED.md](../../GETTING_STARTED.md) |
| [**산업용 가이드**](../../HOW_TO_USE_IT.md) | [HOW_TO_USE_IT.md](../../HOW_TO_USE_IT.md) |

---

*Chronolith: 소프트웨어의 논리적 계보를 보호합니다.*
