# Functions

The function layer is the primary structured entry for When Systems Catch Fire. Each ignition function has one canonical JSON file with its original ID, normalized ID, Chinese title, source note, status, relation links, and explicit placeholders for missing fields.

Primary entries:

- `data/functions/index.jsonl`
- `data/functions/index.csv`
- `data/functions/index.md`
- `data/functions/items/*.json`

Function JSON files are generated from `data/registry/统一函数总表.csv`. Missing source fields remain `null` or `[]`.
