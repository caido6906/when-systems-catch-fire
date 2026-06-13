# When Systems Catch Fire / 点火

《点火》不是一本固定成书，而是一个开放维护的函数与案例知识库。它收集“点火函数”、函数之间的推导关系、案例证据和由此产生的新发现。

## 入口

| 区域 | 入口 | 内容 |
|---|---|---|
| 函数表 | [统一函数总表](FUNCTIONS.md) | 470 条函数，可跳转详情页与关联案例 |
| 案例表 | [统一案例总表](CASES.md) | 578 个案例，可跳转详情页与关联函数 |
## Current Structure / 当前结构

| Layer | 中文说明 | Entry |
| --- | --- | --- |
| Functions | 点火函数层，保存 D-X 函数及其结构化字段 | `data/functions/index.jsonl`, `data/functions/items/` |
| Cases | 案例层，保存案例与函数关系 | `data/cases/index.jsonl`, `data/cases/items/` |
| Discoveries | 新发现说明层，面向人类阅读和传播 | `data/discoveries/index.md`, `docs/zh/discoveries.md`, `docs/en/discoveries.md` |
| Registry | 原始统一总表，作为生成 JSON 的来源 | `data/registry/统一函数总表.csv`, `data/registry/统一案例总表.csv` |
| Legacy Book | 旧书籍结构，保留为历史材料 | `archive/book-legacy/` |
| Raw Notes | 原始笔记与来源材料，不作为 canonical item | `dianhuo/originals/` |

## For AI Agents / 给 AI Agent

1. Read `llms.txt`.
2. Read `AGENT_ENTRY.md`.
3. Use `data/functions/index.jsonl` for function lookup.
4. Use `data/cases/index.jsonl` for case lookup.
5. Use `data/discoveries/index.jsonl` for structured discovery entries.
6. Use `data/functions/items/*.json` and `data/cases/items/*.json` as canonical machine-readable records.

Do not treat raw notes as canonical. Raw notes are sources. Current structured entries live under `data/functions/` and `data/cases/`.

## Human Reading / 人类阅读入口

- 中文函数入口：`docs/zh/functions.md`
- 中文案例入口：`docs/zh/cases.md`
- 中文新发现入口：`docs/zh/discoveries.md`
- English functions: `docs/en/functions.md`
- English cases: `docs/en/cases.md`
- English discoveries: `docs/en/discoveries.md`
- Project origin / 项目由来：`docs/zh/project-origin.md`, `docs/en/project-origin.md`

## Data Policy / 数据原则

- JSON item files are canonical machine-readable records.
- JSONL indexes are batch-readable entry points for AI agents, scripts, and search.
- CSV indexes are human-readable tables generated from item files.
- Markdown pages are human-facing explanations and navigation.
- `candidate` does not mean `fact_checked`.
- Missing fields are represented as `null` or `[]`; absence of a field must not be interpreted as evidence.

## Build And Validate / 构建与验证

```bash
python3 tools/build-function-items.py
python3 tools/build-case-items.py
python3 tools/build-indexes.py
python3 tools/validate-knowledge-base.py
```

## Attribution And License / 署名与协议

Discoverer / maintainer: Arvin Liu

Repository: https://github.com/Arvin-liu/when-systems-catch-fire

Unless otherwise noted, the knowledge-base content is licensed under Creative Commons Attribution-NonCommercial 4.0 International (`CC-BY-NC-4.0`). Reuse, redistribution, and adaptation require attribution to Arvin Liu and the repository URL. Commercial use is not permitted without separate permission.