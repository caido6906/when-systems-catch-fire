# Agent Operation Protocol Update 2026-06-07

## Reason

The previous canon cleanup revealed that the repository needed stricter Agent operation rules.

The issue was not only file content residue, but insufficient operational protocol for canon migration, routing updates, post-change verification, and completion claims.

## Changes

- Added Canon Migration Protocol to `AGENT_ENTRY.md`.
- Added Post-change Verification Checklist to `AGENT_ENTRY.md`.
- Added Completion Claim Rule to `AGENT_ENTRY.md`.
- Added Current Layer Protection Rule to `AGENT_ENTRY.md`.
- Added `agent/agent-operation-checklist.md`.
- Updated `llms.txt`.
- Rebuilt `llms-full.txt`.

## Expected effect

Future Agents should not claim a canon migration is complete unless:

1. current routing is clean,
2. historical files are preserved but isolated,
3. Agent-readable entry points agree,
4. `llms-full.txt` is rebuilt when routing changes,
5. residue scan has passed,
6. remaining uncertainty is stated.

## Status

agent-operation-protocol-updated
