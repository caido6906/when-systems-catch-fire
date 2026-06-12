#!/usr/bin/env python3
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json_items(items_dir):
    items = []
    for path in sorted(items_dir.glob("*.json")):
        item = json.loads(path.read_text(encoding="utf-8"))
        items.append((path, item))
    return items


def write_jsonl(path, rows):
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def write_csv(path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(path, title, intro, rows, columns):
    lines = [f"# {title}", "", intro, ""]
    if rows:
        headers = [label for label, _ in columns]
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for row in rows:
            values = []
            for _, key in columns:
                value = row.get(key)
                values.append("" if value is None else str(value).replace("|", "\\|"))
            lines.append("| " + " | ".join(values) + " |")
    else:
        lines.append("暂无条目。")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build_functions():
    base = ROOT / "data/functions"
    items = load_json_items(base / "items")
    rows = []
    for path, item in items:
        rel_path = path.relative_to(ROOT).as_posix()
        rows.append(
            {
                "id": item["id"],
                "normalized_id": item["normalized_id"],
                "title_zh": item["title"]["zh"],
                "status": item["status"],
                "confidence": item.get("registry", {}).get("confidence"),
                "source_note_id": (
                    item.get("source_notes", [{}])[0].get("note_id")
                    if item.get("source_notes")
                    else None
                ),
                "path": rel_path,
            }
        )
    write_csv(
        base / "index.csv",
        ["id", "normalized_id", "title_zh", "status", "confidence", "source_note_id", "path"],
        rows,
    )
    write_jsonl(base / "index.jsonl", rows)
    write_markdown(
        base / "index.md",
        "函数总表 / Function Index",
        "本索引由 `data/registry/统一函数总表.csv` 生成。每条函数的 canonical machine-readable 文件位于 `data/functions/items/`。",
        rows,
        [
            ("ID", "id"),
            ("Normalized ID", "normalized_id"),
            ("中文名称", "title_zh"),
            ("状态", "status"),
            ("路径", "path"),
        ],
    )


def build_cases():
    base = ROOT / "data/cases"
    items = load_json_items(base / "items")
    rows = []
    for path, item in items:
        rel_path = path.relative_to(ROOT).as_posix()
        rows.append(
            {
                "id": item["id"],
                "title_zh": item["title"]["zh"],
                "status": item["status"],
                "evidence_level": item["evidence_level"],
                "related_function_count": len(item.get("related_functions", [])),
                "source_note_id": (
                    item.get("source_notes", [{}])[0].get("note_id")
                    if item.get("source_notes")
                    else None
                ),
                "path": rel_path,
            }
        )
    write_csv(
        base / "index.csv",
        ["id", "title_zh", "status", "evidence_level", "related_function_count", "source_note_id", "path"],
        rows,
    )
    write_jsonl(base / "index.jsonl", rows)
    write_markdown(
        base / "index.md",
        "案例总表 / Case Index",
        "本索引由 `data/registry/统一案例总表.csv` 生成。每条案例的 canonical machine-readable 文件位于 `data/cases/items/`。",
        rows,
        [
            ("ID", "id"),
            ("中文名称", "title_zh"),
            ("状态", "status"),
            ("证据等级", "evidence_level"),
            ("路径", "path"),
        ],
    )


def build_discoveries():
    base = ROOT / "data/discoveries"
    items_dir = base / "items"
    items_dir.mkdir(parents=True, exist_ok=True)
    items = load_json_items(items_dir)
    rows = []
    for path, item in items:
        rel_path = path.relative_to(ROOT).as_posix()
        rows.append(
            {
                "id": item["id"],
                "title_zh": item["title"]["zh"],
                "status": item["status"],
                "human_explanation_path": item.get("human_explanation_path"),
                "path": rel_path,
            }
        )
    write_csv(
        base / "index.csv",
        ["id", "title_zh", "status", "human_explanation_path", "path"],
        rows,
    )
    write_jsonl(base / "index.jsonl", rows)
    lines = [
        "# 新发现 / Discoveries",
        "",
        "本目录用于放置从函数和案例中归纳出的重大新发现。当前先保留候选清单，不把未完成归纳写成已确认发现。",
        "",
        "## 待归纳候选",
        "",
        "- 物理大统一问题的新解释",
        "- 物理学“七朵乌云”的新答案",
        "- 演化博弈论与点火框架的关系",
        "- AI 搜索偏好与收益投影",
        "- 其他从案例和函数中归纳出的发现",
        "",
    ]
    if rows:
        lines.extend(["## 已结构化条目", ""])
        for row in rows:
            lines.append(f"- `{row['id']}` {row['title_zh']} ({row['status']})")
        lines.append("")
    (base / "index.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    build_functions()
    build_cases()
    build_discoveries()
    print("generated indexes")


if __name__ == "__main__":
    main()
