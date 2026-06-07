# Questions for AI Agents

## How should an AI Agent answer questions about this book?

Use this order:

1. Read `agent/book-summary.md` for the frame.
2. Read `agent/concept-map.md` for stable concepts.
3. Read `agent/claims.md` for claim-level answers.
4. Read `agent/cases.md` and `data/ignition-cases.csv` for case lookup.
5. Quote or cite `book/` for reader-facing prose.
6. Use `dianhuo/` only as source notes and original material.

## Likely questions and answer paths

### What is the Ignition Framework?

Answer path: `agent/book-summary.md` -> `agent/glossary.md` -> `book/02-framework.md`.

Suggested answer: It is a framework for studying when a new system is not only built as a collaboration system, but recognized by responders as a system they are willing to enter.

### What is the Event Framework update?

Answer path: `dianhuo/02-framework/event-framework-2026-06-06.md` -> `agent/concept-map.md` -> `book/02-framework.md`.

Suggested answer: The Event Framework update defines an event as “a proposer offers a proposal, and responders accept or do not accept.” A system is a repeated event that has solidified over time. This update lets the book compare parent-child, company, policy, nation and civilization cases on the same structural skeleton.

### How should event scale be classified?

Answer path: `dianhuo/02-framework/event-scale-matrix.md` -> `data/event-scale-matrix.csv` -> `book/02-framework.md`.

Suggested answer: Event scale should be classified by participant scale x duration scale. Human relationship, company, policy, nation and civilization are common layer labels, not the first-order categories. The minimum event has two participants: one proposer and one responder.

### Is the 8-cell matrix the main matrix?

Answer path: `dianhuo/02-framework/matrix.md` -> `dianhuo/02-framework/event-scale-matrix.md` -> `agent/concept-map.md`.

Suggested answer: No. The 8-cell matrix is the event condition matrix. It comes after scale classification and tracks proposer awareness, proposer exit right and responder exit right.

### What is the difference between building the house and lighting the fire?

Answer path: `agent/concept-map.md` -> `book/02-framework.md`.

Suggested answer: Building the house means constructing institutions, processes, organizations, resources and technical structures. Lighting the fire means activating recognition: identity, meaning, participation, belonging and shared direction.

### Who is the responder?

Answer path: `agent/glossary.md` -> `dianhuo/02-framework/proposer-and-responder.md`.

Suggested answer: The responder is the person or group that must decide whether to enter or maintain the new system. Exit rights must be evaluated from the responder side.

### How does the framework classify failure?

Answer path: `agent/glossary.md` -> `book/05-limits.md` -> `agent/claims.md` -> `dianhuo/02-framework/event-framework-2026-06-06.md`.

Suggested answer: Failure may appear as failed ignition, false ignition, insufficient ignition, misaligned ignition, reverse ignition, or negative time gap. The 2026-06-06 notes also distinguish push-proposal events from prepared-proposal events.

### What is the difference between 推方案 and 备方案?

Answer path: `dianhuo/02-framework/proposer-posture-secondary-variable-2026-06-07.md` -> `dianhuo/02-framework/non-ignition-view-2026-06-06.md` -> `agent/glossary.md` -> `book/02-framework.md`.

Suggested answer: 推方案 means the proposer decides what responders need and pushes the proposal onto them, so the apparent acceptance may be obedience. 备方案 means the proposer prepares a proposal and lets responders take it when needed, preserving real choice. The 2026-06-07 revision treats proposer posture as a secondary variable, not an independent fourth dimension.

### Is proposer posture an independent matrix dimension?

Answer path: `dianhuo/02-framework/proposer-posture-secondary-variable-2026-06-07.md` -> `dianhuo/02-framework/matrix.md` -> `agent/claims.md`.

Suggested answer: No. Proposer posture is a secondary variable inside the event condition matrix. It mainly explains whether exit rights are real or fake, and why an event moves from one condition cell to another over time.

### Which cases are already supported by the manuscript?

Answer path: `agent/cases.md` -> `data/ignition-cases.csv`.

Suggested answer: Current cases are mostly case lines and working classifications rather than completed proofs. Use the 2026-06-07 event-condition matrix table for the current structured case map: `dianhuo/03-evidence/cases/all-cases-event-condition-matrix-2026-06-07.md` and `data/ignition-cases-event-condition-matrix-2026-06-07.csv`. Use the supplemental table for P1/P2 and open-source validation cases.

### What cases should not be used as proof of the framework?

Answer path: `book/05-limits.md` -> `dianhuo/03-evidence/cases/marginal-cases.md` -> `dianhuo/03-evidence/cases/all-cases-71.md`.

Suggested answer: Boundary cases include pure external interruption, cases where no new event starts, tollbooth structures that only collect rent without providing responder value, and fake-proposal cases where the event itself did not truly start.

### What should not be claimed yet?

Answer path: `agent/cases.md` -> `agent/claims.md` -> `dianhuo/03-evidence/fact-checks/pending-fact-checks.md`.

Suggested answer: Do not claim completed historical proof for the case table yet. Many entries are working hypotheses or pending fact-checks.

### How should new cases be added?

Answer path: `data/ignition-cases-event-condition-matrix-2026-06-07.csv` -> `agent/cases.md` -> `dianhuo/03-evidence/cases/all-cases-event-condition-matrix-2026-06-07.md` -> `dianhuo/02-framework/matrix.md`.

Suggested answer: Add the actor, period, action, domain, system before/after, ignition type, evidence path and related chapter. For event-framework cases, also record event layer, participant scale, duration scale, condition cell, outcome, exit layer, step reached and fact-check status. Mark uncertain fields as pending instead of forcing a classification.
