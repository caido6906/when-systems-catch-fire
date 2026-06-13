# When Systems Catch Fire / 点火

一个人类在好奇心的驱动下，借助 AI 做出的发现。
A discovery made by a human being, driven by curiosity and aided by AI.

## 入口 / Entrance

| 区域 / Area | 内容 / Content |
| --- | --- |
| [发现 / Discoveries](DISCOVERIES.md) | 从函数与案例的自举循环中产生的新发现。每条发现都可连接到相关函数、案例和来源。 / New discoveries generated from bootstrap cycles between functions and cases. Each discovery links to related functions, cases, and sources. |
| [函数表 / Functions](FUNCTIONS.md) | 470 条函数。每条函数都可查看定义、公式、来源与关联案例。 / 470 functions. Each function links to its definition, expression, source, and related cases. |
| [案例表 / Cases](CASES.md) | 578 个案例。每个案例都可查看内容、来源与关联函数。 / 578 cases. Each case links to its content, source, and related functions. |

## Current Structure / 当前结构

| Layer | 中文说明 | 主要文件 / Files |
| --- | --- | --- |
| Functions | 点火函数层，保存 D-X 函数及其结构化字段 | `data/functions/unified-functions.json`, `data/functions/unified-functions.jsonl`, `data/functions/items/` |
| Cases | 案例层，保存案例与函数关系 | `data/cases/unified-cases.json`, `data/cases/unified-cases.jsonl`, `data/cases/items/` |
| Discoveries | 新发现说明层，面向人类阅读和传播 | `DISCOVERIES.md`, `data/discoveries/unified-discoveries.json`, `data/discoveries/unified-discoveries.jsonl`, `docs/zh/discoveries/items/` |
| Registry | 原始统一总表，作为生成 JSON 的来源 | `data/registry/统一函数总表.csv`, `data/registry/统一案例总表.csv` |
| Legacy Book | 旧书籍结构，保留为历史材料 | `archive/book-legacy/` |
| Raw Notes | 原始笔记与来源材料，不作为 canonical item | `dianhuo/originals/` |

## For AI Agents / 给 AI Agent

1. Read `llms.txt`.
2. Read `AGENT_ENTRY.md`.
3. Use `data/functions/unified-functions.jsonl` for function lookup.
4. Use `data/cases/unified-cases.jsonl` for case lookup.
5. Use `data/discoveries/unified-discoveries.jsonl` for structured discovery entries.
6. Use `data/functions/items/*.json` and `data/cases/items/*.json` as canonical machine-readable records.

Do not treat raw notes as canonical. Raw notes are sources. Current structured entries live under `data/functions/`, `data/cases/`, and `data/discoveries/`.

## Human Reading / 人类阅读入口

- 中文函数入口 / Chinese functions: `FUNCTIONS.md`, `docs/zh/functions.md`
- 中文案例入口 / Chinese cases: `CASES.md`, `docs/zh/cases.md`
- 中文发现入口 / Chinese discoveries: `DISCOVERIES.md`, `docs/zh/discoveries/items/`
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
