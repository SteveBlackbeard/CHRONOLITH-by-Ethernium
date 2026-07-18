# Chronolith

![Version](https://img.shields.io/badge/version-3.2.0-blue.svg)

Chronolith は、AI を用いた作業セッションをまたいでプロジェクトの意図を運ぶ文書のための、暗号的な完全性レイヤーです。正典となる文書をマークルツリーにハッシュ化し、署名済みの基準状態を記録し、現在の状態がそれと一致しなくなった時点で処理を停止します（フェイルクローズド）。

AI が「記憶する」ことを保証するものではありません。合意された文脈が*どうであったか*の検証可能な記録と、それが逸脱したときの明確な停止を提供します。

## エディション

- **Lite**: 最小限のローカル引き継ぎと署名付きの状態チェック。
- **Pro**: 完全なガーディアン — Ed25519 署名済み基準、追記専用の透明性チェーン、マークル包含証明、暗号化、鍵のローテーション、Bitcoin へのアンカリング。
- **Omega**: RAG 指向の認知マッピングと影響分析。

## インストール

```bash
pip install chronolith
chronolith --help
```

個別パッケージ:

```bash
pip install chronolith-lite
pip install chronolith-pro
pip install chronolith-omega
```

## 検証可能な証拠

本プロジェクトのある状態は **Bitcoin ブロック 958484** にタイムスタンプされています。このリポジトリや作者を信頼する必要はありません。ご自身で検証してください:

```bash
pip install "chronolith-pro[anchor]"
chronolith-pro verify-anchor --proof docs/evidence/ANCHOR_3647dd737ee8.json.ots
```

証明できること: そのデータが当該ブロックの採掘前に存在していたこと。証明できないこと: 誰が書いたか、内容が正しいかどうか。これらの限界は隠さず文書化しています。

## 製品の境界

Chronolith は Python ランタイムおよびガバナンスカーネルです。Seneschal はトークン節約と署名付き権限付与のための、独立した抽出可能なツールです。
