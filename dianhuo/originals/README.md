# Originals / 原文库

This directory preserves public-safe original source material for *When Systems Catch Fire / 点火*.

Distilled chapters, claims, case tables, and Agent-readable files should link back to the relevant source file here when possible.

## What Belongs Here

- Original notes from Get, manual imports, or user-provided source files
- Public-safe excerpts from conversations related to the Ignition Framework / 点火框架
- Draft fragments before they are rewritten into `book/`
- Source-level case notes before they are compressed into `agent/cases.md` or `data/`
- Historical evidence excerpts that need later fact-checking

## What Does Not Belong Here

- Private raw conversations
- Passwords, tokens, API keys, private keys, account credentials
- Precise addresses, IDs, bank information, or other sensitive personal details
- Raw legal, health, family, or private AI memory content
- Unreviewed material that is not safe for a public repository

## Source File Template

```markdown
---
title:
date:
timestamp:
source:
status: raw / cleaned / excerpt / needs_fact_check / public-ready
privacy_level: public-ready / sensitive-summary-only / do-not-store
related_concepts:
related_chapters:
derived_outputs:
---

# Title

## Original Text / 原文

Preserve the public-safe original wording here.

## Source Notes / 来源说明

Record where this came from and what was removed or sanitized.

## Links to Distilled Outputs / 提炼后去向

List related `book/`, `agent/`, or `data/` files.
```

## Rule

Original source preservation comes before distillation. If a future Agent creates a claim, chapter section, or case row from source material, it should preserve or cite the source here first, unless privacy rules forbid raw storage.
