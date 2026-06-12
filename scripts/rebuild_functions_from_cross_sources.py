#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime
import json
import re
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path


ID_RE = re.compile(r"^(?:#{1,6}\s*)?(?P<id>[ATD]\d{1,3})[\.、\t ]+(?P<rest>\S.{1,2000})")
DX_ID_RE = re.compile(r"^(?:#{1,6}\s*)?D-X(?P<num>\d{1,3})[\.、：:\t ]+(?P<rest>\S.{1,2000})")
ID_OR_DX_RE = re.compile(r"^(?:#{1,6}\s*)?(?:[ATD]\d{1,3}|D-X\d{1,3})[\.、：:\t ]+")
SINGLE_FUNCTION_TITLE_RE = re.compile(r"函数\s+(?P<id>[ATD]\d{1,3})$")
BAD_EXTRACT_RE = re.compile(
    r"函数总数|案例总数|基线\d|^\d+$|^\d+[；;]\d+|D\d+-D\d+|推论层D|新增案例|收敛检查|碰撞对象|"
    r"^组\d+|扫描\d*|删除|合并→|降级→|已合并|编号冲突|去重|重复|版编号|"
    r"\t|✅|❌|修正版|已收敛|^D\d+$"
)
SUSPECT_RE = re.compile(r"函数总数|案例总数|删除|合并→|降级→|重复|去掉|二次公式化|补全")
GENERIC_DEFINITION_RE = re.compile(
    r"^(窗口与临界函数|书籍碰撞函数|17域词典簇碰撞|[^\n]{0,20}案例验证|"
    r"公理级，见[ATD]\d+。?|定理级，见[ATD]\d+。?|"
    r".*见[AT]\d+。?|.*涵盖17个领域的函数投影。?)$"
)
WEAK_SINGLE_RE = re.compile(r"案例验证|涵盖17个领域|见[AT]\d+|^公理级|^定理级")
FORMULA_HINT_RE = re.compile(r"[=∝×Σ∑∫σλμθΦΨΩγκβαπρ√]|\\b(d|P|F|H|R|C|I|T|K|S)_")
FULL_TABLE_RE = re.compile(r"统一函数总表|统一案例总表|总表（|总表_")
DERIVATION_RE = re.compile(r"自举循环|函数 D\d+|D\d+[-D\d]*|函数化|碰撞|收敛|新增")
NUMBER_FRAGMENT_RE = re.compile(r"^\d+[.。]?$")
DX_DOOR_LOCK_MAP = {
    "49": "D51",
    "50": "D52",
    "51": "D53",
}
DX_ONSITE_MAP = {
    "52": "D54",
    "53": "D55",
    "54": "D56",
}
DX_LEAST_EFFORT_MAP = {
    "52": "D57",
    "53": "D58",
    "54": "D59",
    "55": "D60",
    "56": "D61",
}
EXCLUDED_FROM_FINAL = {
    "D68": "10. txt:2173 明确删除：D68-D71=D54-D57；10. txt:2215 旧D68-D71→删除，案例指向D54-D57。",
    "D69": "10. txt:2173 明确删除：D68-D71=D54-D57；10. txt:2215 旧D68-D71→删除，案例指向D54-D57。",
    "D70": "10. txt:2173 明确删除：D68-D71=D54-D57；10. txt:2215 旧D68-D71→删除，案例指向D54-D57。",
    "D71": "10. txt:2173 明确删除：D68-D71=D54-D57；10. txt:2215 旧D68-D71→删除，案例指向D54-D57。",
    "D78": "10. txt:2173 明确删除：D78-D83=上层重复。",
    "D79": "10. txt:2173 明确删除：D78-D83=上层重复。",
    "D80": "10. txt:2173 明确删除：D78-D83=上层重复。",
    "D81": "10. txt:2173 明确删除：D78-D83=上层重复。",
    "D82": "10. txt:2173 明确删除：D78-D83=上层重复。",
    "D83": "10. txt:2173 明确删除：D78-D83=上层重复。",
}


