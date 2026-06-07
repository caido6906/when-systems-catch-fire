# Event Condition Matrix

Source: `dianhuo/02-framework/event-framework-2026-06-06.md`;
`dianhuo/02-framework/proposer-posture-secondary-variable-2026-06-07.md`
Saved timestamp: 2026-06-07T01:11:36+08:00
Status: working-draft

## Position in the Framework

This is not the total matrix of the Ignition Framework.

It is the second-layer matrix used after the event scale matrix.

Use the matrices in this order:

1. Event scale matrix: participant scale x duration scale.
2. Event condition matrix: proposer awareness x proposer exit right x responder exit right.
3. Event outcome table: correct ignition, insufficient ignition, misaligned ignition, reverse ignition, or negative time gap.

## Core Update

The 2026-06-06 event-framework note reduces the earlier placeholder matrix into three event-condition variables:

1. 提议者意识：提议者知不知道自己在提议。
2. 提议者退出权：提议者能不能从自己的方案里撤出。
3. 应约者退出权：应约者能不能离开或拒绝。

应约者状态，如积极、消极或无人应约，不再作为前提条件，而是作为事件走向的结果。

## Eight Cells

| Cell | 提议者意识 | 提议者退出权 | 应约者退出权 | Working meaning |
| --- | --- | --- | --- | --- |
| 格1 | 有 | 有 | 有 | 双方都有选择空间，最容易形成真实应约，也最能暴露退化。 |
| 格2 | 有 | 有 | 无 | 提议者可撤，应约者难退，容易滑向推方案和服从。 |
| 格3 | 有 | 无 | 有 | 提议者押上自身，应约者可拒绝，承诺信号较强。 |
| 格4 | 有 | 无 | 无 | 双方都难退，可能点着，也可能形成高压固化。 |
| 格5 | 无 | 有 | 有 | 提议者没有清晰提议意识，但双方仍有退出空间。 |
| 格6 | 无 | 有 | 无 | 提议者可撤、应约者难退，容易成为无意识强制或收割结构。 |
| 格7 | 无 | 无 | 有 | 提议者被事件拖住，应约者有退出空间，事件可能自发演化。 |
| 格8 | 无 | 无 | 无 | 双方都被卷入且缺少提议意识，容易成为惯性系统或封闭结构。 |

## Reading Rule

The cell does not by itself determine the outcome.

The cell also does not determine the event scale.

Proposer posture, such as 推方案 or 备方案, should not be treated as a new
independent dimension. The 2026-06-07 revision classifies it as a secondary
variable inside the event condition matrix.

It mainly explains:

- whether an apparent exit right is real, factual, psychological, or symbolic;
- why one cell drifts into another over time;
- why an event can begin as prepared proposal and later degrade into pushed
  proposal.

For example, 格1 can appear in:

- a two-person relationship event;
- a company culture event;
- a national reform event;
- a civilization-level recognition event.

The same condition cell can therefore recur at different participant-duration levels.

Outcome still depends on event path:

- 点对了
- 点不足
- 点歪了
- 点反了
- 负时间差

## To Be Tested

Each case should record:

- event_layer
- participant_scale
- duration_scale
- condition_cell
- event outcome
- dominant exit layer
- step reached
- evidence source
- whether the classification is working hypothesis or fact-checked
