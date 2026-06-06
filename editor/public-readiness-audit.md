# Public Readiness Audit

## Repository

Arvin-liu/when-systems-catch-fire

Book title: When Systems Catch Fire  
中文书名 / Chinese title: 点火  
Core theory: Ignition Framework / 点火框架  
Repository: when-systems-catch-fire

## Current Visibility

private

## License Check

- LICENSE exists: yes
- NOTICE.md exists: yes
- LICENSE-SUMMARY.md exists: yes
- README license section exists: yes
- llms.txt license section exists: yes
- llms-full.txt license section exists: yes

## Privacy Check

检查是否存在不适合公开的信息：

- 个人隐私: no obvious personal privacy content found in this audit pass.
- 精确地址: no obvious precise address found.
- 账号信息: no obvious account credentials found.
- 法律细节: only general conceptual and license-related references found; no personal legal matter found.
- 健康细节: no obvious health detail found.
- 家庭细节: no obvious family detail found.
- 未脱敏原始对话: no raw dialogue dump found.
- 不适合公开的 AI 记忆内容: no dedicated AI memory vault content found in this repository.

Notes:

- The scan found general policy, law, license, and "exit right" language. These are subject-matter terms, not detected private legal details.
- The repository should still be reviewed manually before public release because historical and policy case notes may contain sensitive judgments or under-supported claims.

## Evidence Check

Several case and evidence files are explicitly marked as working hypotheses, predictions, pending checks, or placeholders. They should not be presented publicly as completed factual proof until supporting sources are added.

Examples requiring review:

- `agent/cases.md`: multiple cases marked "工作假设", "待判定", "预测中", or "待核查".
- `agent/claims.md`: claim C08 is marked `placeholder`; several claims still need stronger evidence framing.
- `data/ignition-cases.csv`: multiple rows contain "待补", "待核查", "工作假设", or "待判定".
- `dianhuo/03-evidence/fact-checks/2026-06-03-five-fact-checks.md`: pending fact-check content.
- `dianhuo/03-evidence/predictions/`: prediction files contain unfinished conditions and "待补" fields.
- `dianhuo/01-manuscript/chapters/`: several chapter drafts still contain "待补".

## Agent-readable Files Check

`llms.txt` and `llms-full.txt` contain license instructions and caution that many case entries are working hypotheses or placeholders. This is good for AI Agent use.

Risks:

- `llms-full.txt` aggregates many unfinished and hypothesis-level materials, so an AI Agent may over-summarize them as established claims if the caution is ignored.
- Case tables and claims should keep explicit status labels before public release.
- If public release is planned, add stronger source references or move speculative predictions into a clearly marked draft/research folder.

## Risk Items

- Historical cases are not yet fully sourced.
- Some predictions and policy/company cases are unfinished.
- Several files use placeholder language that is acceptable for private drafting but weak for public release.
- The repository name is `when-systems-catch-fire`; ensure no public-facing text implies the remote repository must be named `ignition-framework`.
- Review all generated Agent-readable summaries before public release to avoid overstating evidence.

## Recommended Fixes Before Public Release

- Complete or quarantine pending fact-check files under `dianhuo/03-evidence/fact-checks/`.
- Add source citations for historical and policy case claims.
- Keep all prediction content clearly labeled as prediction or draft research.
- Review `llms-full.txt` after each major content update to ensure it does not expose draft-only notes.
- Add a short public release note explaining the distinction between book title, theory name, and repository name.

## Final Recommendation

- ready_to_publish: no
- needs_cleanup: yes
- keep_private_for_now: yes
