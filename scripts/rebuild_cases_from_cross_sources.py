#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime
import json
import re
from pathlib import Path


CASE_HEADING_RE = re.compile(r"^(?:#{1,6}\s*)?#(?P<num>\d{1,3})\s+(?P<rest>\S.+)$")
CASE_LINE_RE = re.compile(r"^#(?P<num>\d{1,3})\s+(?P<rest>\S.+)$")
CASE_TABLE_RE = re.compile(r"^\|.*\|$")
FUNCTION_RE = re.compile(r"(?<![A-Z0-9])[ATD]\d{1,3}(?:-[ATD]?\d{1,3})?")
GENERIC_CASE_RE = re.compile(
    r"二次自举生成|触发：|链条：|机制\d+|国家级/政策级/公司级/边际|社会级/预测/推论/碰撞/书籍/AI/统一收敛|"
    r"组织或制度试图从旧秩序迁移|AI或人机系统在任务执行中同时受上下文窗口"
)
CASE_FUNCTION_REMAP_BY_NAME = {
    "默里实验": {"D53": "D57"},
    "罗森塔尔": {"D55": "D59"},
    "沃尔顿1小时": {"D56": "D60"},
    "沃尔顿21分钟": {"D56": "D60"},
    "沃尔顿10年": {"D57": "D61"},
}


@dataclass
class CaseCandidate:
    case_id: str
    score: int
    source_type: str
    source_id: str
    source_title: str
    source_created_at: str
    source_kind: str
    line: int
    name: str
    level: str
    core_functions: str
    description: str
    finding: str
    raw: str


