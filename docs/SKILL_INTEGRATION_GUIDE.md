# Maestro Agent: Anthropic Skill 集成指南 (Phase 1)

## 📌 什么是 Anthropic Agent Skill？

**Agent Skill** (或者叫 Claude Skill) 是 Anthropic 在 2025 年初提出并广泛应用的一种 Agent 开发范式。它的核心思想是：**“数据驱动指令”取代“硬编码流程”**。

在过去，如果我们想让一个 AI Agent 学会“如何进行深度的代码审查 (Code Review)” 或 “如何写高转化率的营销文案”，我们往往需要在后端的 Python 代码（比如节点路由或 prompt 模板中）硬编码大量的规则。当 Agent 需要的能力越多，系统提示词（System Prompt）就越长、架构也越难以维护。

**Skill (技能)** 的机制是：
- 我们可以将特定任务（如代码审查）的所有提示词、规则、限制条件、甚至依赖的其他外部工具提取出来，独立成一个模块化的“文件夹”。
- 每个文件夹通常包含一个标准的 **`SKILL.md`** 文件（甚至还有同级的辅助脚本或配置文件）。
- 这个 `.md` 文件的头部使用了 YAML 格式（Frontmatter）来申明技能的名称、描述等元数据；正文则是详尽的 Markdown 即自然语言指令。

**系统运行方式：**
在需要时，我们的系统（如 `intentrouter` 路由节点）只需判定当前任务需要哪些“Skill”，然后自动将这段长指令**热加载**（注入）进 Agent 的 System Prompt 中。Agent 就会暂时“掌握”这份技能并按规章办事。

---

## 🏗️ 架构设计图

```text
┌───────────────── 用户输入 ──────────────────┐
│ 用户: "帮我 review 这个路由文件代码..."     │
└──────────────────────┬────────────────────────┘
                       │
             ┌─────────▼─────────┐
             │ Intent Router 节点 │ ─── 判断出需要 Code Review 技能
             └─────────┬─────────┘      
                       │ (1. 解析意图，标记技能)
                       ▼
             ┌─────────────────────────┐     【磁盘文件】
             │    Skill Registry       │ ──> skills/code-reviewer/SKILL.md
             │ (技能解析与管理注册中心) │      (抓取 YAML + 指令文本)
             └─────────┬─────────┘
                       │ (2. 组装后的技能指令块)
                       ▼
             ┌─────────────────────────┐
             │       AgentState        │ ──> 注入字段 `skill_instructions` 
             │   (LangGraph 状态总线)  │
             └─────────┬─────────┘
                       │ (3. 携带技能文本流转)
                       ▼
             ┌─────────────────────────┐
             │   Tool Agent / Executor │ 
             │  动态组装 System Prompt │  ──> System Prompt 首部增加：
             └─────────────────────────┘      "# 加载的技能指令参考：..."
```

---

## 🛠️ Phase 1 具体开发步骤详解

### 1. 规范技能目录结构 (`skills/`)
在项目根目录下创建一个统一的 `skills` 目录。我们用一个示例代码审查技能来验证机制：

```text
maestro-agent/
  ├── skills/
  │   ├── code-reviewer/
  │   │   └── SKILL.md
```
`SKILL.md` 的内容长这样：
```markdown
---
name: code-reviewer
description: 专门用于深度代码评审和漏洞检测的高级技能。
version: 1.0.0
---
# 代码审查指南
请始终遵循以下规则：
1. 先检查基础语法和内存泄漏问题。
2. 指出优化点，但是尽量少做侵入性修改。
3. 如果遇到 Python 代码，着重检查异步 asyncio 并发情况。
...（其他规则）...
```

### 2. 构建解析器 (`intentrouter/skills/skill_registry.py`)
Python 需要读懂 `SKILL.md` 并剥离出顶部的 YAML `---` 部分。我们需要编写一个注册器。
- **作用：** 提供类似 `get_skill(name="code-reviewer")` 的函数。
- **返回值：** 返回一个包含了技能元数据（Metadata）以及纯文本指令（Content）的 Python `Dict` 或 Pydantic 对象。

### 3. AgentState 改造 (`intentrouter/graph/state.py`)
在 LangGraph 图的共享状态字典中，我们增加状态字段：
```python
class AgentState(MessagesState):
    # ... 其他原有属性不变 ...
    active_skills: list[str]            # 当前挂载的技能名列表 (如: ["code-reviewer"])
    skill_instructions: str             # 从 registry 中拉取出的全部文本，准备发给大模型
```

### 4. 节点更新 (比如 `executor` 或 `tool_agent`)
在大模型生成最终回复前，检查 `state.get("skill_instructions")` 是否有值。如果有，将这段文本放置在 Prompt 的最顶部（或紧挨着 System 设定的下方），以最高优先级让 LLM 贯彻执行。

---

## 🚀 为什么这值得做？（长远收益）

除了彻底解耦和方便维护，这一标准还能：
1. **拥抱社区生态**：你可以直接把别人利用 Anthropic 标准写好的优质 `SKILL.md` 拷贝到你的文件夹下，你的 Agent 立马学会神级能力（例如 GitHub 官方操作技能库）。
2. **实现技能自我进化**：后续的 Phase 2 中，我们可以加一个节点，专门监控“执行经常出错”的环节，并自动修改维护对应的 `SKILL.md` 文件。系统运行越久越聪明。

准备好进入 **Phase 1** 把它实现出来了吗？
