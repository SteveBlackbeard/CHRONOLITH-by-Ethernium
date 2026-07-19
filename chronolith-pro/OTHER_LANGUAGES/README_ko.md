# Chronolith Pro: 산업용 연속성 프레임워크

![Version](https://img.shields.io/badge/version-3.2.1-blue.svg)

#### 에디션

[![LITE](https://img.shields.io/badge/Edition-LITE-black)](../../chronolith-lite/) [![PRO](https://img.shields.io/badge/Edition-PRO-black)](../../chronolith-pro/) [![OMEGA](https://img.shields.io/badge/Edition-OMEGA-black)](../../chronolith-omega/)

#### 언어

[![ES](https://img.shields.io/badge/ES-white)](../OTHER_LANGUAGES/README_es.md) [![JA](https://img.shields.io/badge/JA-white)](../OTHER_LANGUAGES/README_ja.md) [![RU](https://img.shields.io/badge/RU-white)](../OTHER_LANGUAGES/README_ru.md) [![ZH](https://img.shields.io/badge/ZH-white)](../OTHER_LANGUAGES/README_zh.md) [![FR](https://img.shields.io/badge/FR-white)](../OTHER_LANGUAGES/README_fr.md) [![IT](https://img.shields.io/badge/IT-white)](../OTHER_LANGUAGES/README_it.md) [![DE](https://img.shields.io/badge/DE-white)](../OTHER_LANGUAGES/README_de.md) [![PT](https://img.shields.io/badge/PT-white)](../OTHER_LANGUAGES/README_pt.md) [![KO](https://img.shields.io/badge/KO-white)](../OTHER_LANGUAGES/README_ko.md) [![AR](https://img.shields.io/badge/AR-white)](../OTHER_LANGUAGES/README_ar.md) [![EN](https://img.shields.io/badge/EN-white)](../README.md)

---

**Pro**는 Lite의 모든 기능에 더해, 당신을 신뢰하지 않는 사람도 검증할 수 있는 증명을 제공합니다.

```bash
pip install chronolith-pro
chronolith-pro sovereign-init     # Ed25519 서명 키 + X25519 암호화 키
chronolith-pro check              # 이제 기준선이 실제로 서명됨
chronolith-pro verify             # 읽기 전용. 회의론자가 실행하는 명령
```

---

## `verify`: 증명하지 않은 것까지 말하는 명령

`verify`는 루트를 재계산하고, 서명된 기준선과 대조하며, Ed25519 서명과 추가 전용 투명성 체인 전체를 검증합니다. 그리고 무엇을 **증명하지 않았는지**도 함께 보고합니다.

```
! authenticity NOT verified: no --expect-fingerprint. This proves internal
  integrity only; a fork that swapped the whole key set would still pass.
```

이 간극을 닫으려면, 별도 경로로 입수한 지문을 `--expect-fingerprint`로 전달하십시오. 도구는 스스로의 한계를 밝히며, 사용자가 실제 검증 범위 이상을 넘겨짚도록 두지 않습니다.

---

## 주권 암호화

- **경로 결속 머클 무결성**: 모든 파일은 경로를 키로 하는 리프입니다. 1바이트 수정은 물론, 이름 변경이나 두 파일 간 내용 교환도 루트 해시를 바꿉니다.

- **Ed25519 서명 기준선**: 체크섬만으로는 사고를 감지할 뿐이며, 서명이 있어야 위조를 감지합니다.

- **DNA 투명성 체인**: 루트의 추가 전용 계보. 절단은 기준선에 결속된 체인 헤드가 드러냅니다.

- **머클 포함 증명**: `prove` 명령으로 저장소 전체를 다시 해싱하지 않고 O(log n) 해시만으로 파일 하나의 소속을 검증합니다.

- **실제 봉인 컨텍스트**: X25519 + ChaCha20-Poly1305, 그리고 암호로 보호되는 키 저장소.

- **키 순환**: 이전 키가 새 키로의 인계를 서명하므로, 폐기된 키로 서명된 이력도 계속 검증 가능합니다.

---

## 외부 증인: 비트코인 앵커

```bash
chronolith-pro anchor
```

OpenTimestamps를 통해 투명성 체인의 헤드에 타임스탬프를 부여합니다. 이로써 제3자는 운영자를 신뢰하지 않고도 특정 시점에 해당 DNA 상태가 존재했음을 확인할 수 있습니다.

실제 앵커가 [`docs/evidence/`](../../docs/evidence/)에 커밋되어 있습니다 — 블록 958484.

앵커는 비동기적으로 확정되며, `chronolith-pro upgrade-anchors`가 대기 중인 항목을 완료합니다. 확정된 뒤에는 아무 동작도 하지 않으므로 예약 실행에 안전합니다.

---

## 알려진 한계

두 가지는 이 설계에 내재된 것이며, 문서화되어 있습니다.

- **키 교체 포크**: 전체 키 집합을 교체한 포크는 자체적으로 일관되므로, 별도 경로로 확보한 지문을 고정하지 않으면 통과합니다.

- **롤백**: 확정된 비트코인 앵커가 없으면, 이전의 유효한 상태로 되돌리는 행위는 외부에서 탐지할 수 없습니다.

자세한 내용: [SOVEREIGN_SECURITY.md](../SOVEREIGN_SECURITY.md)

---

| 안내서 | 링크 |
| :--- | :--- |
| [**빠른 시작**](../../GETTING_STARTED.md) | [GETTING_STARTED.md](../../GETTING_STARTED.md) |
| [**산업용 가이드**](../../HOW_TO_USE_IT.md) | [HOW_TO_USE_IT.md](../../HOW_TO_USE_IT.md) |
| [**보안**](../SOVEREIGN_SECURITY.md) | [SOVEREIGN_SECURITY.md](../SOVEREIGN_SECURITY.md) |

---

*Chronolith: 소프트웨어의 논리적 계보를 보호합니다.*
