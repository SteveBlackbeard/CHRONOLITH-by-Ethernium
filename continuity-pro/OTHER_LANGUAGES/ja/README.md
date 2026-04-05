# CONTINUITY LEGACY: 記憶の守護者 (v3.0) 🛡️🧠🚀

このキットは、人間とAIオペレーター間の**永続的な記憶**が極めて重要であるプロジェクトのために設計された、絶対的な継続性フレームワークです。単なるファイル群ではありません。あなたのエージェントのための**認知オペレーティングシステム**です。

## 🌟 継続性の原則
- **標準メモリ**: 真実はチャットメモリではなく、ファイルシステムに存在します。
- **厳格なクローズアウト**: プッシュの前にパリティの検証を義務付けています。
- **論理的免疫**: 建築上の矛盾を自動的に検出します。
- **モジュール化された知能**: コアは依存関係なし、オプトインで拡張機能をサポート。

## 🚀 クイックスタート (v3.0 モジュラー)

1. **インストール**: `tools/continuity_legacy/` フォルダをご自身のプロジェクトにコピーしてください。
2. **インテリジェントな初期化 (グラスボックス)**:
```powershell
python tools/continuity_legacy/bootstrap_project.py --repo-root . --project-name "My Project" --project-slug my_project --discover
```
*`--discover` フラグは、あなたのスタック (React, Python, Dockerなど) をスキャンし、自動的にルールを提案します。*

3. **オプトイン拡張機能**:
```powershell
# ベクトルデータベース (ChromaDB) サポートを追加
python tools/continuity_legacy/bootstrap_project.py --project-name "AI Core" --project-slug ia_core --with-vector

# メモリグラフ (NetworkX) サポートを追加
python tools/continuity_legacy/bootstrap_project.py --project-name "Brain" --project-slug brain --with-graph
```

4. **継続性サイクル (必須)**:
```powershell
python tools/continuity_legacy/run_continuity_cycle.py --strict
```

## 🏛️ ガバナンスと成熟度
ルートにある公式ドキュメントを参照してください：
- [MAINTAINERS.md](../../MAINTAINERS.md): 守護者の役割と継承。
- [CONTRIBUTING.md](../../CONTRIBUTING.md): 共同作業者のためのパリティガイド。
- [CHANGELOG.md](../../CHANGELOG.md): システム進化の歴史。

---
*"継続性は個人ではなく、プロセスである。"*
依存することなく、コンテキストの永続化、ドキュメントの整合性チェック、および管理されたハンドオフのための再利用可能な規律を提供します。

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
