# CHRONOLITH: トラブルシューティングガイド 🛠️



何かが不一致？パニックにならないでください。継続性に関する一般的な問題の解決策を以下に示します。



---



## 1. 整合性サイクルが失敗する (`doc_parity_check`) ✘



*   **問題**: 「ドキュメント整合性ドリフト（Document parity drift）」エラーが表示され、必須のマーカーが欠落していることが指摘されます。

*   **原因**: ファイル（README や Handoff など）を編集し、システムが整合性を確保するために監視している行を誤って削除してしまいました。

*   **解決策**:

    1.  `outputs/chronolith/chronolith_cycle_report.json` のレポートを確認して、どの「required_string」が欠落しているかを特定します。

    2.  整合性マーカーをドキュメントに戻します。

    3.  `python tools/chronolith/run_chronolith_cycle.py` を再度実行します。



---



## 2. Git Hook がコミット/プッシュをブロックする 🛡️



*   **問題**: Git が変更の保存やアップロードを許可しません。

*   **原因**: 厳格（Strict）モード（`--strict`）になっており、`STATE.json` がファイルの実際の状態と一致していません。

*   **解決策**:

    1.  `python tools/chronolith/chronolith_status.py` を実行して、ヘルスダッシュボードを確認します。

    2.  `python tools/chronolith/run_chronolith_cycle.py` を使用して、状態を同期します。

    3.  緊急の場合は、`git commit -m "msg" --no-verify` を使用できます（推奨されません！）。



---



## 3. AIエージェントが「迷子」またはコンテキストを無視する 🤖



*   **問題**: AIが事実を捏造したり、前のセッションがどこで終了したかわからなくなったりします。

*   **原因**: 標準スターターパックを渡していないか、`LIVE_HANDOFF.md` が空か古い状態です。

*   **解決策**:

    1.  セッションの開始時に、**`AGENT_START.md`** ファイルを確実に渡します。

    2.  `python tools/chronolith/chronolith_suggest.py` を使用して、何が起きたかの概要（サマリー）を生成し、AIに提供します。

    3.  AIに次のように尋ねます： 「ルートにある `STATE.json` を読んで現在の状態を再構築し、次にすべき正確なアクション（Next Exact Action）を教えてください」。



---



## 4. 起動時の「セキュリティ警告」エラー ⚠️



*   **問題**: Pythonスクリプトがルートパスを解決しようとするときにセキュリティエラーをスローします。

*   **原因**: 有効な **CHRONOLITH** リポジトリの外でスクリプトを実行しようとしています。

*   **解決策**:

    1.  プロジェクトのルートにいることを確認します。

    2.  `chronolith.json` ファイルまたは `.chronolith` フォルダが存在することを確認します。

    3.  手動でプロジェクトをコピーした場合は、まず `bootstrap_project.py` を実行してください。



---



## 5. ダッシュボード (`chronolith_status`) が 「Unknown」 または 「Skipped」 ❓



*   **問題**: ヘルスシステムのセクションにデータが表示されません。

*   **原因**: 継続性サイクルを完全に完了していないか、「外部ドキュメント（External Docs）」機能が無効になっています。

*   **解決策**:

    1.  サイクルを実行します： `python tools/chronolith/run_chronolith_cycle.py`。

    2.  外部フォルダ（例： `MYPROJECTDEV`）を使用している場合は、ブートストラップ時に `--enable-external-docs` で有効にしたことを確認してください。

---
*Chronolith: Protecting the logical lineage of your software.*
