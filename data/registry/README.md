# Operational Registry

This directory contains **operational registries** for incremental extraction from GetNote raw originals.

## Positioning

> ⚠️ **Not current canon.** These are **operational registries** — extracted from raw notes, de-duplicated, traceable to source. Do NOT treat registry entries as canonical conclusions.

`统一函数总表.csv` 是当前 D-X 函数层入口。
`统一案例总表.csv` 是当前案例层入口。
它们是 operational registry，不等于全部 canonical。
状态字段为 `candidate` / `working_hypothesis` / `needs_review` / `fact_checked` 等。
不得默认把 `candidate` 当事实核验完成。

## Files

| File | Purpose |
|------|---------|
| `ignition-function-registry.csv` | Functions, function tables, input-output rules extracted from raw notes (legacy/compatibility) |
| `ignition-case-registry.csv` | Cases, tags, and framework mappings extracted from raw notes (legacy/compatibility) |
| `统一函数总表.csv` | High-frequency unified function table — notes titled "统一函数总表" only |
| `统一案例总表.csv` | High-frequency unified case table — notes titled "统一案例总表" only |
| `processed-notes.jsonl` | Deduplication index — which raw notes have been processed |
| `README.md` | This file |

## High-frequency sync path: Unified function/case tables

The high-frequency heartbeat task only routes notes whose title explicitly contains `统一函数总表` or `统一案例总表` into structured tables.

- `统一函数总表` → `data/registry/统一函数总表.csv`
- `统一案例总表` → `data/registry/统一案例总表.csv`
- All other notes → raw-only sync, no registry extraction

This design supports 5–15 minute high-frequency sync: GetNote brain generates dedicated unified table notes, OpenClaw handles local incremental merge, dedup, source tracing, and pushes to GitHub.

The old English registry files are retained as a historical compatibility layer and are NOT the high-frequency sync primary path.

## How to update

Run the extractor script:

```bash
cd /workspace/when-systems-catch-fire
python3 tools/extract-registry.py --repo-root . --notes-dir dianhuo/originals --verbose
```

The script:
1. Reads `processed-notes.jsonl` to find unprocessed files
2. Only processes files whose sha256 has changed
3. Extracts functions and cases conservatively
4. Appends new entries, merges by func_id/case_name
5. Never deletes or overwrites existing data

## Extraction rules

### Functions
- Keywords: "函数", "函数表", "输入", "输出", "规则", "判断", "D-X"
- Preserves original function numbering (e.g., D-X16)
- Unknown inputs/outputs → field empty, status `needs_review`

### Cases
- Keywords: "案例", "政策", "公司", "国家", "事件", "监管", "财政", "改革", "制度"
- Unknown framework location → `unknown`
- Default verification_status → `working_hypothesis` or `unknown` (never `fact_checked`)

## Status values

| Value | Meaning |
|-------|---------|
| `candidate` | Extracted but not yet reviewed |
| `active` | Reviewed and accepted |
| `merged` | Merged into current canon (external tracking) |
| `needs_review` | Insufficient info, needs human review |
| `rejected` | Determined not applicable |

## Safety guarantees

- ✅ Only appends/merges to CSVs
- ✅ Never rewrites existing canonical tables
- ✅ Never modifies `agent/current-canon.md`, `agent/claims.md`, `agent/glossary.md`
- ✅ Never modifies `data/ignition-cases.csv`
- ✅ Failed extraction does not affect raw note sync
- ✅ Idempotent: re-running on already-processed files is a no-op
