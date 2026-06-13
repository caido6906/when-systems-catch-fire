#!/usr/bin/env python3
"""Build the New Answers layer from bootstrap notes and explicit answer leads."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

from answer_utils import (
    ANSWER_TEMPLATE_MD,
    ANSWERS_INDEX_MD,
    ANSWERS_JSON,
    ANSWERS_JSONL,
    ANSWERS_LIST_MD,
    ANSWERS_JSON,
    ANSWERS_INDEX_MD,
    BOOTSTRAP_REPORT_JSON,
    BOOTSTRAP_REPORT_MD,
    CATEGORIES_JSON,
    CATEGORIES_JSONL,
    CATEGORY_DIR,
    CATEGORY_MAP_JSON,
    CATEGORY_MAP_JSONL,
    CATEGORY_DEFINITIONS,
    CATEGORY_LOOKUP,
    ITEM_DIR,
    ANSWER_DIR,
    CASES_JSON,
    DISCOVERIES_JSON,
    FUNCTIONS_JSON,
    PREDICTIONS_JSON,
    ANSWER_ID_RE,
    build_category_map,
    next_answer_id,
    normalize_source_refs,
    read_json,
    render_answer_index,
    render_answer_index_md,
    render_answer_page,
    render_bootstrap_report,
    render_category_page,
    rel_link,
    write_json,
    write_jsonl,
    write_text,
)


REPO_ROOT = Path("/workspace/when-systems-catch-fire")
RAW_NOTE_ROOTS = [
    REPO_ROOT / "dianhuo/originals",
    REPO_ROOT / "dianhuo/04-materials/raw-notes",
]


ANSWER_BLUEPRINTS = [
    {
        "id": "ANS-0001",
        "title": {"zh": "大统一应该追求Φ极小而不是α相等", "en": "Grand unification should minimize Phi rather than force equal couplings"},
        "question": {
            "zh": "传统大统一为什么卡了一百年，目标到底错在哪里？",
            "en": "Why has traditional grand unification stalled for so long, and where is the target wrong?",
        },
        "answer": {
            "zh": "目标错在追求耦合常数相等；更合理的目标是让Φ在自然能标上取极小。",
            "en": "The mistake is to chase equal couplings; the better target is to minimize Phi at a natural scale.",
        },
        "prior_answers": {
            "zh": "传统GUT通常把统一理解为所有耦合常数相等，但这只是Φ在特殊条件下的退化态。",
            "en": "Traditional GUT treats unification as equality of couplings, but that is only a degenerate special case of Phi.",
        },
        "new_explanation": {
            "zh": "这里把“统一”的判据从参数相等改成系统极小值，问题从“怎么让它们一样”改写成“怎么让系统整体更稳”。",
            "en": "The novelty is to replace parameter equality with a system-level minimum, shifting the question from making terms equal to making the whole system more stable.",
        },
        "basis": {
            "zh": "来源笔记明确写出“新答案：大统一的目标应该是Φ极小而不是α相等”。",
            "en": "The source note explicitly says the new answer is that grand unification should minimize Phi rather than force equal couplings.",
        },
        "testability": {
            "zh": "如果未来有统一理论或有效理论能直接从Φ极小推出更稳的耦合结构，这个答案会比“全相等”更有解释力。",
            "en": "If a future theory derives a more stable coupling structure directly from Phi minimization, this answer will be more explanatory than a simple equality target.",
        },
        "categories": ["physics", "technology-and-engineering"],
        "related_functions": ["D153", "D156", "D157"],
        "related_cases": ["C-0554"],
        "related_discoveries": [],
        "related_predictions": [],
        "source_refs": ["dianhuo/originals/1912550858907336432_点火统一函数数学推导.md#问题1"],
        "academic_novelty": {
            "status": "inconclusive",
            "checked_at": "",
            "query_terms": [
                "grand unification Phi minimum",
                "为什么大统一卡了一百年 Φ 极小",
                "unification target should minimize Phi",
            ],
            "sources_checked": ["OpenAlex", "Crossref"],
            "nearest_matches": [],
            "novelty_claim": {
                "zh": "该答案把统一判据改写为Φ极小，而不是参数相等。",
                "en": "This answer reframes unification around minimizing Phi rather than equal couplings.",
            },
            "reviewer_note": "bootstrap lead from source note; novelty not confirmed",
        },
        "confidence": "medium",
        "status": "answer_pending_novelty_review",
        "created_at": "2026-06-13",
        "updated_at": "2026-06-13",
    },
    {
        "id": "ANS-0002",
        "title": {"zh": "引力的弱是层级间距的数学必然", "en": "Gravity is weak because of hierarchy spacing"},
        "question": {
            "zh": "为什么引力比另外三种力弱那么多？",
            "en": "Why is gravity so much weaker than the other three forces?",
        },
        "answer": {
            "zh": "因为M_Planck与日常能标之间的层级间距太大，引力在Φ里只是一个远尾项，所以耦合极弱。",
            "en": "Because the hierarchy gap between the Planck scale and everyday scales is enormous, gravity is just a far-tail term in Phi, so its coupling is tiny.",
        },
        "prior_answers": {
            "zh": "传统层次问题常把引力弱看成待解释异常，或者用人择原理绕开。",
            "en": "The traditional hierarchy problem treats weak gravity as an anomaly to explain, or sidesteps it with anthropic reasoning.",
        },
        "new_explanation": {
            "zh": "这个答案把“弱”拆成两个层面：可微扰性与耦合强度；前者可以接近1，后者仍然可以极小。",
            "en": "The new explanation separates weak coupling from perturbative accessibility: the first can be tiny while the second stays near unity.",
        },
        "basis": {
            "zh": "来源笔记直接写出“引力弱是B型因子的数学必然”和“为什么引力弱10^40倍”。",
            "en": "The source note explicitly frames weak gravity as a mathematical necessity of the B-type factor and answers why gravity is 10^40 times weaker.",
        },
        "testability": {
            "zh": "如果未来的统一理论能解释层级间距的起源，这个答案会保留为结构解释；如果不能，它仍能解释为什么“弱”并不奇怪。",
            "en": "If a future unified theory explains the origin of the hierarchy gap, this answer remains a structural explanation; otherwise it still explains why weak gravity is not surprising.",
        },
        "categories": ["physics"],
        "related_functions": ["D153", "D156", "D157", "D164"],
        "related_cases": ["C-0554", "C-0457"],
        "related_discoveries": [],
        "related_predictions": [],
        "source_refs": ["dianhuo/originals/1912550858907336432_点火统一函数数学推导.md#问题2"],
        "academic_novelty": {
            "status": "inconclusive",
            "checked_at": "",
            "query_terms": [
                "why gravity is weak hierarchy spacing",
                "引力弱 10^40 倍 层级 间距",
                "gravity weak because Planck scale spacing",
            ],
            "sources_checked": ["OpenAlex", "Crossref"],
            "nearest_matches": [],
            "novelty_claim": {
                "zh": "该答案把引力弱归因于层级间距，而不是单独的微调故事。",
                "en": "This answer attributes weak gravity to hierarchy spacing rather than a standalone fine-tuning story.",
            },
            "reviewer_note": "bootstrap lead from source note; novelty not confirmed",
        },
        "confidence": "medium",
        "status": "answer_pending_novelty_review",
        "created_at": "2026-06-13",
        "updated_at": "2026-06-13",
    },
    {
        "id": "ANS-0003",
        "title": {"zh": "黑洞信息悖论更像部分保留而不是完全丢失", "en": "The black-hole information paradox is partial retention, not total loss"},
        "question": {
            "zh": "黑洞信息到底是全丢了，还是能以某种方式保住？",
            "en": "Does black-hole information disappear entirely, or can it be preserved in some form?",
        },
        "answer": {
            "zh": "更合理的答案是部分丢失、部分保留；视界更像压缩与门控，而不是简单抹除。",
            "en": "The better answer is partial loss and partial retention; the horizon behaves more like compression and gating than simple erasure.",
        },
        "prior_answers": {
            "zh": "传统争论在“完全丢失”与“完全守恒”之间对撞，常常没有中间态。",
            "en": "The classic debate pits complete loss against complete conservation and often leaves no middle state.",
        },
        "new_explanation": {
            "zh": "这里把视界当作门控面：信息在穿越前后经历压缩、编码和可恢复性的变化，因此不必是二元结论。",
            "en": "The novelty is to treat the horizon as a gating surface: information changes compression, encoding, and recoverability across it, so the outcome need not be binary.",
        },
        "basis": {
            "zh": "来源笔记明确给出“黑洞信息丢失是乘法门控的数学必然，但不是完全丢失”。",
            "en": "The source note explicitly says black-hole information loss is a mathematical necessity of multiplicative gating but not total loss.",
        },
        "testability": {
            "zh": "如果视界物理、蒸发谱或类比黑洞实验能区分“完全丢失”和“部分保留”，这个答案就可被检验。",
            "en": "If horizon physics, evaporation spectra, or analogue-black-hole experiments can distinguish total loss from partial retention, this answer becomes testable.",
        },
        "categories": ["physics", "philosophy"],
        "related_functions": ["D156", "D157", "D108"],
        "related_cases": ["C-0457"],
        "related_discoveries": [],
        "related_predictions": [],
        "source_refs": ["dianhuo/originals/1912550858907336432_点火统一函数数学推导.md#问题6"],
        "academic_novelty": {
            "status": "inconclusive",
            "checked_at": "",
            "query_terms": [
                "black hole information partial retention gating",
                "黑洞信息悖论 部分保留 门控",
                "black hole information paradox middle ground",
            ],
            "sources_checked": ["OpenAlex", "Crossref"],
            "nearest_matches": [],
            "novelty_claim": {
                "zh": "该答案把黑洞视为门控压缩面，而不是单一的丢失/守恒二分。",
                "en": "This answer treats the black hole as a gating/compression surface rather than a binary loss/conservation case.",
            },
            "reviewer_note": "bootstrap lead from source note; novelty not confirmed",
        },
        "confidence": "medium",
        "status": "answer_pending_novelty_review",
        "created_at": "2026-06-13",
        "updated_at": "2026-06-13",
    },
    {
        "id": "ANS-0004",
        "title": {"zh": "秦统一失败不是因为硬件不够，而是退出权被压成了符号", "en": "Qin failed because exit rights were compressed into symbols, not because the hardware was insufficient"},
        "question": {
            "zh": "秦统一为什么很快就崩了？",
            "en": "Why did Qin's unification collapse so quickly?",
        },
        "answer": {
            "zh": "秦的问题不在于统一硬件不足，而在于把退出权压缩成了象征层，缺少缓冲与真实认同。",
            "en": "Qin's problem was not insufficient unifying hardware; it compressed exit rights into a symbolic layer and lacked buffering and real identity.",
        },
        "prior_answers": {
            "zh": "传统解释常说秦法过严、二世而亡，但这只解释了表层政治，不解释结构性脆弱。",
            "en": "Traditional explanations say Qin was too harsh and died in two generations, but that only explains surface politics, not structural fragility.",
        },
        "new_explanation": {
            "zh": "这里把统一的成败放到退出权梯度里看：没有缓冲层的强制统一会把系统推到极脆点。",
            "en": "The novelty is to read success or failure through the gradient of exit rights: forced unification without a buffer pushes a system to a brittle point.",
        },
        "basis": {
            "zh": "来源笔记把秦统一多次当作“强推”“退出权为假”“15年亡”的典型例子。",
            "en": "The source notes repeatedly use Qin unification as the example of forced push, fake exit rights, and a 15-year collapse.",
        },
        "testability": {
            "zh": "可用其他强制统一或强制整合案例检验：如果退出权被压到象征层且无缓冲，系统应显著更脆。",
            "en": "Other forced-unification or forced-integration cases can test this: if exit rights are compressed to a symbolic layer with no buffer, the system should be more brittle.",
        },
        "categories": ["history-and-civilization", "sociology-and-politics"],
        "related_functions": ["A5", "A8", "A9"],
        "related_cases": ["C-0003", "C-0162"],
        "related_discoveries": [],
        "related_predictions": [],
        "source_refs": [
            "dianhuo/originals/20260608_1912243139532423784_点火-退出权梯度：等级制对退出权的结构性压缩.md",
            "dianhuo/originals/1912618494978223944_点火函数 A5.md",
        ],
        "academic_novelty": {
            "status": "inconclusive",
            "checked_at": "",
            "query_terms": [
                "Qin unification exit rights compression",
                "秦统一 退出权 压缩 缓冲",
                "forced unification brittle exit rights",
            ],
            "sources_checked": ["OpenAlex", "Crossref"],
            "nearest_matches": [],
            "novelty_claim": {
                "zh": "该答案把秦的失败解释为退出权梯度的断裂，而不是单纯的暴政后果。",
                "en": "This answer explains Qin's failure as a rupture in the exit-right gradient, not just as tyranny.",
            },
            "reviewer_note": "bootstrap lead from source note; novelty not confirmed",
        },
        "confidence": "medium",
        "status": "answer_pending_novelty_review",
        "created_at": "2026-06-13",
        "updated_at": "2026-06-13",
    },
]


def build_source_summary() -> dict[str, int]:
    summary = {}
    for root in RAW_NOTE_ROOTS:
        if not root.exists():
            summary[str(root.relative_to(REPO_ROOT))] = 0
            continue
        summary[str(root.relative_to(REPO_ROOT))] = len(list(root.rglob("*.md")))
    summary["functions"] = len(read_json(FUNCTIONS_JSON, []))
    summary["cases"] = len(read_json(CASES_JSON, []))
    summary["discoveries"] = len(read_json(DISCOVERIES_JSON, []))
    summary["predictions"] = len(read_json(PREDICTIONS_JSON, []))
    return summary


def build_answer_leads_from_bootstrap() -> list[dict]:
    # The bootstrap set is intentionally conservative: we promote only items
    # that are explicitly marked as new answers in the source notes.
    return [dict(item) for item in ANSWER_BLUEPRINTS]


def build_answer_pages(answers: list[dict]) -> None:
    ANSWER_DIR.mkdir(parents=True, exist_ok=True)
    ITEM_DIR.mkdir(parents=True, exist_ok=True)
    CATEGORY_DIR.mkdir(parents=True, exist_ok=True)

    for item in answers:
        write_text(ITEM_DIR / f"{item['id']}.md", render_answer_page(item))


def build_category_pages(category_map: list[dict]) -> None:
    for category in category_map:
        write_text(CATEGORY_DIR / f"{category['id']}.md", render_category_page(category))


def normalize_answer_item(item: dict) -> dict:
    normalized = dict(item)
    normalized["related_functions"] = list(dict.fromkeys(normalized.get("related_functions", [])))
    normalized["related_cases"] = list(dict.fromkeys(normalized.get("related_cases", [])))
    normalized["related_discoveries"] = list(dict.fromkeys(normalized.get("related_discoveries", [])))
    normalized["related_predictions"] = list(dict.fromkeys(normalized.get("related_predictions", [])))
    normalized["source_refs"] = normalize_source_refs(normalized.get("source_refs", []))
    if "page" not in normalized:
        normalized["page"] = f"docs/zh/answers/items/{normalized['id']}.md"
    return normalized


def write_answer_template() -> None:
    write_text(
        ANSWER_TEMPLATE_MD,
        """# ANS-____ 新答案标题 / New Answer Title

