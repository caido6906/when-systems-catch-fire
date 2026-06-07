# Agent Operation Checklist

status: current
purpose: Operational checklist for AI Agents working with this repository.

## Before editing

1. Read `AGENT_ENTRY.md`.
2. Read `agent/current-canon.md`.
3. Read `llms.txt`.
4. Identify whether the task is:
 - content update
 - canon migration
 - source preservation
 - case fact-check
 - book-layer rewrite
 - data update
 - archive cleanup
 - audit only
5. Identify the current layer, source layer, and archive layer affected by the task.
6. Do not edit stable files until the target layer is clear.

## During editing

1. Preserve old versions under `archive/` when replacing stable files.
2. Add metadata to archived files.
3. Keep current files free of superseded conclusions.
4. Keep source files traceable.
5. Do not silently rewrite old history.
6. Do not promote working hypotheses to facts.
7. Do not rebuild book narrative before evidence status is clear.
8. If routing changes, update all entry points.

## Required files to check after canon changes

- `agent/current-canon.md`
- `README.md`
- `SUMMARY.md`
- `llms.txt`
- `llms-full.txt`
- `agent/book-summary.md`
- `agent/concept-map.md`
- `agent/claims.md`
- `data/README.md`
- relevant CSV files under `data/`
- relevant files under `archive/`
- relevant files under `dianhuo/`

## Residue scan

Before completion, search for old or superseded phrases, paths, and conclusions.

For the 2026-06-07 canon migration, examples include:

- `24格矩阵精度足够`
- `覆盖全部67个案例`
- `没有遗漏也没有冗余`
- `第七维度`
- `第四个关键变量`
- `all-cases-71.md` as current
- `ignition-cases-event-framework-2026-06-06.csv` as current
- old `data/ignition-cases.csv` as canonical
- old paths that were moved to `archive/`

Residue may remain in `archive/` or clearly marked historical sections.

Residue must not appear as current conclusion in:

- `book/`
- `agent/`
- `data/ignition-cases.csv`
- `README.md`
- `SUMMARY.md`
- `llms.txt`
- `llms-full.txt`

## Completion report template

When reporting completion, use this structure:

```text
Status:
Commit range:
Files changed:
Current layer checked:
Source / historical layer checked:
Archive layer checked:
llms-full rebuilt:
Residue scan:
Remaining uncertainty:
Next recommended task:
```

## Hard rule

A repository update is not complete when files have merely been changed.

It is complete only when the current reading path, historical preservation path, and Agent-readable routing path all agree.
