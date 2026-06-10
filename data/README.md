# Data Layer

## Canonical case table

Current canonical case table:

- `data/ignition-cases.csv`

This file mirrors the 2026-06-07 Event Condition Matrix case table.

Source:

- `data/ignition-cases-event-condition-matrix-2026-06-07.csv`
- `dianhuo/03-evidence/cases/all-cases-event-condition-matrix-2026-06-07.md`

## Case status

Most case entries are not fact-checked conclusions.

Valid status values:

- `working_hypothesis`
- `validation_hypothesis`
- `prediction`
- `boundary`
- `fact_checked`

Note: `fact_checked` is a reserved/promoted status. Do not assume the current table contains fact-checked cases unless the specific row is marked `fact_checked` and links to evidence.

No case should be cited as completed proof unless its status is `fact_checked`.

## Deprecated data

Deprecated or historical data files are stored under:

- `archive/data/`
