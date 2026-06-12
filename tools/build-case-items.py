#!/usr/bin/env python3
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/registry/统一案例总表.csv"
ITEMS_DIR = ROOT / "data/cases/items"


def clean(value):
    if value is None:
        return None
    value = value.strip()
    return value or None


def slug_for(case_id):
    return case_id.lower().replace("_", "-")


def should_skip(row):
    case_id = clean(row.get("案例ID"))
    status = (clean(row.get("状态")) or "").lower()
    if not case_id:
        return True
    if case_id.lower() in {"c-unknown", "unknown"}:
        return True
    if "unknown" in case_id.lower():
        return True
    if "quarantine" in status:
        return True
    return False


def split_function_ids(value):
    text = clean(value)
    if not text:
        return []
    return sorted(set(re.findall(r"D-X\d+", text, flags=re.IGNORECASE)))


def normalize_function_id(function_id):
    match = re.fullmatch(r"D-X(\d+)", function_id, flags=re.IGNORECASE)
    if match:
        return f"D-X{int(match.group(1)):04d}"
    return function_id


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
        }
    ]


def evidence_level(row):
    value = clean(row.get("验证状态"))
    if not value:
        return "unknown"
    lowered = value.lower()
    if "fact" in lowered or "checked" in lowered or "核验" in value:
        return "externally_checked"
    if "argued" in lowered or "论证" in value:
        return "argued"
    if "text" in lowered or "文本" in value:
        return "textual"
    return "unknown"


def status_for(row, case_id):
    status = clean(row.get("状态")) or "candidate"
    if not re.fullmatch(r"C-\d+", case_id, flags=re.IGNORECASE):
        return "candidate"
    return status


def build_item(row):
    case_id = clean(row.get("案例ID"))
    title_zh = clean(row.get("案例名称"))
    related_functions = []
    for function_id in split_function_ids(row.get("关联函数ID")):
        normalized = normalize_function_id(function_id.upper())
        related_functions.append(
            {
                "function_id": function_id.upper(),
                "path": f"data/functions/items/{normalized}.json",
                "relation": "related",
            }
        )

    raw_case_type = clean(row.get("案例类型"))
    case_type = [raw_case_type] if raw_case_type else ["other"]

    return {
        "id": case_id,
        "slug": slug_for(case_id),
        "type": "ignition_case",
        "status": status_for(row, case_id),
        "language": ["zh"],
        "title": {"zh": title_zh, "en": None},
        "summary": {"zh": clean(row.get("摘要")), "en": None},
        "case_type": case_type,
        "related_functions": related_functions,
        "source_notes": source_note(row),
        "evidence_level": evidence_level(row),
        "license": "CC-BY-NC-4.0",
        "created_at": clean(row.get("首次发现时间")),
        "updated_at": clean(row.get("最后更新时间")),
        "registry": {
            "framework_position": clean(row.get("框架位置")),
            "event_level": clean(row.get("事件层级")),
            "participant_scale": clean(row.get("参与者规模")),
            "validation_status": clean(row.get("验证状态")),
            "cross_reference": clean(row.get("交叉引用")),
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
        if not item["id"] or not item["title"]["zh"]:
            continue
        target = ITEMS_DIR / f"{item['id']}.json"
        target.write_text(
            json.dumps(item, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        count += 1

    print(f"generated {count} case items")


if __name__ == "__main__":
    main()
