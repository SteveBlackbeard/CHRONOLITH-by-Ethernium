# Chronolith

![Version](https://img.shields.io/badge/version-3.2.0-blue.svg)

Chronolith는 AI 지원 세션 전반에 걸쳐 프로젝트의 의도를 담는 문서를 위한 암호학적 무결성 계층입니다. 정본 문서를 머클 트리로 해시하고 서명된 기준선을 기록하며, 현재 상태가 그와 일치하지 않으면 작업을 중단합니다(fail-closed).

AI가 "기억한다"고 보장하지 않습니다. 합의된 맥락이 *무엇이었는지*에 대한 검증 가능한 기록과, 그것이 어긋났을 때의 확실한 중단을 제공합니다.

## 에디션

- **Lite**: 최소한의 로컬 인계와 서명된 상태 검사.
- **Pro**: 완전한 가디언 — Ed25519 서명 기준선, 추가 전용 투명성 체인, 머클 포함 증명, 암호화, 키 교체, 비트코인 앵커링.
- **Omega**: RAG 지향 인지 매핑과 영향 분석.

## 설치

```bash
pip install chronolith
chronolith --help
```

개별 패키지:

```bash
pip install chronolith-lite
pip install chronolith-pro
pip install chronolith-omega
```

## 검증 가능한 증거

이 프로젝트의 한 상태는 **비트코인 블록 958484**에 타임스탬프되어 있습니다. 이 저장소나 작성자를 신뢰할 필요가 없습니다. 직접 확인하십시오:

```bash
pip install "chronolith-pro[anchor]"
chronolith-pro verify-anchor --proof docs/evidence/ANCHOR_3647dd737ee8.json.ots
```

증명하는 것: 해당 데이터가 그 블록이 채굴되기 전에 존재했다는 사실. 증명하지 않는 것: 누가 썼는지, 또는 내용이 올바른지. 이러한 한계는 숨기지 않고 문서화되어 있습니다.

## 제품 경계

Chronolith는 Python 런타임이자 거버넌스 커널입니다. Seneschal은 토큰 절약과 서명된 권한 부여를 위한 별도의 분리 가능한 도구입니다.
