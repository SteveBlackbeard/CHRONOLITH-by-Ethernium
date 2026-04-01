# CONTINUITY LEGACY (by Ethernium)

`CONTINUITY LEGACY` は、永続的な継続性、標準的なメモリ、および人間とAIオペレーター間の再現可能なハンドオフを構築するための独立したスターターキットです。

このツールキットは「継続性第一」を掲げており、外部フレームワークに依存することなく、コンテキストの永続化、ドキュメントの整合性チェック、および管理されたハンドオフのための再利用可能な規律を提供します。

## 主な機能
- 最小限の標準メモリサーフェス
- 継続性ブートストラップスナップショット
- ドキュメント整合性（パリティ）チェック
- システムメンバーシップチェック
- オプションの外部開発レイヤー（例：`PROJECTDEV/`）
- 厳格な継続性クローズアウトコマンド
- テンプレートをパーソナライズするためのブートストラッパー

## クイックスタート

### 1. プロの方法 (CLI) - 推奨
グローバルCLIをインストールして、プロジェクトをワンステップで初期化します：

```powershell
pip install continuity-legacy
continuity-legacy init "My Project"
```

### 2. 手動コントロール (コピー/ペースト)
1. このフォルダを新しいプロジェクトのルートにコピーします。
2. ブートストラッパーを実行します：

```powershell
python tools/continuity_legacy/bootstrap_project.py --repo-root . --project-name "My Project" --project-slug my_project
```

3. 外部継続性レイヤーが必要な場合：

```powershell
python tools/continuity_legacy/bootstrap_project.py --repo-root . --project-name "My Project" --project-slug my_project --enable-external-docs
```

## 自動ガード (Continuity Guard)
手動の労力をかけずにプロジェクトの整合性を維持するため、2つの安全レイヤーが含まれています：

1. **ローカルガード (`pre-commit`)**: デフォルトでインストールされます。ソフトモードを使用して、作業中に整合性の欠如やマーカーの不足を警告しますが、クリエイティブな流れを止めることはありません。
2. **境界ガード (`pre-push`)**: デフォルトでインストールされます。厳格（Strict）モードを使用して、継続性サイクルが100%有効でない限り、GitHubへのプッシュをブロックします。

## 主要ファイル
- `PROJECT_CONTEXT.md`
- `STATE.json`
- `ROADMAP.md`
- `.continuity/LIVE_HANDOFF.md`
- `AGENT_START.md` (新しいAIエージェントに渡すファイル)

---
**詳細は、ルートディレクトリにある「ユースケース」および「トラブルシューティングガイド」を参照してください。**
