# CHRONOLITH: 故障排除指南 🛠️



不匹配？不要惊慌。以下是解决常见连续性问题的方案。



---



## 1. 一致性周期失败 (`doc_parity_check`) ✘



*   **问题**: 你收到“文档一致性漂移 (Document parity drift)”错误，指示缺少强制标记。

*   **原因**: 你编辑了某个文件（如 README 或 Handoff）并意外删除了系统为确保一致性而监控的一行。

*   **解决方案**:

    1.  查看 `outputs/chronolith/chronolith_cycle_report.json` 以查看哪个“required_string”缺失。

    2.  将一致性标记重新添加回文档。

    3.  再次运行 `python tools/chronolith/run_chronolith_cycle.py`。



---



## 2. Git Hook 拦截我的提交或推送 🛡️



*   **问题**: Git 不允许你保存或上传更改。

*   **原因**: 你处于严格模式 (`--strict`)，且你的 `STATE.json` 与文件的实际状态不匹配。

*   **解决方案**:

    1.  运行 `python tools/chronolith/chronolith_status.py` 以查看健康仪表板。

    2.  使用 `python tools/chronolith/run_chronolith_cycle.py` 同步状态。

    3.  如果是紧急情况，你可以使用 `git commit -m "msg" --no-verify`（不推荐！）。



---



## 3. 我的 AI 代理似乎“迷失”或忽视了上下文 🤖



*   **问题**: AI 开始捏造事实，或者不知道上一个会话在哪里结束。

*   **原因**: 你没有移交规范的启动包，或者 `LIVE_HANDOFF.md` 为空/已过时。

*   **解决方案**:

    1.  确保在会话开始时移交 **`AGENT_START.md`** 文件。

    2.  使用 `python tools/chronolith/chronolith_suggest.py` 生成已发生事情的良好摘要并提供给 AI。

    3.  詢問 AI： *"Reconstruct your current state by reading the root STATE.json and tell me what your Next Exact Action is"* (阅读根 `STATE.json` 来重建你的当前状态，并告诉我你的下一步精确动作)。



---



## 4. 启动时的“安全警告”错误 ⚠️



*   **问题**: Python 脚本在尝试解析根路径时抛出安全错误。

*   **原因**: 你尝试在有效的 **CHRONOLITH** 存储库之外运行脚本。

*   **解决方案**:

    1.  确保你位于项目根目录。

    2.  检查 `chronolith.json` 文件或 `.chronolith` 文件夹是否存在。

    3.  如果你是手动复制的项目，请务必先运行 `bootstrap_project.py`。



---



## 5. 仪表板 (`chronolith_status`) 显示“Unknown”或“Skipped” ❓



*   **问题**: 健康系统的某些部分不显示数据。

*   **原因**: 你尚未完成完整的一致性周期，或者“外部文档”功能已禁用。

*   **解决方案**:

    1.  运行周期： `python tools/chronolith/run_chronolith_cycle.py`。

    2.  如果使用外部文件夹（例如 `MYPROJECTDEV`），请确保你在引导时使用 `--enable-external-docs` 启用了它。

---
*Chronolith: Protecting the logical lineage of your software.*