@dataclass
class Candidate:
    function_id: str
    score: int
    source_type: str
    source_id: str
    source_title: str
    source_created_at: str
    source_kind: str
    line: int
    name: str
    expression: str
    raw: str


def sort_key(function_id: str) -> tuple[int, int]:
    return {"A": 0, "T": 1, "D": 2}.get(function_id[0], 9), int(function_id[1:])


def split_name_expression(rest: str, context: str) -> tuple[str, str]:
    parts = re.split(r"\s+[—–-]\s+|——|：|:", rest, 1)
    name = parts[0].strip()
    name = re.sub(r"\s*·.*$", "", name).strip()
    if len(parts) > 1:
        expression = parts[1].strip()
    else:
        expression = context.strip()
    return name, expression


def collect_context(lines: list[str], index: int) -> str:
    context_lines = []
    for line in lines[index : index + 12]:
        stripped = line.strip()
        if not stripped:
            continue
        if ID_OR_DX_RE.match(stripped):
            break
        if stripped.startswith(("## ", "### ", "#### ")) and context_lines:
            break
        context_lines.append(stripped)
        if len(context_lines) >= 6:
            break
    return " ".join(context_lines)[:1200]


def definition_from_single_function_note(lines: list[str]) -> tuple[int, str] | None:
    for index, line in enumerate(lines, 1):
        stripped = line.strip()
        for prefix in ("**定义**：", "**定义**:", "定义：", "定义:"):
            if stripped.startswith(prefix):
                return index, stripped.removeprefix(prefix).strip()
        if stripped in {"## 定义", "### 定义"}:
            for offset, next_line in enumerate(lines[index : index + 5], index + 1):
                next_stripped = next_line.strip()
                if next_stripped:
                    return offset, next_stripped
    return None


def is_generic_definition(name: str, expression: str) -> bool:
    text = " ".join(part.strip() for part in (name, expression) if part.strip())
    if not text:
        return True
    if NUMBER_FRAGMENT_RE.match(expression.strip()):
        return True
    if GENERIC_DEFINITION_RE.match(text):
        return True
    if WEAK_SINGLE_RE.search(text) and not FORMULA_HINT_RE.search(text):
        return True
    return False


def load_history(history_dir: Path) -> list[tuple[str, str, str, str]]:
    sources = []
    for path in sorted(history_dir.glob("*. txt"), key=lambda p: int(p.stem.split(".")[0])):
        sources.append(("history", path.name, "", "", "history", path.read_text(encoding="utf-8", errors="ignore")))
    return sources


