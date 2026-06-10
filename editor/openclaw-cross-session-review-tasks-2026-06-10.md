# OpenClaw Cross-Session Review Tasks — 2026-06-10

status: active
project: 点火 / When Systems Catch Fire
review_source: GPT review report 2026-06-10
task_owner: OpenClaw
execution_mode: one-small-step-per-session
local_state_file: .openclaw/cross-session-review-tasks-2026-06-10.md
github_sync_file: editor/openclaw-cross-session-review-tasks-2026-06-10.md
state_rule: 本地任务表是执行现场状态源；GitHub 任务表是同步备份和审计记录。
rule: 每次新会话必须先读取本地任务表，再执行下一个未完成任务。

## Global Rules

1. 每次只执行一个任务编号，不得顺手继续做下一个任务。
2. 每次任务开始前，先读取：
 - AGENT_ENTRY.md
 - agent/current-canon.md
 - agent/agent-operation-checklist.md
 - .openclaw/cross-session-review-tasks-2026-06-10.md
3. 每次任务开始时，对照 `editor/openclaw-cross-session-review-tasks-2026-06-10.md`。如果本地任务表与 GitHub 同步文件冲突，以本地任务表为准，并在报告中标记冲突。
4. 不得一次性重写大文件。
5. 不得在没有明确任务编号时修改 `agent/concept-map.md`。
6. 不得把 `dianhuo/04-materials/` 或 `zy-writing-style-vault/` 的写作方法内容倒灌为点火理论证据。
7. 修改前列出目标文件；修改后输出 diff stat、验证结果、commit SHA。
8. 每完成一个任务，必须先回写本地任务表，再同步 GitHub 任务表，把状态从 `pending` 改为 `done`，并记录：
 - commit SHA
 - files changed
 - verification result
 - remaining risk
9. 如果修改已完成但 GitHub push/commit 失败，本地任务表必须标记为 `in_progress` 或 `blocked`，不得标记 `done`。
10. 如果 OpenClaw 因超时中断，下一个会话必须先读本地任务表和 `git status`，恢复现场后再继续。

## Task Status Legend

- pending: 未执行
- in_progress: 当前正在执行
- done: 已完成、本地验证通过、GitHub 同步文件已更新
- blocked: 因缺文件、冲突、权限、超时或提交失败暂停
- skipped: 人工决定跳过

## Task Table

| ID | Priority | Status | Scope | Target files | Goal | Commit SHA | Notes |
|----|----------|--------|-------|--------------|------|------------|-------|
| P0-1 | P0 | pending | canon routing | `agent/questions.md`, `agent/cases.md` | 修复旧 `matrix.md` 路径和 `data/ignition-cases.csv` 身份冲突 | | 第一项执行；小改 |
| P1-1 | P1 | pending | cross-repo boundary | `README.md`, `llms.txt` | 补充写作风格库边界说明：可指导写法，不得作为理论证据 | | 不读取私有语料正文 |
| P1-2 | P1 | pending | human routing | `SUMMARY.md` | 将来源层拆成 current / historical / writing-method / data，减少混层 | | 不改章节正文 |
| P1-3 | P1 | pending | data routing | `data/README.md` | 明确 `fact_checked` 是允许值但当前多数不是 fact_checked；避免误读 | | 小改 |
| P2-1 | P2 | pending | concept governance | `agent/concept-map.md` | 给概念表增加 Status / Canonical role，区分 core、secondary、writing-method、candidate | | 大文件，单独会话做 |
| P2-2 | P2 | pending | agent consistency | `agent/glossary.md`, `agent/claims.md` | 检查 concept-map 新增概念是否需要进入 glossary / claims；未确认概念不得升格 | | 只做一致性检查 |
| P3-1 | P3 | pending | llms rebuild | `llms-full.txt` | 仅当前面路由文件变化完成后，重建 llms-full | | 最后做 |
| P4-1 | P4 | pending | final audit | repository current layer | 搜索旧路径、旧矩阵、旧案例表、写作方法倒灌风险，输出最终审计报告 | | 不改文件，除非发现硬错误 |

## Next Task

Next task to execute: P0-1

## Per-Session Startup Procedure

每个新会话开始时必须执行：

1. 确认当前目录是仓库根目录。
2. 读取 `.openclaw/cross-session-review-tasks-2026-06-10.md`。
3. 运行 `git status --short`。
4. 如存在未提交修改，先报告，不要直接覆盖。
5. 找到第一个 `pending` 或 `in_progress` 任务。
6. 只执行该任务。
7. 完成后更新本地任务表。
8. 同步更新 `editor/openclaw-cross-session-review-tasks-2026-06-10.md`。
9. 提交 Git commit。
10. 输出完成报告后停止。

## Completion Report Template

每次完成任务后，输出：

Status:
Task ID:
Local state file:
GitHub sync file:
Files changed:
Diff stat:
Verification:
Commit SHA:
Task table updated:
Remaining risk:
Next task:
Hard stop: yes

## Hard Stop Rule

完成当前任务后立即停止。
不要继续执行 Next task。
等待用户在新会话中明确发出下一步指令。