def parse_dt(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def load_history(history_dir: Path) -> list[tuple[str, str, str, str, str, str]]:
    sources = []
    for path in sorted(history_dir.glob("*. txt"), key=lambda p: int(p.stem.split(".")[0])):
        sources.append(("history", path.name, "", "", "history", path.read_text(encoding="utf-8", errors="ignore")))
    return sources


def getnote_kind(title: str) -> str:
    if "统一案例总表" in title or "案例总表" in title:
        return "case_table"
    if "跑两张表" in title or "案例" in title or "自举循环" in title:
        return "case_derivation"
    return "note"


def load_getnote(path: Path, before: datetime | None) -> list[tuple[str, str, str, str, str, str]]:
    sources = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            note = json.loads(line)
            created_at = note.get("created_at", "")
            created_dt = parse_dt(created_at)
            if before and created_dt and created_dt >= before:
                continue
            title = note.get("title", "")
            kind = getnote_kind(title)
            content = note.get("content", "")
            sources.append(("getnote", note.get("note_id", ""), title, created_at, kind, f"{title}\n{content}"))
    return sources


def clean_cell(value: str) -> str:
    return value.strip().strip("|").strip()


def split_table(line: str) -> list[str]:
    return [clean_cell(cell) for cell in line.strip().strip("|").split("|")]


def normalize_case_num(value: str) -> int | None:
    value = value.strip()
    if "-" in value or "—" in value:
        return None
    value = value.removeprefix("#")
    if value.isdigit():
        number = int(value)
        if 1 <= number <= 578:
            return number
    return None


def extract_functions(text: str) -> str:
    funcs = FUNCTION_RE.findall(text)
    seen = []
    for func in funcs:
        if func not in seen:
            seen.append(func)
    return "/".join(seen[:8])


def normalize_case_references(row: dict) -> dict:
    joined = " ".join(str(row.get(field, "")) for field in ("name", "description", "finding"))
    replacements: dict[str, str] = {}
    for marker, mapping in CASE_FUNCTION_REMAP_BY_NAME.items():
        if marker in joined:
            replacements.update(mapping)
    if not replacements:
        if not row.get("core_functions"):
            row["core_functions"] = extract_functions(joined)
        return row
    for field in ("core_functions", "description", "finding"):
        value = str(row.get(field, ""))
        for old, new in replacements.items():
            value = re.sub(rf"(?<![A-Z0-9]){old}(?!\d)", new, value)
        row[field] = value
    if not row.get("core_functions"):
        row["core_functions"] = extract_functions(" ".join(str(row.get(field, "")) for field in ("description", "finding")))
    return row


def score_candidate(source_type: str, source_kind: str, title: str, raw: str, name: str, description: str) -> int:
    score = 100
    if source_type == "history":
        score += 80
    else:
        score += 40
    if source_kind == "case_derivation":
        score += 40
    elif source_kind == "case_table":
        score += 10
    if "逐条完整版" in title:
        score += 30
    if "核心函数" in raw or "验证函数" in raw:
        score += 30
    if len(description) > 20:
        score += 20
    if GENERIC_CASE_RE.search(raw) or GENERIC_CASE_RE.search(name):
        score -= 160
    if not name or name.startswith("[") or "其余" in name:
        score -= 120
    return score


def candidate_from_table(
    number: int,
    cells: list[str],
    source_type: str,
    source_id: str,
    source_title: str,
    source_created_at: str,
    source_kind: str,
    line_number: int,
    raw: str,
) -> CaseCandidate | None:
    if len(cells) < 2:
        return None
    if cells[0].isdigit() and len(cells) >= 3 and cells[1].startswith("#"):
        name = cells[2]
        level = cells[3] if len(cells) > 3 else ""
        core = cells[4] if len(cells) > 4 else extract_functions(raw)
        description = cells[5] if len(cells) > 5 else ""
        finding = cells[7] if len(cells) > 7 else ""
    else:
        name = cells[1] if len(cells) > 1 else ""
        level = cells[2] if len(cells) > 2 else ""
        core_candidate = cells[6] if len(cells) > 6 else ""
        core = core_candidate if FUNCTION_RE.search(core_candidate) else extract_functions(raw)
        description = cells[7] if len(cells) > 7 else ""
        if len(cells) > 8:
            finding = cells[8]
        elif core_candidate and core_candidate != core:
            finding = core_candidate
        else:
            finding = ""
    score = score_candidate(source_type, source_kind, source_title, raw, name, description)
    if score <= 0:
        return None
    return CaseCandidate(
        case_id=f"#{number}",
        score=score,
        source_type=source_type,
        source_id=source_id,
        source_title=source_title,
        source_created_at=source_created_at,
        source_kind=source_kind,
        line=line_number,
        name=name,
        level=level,
        core_functions=core or extract_functions(raw),
        description=description,
        finding=finding,
        raw=raw[:1200],
    )


def candidate_from_line(
    number: int,
    rest: str,
    source_type: str,
    source_id: str,
    source_title: str,
    source_created_at: str,
    source_kind: str,
    line_number: int,
    raw: str,
) -> CaseCandidate | None:
    tab_parts = [part.strip() for part in rest.split("\t") if part.strip()]
    if len(tab_parts) >= 4:
        name = tab_parts[0]
        core = tab_parts[1] if FUNCTION_RE.search(tab_parts[1]) else extract_functions(rest)
        description = tab_parts[-1]
        finding = tab_parts[-1]
    else:
        name = rest
        for sep in ("。核心函数", "核心函数：", "核心函数:", "→", "——", "—"):
            if sep in name:
                name = name.split(sep, 1)[0].strip()
                break
        core_match = re.search(r"核心函数[：:]\s*([^。；;，,\n]+)", rest)
        if core_match:
            core = core_match.group(1).strip()
        else:
            core = extract_functions(rest)
        description = rest
        finding = ""
    score = score_candidate(source_type, source_kind, source_title, raw, name, rest)
    if score <= 0:
        return None
    return CaseCandidate(
        case_id=f"#{number}",
        score=score,
        source_type=source_type,
        source_id=source_id,
        source_title=source_title,
        source_created_at=source_created_at,
        source_kind=source_kind,
        line=line_number,
        name=name,
        level="",
        core_functions=core,
        description=description,
        finding=finding,
        raw=raw[:1200],
    )


def extract_candidates(sources: list[tuple[str, str, str, str, str, str]]) -> dict[int, list[CaseCandidate]]:
    records: dict[int, list[CaseCandidate]] = defaultdict(list)
    for source_type, source_id, source_title, source_created_at, source_kind, text in sources:
        lines = text.splitlines()
        for index, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped:
                continue
            if CASE_TABLE_RE.match(stripped):
                cells = split_table(stripped)
                if not cells or cells[0] in {"---", "编号", "序号"}:
                    continue
                number = normalize_case_num(cells[0])
                if number is None and len(cells) > 1:
                    number = normalize_case_num(cells[1])
                if number is not None:
                    candidate = candidate_from_table(
                        number, cells, source_type, source_id, source_title, source_created_at, source_kind, index, stripped
                    )
                    if candidate:
                        records[number].append(candidate)
                continue
            match = CASE_HEADING_RE.match(stripped) or CASE_LINE_RE.match(stripped)
            if not match:
                continue
            number = int(match.group("num"))
            if not 1 <= number <= 578:
                continue
            candidate = candidate_from_line(
                number,
                match.group("rest").strip(),
                source_type,
                source_id,
                source_title,
                source_created_at,
                source_kind,
                index,
                stripped,
            )
            if candidate:
                records[number].append(candidate)
    return records


def choose(records: dict[int, list[CaseCandidate]]) -> list[dict]:
    rows = []
    for number in range(1, 579):
        candidates = sorted(
            records.get(number, []),
            key=lambda c: (bool(GENERIC_CASE_RE.search(c.raw)), -c.score),
        )
        if not candidates:
            rows.append(
                {
                    "case_id": f"#{number}",
                    "name": "",
                    "level": "",
                    "core_functions": "",
                    "description": "",
                    "finding": "",
                    "status": "MISSING",
                    "best_source": "",
                    "best_source_title": "",
                    "best_source_kind": "",
                    "candidate_count": 0,
                    "candidates": [],
                }
            )
            continue
        best = candidates[0]
        generic = bool(GENERIC_CASE_RE.search(best.raw))
        has_history = any(c.source_type == "history" for c in candidates)
        has_getnote = any(c.source_type == "getnote" for c in candidates)
        if generic:
            status = "WEAK_TEMPLATE"
        elif has_history and has_getnote:
            status = "CROSS_VERIFIED"
        elif best.source_type == "history":
            status = "HISTORY_ONLY"
        else:
            status = "GETNOTE_ONLY"
        row = {
                "case_id": best.case_id,
                "name": best.name,
                "level": best.level,
                "core_functions": best.core_functions,
                "description": best.description,
                "finding": best.finding,
                "status": status,
                "best_source": f"{best.source_type}:{best.source_id}:{best.line}",
                "best_source_title": best.source_title,
                "best_source_kind": best.source_kind,
                "candidate_count": len(candidates),
                "candidates": [asdict(c) for c in candidates[:20]],
            }
        rows.append(normalize_case_references(row))
    return rows


def md_escape(value: object) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", "<br>")


def write_outputs(rows: list[dict], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "cases_rebuild_candidates_578.jsonl").open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    with (out_dir / "cases_rebuild_final_578.jsonl").open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    with (out_dir / "cases_rebuild_final_578.md").open("w", encoding="utf-8") as f:
        f.write("# 统一案例总表（案例阶段源文交叉重建版）\n\n")
        f.write("生成规则：候选来自历史会话 zip 与 GetNote 点火知识库；GetNote 只取 2026-06-13 00:00:00 前内容；模板化触发链条不作为最终候选优先来源。\n\n")
        statuses = {}
        for row in rows:
            statuses[row["status"]] = statuses.get(row["status"], 0) + 1
        f.write(f"- total: `{len(rows)}`\n")
        for status, count in sorted(statuses.items()):
            f.write(f"- {status}: `{count}`\n")
        f.write("\n| 序 | 案例ID | 案例名 | 层级 | 核心函数 | 案例说明 | 关键发现 | 源文回指 | 状态 |\n")
        f.write("|---:|---|---|---|---|---|---|---|---|\n")
        for index, row in enumerate(rows, 1):
            f.write(
                f"| {index} | {row['case_id']} | {md_escape(row['name'])} | {md_escape(row['level'])} | "
                f"{md_escape(row['core_functions'])} | {md_escape(row['description'][:420])} | "
                f"{md_escape(row['finding'][:240])} | {md_escape(row['best_source'])} | {row['status']} |\n"
            )
    with (out_dir / "cases_rebuild_audit.md").open("w", encoding="utf-8") as f:
        f.write("# 案例表逐个重建审计（案例阶段）\n\n")
        f.write("候选来自历史会话 zip 与 GetNote 点火知识库；GetNote 只取 2026-06-13 00:00:00 前内容；模板化触发链条降为弱证据。\n\n")
        statuses = {}
        for row in rows:
            statuses[row["status"]] = statuses.get(row["status"], 0) + 1
        f.write(f"- total: `{len(rows)}`\n")
        for status, count in sorted(statuses.items()):
            f.write(f"- {status}: `{count}`\n")
        f.write("\n| 序 | 案例ID | 状态 | 案例名 | 核心函数 | 摘要 | 最佳来源 | 候选数 |\n")
        f.write("|---:|---|---|---|---|---|---|---:|\n")
        for index, row in enumerate(rows, 1):
            f.write(
                f"| {index} | {row['case_id']} | {row['status']} | {md_escape(row['name'])} | "
                f"{md_escape(row['core_functions'])} | {md_escape(row['description'][:260])} | "
                f"{md_escape(row['best_source'])} | {row['candidate_count']} |\n"
            )
    with (out_dir / "cases_rebuild_missing_or_weak.md").open("w", encoding="utf-8") as f:
        f.write("# 案例缺口与弱证据清单\n\n")
        f.write("| 案例ID | 状态 | 当前候选名 | 最佳来源 |\n")
        f.write("|---|---|---|---|\n")
        for row in rows:
            if row["status"] in {"MISSING", "WEAK_TEMPLATE"}:
                f.write(f"| {row['case_id']} | {row['status']} | {md_escape(row['name'])} | {md_escape(row['best_source'])} |\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--history-dir", default="/tmp/ignition_rebuild/history/新建文件夹")
    parser.add_argument("--getnote-jsonl", default="/tmp/ignition_rebuild/getnote_pointfire_notes.jsonl")
    parser.add_argument("--getnote-before", default="2026-06-13 00:00:00")
    parser.add_argument("--out-dir", default="data/rebuild")
    args = parser.parse_args()

    before = parse_dt(args.getnote_before) if args.getnote_before else None
    sources = load_history(Path(args.history_dir)) + load_getnote(Path(args.getnote_jsonl), before)
    rows = choose(extract_candidates(sources))
    write_outputs(rows, Path(args.out_dir))
    print(json.dumps({"rows": len(rows), "out_dir": args.out_dir}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
