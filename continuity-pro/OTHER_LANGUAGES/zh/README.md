# Continuity Legacy: Persistent Governance Layer 



`CONTINUITY LEGACY` 是一个独立的启动工具包，用于构建具有持久连续性、规范内存以及在人类和 AI 操作员之间可重复移交 (handoff) 的项目。



该工具包以连续性为核心：它提供了一种可重用的规则，用于上下文持久化、文档一致性检查和受控移交，且不依赖于任何外部框架。



## 包含内容

- 最小化规范内存表面

- 连续性引导快照 (bootstrap snapshot)

- 文档一致性 (parity) 检查

- 系统成员身份检查

- 可选的外部开发层 (例如 `PROJECTDEV/`)

- 严格的连续性周期关闭命令

- 用于根据新项目对模板进行个性化的引导程序 (bootstrapper)



## 快速开始



### 1. 专业方法 (CLI) - 推荐

安装全局 CLI 以一步完成项目初始化：



```powershell

pip install continuity-legacy

continuity-legacy init "My Project"

```



### 2. 手动控制 (复制/粘贴)

1. 将此文件夹复制到新项目的根目录下。

2. 运行引导程序：



```powershell

python tools/continuity_legacy/bootstrap_project.py --repo-root . --project-name "My Project" --project-slug my_project

```



3. 如果你需要外部连续性层：



```powershell

python tools/continuity_legacy/bootstrap_project.py --repo-root . --project-name "My Project" --project-slug my_project --enable-external-docs

```



## 自动后卫 (Continuity Guard)

为了确保项目在无需手动干预的情况下保持连贯，该工具包包含两个安全层：



1. **本地后卫 (`pre-commit`)**: 默认安装。使用软模式 (Soft Mode) 在工作时提醒偏差或缺少标记，而不会阻塞你的创意流程。

2. **边界后卫 (`pre-push`)**: 默认安装。使用严格模式 (Strict Mode) 拦截推送到 GitHub，除非连续性周期 100% 有效。



## 核心文件

- `PROJECT_CONTEXT.md`

- `STATE.json`

- `ROADMAP.md`

- `.continuity/LIVE_HANDOFF.md`

- `AGENT_START.md` (交给新 AI 代理的文件)



---

**更多详情，请参阅根目录下的“使用案例”和“故障排除指南”。**

---

| Guide | Link |
| :--- | :--- |
| [**Industrial Guide**](../../../docs/HOW_TO_USE_IT.md) | [HOW_TO_USE_IT.md](../../../docs/HOW_TO_USE_IT.md) |
| [**Release Manifest**](../../../RELEASE_NOTES_MANIFEST.md) | [RELEASE_NOTES_MANIFEST.md](../../../RELEASE_NOTES_MANIFEST.md) |

---

---
*Continuity Legacy: Protecting the logical lineage of your software.*
