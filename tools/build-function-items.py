#!/usr/bin/env python3
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/registry/统一函数总表.csv"
ITEMS_DIR = ROOT / "data/functions/items"


def clean(value):
    if value is None:
        return None
    value = value.strip()
    return value or None


def normalize_function_id(function_id):
    value = clean(function_id)
    if not value:
        return None
    match = re.fullmatch(r"D-X(\d+)", value, flags=re.IGNORECASE)
    if match:
        return f"D-X{int(match.group(1)):04d}"
    return value


def slug_for(normalized_id):
    return normalized_id.lower().replace("_", "-")


def should_skip(row):
    function_id = clean(row.get("函数ID"))
    status = (clean(row.get("状态")) or "").lower()
    if not function_id:
        return True
    if function_id.lower() in {"f-unknown", "d-unknown", "unknown"}:
        return True
    if "unknown" in function_id.lower():
        return True
    if "quarantine" in status:
        return True
    return False


def split_ids(value, pattern):
    text = clean(value)
    if not text:
        return []
    return sorted(set(re.findall(pattern, text, flags=re.IGNORECASE)))


def source_note(row):
    note_id = clean(row.get("来源笔记ID"))
    source_file = clean(row.get("来源文件"))
    if not note_id and not source_file:
        return []
    return [
        {
            "note_id": note_id,
            "title": source_file,
            "path": f"dianhuo/originals/{source_file}" if source_file else None,
            "quote_range": None,
        }
    ]


def build_item(row):
    function_id = clean(row.get("函数ID"))
    normalized_id = normalize_function_id(function_id)
    title_zh = clean(row.get("函数名称"))
    summary = clean(row.get("规则摘要"))
    mechanism = clean(row.get("操作用途"))
    status = clean(row.get("状态")) or "candidate"
    related_cases = []
    for case_id in split_ids(row.get("关联案例"), r"C-\d+"):
        related_cases.append(
            {
                "type": "case",
                "id": case_id.upper(),
                "path": f"data/cases/items/{case_id.upper()}.json",
                "relation": "related",
            }
        )

    return {
        "id": function_id,
        "normalized_id": normalized_id,
        "slug": slug_for(normalized_id),
        "type": "ignition_function",
        "status": status,
        "language": ["zh"],
        "title": {"zh": title_zh, "en": None},
        "short_definition": {"zh": summary, "en": None},
        "formal_expression": {
            "text": None,
            "math": None,
            "notes": {"zh": None, "en": None},
        },
        "mechanism": {"zh": mechanism, "en": None},
        "derived_from": [],
        "derives": [],
        "answers_questions": [],
        "related_cases": related_cases,
        "source_notes": source_note(row),
        "novelty": {
            "claim": {"zh": None, "en": None},
            "search_status": "not_searched",
            "notes": {"zh": None, "en": None},
        },
        "attribution": {
            "discoverer": "Arvin Liu",
            "co_reasoning": "AI-assisted mathematical / structural reasoning",
            "maintainer": "Arvin Liu",
        },
        "license": "CC-BY-NC-4.0",
        "created_at": clean(row.get("首次发现时间")),
        "updated_at": clean(row.get("最后更新时间")),
        "registry": {
            "function_type": clean(row.get("函数类型")),
            "input_variables": clean(row.get("输入变量")),
            "output_judgment": clean(row.get("输出判断")),
            "operation_use": mechanism,
            "confidence": clean(row.get("置信度")),
            "source_hash": clean(row.get("来源哈希")),
            "notes": clean(row.get("备注")),
        },
    }


def main():
    ITEMS_DIR.mkdir(parents=True, exist_ok=True)
    for old_file in ITEMS_DIR.glob("*.json"):
        old_file.unlink()

    with REGISTRY.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    count = 0
    for row in rows:
        if should_skip(row):
            continue
        item = build_item(row)
        if not item["normalized_id"] or not item["title"]["zh"]:
            continue
        target = ITEMS_DIR / f"{item['normalized_id']}.json"
        target.write_text(
            json.dumps(item, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        count += 1

    print(f"generated {count} function items")


if __name__ == "__main__":
    main()
