# AGENT_ENTRY.md

This is the highest-priority entry file for AI Agents working with this repository.

If the user asks you to save, store, archive, import, update, or organize content in this repository, read this file first.

## Core Rule

Do not treat this repository as a raw chat dump.

Only save content that has long-term value for this repository's purpose.

Do not save ordinary curiosity, temporary search results, casual chat, transactional tasks, sensitive raw details, passwords, tokens, private keys, account credentials, exact addresses, or unreviewed private material.

## First Reading Order

Before writing anything, read in this order:

1. `AGENT_ENTRY.md`
2. `README.md`
3. `llms.txt`
4. `AGENTS.md` if present
5. repository-specific protocol files if present
6. `agent/reading-path.md` if present
7. relevant files under `agent/`, `projects/`, `knowledge/`, `book/`, `corpus/`, `data/`, or `editor/`

## Write Safety

Before writing:

1. Identify the repository type.
2. Identify the user's intent.
3. Decide whether the content deserves long-term storage.
4. Select the correct storage layer.
5. Preserve source, status, privacy level, and uncertainty.
6. Do not overwrite stable files unless explicitly instructed.
7. Prefer proposals, checkpoints, inbox, or editor files before stable memory.
8. Log important changes.

## Required Metadata

Every saved item should include, when applicable:

- source
- date
- status
- privacy_level
- confidence
- related_project or related_concepts
- recommended_storage_location
- whether user confirmation is needed

## Forbidden Actions

Do not:

- invent user history
- write AI inference as user-confirmed fact
- overwrite original user writing
- overwrite stable memory without instruction
- save full raw conversations unless explicitly requested
- expose private repository content publicly
- change repository visibility
- change license terms
- move or delete files without explicit instruction

## Repository Type

This repository is a public non-commercial open content book project.

Book title: 点火 / When Systems Catch Fire  
Core theory: Ignition Framework / 点火框架  
Repository form: Agent-readable book project and AI-readable open knowledge repository  
License: CC BY-NC-SA 4.0

## Repository Purpose

This repository stores a dual-reader book project:

- Human-readable layer: `book/`, `SUMMARY.md`, narrative chapters.
- Agent-readable layer: `agent/`, `data/`, `llms.txt`, `llms-full.txt`.

The goal is to develop and maintain the Ignition Framework: a theory about key persons, key periods, key actions, and changes in system combustion conditions.

## When User Says "Save This"

If the user asks to save the current conversation into this repository, save only content related to:

- Ignition Framework / 点火框架
- key person / key period / key action
- system combustion conditions
- historical cases
- theory refinements
- claims, counterexamples, limits
- case evidence
- chapter ideas
- public-ready passages
- Agent-readable summaries

Do not save unrelated personal memory, writing style notes, general curiosity entries, or private AI memory here.

## Preferred Storage Locations

- Theory definition or conceptual refinement: `agent/concept-map.md`
- Claims and arguments: `agent/claims.md`
- Cases and evidence: `agent/cases.md` or `data/ignition-cases.csv`
- Chapter material: `book/`
- Public-ready fragments: `editor/public-export-candidates.md` if present, otherwise create under `editor/`
- Open questions: `agent/questions.md`
- Publication or repository status: `editor/publication-status.md` if present

## Special Caution

This is a public repository. Do not store private user details, raw private conversations, sensitive legal/health/family information, or private AI memory.

Unverified historical claims must be marked as `needs_fact_check` or `working hypothesis`.

## User Save Command

When the user says something like:

"把我们刚刚聊的、值得长期保存的内容，存到这个仓库里。"

or:

"[SAVE] Save the valuable parts of this conversation into this repository."

the Agent should:

1. Read `AGENT_ENTRY.md`.
2. Read repository-specific protocol files.
3. Identify whether the conversation actually belongs in this repository.
4. Extract only long-term valuable content.
5. Reject or ignore temporary, sensitive, or unrelated content.
6. Choose the correct storage layer.
7. Create or update files according to repository rules.
8. Add metadata.
9. Report exactly what was saved, where it was saved, what was not saved, and what needs user confirmation.
