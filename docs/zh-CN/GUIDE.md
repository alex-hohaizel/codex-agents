# Codex Agent System 使用指南

在 Codex 中完成一项具体任务，和专长角色一起开发产品，或设计可复用的智能体。系统为每项工作记录实际来源、负责人和可以验证的结果。

[English](../en/GUIDE.md) · [Українська](../uk/GUIDE.md) · [Deutsch](../de/GUIDE.md) · [Italiano](../it/GUIDE.md) · [Español](../es/GUIDE.md) · [Français](../fr/GUIDE.md) · [简体中文](../zh-CN/GUIDE.md)

首次使用请打开[分步入门](../../START_HERE.md#install-and-verify)，再[跟随一个请求走完整个项目](../technical/END_TO_END.md)，从选定团队到审核发布证据。 [打开完整流程图](../../assets/marketing/release-1.7/workflow-en.svg) · [文档索引](../INDEX.md)

商业候选包包含统一安装流程和已购版本权益记录。选择前请阅读[买家指南](../commercial/BUYER_GUIDE.md)、[许可](../commercial/LICENSING.md)和[运行环境限制](../commercial/WORKBENCH_RUNTIME.md)。

## 选择起点

- **试用 Codex。** [安装并验证](#install) · [完成第一个任务](#first-task) · [查看图解流程](../../marketing/zh-CN/README.md)
- **开发或运营项目。** [选择工作流](#workflow) · [查找技能或角色](#catalog) · [本地工作台](#workbench) · [运维与恢复](#operations)
- **了解系统如何工作。** [Harness 运行框架](#harness) · [子智能体](#subagents) · [上下文胶囊](#context) · [模型与成本](#models)
- **寻找和验证证据。** [知识检索（RAG）](#retrieval) · [评估（evals）](#evals) · [工具与权限](#permissions)

[技术主题（英文）](../OPERATING_MODEL.md#engineering-topics) · [RAG 实例（英文）](../technical/RETRIEVAL.md) · [产品需求](../../governance/requirements.csv)

<a name="install"></a>
## 安装并确认技能可用

### 适用于 Windows、macOS 和 Linux 的现成安装包

从[稳定发行版](https://github.com/alex-hohaizel/codex-agents/releases/latest)下载现成的 **Universal** 归档或与你的系统、CPU 对应的包。完整解压，阅读 `START_HERE.html`，然后在 Windows 打开 `Start.cmd`、macOS 打开 `Start.command`、Linux 打开 `Start.sh`。包中已包含 Python、Node 和构建后的界面，无须另行安装这些运行时。GitHub 自动生成的源码 ZIP 属于开发者流程。安装向导提供英语和乌克兰语；本手册用简体中文解释同一流程。

依次选择 **Check now → Prepare plan**，核对目标与冲突，批准准确的计划，再选择 **Install reviewed plan → Verify files → Check in Codex**。默认安装包含 33 项技能、Orchestrator、配置和十二个角色。实际使用代理需要你自己的 Codex 账户。**Create practice project → Open folder → Open Codex → Copy prompt** 只准备第一个练习，不会执行模型。保留日志；恢复时使用所选操作及原来的计划。[完整安装与恢复](../INSTALL.md#recommended-local-browser-installer)

项目自己的 Python/venv 与 Node 保持优先级。工具包辅助脚本使用 `AGENT_SYSTEM_PYTHON` 指定的解释器。Maintenance 仍是所有者单独使用的工具：通过受支持的技能管理器安装包内 `product/maintenance-skill` 或仓库的 `maintenance-skill`，先预览来源和目标，再验证结果。模型和外部服务使用各自账户并单独计费。

### 从源码安装的进阶流程

1. 打开 `alex-hohaizel/codex-agents` 的稳定发行版。macOS 或 Linux 上的终端步骤需要 Bash、Python 3.9+、Git、已登录的 GitHub CLI（`gh`）和 Codex。需要引导时，可以请 Codex 用简体中文说明每一步，并保留准确的选项和路径。
2. 按带来源证明的流程安装。验签工具根据源码提交、工作流与清单验证归档摘要和 GitHub 来源证明。尚未安装受管理的核心套件时选择全新安装，已有套件时提供经确认的已安装版本。[稳定发行版](https://github.com/alex-hohaizel/codex-agents/releases/latest) · [完整命令](../INSTALL.md#steps)
3. 在审查结果中核对 33 项技能、安装位置、图标文件和引用的保留计划以及未解决的冲突。应用审核过的计划，并用返回的日志验证文件。受管理的 Codex 配置和十二个角色通过各自的审查与日志安装。[配置与角色](../INSTALL.md#profile-and-roles)
4. 按需单独安装 Orchestrator 和维护技能。在 Agent Atelier 中预览准确的可选技能来源、目标位置和改动，再应用并验证。也可通过 Codex 支持的个人技能管理界面使用完整的可选技能目录。[可选组件](../INSTALL.md#optional-components)
5. 在目标产品目录中打开新的 Codex 对话。调用 `$agent-foundry` 或选定技能。宿主若提供实际解析的路径，请将它与安装的来源核对，然后用一项结果可见的任务验证技能实际运行。[Codex 技能发现](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)

ChatGPT Work 通过自身界面管理个人技能。使用 Work 包，并在对应宿主中检查实际保存和加载的记录。本地 Codex 安装有独立流程。[安装包](../../governance/PACKAGES.md)

<a name="first-task"></a>
## 完成第一次修改

创建一个临时目录并在其中打开新的 Codex 对话。将 `# Cheklist` 写入 `README.md`，在 `notes.txt` 中写一行需要保留的内容。用简体中文提出请求：

```text
修正 README.md 标题中的拼写错误，保持 notes.txt 原样。
给出修正后的标题，并说明你如何验证这两个文件。
```

看到 `# Checklist` 并且 `notes.txt` 内容不变后即可验收。这类小任务可直接执行。对于较大的项目，将目标、项目路径、允许的改动和可观察的验收条件交给 Orchestrator。例如审查结账流程，保留已批准的支付契约，仅报告可复现的问题。[可复现的第一项任务](../../START_HERE.md#install-and-verify)

<a name="workflow"></a>
## 选择工作路径并保留上下文

可直接完成任务、调用技能或由 `$atelier-orchestrator` 选择。应用、聊天机器人和游戏的完整生命周期由相应的主管技能协调。用 `$agent-foundry` 为重复出现的工作设计智能体或团队，构建前审阅方案资料，随后用原始任务验证准备好的包。用 `$design-specialist-skills` 设计带有清晰触发条件和验收用例的可复用流程。

<a name="harness"></a>
### Harness 运行框架与权限

Codex 提供运行时、工具和权限控制。仓库提供 `AGENTS.md`、技能描述和资源、领域契约、角色与检查。确认实际加载的指令，并在工具真正执行时核对权限。 [运行框架与权限](../OPERATING_MODEL.md#harness-and-authority)

<a name="subagents"></a>
### 角色与子智能体

把独立产出或独立审查交给合适的角色。写明执行者、来源版本、输入路径、写入范围、交付物、限制、停止条件和返回位置。为共享的可变状态指定一个写入负责人。集成前取回子智能体的实际结果。 [工作路径与子智能体](../OPERATING_MODEL.md#routes-and-subagents)

如果项目使用本地工单投影管理待办事项，可以先起草并审阅调整方案，再应用已获批准的变更。将就绪工单交给实施者之前，请从项目中回读写入回执。在接收工单的 Codex 会话中再次验证交接，并保留返回的结果供独立复核。 [已批准的计划调整和实施交接](../technical/TICKET_REPLAN.md)

并行工作时，从同一个提交为各执行者分配独立的 Git worktree。执行者中断时保存检查点，在新会话中验证后继续，并在专用 worktree 中集成已审阅的提交。 [协调 worktree 并恢复执行](../technical/TICKET_WORKTREES.md)

将明确关联的 GitHub Issues 与项目任务视图核对。请独立 QA 把验收标准和风险检查关联到该候选版本的实际证据。如果外部操作的结果未知，请在目标系统核实后再记录决定。 [核对 GitHub Issues](../technical/TICKET_GITHUB.md) · [审查候选版本的证据](../technical/TICKET_QUALITY_GATE.md)

面对重要决策，请不同专家根据相同的证据独立提出意见，再请他们回应最关键的分歧。由决策负责人确定下一步。 [组织团队讨论](../../optional-skills/atelier-orchestrator/references/team-deliberation.md)

待办清单变更时保留原迭代计划。先核对拟新增的任务及其依赖，再调整范围。检查 PRD 和架构文档是否覆盖所有适用要求，并对新版本重新开展评审。 [规划迭代](../technical/TICKET_TREE.md#keep-a-sprint-plan-while-the-backlog-changes) · [评审产品规格](../technical/TICKET_PRODUCT_SPEC.md)

根据保存的工作坊记录，在新会话中继续头脑风暴或检验提案。依据来源编写简报、PRFAQ，或分别编写设计和体验文档，并保留待决定事项。先审核导入的 Codex 技能和角色，再在新项目中暂存。对于已映射的 GitHub 议题，先审查拟议变更，再读取实际结果，然后决定是否重试。 [工作坊](../technical/WORKSHOP.md) · [产品引导](../technical/PRODUCT_FACILITATION.md) · [通过 Foundry 导入](../technical/CONSTRUCTOR_IMPORT.md) · [GitHub 写入](../technical/TICKET_GITHUB.md#apply-a-reviewed-change-to-a-mapped-issue)

根据已审阅的 DESIGN 和 EXPERIENCE 构建交互式浏览器原型，或使用模板注册表将草稿、修订和评审绑定到确切来源。审核 现有模块并将已审阅的迁移暂存到新目录。同步任务树前，对照本地、上次观测与远程状态，每次核对一项变更。 [UX 原型](../technical/UX_PROTOTYPE.md) · [模板](../technical/DOCUMENT_TEMPLATES.md) · [模块迁移](../technical/MODULE_MIGRATION.md) · [任务树](../technical/TRACKER_SYNC.md) · [跟踪器服务商](../technical/TRACKER_PROVIDERS.md)

<a name="context"></a>
### 上下文胶囊

从项目的权威需求、身份、当前决策和检查点开始。固定来源的准确哈希，并携带适用要求、许可操作、延后事项、交付物、未确认的影响和下一步。来源发生变更或不可读时，重新验证受影响的义务。交接只传递下一项工作需要的内容，原始来源继续作为准据。

将 `preferred_language` 写入项目上下文，并在交接中传递。保留命令、选择器、标识符、引用与原文摘录。[工作模型](../OPERATING_MODEL.md#project-context-and-handoffs) · [项目上下文模板](../../templates/project-context.json) · [交接模板](../../templates/HANDOFF.md)

<a name="models"></a>
### 模型与成本

比较不同路径时，记录模型、推理强度和结果。成本较低的方案在相同输入下通过相同的验收检查后，方可采用。 [模型选择与成本](../OPERATING_MODEL.md#models-and-cost)

<a name="retrieval"></a>
## 加入知识检索和 RAG

先使用已验证的路径、精确的标识符、结构化查询和关键词搜索。相关证据反复难以找到时，再加入检索增强生成。选择索引或向量库之前，在同一经授权的语料库上比较关键词、语义和混合检索。检查命中率、引用准确性、无答案场景、多语言、撤销或过期来源、相邻的私有项目、延迟与成本。为每个片段记录权限和来源版本，在检索和引用之前核对权限，并支持删除或重建。检索文本只作为数据处理，任务权限由项目和实际工具控制。

用 `$chatbot-atelier-knowledge` 设计语料、检索、基于来源的回答与维护。DATA、ANALYSIS、LLM、PREDICTION、ADAPTATION、MEDIA 和 EVALUATION 是面向不同工作的配置。选择能覆盖需求的最小配置，并在实际使用端验证结果。[检索技术指南](../OPERATING_MODEL.md#retrieval-and-rag) · [AI 和数据配置](../../standards/ai-production.md)

<a name="evals"></a>
## 用评估验证行为和证据

固定代表性输入、源码版本、模型、运行环境、预期结果、失败情形及时间或成本限制。验证显式调用和自然选择、相邻请求、拒绝访问、过期来源与恢复。用实际使用端检验准确的交付物，分别记录结构校验、原生行为、工具回执和独立验收。原始请求和私有路径放在隔离的测试目录内。

从仓库根目录使用已登录、受支持的 Codex CLI 运行小规模实测：

```bash
receipt_dir="$(mktemp -d)"
python3 -B evaluations/native_canary.py --case p01-direct --output "$receipt_dir/direct.jsonl"
```

该测试会在临时项目中修正指定的错字，并检查另一文件。测试集还涵盖限定范围的交接、已批准的智能体方案以及新生成技能的第一次调用。关于外部产品的结论需要来自其实际运行环境的证据。[评估、输入和回执](../../evaluations/README.md) · [验证](../../governance/VALIDATION.md)

<a name="workbench"></a>
## 在 Windows、macOS 或 Linux 上使用 Agent Atelier

现成包提供 Windows 的 `Start-Workbench.cmd`、macOS 的 `Start-Workbench.command` 和 Linux 的 `Start-Workbench.sh`。打开对应启动器即可使用构建后的界面，无须运行 npm 构建。运行时可用性与发行版实际原生测试证明应分开核对。以下源码构建步骤保留为可选开发者流程；后续项目操作与恢复步骤适用于两种流程。[现成工作台与数据恢复](../commercial/WORKBENCH_RUNTIME.md)

1. 打开当前源码，按 Node.js 锁文件构建。在 `apps/agent-atelier/` 中运行：

```bash
npm ci --ignore-scripts
npm run build
node launcher/atelier.mjs start
node launcher/atelier.mjs status
node launcher/atelier.mjs doctor
```

2. 在本地面板找到项目并查看覆盖范围。Codex 已登记但没有对话的项目也可能出现。打开历史和产出时，面板按需读取。先预览准确的项目目录，再明确绑定。演示模式显示虚构记录。
3. 打开工作项与它有来源依据的下一步。将它带入表单，核对目标、验收条件、输入、权限和技能，并检查 Orchestrator 路线。准备任务，只启动获准的执行，随后核对结果和回执。只有上下文、身份均受支持且当前没有写入者时，才续接已有对话。保存的上下文无法恢复时，新建有明确范围的任务。
4. 在连接页面查看应用、插件和连接器。宿主支持时，可以查询 OpenAI 官方文档，预览并下载 Codex 生成的 PNG，在 Openverse 搜索注明来源和授权的图像或音频，并通过现有 GitHub CLI 登录读取仓库元数据。只使用实际环境和账户支持的操作。[工作台手册](../../apps/agent-atelier/README.md) · [API 和连接能力](../../apps/agent-atelier/shared/API.md)

<a name="operations"></a>
## 运维、恢复与更新

<a name="permissions"></a>
### 工具与权限

用工具执行写入前，核对操作、目标、授权、费用、限制和预期回执。超时或缺少回执时，首先读取这项确切请求的权威状态。仅在权限仍有效并有经过验证的去重保障时重试。记录未确认的影响及证据。在真实产品中验收结果，分别记录任务准备、命令执行和文件创建。 [工具执行结果与证据](../OPERATING_MODEL.md#tools-evidence-and-recovery)

### 恢复与更新

更新时使用稳定发行包及其确切计划，并保留日志和原有状态。发生中断后，先核对真实目标再续接。通过各自日志回滚核心、配置或可选技能。按手册备份工作台数据库和文件，使用正确的数据目录重启，并验查项目列表及一个小任务。产品数据、原生对话与账户各有自己的负责人和恢复流程。[安装与恢复](../INSTALL.md#rollback) · [恢复工作](../../governance/RESUMABLE_WORK.md)

<a name="catalog"></a>
## 选择技能或产品系列

| 选择器 | 用途 |
| --- | --- |
| `$atelier-orchestrator` | 选择路径、继续与协调工作 |
| `$agent-foundry` | 设计承担实际重复任务的智能体或团队 |
| `$design-specialist-skills` | 设计解决特定问题的可复用技能或技能系列 |
| `$app-atelier-director` | 应用调研、概念、规格、体验、开发、支持、增长、质量、发布与运维 |
| `$chatbot-atelier-director` | 受众和渠道、产品、对话、知识、集成、媒体、开发、质量、发布与运维 |
| `$gamedev-director` | 工作室、游戏概念、预制作、资源、开发、质量、发布与持续运营 |
| `$codex-agents-maintenance` | 获准的技能和文档变更、验收及发行包维护 |

### 全部领域技能与角色

**应用团队**

- [`$app-atelier-director`](../../kit/skills/app-atelier-director/SKILL.md) · 生命周期协调
- [`$app-atelier-research`](../../kit/skills/app-atelier-research/SKILL.md) · 用户和市场调研
- [`$app-atelier-concepts`](../../kit/skills/app-atelier-concepts/SKILL.md) · 产品概念
- [`$app-atelier-specification`](../../kit/skills/app-atelier-specification/SKILL.md) · 需求与契约
- [`$app-atelier-experience`](../../kit/skills/app-atelier-experience/SKILL.md) · 体验与无障碍
- [`$app-atelier-build`](../../kit/skills/app-atelier-build/SKILL.md) · 开发实现
- [`$app-atelier-growth`](../../kit/skills/app-atelier-growth/SKILL.md) · 用户增长
- [`$app-atelier-support`](../../kit/skills/app-atelier-support/SKILL.md) · 客户支持流程
- [`$app-atelier-qa`](../../kit/skills/app-atelier-qa/SKILL.md) · 独立质量审查
- [`$app-atelier-release`](../../kit/skills/app-atelier-release/SKILL.md) · 发布
- [`$app-atelier-operations`](../../kit/skills/app-atelier-operations/SKILL.md) · 运维

**聊天机器人团队**

- [`$chatbot-atelier-director`](../../kit/skills/chatbot-atelier-director/SKILL.md) · 生命周期协调
- [`$chatbot-atelier-research`](../../kit/skills/chatbot-atelier-research/SKILL.md) · 用户与渠道调研
- [`$chatbot-atelier-specification`](../../kit/skills/chatbot-atelier-specification/SKILL.md) · 行为与状态契约
- [`$chatbot-atelier-conversation`](../../kit/skills/chatbot-atelier-conversation/SKILL.md) · 对话设计
- [`$chatbot-atelier-knowledge`](../../kit/skills/chatbot-atelier-knowledge/SKILL.md) · 知识与检索
- [`$chatbot-atelier-integrations`](../../kit/skills/chatbot-atelier-integrations/SKILL.md) · 集成与回执
- [`$chatbot-atelier-media`](../../kit/skills/chatbot-atelier-media/SKILL.md) · 媒体
- [`$chatbot-atelier-build`](../../kit/skills/chatbot-atelier-build/SKILL.md) · 开发实现
- [`$chatbot-atelier-qa`](../../kit/skills/chatbot-atelier-qa/SKILL.md) · 质量审查
- [`$chatbot-atelier-release`](../../kit/skills/chatbot-atelier-release/SKILL.md) · 发布
- [`$chatbot-atelier-operations`](../../kit/skills/chatbot-atelier-operations/SKILL.md) · 运维与恢复

**游戏团队**

- [`$gamedev-director`](../../kit/skills/gamedev-director/SKILL.md) · 生命周期协调
- [`$gamedev-studio`](../../kit/skills/gamedev-studio/SKILL.md) · 工作室流程
- [`$gamedev-concepts`](../../kit/skills/gamedev-concepts/SKILL.md) · 可玩的概念
- [`$gamedev-preproduction`](../../kit/skills/gamedev-preproduction/SKILL.md) · 系统和生产规划
- [`$gamedev-assets`](../../kit/skills/gamedev-assets/SKILL.md) · 资源制作
- [`$gamedev-build`](../../kit/skills/gamedev-build/SKILL.md) · 玩法实现
- [`$gamedev-qa`](../../kit/skills/gamedev-qa/SKILL.md) · 质量审查
- [`$gamedev-release`](../../kit/skills/gamedev-release/SKILL.md) · 发布
- [`$gamedev-liveops`](../../kit/skills/gamedev-liveops/SKILL.md) · 持续运营

**Codex 专长角色**

- [`foundry-architecture`](../../agent-profiles/foundry-architecture.toml) · 架构
- [`foundry-backend`](../../agent-profiles/foundry-backend.toml) · 后端
- [`foundry-conversation`](../../agent-profiles/foundry-conversation.toml) · 对话
- [`foundry-cost`](../../agent-profiles/foundry-cost.toml) · 成本
- [`foundry-integrations`](../../agent-profiles/foundry-integrations.toml) · 集成
- [`foundry-judge`](../../agent-profiles/foundry-judge.toml) · 独立评判
- [`foundry-platform`](../../agent-profiles/foundry-platform.toml) · 目标平台
- [`foundry-privacy`](../../agent-profiles/foundry-privacy.toml) · 隐私
- [`foundry-product`](../../agent-profiles/foundry-product.toml) · 产品
- [`foundry-qa`](../../agent-profiles/foundry-qa.toml) · 质量
- [`foundry-reliability`](../../agent-profiles/foundry-reliability.toml) · 可靠性
- [`foundry-skeptic`](../../agent-profiles/foundry-skeptic.toml) · 批判性审查

完整目录列出所有技能的稳定名称和十二个角色。[完整目录](../CAPABILITIES.md#all-skills-and-roles) · [图解示例](../../marketing/zh-CN/README.md) · [其他语言](../../START_HERE.md#use-another-language)
