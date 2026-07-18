# Chronolith

![Version](https://img.shields.io/badge/version-3.2.0-blue.svg)

Chronolith 是一个加密完整性层，用于承载项目意图、跨越 AI 辅助会话的文档。它将你的规范文档哈希为默克尔树，记录一份已签名的基准，并在当前状态与之不符时以失败关闭（fail-closed）的方式中止。

它并不保证 AI 会「记住」。它提供的是关于既定上下文*曾经是什么*的可验证记录，以及在其漂移时的硬性中止。

## 版本

- **Lite**：最小化的本地交接与签名状态检查。
- **Pro**：完整守护者 —— Ed25519 签名基准、仅追加的透明链、默克尔包含证明、加密、密钥轮换与比特币锚定。
- **Omega**：面向 RAG 的认知映射与影响分析。

## 安装

```bash
pip install chronolith
chronolith --help
```

单独安装各组件：

```bash
pip install chronolith-lite
pip install chronolith-pro
pip install chronolith-omega
```

## 可验证的证据

本项目的某个状态已被时间戳记录于**比特币区块 958484**。你无需信任本仓库或其作者——请自行验证：

```bash
pip install "chronolith-pro[anchor]"
chronolith-pro verify-anchor --proof docs/evidence/ANCHOR_3647dd737ee8.json.ots
```

它能证明的：这份确切数据在该区块被挖出之前就已存在。它不能证明的：由谁撰写，或内容是否正确。这些边界均已记录，并未隐瞒。

## 产品边界

Chronolith 是 Python 运行时与治理内核。Seneschal 是一个独立、可抽离的工具，用于令牌节流与签名能力授权。
