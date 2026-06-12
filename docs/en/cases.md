# Cases

The case layer is the second structured entry for When Systems Catch Fire. Each case has one canonical JSON file with its ID, Chinese title, summary, case type, related functions, source notes, and evidence level.

Primary entries:

- `data/cases/index.jsonl`
- `data/cases/index.csv`
- `data/cases/index.md`
- `data/cases/items/*.json`

Case JSON files are generated from `data/registry/统一案例总表.csv`. Existing stable IDs are preserved. Temporary IDs are not renumbered automatically.