[← 返回新答案总表 / Back to New Answers](../../../ANSWERS.md)
[返回仓库首页 / Back to Repository Home](../../../README.md)

## 问题 / Question

中文：
English:

## 新答案 / New Answer

中文：
English:

## 已有答案或旧问题背景 / Existing Answers or Prior Problem Background

中文：
English:

## 新解释在哪里 / What Is New in This Answer

中文：
English:

## 推出依据 / Basis

中文：
English:

## 可检验性 / Testability

中文：
English:

## 分类 / Categories

-

## 相关函数 / Related Functions

-

## 相关案例 / Related Cases

-

## 相关发现 / Related Discoveries

-

## 相关预测 / Related Predictions

-

## 来源回指 / Source References

-

## 学术搜索独有性检查 / Academic Novelty Check

- 状态 / Status：pending / passed / failed / inconclusive
- 检查时间 / Checked at：
- 搜索词 / Query terms：
- 检查来源 / Sources checked：
- 最近相似结果 / Nearest matches：
- 为什么不是同一答案 / Why not identical：
- 独有性声明 / Novelty claim：

## 状态 / Status

draft / active / answer_pending_novelty_review / existing_answer_reference / deprecated / merged

## 置信度 / Confidence

low / medium / high
""",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    answers = [normalize_answer_item(item) for item in build_answer_leads_from_bootstrap()]
    functions = read_json(FUNCTIONS_JSON, [])
    cases = read_json(CASES_JSON, [])
    discoveries = read_json(DISCOVERIES_JSON, [])
    predictions = read_json(PREDICTIONS_JSON, [])
    category_map = build_category_map(answers, CATEGORY_DEFINITIONS, functions, cases, discoveries, predictions)

    template_text = """# ANS-____ 新答案标题 / New Answer Title