def parse_dt(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def getnote_kind(title: str) -> str:
    if "统一案例总表" in title:
        return "case_table"
    if "统一函数总表" in title or "函数总表" in title:
        return "function_table"
    if DERIVATION_RE.search(title):
        return "derivation"
    return "note"


def load_getnote(path: Path, before: datetime | None) -> list[tuple[str, str, str, str, str, str]]:
    sources = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            note = json.loads(line)
            title = note.get("title", "")
            created_at = note.get("created_at", "")
            created_dt = parse_dt(created_at)
            if before and created_dt and created_dt >= before:
                continue
            kind = getnote_kind(title)
            if kind == "case_table":
                continue
            content = note.get("content", "")
            sources.append(("getnote", note.get("note_id", ""), title, created_at, kind, f"{title}\n{content}"))
    return sources


def score_candidate(
    source_type: str,
    source_title: str,
    source_kind: str,
    function_id: str,
    line: str,
    rest: str,
    name: str,
    prev_context: str,
) -> int:
    score = 100
    score += 60 if source_type == "getnote" else 45
    if source_kind == "derivation":
        score += 80
    elif source_kind == "function_table":
        score -= 70
    elif source_kind == "history":
        score += 35
    if f"函数 {function_id}" in source_title or source_title.endswith(function_id) or re.search(rf"\b{function_id}\b", source_title):
        score += 80
    if line.lstrip().startswith("#"):
        score += 20
    if "收敛函数" in prev_context or "向下推导新函数" in prev_context or "函数化收敛" in prev_context:
        score += 80
    if "向下推导新函数" in prev_context:
        score += 50
    if FULL_TABLE_RE.search(source_title):
        score -= 50
    if BAD_EXTRACT_RE.search(name) or BAD_EXTRACT_RE.search(rest[:120]):
        score -= 250
    if len(name) < 3:
        score -= 50
    if SUSPECT_RE.search(name) or SUSPECT_RE.search(rest[:160]):
        score -= 50
    return score


def score_single_function_note(function_id: str, source_title: str, rest: str, name: str, expression: str) -> int:
    if is_generic_definition(name, expression):
        return 35
    score = 260
    if f"函数 {function_id}" in source_title or source_title.endswith(function_id):
        score += 120
    if FORMULA_HINT_RE.search(f"{name} {expression}"):
        score += 80
    if len(expression) > 20:
        score += 20
    if BAD_EXTRACT_RE.search(name) or BAD_EXTRACT_RE.search(rest[:120]):
        score -= 250
    return score


def map_dx_alias(num: str, source_id: str, source_title: str, prev_context: str) -> str | None:
    context = f"{source_id}\n{source_title}\n{prev_context}"
    if (source_id == "17. txt" or "门锁交替" in context or "自锁结构" in context) and num in DX_DOOR_LOCK_MAP:
        return DX_DOOR_LOCK_MAP[num]
    if (source_id == "18. txt" or "《去现场》" in context or "去现场" in context) and num in DX_ONSITE_MAP:
        return DX_ONSITE_MAP[num]
    least_effort_primary = source_id == "19. txt" or "D-X52~D-X56" in source_title
    if least_effort_primary and ("《最小努力法则》" in context or "最小努力法则" in context) and num in DX_LEAST_EFFORT_MAP:
        return DX_LEAST_EFFORT_MAP[num]
    return None


def extract_candidates(sources: list[tuple[str, str, str, str]]) -> dict[str, list[Candidate]]:
    records: dict[str, list[Candidate]] = defaultdict(list)
    for source_type, source_id, source_title, source_created_at, source_kind, text in sources:
        lines = text.splitlines()
        title_match = SINGLE_FUNCTION_TITLE_RE.search(source_title)
        if source_type == "getnote" and title_match:
            function_id = title_match.group("id")
            definition = definition_from_single_function_note(lines)
            if definition:
                line_number, rest = definition
                name, expression = split_name_expression(rest, "")
                if "，" in name and len(name) > 18:
                    left, right = name.split("，", 1)
                    name, expression = left.strip(), f"{right.strip()} {expression}".strip()
                elif "," in name and len(name) > 18:
                    left, right = name.split(",", 1)
                    name, expression = left.strip(), f"{right.strip()} {expression}".strip()
                single_score = score_single_function_note(function_id, source_title, rest, name, expression)
                records[function_id].append(
                    Candidate(
                        function_id=function_id,
                        score=single_score,
                        source_type=source_type,
                        source_id=source_id,
                        source_title=source_title,
                        source_created_at=source_created_at,
                        source_kind="single_function_note",
                        line=line_number,
                        name=name,
                        expression=expression[:900],
                        raw=f"{function_id}. {rest}"[:900],
                    )
                )
        for index, line in enumerate(lines, 1):
            stripped = line.strip()
            dx_match = DX_ID_RE.match(stripped)
            prev_context = "\n".join(lines[max(0, index - 8) : index])
            if dx_match:
                function_id = map_dx_alias(dx_match.group("num"), source_id, source_title, prev_context)
            else:
                function_id = None
            if dx_match and function_id:
                rest = dx_match.group("rest").strip()
                context = collect_context(lines, index)
                name, expression = split_name_expression(rest, context)
                score = score_candidate(source_type, source_title, source_kind, function_id, stripped, rest, name, prev_context) + 120
                if score > 0:
                    records[function_id].append(
                        Candidate(
                            function_id=function_id,
                            score=score,
                            source_type=source_type,
                            source_id=source_id,
                            source_title=source_title,
                            source_created_at=source_created_at,
                            source_kind=source_kind,
                            line=index,
                            name=name,
                            expression=expression[:900],
                            raw=stripped[:900],
                        )
                    )
            match = ID_RE.match(stripped)
            if not match:
                continue
            function_id = match.group("id")
            rest = match.group("rest").strip()
            context = collect_context(lines, index)
            name, expression = split_name_expression(rest, context)
            score = score_candidate(source_type, source_title, source_kind, function_id, stripped, rest, name, prev_context)
            if score <= 0:
                continue
            records[function_id].append(
                Candidate(
                    function_id=function_id,
                    score=score,
                    source_type=source_type,
                    source_id=source_id,
                    source_title=source_title,
                    source_created_at=source_created_at,
                    source_kind=source_kind,
                    line=index,
                    name=name,
                    expression=expression[:900],
                    raw=stripped[:900],
                )
            )
    return records


def choose(records: dict[str, list[Candidate]]) -> list[dict]:
    rows = []
    for function_id in sorted(records, key=sort_key):
        candidates = sorted(
            records[function_id],
            key=lambda c: (
                NUMBER_FRAGMENT_RE.match(c.expression.strip()) is not None,
                bool(SUSPECT_RE.search(f"{c.name} {c.expression}")),
                is_generic_definition(c.name, c.expression),
                -c.score,
            ),
        )
        best = candidates[0]
        source_types = sorted({c.source_type for c in candidates})
        source_kinds = sorted({c.source_kind for c in candidates})
        suspect = bool(SUSPECT_RE.search(f"{best.name} {best.expression}"))
        has_history = any(c.source_type == "history" for c in candidates)
        has_getnote = any(c.source_type == "getnote" for c in candidates)
        has_strong_source = any(
            c.source_kind in {"history", "derivation"} and not is_generic_definition(c.name, c.expression)
            for c in candidates
        )
        generic_best = is_generic_definition(best.name, best.expression)
        if has_history and has_getnote and not suspect and not generic_best:
            status = "CROSS_VERIFIED"
        elif suspect:
            status = "SUSPECT"
        elif generic_best and not has_strong_source:
            status = "WEAK_SINGLE"
        else:
            status = "SINGLE_SOURCE"
        rows.append(
            {
                "function_id": function_id,
                "name": best.name,
                "expression": best.expression,
                "status": status,
                "candidate_count": len(candidates),
                "source_types": source_types,
                "source_kinds": source_kinds,
                "best_source": f"{best.source_type}:{best.source_id}:{best.line}",
                "best_source_title": best.source_title,
                "best_source_created_at": best.source_created_at,
                "best_source_kind": best.source_kind,
                "best_score": best.score,
                "generic_best": generic_best,
                "has_strong_source": has_strong_source,
                "raw": best.raw,
                "candidates": [asdict(c) for c in candidates[:20]],
            }
        )
    return rows


def md_escape(value: object) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", "<br>")


def write_outputs(rows: list[dict], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "functions_rebuild_candidates.jsonl").open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    active_rows = [row for row in rows if row["function_id"] not in EXCLUDED_FROM_FINAL]
    excluded_rows = [row for row in rows if row["function_id"] in EXCLUDED_FROM_FINAL]
    with (out_dir / "functions_rebuild_final_470.jsonl").open("w", encoding="utf-8") as f:
        for row in active_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    counts = {
        "total_ids": len(rows),
        "final_ids": len(active_rows),
        "excluded_ids": len(excluded_rows),
        "cross_verified": sum(r["status"] == "CROSS_VERIFIED" for r in rows),
        "single_source": sum(r["status"] == "SINGLE_SOURCE" for r in rows),
        "suspect": sum(r["status"] == "SUSPECT" for r in rows),
        "weak_single": sum(r["status"] == "WEAK_SINGLE" for r in rows),
        "final_A": sum(r["function_id"].startswith("A") for r in active_rows),
        "final_T": sum(r["function_id"].startswith("T") for r in active_rows),
        "final_D": sum(r["function_id"].startswith("D") for r in active_rows),
    }
    with (out_dir / "functions_rebuild_audit.md").open("w", encoding="utf-8") as f:
        f.write("# 函数表逐条重建审计（函数阶段）\n\n")
        f.write("本表由历史会话 zip 与 GetNote 点火知识库交叉抽取生成；0点以后笔记被排除，统一函数总表只作为弱证据，统一案例总表不参与函数抽取。\n\n")
        for key, value in counts.items():
            f.write(f"- {key}: `{value}`\n")
        f.write("\n| 序 | 函数ID | 状态 | 函数名 | 表达/定义摘要 | 最佳来源 | 来源类型 | 分数 | 候选数 |\n")
        f.write("|---:|---|---|---|---|---|---|---:|---:|\n")
        for index, row in enumerate(rows, 1):
            f.write(
                f"| {index} | {row['function_id']} | {row['status']} | {md_escape(row['name'])} | "
                f"{md_escape(row['expression'][:260])} | {md_escape(row['best_source'])} | "
                f"{md_escape(row['best_source_kind'])} | {row['best_score']} | {row['candidate_count']} |\n"
            )
    with (out_dir / "functions_rebuild_final_470.md").open("w", encoding="utf-8") as f:
        f.write("# 统一函数总表（函数阶段源文交叉重建版）\n\n")
        f.write("生成规则：候选来自历史会话 zip 与 GetNote 点火知识库；GetNote 只取 2026-06-13 00:00:00 前内容；D68-D71、D78-D83 按 10.txt 明确删除记录移入排除审计。\n\n")
        f.write(f"- final_total: `{len(active_rows)}`\n")
        f.write(f"- A: `{counts['final_A']}`\n")
        f.write(f"- T: `{counts['final_T']}`\n")
        f.write(f"- D: `{counts['final_D']}`\n")
        f.write("\n| 序 | 函数ID | 层级 | 函数名 | 定义/表达 | 源文回指 | 来源类型 | 状态 |\n")
        f.write("|---:|---|---|---|---|---|---|---|\n")
        for index, row in enumerate(active_rows, 1):
            level = {"A": "公理", "T": "定理", "D": "推论"}.get(row["function_id"][0], "")
            f.write(
                f"| {index} | {row['function_id']} | {level} | {md_escape(row['name'])} | "
                f"{md_escape(row['expression'][:420])} | {md_escape(row['best_source'])} | "
                f"{md_escape(row['best_source_kind'])} | {row['status']} |\n"
            )
    with (out_dir / "functions_rebuild_excluded.md").open("w", encoding="utf-8") as f:
        f.write("# 函数候选排除审计\n\n")
        f.write("以下候选有抽取来源，但源文同时给出重复/上层重复判定，因此不进入函数阶段 470 条最终表。\n\n")
        f.write("| 函数ID | 候选名 | 候选来源 | 排除依据 |\n")
        f.write("|---|---|---|---|\n")
        for row in excluded_rows:
            f.write(
                f"| {row['function_id']} | {md_escape(row['name'])} | {md_escape(row['best_source'])} | "
                f"{md_escape(EXCLUDED_FROM_FINAL[row['function_id']])} |\n"
            )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--history-dir", default="/tmp/ignition_rebuild/history/新建文件夹")
    parser.add_argument("--getnote-jsonl", default="/tmp/ignition_rebuild/getnote_pointfire_notes.jsonl")
    parser.add_argument("--getnote-before", default="2026-06-13 00:00:00")
    parser.add_argument("--out-dir", default="data/rebuild")
    args = parser.parse_args()

    before = parse_dt(args.getnote_before) if args.getnote_before else None
    sources = load_history(Path(args.history_dir)) + load_getnote(Path(args.getnote_jsonl), before)
    records = extract_candidates(sources)
    rows = choose(records)
    write_outputs(rows, Path(args.out_dir))
    print(json.dumps({"rows": len(rows), "out_dir": args.out_dir}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
