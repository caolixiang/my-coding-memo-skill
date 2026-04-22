# My Coding Memo Skill

[English](#english) | [中文](#中文)

<a id="english"></a>
## English Version

This is a **project-agnostic memo and phase-based planning workflow** plugin/skill designed for coding agents (such as Claude, Codex, etc.). Its core objective is to introduce a reusable, file-based persistent state tracking and planning constraint mechanism into any code repository.

By integrating this workflow into your project, you can enable AI coding assistants to work in a more organized, phased, and documented manner. This ensures that work state can be seamlessly restored when context is truncated or when starting a new conversation.

### Core Mechanism

The core constraints of this workflow are implemented entirely through plain text files in the repository. Even without using the bundled helper scripts, the workflow functions perfectly as long as these file conventions are followed:

- **`AGENTS.md` / `CLAUDE.md`**: Establishes global behavioral guidelines for the AI assistant in the project root, enforcing a "phase-based" workflow and strict file reading/writing requirements.
- **`docs/plan/TEMPLATE.md`**: The phase-based plan template. It includes mandatory structures such as "Today's Goals", "Phase Plan", "Test Log", and "Commit Log".
- **`docs/memo/TEMPLATE.md`**: The activity memo template. Used to record specific action items and change summaries in chronological order.
- **`docs/plan/YYYYMMDD.md`** and **`docs/memo/YYYYMMDD.md`**: The daily workflow documents, generated based on the current date (incorporating the user's timezone).

### Workflow Rules

After introducing this workflow, the AI assistant will follow these core principles:
1. **Phased Execution**: Tasks are broken down into numbered phases. The AI will not start the next phase until the current phase is verified and the code is committed.
2. **One Commit Per Phase**: After each phase is completed, a code commit is created (unless explicitly rejected by the user).
3. **Delayed Document Commit (Rollover)**: The plan and memo files updated today are not committed alongside the code changes. Instead, they are bundled and archived in a dedicated Docs-only commit **before writing new code on the next workday**.
4. **State Restoration**: When starting a new conversation or losing state due to context compression, the AI is forced to first read the latest plan and memo files to restore context.

### Usage

For agents with terminal execution capabilities and support for a Skills plugin mechanism (such as Codex, Claude Agent, etc.), you can run scripts to automate the workflow state maintenance.

1. **Install Skill**: Copy the `skills` folder from this project to the global configuration or project-specific skill directory of your corresponding agent.
   - **Global Installation Example**: Place it in the `~/.codex/skills/` or `~/.claude/skills/` directory.
   - **Project-Level Installation Example**: Place it in the `/path/to/my_project/.codex/skills/` or `/path/to/my_project/.claude/skills/` directory.
   > [!NOTE]
   > After copying, for clients like Codex, **you need to restart the application** to reload the skill list.
2. **Invoke via Prompt**:
   - **Codex Invocation**: Use the exclusive command starting with `$`, e.g., input `$my-coding-memo-skill` directly in the chat.
   - **Claude Invocation**: Use natural language prompts, e.g., input `"Run my-coding-memo-skill"`.
3. **Automated Execution**: Because skills are universal, the agent will automatically recognize and call the built-in Python scripts within this Skill:
   - Automatically execute `install_workflow.py` (for Claude, it will also automatically update/generate `CLAUDE.md`) to install or repair templates.
   - Automatically execute `prepare_day.py` to create today's plan/memo files.
   - Automatically read the latest historical context, report the current plan progress to you, and seamlessly enter the day's code development.

### Directory Structure

```text
skills/
├── SKILL.md                          # Skill description and core usage guide
├── references/
│   └── workflow-spec.md              # Detailed workflow contract specifications, rules, and template requirements
├── agents/
│   └── openai.yaml                   # Metadata and default prompt for OpenAI Agent
└── scripts/
    ├── install_workflow.py           # Workflow initialization script
    ├── prepare_day.py                # Daily work environment preparation script
    ├── workflow_common.py            # Common functions, timezone parsing, and default Markdown templates
    └── claude-memory-template.md     # Instruction block template to be inserted into CLAUDE.md
```

### Notes

- The modifications made by this tool's scripts are highly **idempotent** and can be safely executed multiple times.
- This tool is designed to respect the repository's existing documents. By default, it **will not overwrite** Plan / Memo templates that the user has modified, nor will it break non-workflow content in the existing `AGENTS.md`.

---

<a id="中文"></a>
## 中文版

这是一个为编程智能体（Coding Agents，如 Claude, Codex 等）设计的**项目无关（Project-Agnostic）的备忘录与阶段性计划工作流**插件/技能。它的核心目标是为任何代码仓库引入一套可复用的、基于文件的持久化状态跟踪和计划约束机制。

通过在项目中引入该工作流，你可以让 AI 编程助手以更有条理、有阶段性、有记录的方式开展工作，确保在对话上下文截断或开启新对话时，工作状态得以无缝恢复。

### 核心机制

本工作流的核心约束完全基于代码仓库中的纯文本文件实现。即使不使用配套的辅助脚本，只要遵循这些文件规范，工作流依然可以正常运转：

- **`AGENTS.md` / `CLAUDE.md`**：在项目根目录约定 AI 助手的全局行为准则，强制执行基于“阶段（Phase）”的工作流和严格的文件读写要求。
- **`docs/plan/TEMPLATE.md`**：阶段性计划模板。包含了“今日目标”、“阶段计划”、“测试记录”、“提交记录”等强制结构。
- **`docs/memo/TEMPLATE.md`**：活动备忘录模板。用于按时间顺序记录具体的操作项和变更总结。
- **`docs/plan/YYYYMMDD.md`** 和 **`docs/memo/YYYYMMDD.md`**：每日的具体工作流文档，基于当天的日期（结合用户所在时区）生成。

### 工作流规则

引入本工作流后，AI 助手将遵循以下核心原则工作：
1. **阶段性执行**：将任务拆分为编号阶段（Phases）进行，在当前阶段通过验证并提交代码前，不开启下一阶段。
2. **每次阶段一提交**：每个阶段完成后，进行一次代码 Commit（除非用户明确拒绝）。
3. **延迟的文档 Commit (Rollover)**：当天更新的 plan 和 memo 文件不在包含代码变更的 commit 中提交；而是在**下一个工作日**开始写新代码之前，进行一次专属的 Docs-only commit 进行打包归档。
4. **状态恢复**：在开启新对话或因上下文压缩导致状态丢失时，AI 会被强制要求首先读取最新的 plan 和 memo 文件以恢复上下文。

### 使用方式

对于具备终端执行能力、且支持 Skills 插件机制的智能体（如 Codex, Claude Agent 等），可以直接运行脚本来自动化维护工作流状态。

1. **安装 Skill**：将本项目的 `skills` 文件夹复制到该智能体对应的全局配置，或某个具体项目的特定技能目录中。
   - **全局安装示例**：放入 `~/.codex/skills/` 或 `~/.claude/skills/` 目录。
   - **项目级安装示例**：放入 `/path/to/my_project/.codex/skills/` 或 `/path/to/my_project/.claude/skills/` 目录。
   > [!NOTE]
   > 复制完成后，对于 Codex 等客户端，**需要重启软件**才能重新加载技能列表。
2. **通过 Prompt 唤醒**：
   - **Codex 唤醒方式**：在对话中直接使用 `$` 开头的专属指令，输入 `$my-coding-memo-skill`。
   - **Claude 唤醒方式**：直接通过自然语言提示，例如输入 `"运行 my-coding-memo-skill"` 或 `"Run my-coding-memo-skill"`。
3. **自动执行**：由于 Skills 是通用的，智能体会自动识别并调用该 Skill 下内置的 Python 脚本：
   - 自动执行 `install_workflow.py`（针对 Claude 也会自动更新/生成 `CLAUDE.md`）来安装或修复模板。
   - 自动执行 `prepare_day.py` 创建当天的 plan/memo 文件。
   - 自动读取最新的历史上下文，并向你汇报当前的计划进度，随后便可无缝进入当天的代码开发。

### 目录结构

```text
skills/
├── SKILL.md                          # 技能描述与核心使用指南
├── references/
│   └── workflow-spec.md              # 详尽的工作流契约规范、规则与模板要求
├── agents/
│   └── openai.yaml                   # 针对 OpenAI Agent 的元数据和默认 Prompt
└── scripts/
    ├── install_workflow.py           # 工作流初始化脚本
    ├── prepare_day.py                # 每日工作环境准备脚本
    ├── workflow_common.py            # 公共函数、时区解析与默认 Markdown 模板
    └── claude-memory-template.md     # 供 CLAUDE.md 插入的指令块模板
```

### 注意事项

- 此工具脚本的修改行为具有良好的**幂等性**，可以安全地多次执行。
- 此工具设计尊重原仓库的既有文档，默认**不会覆盖**用户自己二次修改过的 Plan / Memo 模板，也不会破坏原有的 `AGENTS.md` 中的非本工作流内容。