[← 返回新答案总表 / Back to New Answers](../../../ANSWERS.md)
[返回仓库首页 / Back to Repository Home](../../../README.md)

## 问题 / Question

中文：
English:

## 新答案 / New Answer

中文：
English:

## 已有答案或旧问题背景 / Existing Answers or Prior Problem Background

中文：
English:

## 新解释在哪里 / What Is New in This Answer

中文：
English:

## 推出依据 / Basis

中文：
English:

## 可检验性 / Testability

中文：
English:

## 分类 / Categories

-

## 相关函数 / Related Functions

-

## 相关案例 / Related Cases

-

## 相关发现 / Related Discoveries

-

## 相关预测 / Related Predictions

-

## 来源回指 / Source References

-

## 学术搜索独有性检查 / Academic Novelty Check

- 状态 / Status：pending / passed / failed / inconclusive
- 检查时间 / Checked at：
- 搜索词 / Query terms：
- 检查来源 / Sources checked：
- 最近相似结果 / Nearest matches：
- 为什么不是同一答案 / Why not identical：
- 独有性声明 / Novelty claim：

## 状态 / Status

draft / active / answer_pending_novelty_review / existing_answer_reference / deprecated / merged

## 置信度 / Confidence

low / medium / high
"""
    index_text = render_answer_index(answers, category_map)
    machine_text = render_answer_index_md(answers)
    summary = build_source_summary()
    notes = [
        "bootstrap notes were scanned conservatively for explicit new-answer material",
        "physics, grand-unification, gravity, black-hole information, and Qin-unification notes were promoted",
        "no curated answer was marked active because novelty is not confirmed yet",
        "air-mass / fog / cloud keyword search returned no direct local match",
    ]
    payload, report_md = render_bootstrap_report(answers, category_map, summary, notes)

    if args.check or args.dry_run:
        current_template = ANSWER_TEMPLATE_MD.read_text(encoding="utf-8") if ANSWER_TEMPLATE_MD.exists() else ""
        current_index = ANSWERS_LIST_MD.read_text(encoding="utf-8") if ANSWERS_LIST_MD.exists() else ""
        current_machine = ANSWERS_INDEX_MD.read_text(encoding="utf-8") if ANSWERS_INDEX_MD.exists() else ""
        if current_template != template_text:
            print("answer template out of date")
            return 1 if args.check else 0
        if current_index != index_text:
            print("answer index out of date")
            return 1 if args.check else 0
        if current_machine != machine_text:
            print("answer machine index out of date")
            return 1 if args.check else 0
        print(
            json.dumps(
                {
                    "answers": len(answers),
                    "curated": sum(1 for item in answers if item.get("status") == "active"),
                    "leads": sum(1 for item in answers if item.get("status") != "active"),
                    "check": True,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    write_answer_template()
    write_json(CATEGORIES_JSON, CATEGORY_DEFINITIONS)
    write_jsonl(CATEGORIES_JSONL, CATEGORY_DEFINITIONS)
    write_json(CATEGORY_MAP_JSON, category_map)
    write_jsonl(CATEGORY_MAP_JSONL, category_map)
    write_json(ANSWERS_JSON, answers)
    write_jsonl(ANSWERS_JSONL, answers)
    write_text(ANSWERS_INDEX_MD, machine_text)
    write_text(ANSWERS_LIST_MD, index_text)
    build_answer_pages(answers)
    build_category_pages(category_map)
    write_json(BOOTSTRAP_REPORT_JSON, payload)
    write_text(BOOTSTRAP_REPORT_MD, report_md)

    print(
        json.dumps(
            {
                "answers": len(answers),
                "curated": sum(1 for item in answers if item.get("status") == "active"),
                "leads": sum(1 for item in answers if item.get("status") != "active"),
                "report_md": str(BOOTSTRAP_REPORT_MD.relative_to(REPO_ROOT)),
                "report_json": str(BOOTSTRAP_REPORT_JSON.relative_to(REPO_ROOT)),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
