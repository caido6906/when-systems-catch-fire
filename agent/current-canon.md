# Current Canon / 当前主版本

status: current-routing-map
updated_at: 2026-06-07
project: 点火 / When Systems Catch Fire

## 当前框架版本

当前框架版本为 2026-06-07 事件条件矩阵版。

当前主框架文件：

- `dianhuo/02-framework/event-condition-matrix-2026-06-07.md`
- `dianhuo/02-framework/proposer-posture-secondary-variable-2026-06-07.md`
- `dianhuo/02-framework/event-scale-matrix.md`
- `data/event-scale-matrix.csv`

## 当前核心结论

1. 事件尺度 = 参与者规模 × 持续时间。
2. 文明、国家、政策、公司、人际不是第一性分类，而是尺度矩阵中的常见区域标签。
3. 8 格矩阵是事件条件矩阵，不是总矩阵。
4. 应约者状态是事件走向的结果变量，不再作为条件变量。
5. 提议者姿态，即推方案 / 备方案，是事件条件矩阵内的次级变量，不是独立新维度。
6. 案例表目前仍是 working hypothesis / validation hypothesis / prediction / boundary，不是完成史实证明。

## 当前案例表

当前主案例表为：

- `data/ignition-cases.csv`
- `data/ignition-cases-event-condition-matrix-2026-06-07.csv`
- `dianhuo/03-evidence/cases/all-cases-event-condition-matrix-2026-06-07.md`

补充验证案例为：

- `data/ignition-supplemental-cases-event-condition-matrix-2026-06-07.csv`
- `dianhuo/03-evidence/cases/supplemental-cases-event-condition-matrix-2026-06-07.md`

## 历史材料与被取代材料

以下文件只能作为来源追溯或思想演化材料，不得作为当前结论直接引用：

- `archive/framework/matrix-24cell-superseded-2026-06-07.md` 中的 24 格矩阵、67 案例无遗漏无冗余等旧结论。
- `data/ignition-cases.csv` 的旧 16 行窄表版本。
- `data/ignition-cases-event-framework-2026-06-06.csv`
- `dianhuo/03-evidence/cases/all-cases-71.md`
- `dianhuo/01-manuscript/book.md`

## 使用规则

AI Agent 回答、整理、引用、改写本仓库内容时，应优先使用：

1. `agent/current-canon.md`
2. `book/`
3. `agent/`
4. `data/ignition-cases.csv`
5. 2026-06-07 事件条件矩阵相关文件

`dianhuo/` 中未被本文件列为 current 的内容，只作来源追溯、历史演化、证据补充或旧稿保存使用。

## 理论校验层 / Theory Review Layer

`theory/` 目录是点火框架的理论校验层、边界层、反例层和审稿层。它用于约束、审查、压缩和反驳当前框架，但不直接替代当前主框架文件。

当前主框架仍以：

- `agent/current-canon.md`
- `dianhuo/02-framework/event-condition-matrix-2026-06-07.md`
- `dianhuo/02-framework/proposer-posture-secondary-variable-2026-06-07.md`
- `data/ignition-cases.csv`

为准。

`theory/` 下文件的使用规则是：

- 可以用于判断框架边界、反例、竞争解释、尺度限制；
- 不得把 `theory/` 中的假说、审稿意见、反例条目直接写成框架结论；
- 若 `theory/` 与主框架冲突，应标记为「待修正冲突」，而不是直接覆盖主框架。

## 层级关系总表

| 层级 | 路径 | 规则 |
|------|------|------|
| 主框架层 | `book/`, `agent/`, `data/` | 可被引用的当前理论内容 |
| 框架定义层 | `dianhuo/02-framework/` | 框架定义来源，以 current-canon 指定为准 |
| 理论校验层 | `theory/` | 边界、反例、竞争理论、尺度声明；不得替代主框架 |
| 书稿写作方法论层 | `dianhuo/04-materials/`, `dianhuo/01-manuscript/` | 叙写策略、风格锚点；不得作为理论证据 |
| 项目元记录层 | `editor/` | 发布状态、迁移说明、操作协议；不得作为理论证据 |
| 原文暂存层（入口层） | `dianhuo/originals/` | 未经审阅的原始笔记、来源摘录；不得直接作为主框架结论；等待 GPT 审阅 |
| 已处理历史数据层（追溯层） | `dianhuo/source-history/` | 已被 GPT 审阅、Pro 提炼或确认无需提炼的原文；不得重复提炼；不得直接作为当前结论引用 |
| 历史归档层 | `archive/` | 已淘汰的旧版本；不得作为当前主结论 |

### 双层结构规则

参见 `AGENT_ENTRY.md` 中的「双层结构规则」与「三 Agent 流水线规则」。

**Flash 权限边界**：只允许写入 `dianhuo/originals/`。不得修改主框架层、理论校验层、当前正典层、已处理历史数据层。

**GPT 审阅位置**：`dianhuo/originals/` 中的材料。

**Pro 提炼与归档规则**：只在 GPT 给出提炼意见后执行。完成提炼后必须将原文移动到 `dianhuo/source-history/`。

**已处理原文不得重复提炼**：`dianhuo/source-history/` 中的文件不具有 `status: raw-inbox` 或 `processed_status: unprocessed`，不得被当成未处理原文再次提炼。

**引用限制**：`dianhuo/originals/` 和 `dianhuo/source-history/` 都不得直接作为当前结论引用。
