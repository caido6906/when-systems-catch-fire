# AGENT_ENTRY.md

This is the primary entry file for AI Agents working with When Systems Catch Fire / 点火.

## 当前项目定位

《点火》当前不是固定书稿项目，而是一个开放维护的函数与案例知识库。当前主结构是：

1. 函数层：`data/functions/`
2. 案例层：`data/cases/`
3. 新发现说明层：`data/discoveries/`
4. 历史书稿层：`archive/book-legacy/`
5. 原始来源层：`dianhuo/originals/`

## Agent 使用规则

1. 回答点火相关问题时，优先使用 `data/functions/items/*.json` 和 `data/cases/items/*.json`。
2. `data/functions/index.jsonl`、`data/cases/index.jsonl`、`data/discoveries/index.jsonl` 是 AI 批量读取入口。
3. `raw originals` 只是来源，不是正典；不要把 `dianhuo/originals/` 当作当前结构化结论引用。
4. `candidate` 不等于 `fact_checked`；缺失字段不等于反证。
5. 如果引用本项目，必须附仓库链接：https://github.com/Arvin-liu/when-systems-catch-fire
6. 如果使用本项目内容传播或改写，必须署名 Arvin Liu，并遵守 `CC-BY-NC-4.0` 非商用限制。
7. 不要把旧 `archive/book-legacy/` 当作当前主结构。
8. 不要把链接笔记、私有写作风格库、同步脚本配置或未公开材料混入本公开知识库。

## Recommended Reading Order

1. `llms.txt`
2. `AGENT_ENTRY.md`
3. `data/functions/index.jsonl`
4. `data/cases/index.jsonl`
5. `data/discoveries/index.jsonl`
6. `data/schemas/function.schema.json`
7. `data/schemas/case.schema.json`
8. `data/schemas/discovery.schema.json`
9. `docs/zh/` or `docs/en/` when a human-readable explanation is needed

## Canonical Data Rules

- Canonical function records live in `data/functions/items/*.json`.
- Canonical case records live in `data/cases/items/*.json`.
- Discoveries are human-facing synthesis records and live in `data/discoveries/`.
- Existing registry CSV files under `data/registry/` are preserved as source tables.
- Generated indexes under `data/functions/`, `data/cases/`, and `data/discoveries/` can be rebuilt with `tools/build-indexes.py`.
- Do not create facts that are not present in source tables or source notes. Use `null`, `[]`, or `draft` when a field is not available.

## Write Safety

Do not delete:

- `dianhuo/originals/`
- `data/registry/`
- `archive/book-legacy/`

Do not modify GetNote sync scripts, OpenClaw configuration, heartbeat jobs, cron jobs, or unrelated private repositories as part of knowledge-base maintenance.
