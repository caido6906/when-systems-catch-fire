---
canonical: false
status: repo-map
use_rule: 仓库地图与层级路由说明；不得替代 current-canon、稳定风格画像或主框架文件。
---
# Repository Map / 仓库地图

## 层级路由表

| 层级 | 路径 | 引用规则 |
|------|------|----------|
| 当前正典层 | `book/`, `agent/current-canon.md`, `data/ignition-cases.csv` | 可被引用的当前理论内容 |
| 框架定义层 | `dianhuo/02-framework/` | 以 current-canon 指定为准 |
| 理论校验层 | `theory/` | 边界、反例、竞争理论；不得替代主框架 |
| 案例/证据材料层 | `dianhuo/03-evidence/` | 以 current-canon 指定为准 |
| **原文暂存层（入口层）** | `dianhuo/originals/` | ⚠️ 入口层，不得直接作为当前主框架结论引用；等待 GPT 审阅 |
| **已处理历史数据层（追溯层）** | `dianhuo/source-history/` | ⚠️ 仅供追溯，不得重复提炼，不得直接作为当前结论引用 |
| 写作方法论层 | `dianhuo/04-materials/`, `dianhuo/01-manuscript/` | 不得作为理论证据 |
| 项目元记录层 | `editor/` | 不得作为理论证据 |
| 历史归档层 | `archive/` | 不得作为当前结论引用 |

## Agent 流水线权限图

```
Flash  ──→  dianhuo/originals/   (只写入，不改写，不提炼)
GPT    ──→  审阅意见             (给提炼意见，不直接写入仓库)
Pro    ──→  提炼结果 + 移动原文到 dianhuo/source-history/
```

## 流水线规则

1. **Flash**：只允许将新原文导入 `dianhuo/originals/`。不改写、不提炼、不归类为理论结论、不修改主框架层/理论校验层/当前正典层/已处理历史数据层。导入完成后只输出导入报告，等待 GPT 审阅。
2. **GPT**：审阅 `dianhuo/originals/` 中的材料，给出是否可提炼、提炼方向、注意事项。不能在没有 Pro 时自行执行结构化提炼与归档。
3. **Pro**：只在 GPT 给出提炼意见后，对原文暂存层中的材料进行结构化提炼。完成提炼后，必须把对应原文移动到 `dianhuo/source-history/`，并在 frontmatter 中写明 `derived_to`。不得把原文层中的强判断直接写成当前结论。

## 入口文件优先级

1. AGENT_ENTRY.md
2. agent/current-canon.md
3. README.md
4. llms.txt
5. agent/repo-map.md（本文件）

updated_at: 2026-06-08
