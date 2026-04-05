# CONTINUITY LEGACY: 实际使用案例 🚀



本文档详细介绍了如何将连续性理念应用于现实场景。



---



## 1. 使用 AI 构建复杂系统 🏗️

在构建具有多个组件（如数据库、API、前端）的架构时，AI 经常会忽视过去的架构决策。



*   **使用 CONTINUITY LEGACY**: 

    -   在 `PROJECT_CONTEXT.md` 中定义基础架构。

    -   每次更改数据库模式 (schema) 时，在 `DECISIONS_LOG.md` 中记录。

    -   在会话结束时，`LIVE_HANDOFF.md` 应指明哪些表已迁移，哪些待处理。

*   **收益**: 下一个代理将知道你 *为什么* 选择 PostgreSQL 而不是 MongoDB，且不会在半途尝试更改逻辑。



---



## 2. 具有“学习”能力的认知代理 🧠

自主工作的代理需要一个规范的地方来存储它学到的关于环境的信息。



*   **使用 CONTINUITY LEGACY**: 

    -   代理使用 `TIMELINE.md` 记录其发现（例如，“在 API X 上检测到错误 403；需要类型 Y 的令牌”）。

    -   代理更新 `STATE.json` 以反映其对系统的新“知识”水平。

*   **收益**: 连续性不仅关乎代码，还关乎 **积累的知识**。



---



## 3. 从内存/RAG 工具迁移 ⚡

如果你已经在使用向量数据库 (RAG) 作为 AI 的内存，你可能会觉得它在处理当前会话状态时不够精确。



*   **使用 CONTINUITY LEGACY**: 

    -   将 RAG 用于“历史数据”或“参考库”。

    -   将 **CONTINUITY LEGACY** 用作 **活跃运营状态**。

    -   将 `context_bootstrap_summary.json` 注入代理的系统提示词 (System Prompt)。

*   **收益**: 你从“统计式”内存 (RAG) 转向“确定式”内存 (连续性)。AI 对 *当前* 正在发生的事情始终会有正确的认知。



---



## 4. 多代理工作 (扩展结对编程) 🤝

当你在不同的 AI 之间切换时（例如，用 Claude 编程，但用 GPT-4 部署）。



*   **使用 CONTINUITY LEGACY**: 

    -   Claude 生成 `LIVE_HANDOFF.md`。

    -   GPT-4 在进入时读取 `AGENT_START.md`。

    -   双方都通过 `--strict` 周期验证一致性。

*   **收益**: 知识的“移交”是瞬间完成的，且没有人为错误。模型之间没有“信号损失”。

---
*Continuity Legacy: Protecting the logical lineage of your software.*
