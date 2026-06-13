#!/usr/bin/env python3
"""Render human-friendly linked entrances from unified function/case source tables.

This script reads the full reconstructed Markdown tables under `data/functions/`
and `data/cases/`, then generates:

* machine-readable JSON / JSONL / minified JSON
* markdown indexes for GitHub browsing
* per-item markdown pages for functions and cases
* a short front-door section in README.md
* a render report with validation and dangling-reference counts

The source tables contain a few malformed pipe characters inside formula text.
We treat escaped pipes (`\\|`) as literals, then apply a small set of repair
heuristics for the rare rows where an unescaped pipe splits a signature or
formula.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence


REPO_ROOT = Path("/workspace/when-systems-catch-fire")
FUNC_SOURCE = REPO_ROOT / "data/functions/统一函数总表_470条_源文交叉重建版_v4.md"
CASE_SOURCE = REPO_ROOT / "data/cases/统一案例总表_578案例_源文交叉重建版_v4.md"

OUT_FUNC_JSON = REPO_ROOT / "data/functions/unified-functions.json"
OUT_FUNC_JSONL = REPO_ROOT / "data/functions/unified-functions.jsonl"
OUT_FUNC_MIN_JSON = REPO_ROOT / "data/functions/unified-functions.min.json"
OUT_FUNC_INDEX_MD = REPO_ROOT / "data/functions/unified-functions-index.md"

OUT_CASE_JSON = REPO_ROOT / "data/cases/unified-cases.json"
OUT_CASE_JSONL = REPO_ROOT / "data/cases/unified-cases.jsonl"
OUT_CASE_MIN_JSON = REPO_ROOT / "data/cases/unified-cases.min.json"
OUT_CASE_INDEX_MD = REPO_ROOT / "data/cases/unified-cases-index.md"

OUT_REPORT = REPO_ROOT / "data/rebuild/human-entry-render-report.md"

FUNC_DOC_INDEX = REPO_ROOT / "docs/zh/functions.md"
CASE_DOC_INDEX = REPO_ROOT / "docs/zh/cases.md"
FUNC_DOC_DIR = REPO_ROOT / "docs/zh/functions/items"
CASE_DOC_DIR = REPO_ROOT / "docs/zh/cases/items"
README = REPO_ROOT / "README.md"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_lines(path: Path) -> List[str]:
    return path.read_text(encoding="utf-8").splitlines()


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, value) -> None:
    write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def write_jsonl(path: Path, rows: Sequence[dict]) -> None:
    body = "\n".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) for row in rows)
    write_text(path, body + ("\n" if body else ""))


def natural_case_key(case_id: str) -> int:
    m = re.search(r"#(\d+)", case_id)
    return int(m.group(1)) if m else 10**9


def normalize_pipe_literals(text: str) -> str:
    return text.replace("\\|", "[[PIPE]]")


def restore_pipe_literals(text: str) -> str:
    return text.replace("[[PIPE]]", "|")


def split_row(line: str) -> List[str]:
    """Split a markdown row while preserving escaped pipes.

    The source tables are not perfectly escaped, so we preserve literal `\\|`.
    """
    safe = normalize_pipe_literals(line.strip())
    parts = [part.strip() for part in safe.split("|")]
    return [restore_pipe_literals(part) for part in parts]


def is_row(line: str) -> bool:
    s = line.strip()
    return s.startswith("|") and not s.startswith("|---")


def source_ref_to_note_id(source_ref: str) -> str:
    source_ref = source_ref.strip()
    if source_ref.startswith("getnote:"):
        parts = source_ref.split(":")
        if len(parts) >= 2:
            return parts[1]
    if ":" in source_ref:
        return source_ref.rsplit(":", 1)[0]
    return source_ref


def source_ref_to_file(source_ref: str) -> str:
    source_ref = source_ref.strip()
    if ":" in source_ref:
        return source_ref.rsplit(":", 1)[0]
    return source_ref


def strip_trailing_var(text: str) -> str:
    """Drop a dangling formula variable from the end of the title text."""
    return re.sub(r"[，, ]+[A-Za-z_][A-Za-z0-9_]*\s*$", "", text).strip()


def clean_title(text: str) -> str:
    text = strip_trailing_var(text)
    return re.sub(r"[，,。．.\s]+$", "", text).strip()


def normalize_signature(text: str) -> str:
    """Normalize malformed pipe-separated signatures like `H(t | L)`."""
    chars = []
    depth = 0
    for ch in text:
        if ch == "(":
            depth += 1
            chars.append(ch)
        elif ch == ")":
            depth = max(0, depth - 1)
            chars.append(ch)
        elif ch == "|" and depth > 0:
            chars.append(",")
        else:
            chars.append(ch)
    normalized = "".join(chars)
    normalized = re.sub(r"\s*,\s*", ",", normalized)
    return normalized


def parse_function_middle(middle_parts: List[str]) -> tuple[str, str]:
    """Derive function title and content from the middle cell blob."""
    blob = " | ".join(middle_parts).strip()
    blob = restore_pipe_literals(blob)
    if not blob:
        return "", ""

    # Preferred split: title + formula/explanation separated by em dash.
    if "—" in blob:
        left, right = blob.split("—", 1)
        title = clean_title(normalize_signature(left).strip())
        content = right.strip()
        return title, content

    # If there is an assignment, split before the first assignment variable.
    assign = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*=", blob)
    if assign:
        left = blob[: assign.start()].strip()
        var = assign.group(1)
        right = blob[assign.start():].strip()
        title = clean_title(normalize_signature(left).strip())
        content = right
        # Some rows carry the formula label in the title text before the assignment.
        # Preserve the formula and keep the human-readable title clean.
        if title.endswith(var):
            title = title[: -len(var)].rstrip(" ，,")
        return title, content

    # Fallback: treat everything as title if no formula separator is obvious.
    title = clean_title(normalize_signature(blob).strip())
    return title, ""


def parse_case_middle(middle_parts: List[str]) -> tuple[str, str]:
    """Derive case title and content from the middle cell blob."""
    blob = " | ".join(middle_parts).strip()
    blob = restore_pipe_literals(blob)
    if not blob:
        return "", ""

    # Most case rows begin with the case title, followed by function refs and text.
    # We keep the full blob as content and extract the leading title with light repair.
    if "—" in blob:
        left, right = blob.split("—", 1)
        title = clean_title(normalize_signature(left).strip())
        content = right.strip()
        return title, content

    # If the row contains a formula-like assignment, use it as a content boundary.
    assign = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*=", blob)
    if assign:
        left = blob[: assign.start()].strip()
        var = assign.group(1)
        right = blob[assign.start():].strip()
        title = clean_title(normalize_signature(strip_trailing_var(left)).strip())
        if title.endswith(var):
            title = title[: -len(var)].rstrip(" ，,")
        return title, right

    # Default: the first chunk is the title, the rest is descriptive content.
    # This keeps the pages readable even when the source row has nested markdown tables.
    return clean_title(normalize_signature(blob).strip()), ""


def parse_function_table(path: Path) -> List[dict]:
    lines = read_lines(path)
    header_idx = next(
        (i for i, line in enumerate(lines) if line.strip().startswith("| 序 | 函数ID |")),
        None,
    )
    if header_idx is None:
        raise RuntimeError(f"Could not find function table header in {path}")

    records: List[dict] = []
    for lineno in range(header_idx + 2, len(lines) + 1):
        line = lines[lineno - 1]
        if not is_row(line):
            if records:
                break
            continue
        parts = split_row(line)
        # Expected shape after `split`: [empty, seq, id, level, middle..., source_ref, source_type, status, empty]
        if len(parts) < 10:
            raise RuntimeError(f"Malformed function row at {path}:{lineno}: {line}")
        seq = parts[1]
        fid = parts[2]
        level = parts[3]
        middle_parts = parts[4:-4]
        source_ref = parts[-4]
        source_type = parts[-3]
        status = parts[-2]

        if len(middle_parts) == 1:
            title = normalize_signature(middle_parts[0]).strip()
            content = ""
        elif len(middle_parts) == 2:
            if not middle_parts[1].strip():
                title = clean_title(normalize_signature(middle_parts[0]).strip())
                content = ""
            # Fast path for well-formed rows; detect the few malformed rows below.
            elif ("=" in middle_parts[0]) or (middle_parts[0].count("(") > middle_parts[0].count(")")) or middle_parts[0].endswith("("):
                title, content = parse_function_middle(middle_parts)
            else:
                title = clean_title(normalize_signature(middle_parts[0]).strip())
                content = restore_pipe_literals(middle_parts[1].strip())
        else:
            title, content = parse_function_middle(middle_parts)

        raw_middle = " | ".join(middle_parts).strip()
        source_note_id = source_ref_to_note_id(source_ref)
        source_file = source_ref_to_file(source_ref)
        record = {
            "id": fid,
            "normalized_id": fid,
            "title": title,
            "level": level,
            "status": status,
            "expression_or_content": content,
            "source": {
                "source_table": str(path.relative_to(REPO_ROOT)),
                "source_line": lineno,
                "source_note_id": source_note_id,
                "source_file": source_file,
                "source_reference": source_ref,
                "raw_excerpt": line.strip(),
            },
            "links": {
                "human_page": f"docs/zh/functions/items/{fid}.md",
                "related_cases": [],
            },
            "_seq": int(seq),
            "_raw_middle": raw_middle,
            "_source_type": source_type,
        }
        records.append(record)

    if len(records) != 470:
        raise RuntimeError(f"Expected 470 functions, parsed {len(records)} from {path}")

    seen = set()
    for record in records:
        if record["id"] in seen:
            raise RuntimeError(f"Duplicate function ID detected: {record['id']}")
        seen.add(record["id"])
        if not record["title"].strip():
            raise RuntimeError(f"Empty function title for {record['id']}")
    return records


def parse_case_table(path: Path) -> List[dict]:
    lines = read_lines(path)
    header_idx = next(
        (i for i, line in enumerate(lines) if line.strip().startswith("| 序 | 案例ID |")),
        None,
    )
    if header_idx is None:
        raise RuntimeError(f"Could not find case table header in {path}")

    records: List[dict] = []
    for lineno in range(header_idx + 2, len(lines) + 1):
        line = lines[lineno - 1]
        if not is_row(line):
            if records:
                break
            continue
        parts = split_row(line)
        # Expected shape after `split`: [empty, seq, id, title, level, middle..., source_ref, status, empty]
        if len(parts) < 11:
            raise RuntimeError(f"Malformed case row at {path}:{lineno}: {line}")

        seq = parts[1]
        cid = parts[2]
        title_candidate = parts[3]
        level = parts[4]
        middle_parts = parts[5:-3]
        source_ref = parts[-3]
        status = parts[-2]

        if len(middle_parts) == 1:
            title = normalize_signature(title_candidate).strip()
            content = restore_pipe_literals(middle_parts[0].strip())
        else:
            # Reconstruct the title from the first cell, then treat the remainder as content.
            # This works for both clean rows and rows with embedded markdown tables.
            title = normalize_signature(title_candidate).strip()
            content = restore_pipe_literals(" | ".join(middle_parts).strip())

        source_note_id = source_ref_to_note_id(source_ref)
        source_file = source_ref_to_file(source_ref)
        numeric = int(re.search(r"#(\d+)", cid).group(1))
        normalized = f"C-{numeric:04d}"
        record = {
            "id": cid,
            "normalized_id": normalized,
            "title": title,
            "status": status,
            "level": level,
            "description_or_content": content,
            "related_functions": [],
            "source": {
                "source_table": str(path.relative_to(REPO_ROOT)),
                "source_line": lineno,
                "source_note_id": source_note_id,
                "source_file": source_file,
                "source_reference": source_ref,
                "raw_excerpt": line.strip(),
            },
            "links": {
                "human_page": f"docs/zh/cases/items/{normalized}.md",
                "related_function_pages": [],
            },
            "_seq": int(seq),
            "_raw_middle": " | ".join(middle_parts).strip(),
        }
        records.append(record)

    if len(records) != 578:
        raise RuntimeError(f"Expected 578 cases, parsed {len(records)} from {path}")

    seen = set()
    for record in records:
        if record["normalized_id"] in seen:
            raise RuntimeError(f"Duplicate case ID detected: {record['normalized_id']}")
        seen.add(record["normalized_id"])
        if not record["title"].strip():
            raise RuntimeError(f"Empty case title for {record['id']}")
    return records


FUNC_REF_RE = re.compile(r"\b([ATD]\d{1,3})\b")


def extract_function_refs(text: str) -> List[str]:
    refs: List[str] = []
    seen = set()
    for match in FUNC_REF_RE.finditer(text):
        ref = match.group(1)
        if ref not in seen:
            seen.add(ref)
            refs.append(ref)
    return refs


def build_relationships(functions: List[dict], cases: List[dict]) -> dict:
    function_map = {f["id"]: f for f in functions}
    case_map = {c["normalized_id"]: c for c in cases}
    dangling = []

    for case in cases:
        related = extract_function_refs(case["title"] + " " + case["description_or_content"])
        case["related_functions"] = related
        case["links"]["related_function_pages"] = [
            f"docs/zh/functions/items/{ref}.md" for ref in related if ref in function_map
        ]
        for ref in related:
            if ref not in function_map:
                dangling.append({"case": case["normalized_id"], "ref": ref})

    for func in functions:
        related_cases = [
            case["normalized_id"]
            for case in cases
            if func["id"] in case["related_functions"]
        ]
        func["links"]["related_cases"] = related_cases

    return {
        "function_map": function_map,
        "case_map": case_map,
        "dangling": dangling,
    }


def minimal_functions(functions: List[dict]) -> List[dict]:
    return [
        {
            "id": f["id"],
            "normalized_id": f["normalized_id"],
            "title": f["title"],
            "status": f["status"],
            "level": f["level"],
            "related_case_count": len(f["links"]["related_cases"]),
            "source_note_id": f["source"]["source_note_id"],
            "links": {"human_page": f["links"]["human_page"]},
        }
        for f in functions
    ]


def minimal_cases(cases: List[dict]) -> List[dict]:
    return [
        {
            "id": c["id"],
            "normalized_id": c["normalized_id"],
            "title": c["title"],
            "status": c["status"],
            "related_function_count": len(c["related_functions"]),
            "source_note_id": c["source"]["source_note_id"],
            "links": {"human_page": c["links"]["human_page"]},
        }
        for c in cases
    ]


def render_md_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def render_functions_root(functions: List[dict]) -> str:
    rows = []
    for f in functions:
        rows.append(
            [
                f"[{f['id']}](docs/zh/functions/items/{f['id']}.md)",
                escape_md(f["title"]),
                escape_md(f["level"]),
                escape_md(f["status"]),
                str(len(f["links"]["related_cases"])),
            ]
        )
    return "\n".join(
        [
            "# 统一函数总表",
            "",
            f"{len(functions)} 条函数。每条函数可点击进入详情页，并反向查看关联案例。",
            "",
            f"- 机器数据：[`data/functions/unified-functions.json`](data/functions/unified-functions.json)",
            f"- JSONL：[`data/functions/unified-functions.jsonl`](data/functions/unified-functions.jsonl)",
            f"- 重建审计：[`data/rebuild/human-entry-render-report.md`](data/rebuild/human-entry-render-report.md)",
            "",
            render_md_table(["编号", "函数名称", "层级", "状态", "关联案例"], rows),
            "",
        ]
    )


def render_cases_root(cases: List[dict]) -> str:
    rows = []
    for c in cases:
        related = " / ".join(c["related_functions"][:3]) if c["related_functions"] else "暂无明确关联函数"
        if len(c["related_functions"]) > 3:
            related += " …"
        rows.append(
            [
                f"[{c['id']}](docs/zh/cases/items/{c['normalized_id']}.md)",
                escape_md(c["title"]),
                escape_md(c["status"]),
                escape_md(related),
            ]
        )
    return "\n".join(
        [
            "# 统一案例总表",
            "",
            f"{len(cases)} 个案例。每个案例可点击进入详情页，并查看关联函数。",
            "",
            f"- 机器数据：[`data/cases/unified-cases.json`](data/cases/unified-cases.json)",
            f"- JSONL：[`data/cases/unified-cases.jsonl`](data/cases/unified-cases.jsonl)",
            f"- 重建审计：[`data/rebuild/human-entry-render-report.md`](data/rebuild/human-entry-render-report.md)",
            "",
            render_md_table(["编号", "案例名称", "状态", "关联函数"], rows),
            "",
        ]
    )


def escape_md(text: str) -> str:
    return text.replace("|", "\\|")


def render_index_page(
    title: str,
    intro: str,
    source_links: Sequence[str],
    rows_headers: Sequence[str],
    rows: Sequence[Sequence[str]],
) -> str:
    return "\n".join(
        [
            f"# {title}",
            "",
            intro,
            "",
            *source_links,
            "",
            render_md_table(rows_headers, rows),
            "",
        ]
    )


def render_function_page(func: dict) -> str:
    related_cases = func["links"]["related_cases"]
    case_lines = []
    if related_cases:
        for case_id in related_cases:
            case_lines.append(f"- [{case_id}](../../cases/items/{case_id}.md)")
    else:
        case_lines.append("- 暂无明确关联案例")

    content = func["expression_or_content"].strip() or "暂无明确内容"
    return "\n".join(
        [
            f"# {func['id']} {func['title']}",
            "",
            "[← 返回函数表](../../functions.md) ｜ [返回仓库首页](../../../README.md)",
            "",
            "## 函数内容",
            "",
            content,
            "",
            "## 层级与状态",
            "",
            f"- 层级：{func['level']}",
            f"- 状态：{func['status']}",
            "",
            "## 关联案例",
            "",
            *case_lines,
            "",
            "## 来源回指",
            "",
            f"- 源总表：`{func['source']['source_table']}`",
            f"- 源行：{func['source']['source_line']}",
            f"- 来源笔记ID：`{func['source']['source_note_id']}`",
            f"- 来源文件：`{func['source']['source_file']}`",
            "",
            "## 源文片段",
            "",
            f"> {func['source']['raw_excerpt']}",
            "",
        ]
    )


def render_case_page(case: dict) -> str:
    related_functions = case["related_functions"]
    func_lines = []
    if related_functions:
        for func_id in related_functions:
            func_lines.append(
                f"- [{func_id}](../../functions/items/{func_id}.md)"
            )
    else:
        func_lines.append("- 暂无明确关联函数")

    content = case["description_or_content"].strip() or "暂无明确内容"
    return "\n".join(
        [
            f"# {case['id']} {case['title']}",
            "",
            "[← 返回案例表](../../cases.md) ｜ [返回仓库首页](../../../README.md)",
            "",
            "## 案例内容",
            "",
            content,
            "",
            "## 关联函数",
            "",
            *func_lines,
            "",
            "## 状态",
            "",
            f"- 状态：{case['status']}",
            "",
            "## 来源回指",
            "",
            f"- 源总表：`{case['source']['source_table']}`",
            f"- 源行：{case['source']['source_line']}",
            f"- 来源笔记ID：`{case['source']['source_note_id']}`",
            f"- 来源文件：`{case['source']['source_file']}`",
            "",
            "## 源文片段",
            "",
            f"> {case['source']['raw_excerpt']}",
            "",
        ]
    )


def render_summary_index(
    title: str,
    source_links: Sequence[str],
    records: Sequence[dict],
    headers: Sequence[str],
    row_builder,
) -> str:
    rows = [row_builder(record) for record in records]
    parts = [f"# {title}", ""]
    parts.extend([f"- {link}" for link in source_links])
    parts.append("")
    parts.append(render_md_table(headers, rows))
    parts.append("")
    return "\n".join(parts)


def update_readme(functions: List[dict], cases: List[dict]) -> None:
    text = README.read_text(encoding="utf-8")
    lines = text.splitlines()
    anchor_idx = next(
        (i for i, line in enumerate(lines) if line.strip() == "## Current Structure / 当前结构"),
        None,
    )
    if anchor_idx is not None:
        suffix = "\n".join(lines[anchor_idx:]).lstrip("\n")
    else:
        first_heading_idx = next((i for i, line in enumerate(lines[1:], start=1) if line.startswith("## ")), len(lines))
        if first_heading_idx < len(lines) and lines[first_heading_idx].strip() == "## 入口":
            next_heading_idx = next(
                (i for i, line in enumerate(lines[first_heading_idx + 1 :], start=first_heading_idx + 1) if line.startswith("## ")),
                len(lines),
            )
            suffix = "\n".join(lines[next_heading_idx:]).lstrip("\n")
        else:
            suffix = "\n".join(lines[first_heading_idx:]).lstrip("\n")

    intro = "\n".join(
        [
            "# When Systems Catch Fire / 点火",
            "",
            "《点火》不是一本固定成书，而是一个开放维护的函数与案例知识库。它收集“点火函数”、函数之间的推导关系、案例证据和由此产生的新发现。",
            "",
            "## 入口",
            "",
            "| 区域 | 入口 | 内容 |",
            "|---|---|---|",
            "| 函数表 | [统一函数总表](FUNCTIONS.md) | 470 条函数，可跳转详情页与关联案例 |",
            "| 案例表 | [统一案例总表](CASES.md) | 578 个案例，可跳转详情页与关联函数 |",
            "",
        ]
    )

    new_text = intro + suffix
    write_text(README, new_text)


def make_report(
    functions: List[dict],
    cases: List[dict],
    dangling: List[dict],
) -> str:
    dangling_lines = ["- `{} → {}`".format(item["case"], item["ref"]) for item in dangling[:20]]
    if not dangling_lines:
        dangling_lines = ["- 无"]
    else:
        if len(dangling) > 20:
            dangling_lines.append(f"- … 还有 {len(dangling) - 20} 条")
    func_cases = sum(len(f["links"]["related_cases"]) for f in functions)
    case_funcs = sum(len(c["related_functions"]) for c in cases)
    return "\n".join(
        [
            "# Human Entry Render Report",
            "",
            "## Source Tables",
            "",
            f"- `{FUNC_SOURCE.relative_to(REPO_ROOT)}`",
            f"- `{CASE_SOURCE.relative_to(REPO_ROOT)}`",
            "",
            "## Counts",
            "",
            f"- 函数：{len(functions)}",
            f"- 案例：{len(cases)}",
            f"- 函数关联案例总数：{func_cases}",
            f"- 案例关联函数总数：{case_funcs}",
            f"- dangling references：{len(dangling)}",
            "",
            "## Dangling References",
            "",
            *dangling_lines,
            "",
        ]
    )


def main() -> None:
    ensure_dir(FUNC_DOC_DIR)
    ensure_dir(CASE_DOC_DIR)
    ensure_dir(OUT_REPORT.parent)

    functions = parse_function_table(FUNC_SOURCE)
    cases = parse_case_table(CASE_SOURCE)
    rel = build_relationships(functions, cases)
    dangling = rel["dangling"]

    # Validation.
    assert len(functions) == 470, len(functions)
    assert len(cases) == 578, len(cases)
    assert len({f["id"] for f in functions}) == len(functions)
    assert len({c["normalized_id"] for c in cases}) == len(cases)
    assert all(f["title"].strip() for f in functions)
    assert all(c["title"].strip() for c in cases)
    assert all(f["source"]["source_table"] and f["source"]["source_line"] for f in functions)
    assert all(c["source"]["source_table"] and c["source"]["source_line"] for c in cases)

    # Generate function/case item pages.
    for func in functions:
        write_text(FUNC_DOC_DIR / f"{func['id']}.md", render_function_page(func))
    for case in cases:
        write_text(CASE_DOC_DIR / f"{case['normalized_id']}.md", render_case_page(case))

    # Root entrance pages and docs indexes.
    write_text(REPO_ROOT / "FUNCTIONS.md", render_functions_root(functions))
    write_text(REPO_ROOT / "CASES.md", render_cases_root(cases))

    func_rows = [
        [
            f"[{f['id']}]({f['links']['human_page']})",
            escape_md(f["title"]),
            escape_md(f["level"]),
            escape_md(f["status"]),
            str(len(f["links"]["related_cases"])),
        ]
        for f in functions
    ]
    case_rows = [
        [
            f"[{c['id']}]({c['links']['human_page']})",
            escape_md(c["title"]),
            escape_md(c["status"]),
            escape_md(" / ".join(c["related_functions"][:3]) if c["related_functions"] else "暂无明确关联函数"),
        ]
        for c in cases
    ]

    write_text(
        FUNC_DOC_INDEX,
        render_index_page(
            "函数索引",
            "从这里按人类阅读顺序浏览 470 条函数，并跳转到单页详情。",
            ["- 机器数据：[`data/functions/unified-functions.json`](../data/functions/unified-functions.json)",
             "- JSONL：[`data/functions/unified-functions.jsonl`](../data/functions/unified-functions.jsonl)",
             "- Root：[`FUNCTIONS.md`](../FUNCTIONS.md)"],
            ["编号", "函数名称", "层级", "状态", "关联案例"],
            func_rows,
        ),
    )
    write_text(
        CASE_DOC_INDEX,
        render_index_page(
            "案例索引",
            "从这里按人类阅读顺序浏览 578 个案例，并跳转到单页详情。",
            ["- 机器数据：[`data/cases/unified-cases.json`](../data/cases/unified-cases.json)",
             "- JSONL：[`data/cases/unified-cases.jsonl`](../data/cases/unified-cases.jsonl)",
             "- Root：[`CASES.md`](../CASES.md)"],
            ["编号", "案例名称", "状态", "关联函数"],
            case_rows,
        ),
    )

    # Machine-readable outputs.
    func_public = [{k: v for k, v in f.items() if not k.startswith("_")} for f in functions]
    case_public = [{k: v for k, v in c.items() if not k.startswith("_")} for c in cases]
    write_json(OUT_FUNC_JSON, func_public)
    write_jsonl(OUT_FUNC_JSONL, func_public)
    write_json(OUT_FUNC_MIN_JSON, minimal_functions(func_public))
    write_text(
        OUT_FUNC_INDEX_MD,
        render_summary_index(
            "函数机器索引",
            ["[`data/functions/unified-functions.json`](unified-functions.json)", "[`data/functions/unified-functions.jsonl`](unified-functions.jsonl)"],
            func_public,
            ["编号", "中文名称", "状态", "路径"],
            lambda f: [f"[{f['id']}](items/{f['id']}.md)", escape_md(f["title"]), escape_md(f["status"]), f"items/{f['id']}.md"],
        ),
    )

    write_json(OUT_CASE_JSON, case_public)
    write_jsonl(OUT_CASE_JSONL, case_public)
    write_json(OUT_CASE_MIN_JSON, minimal_cases(case_public))
    write_text(
        OUT_CASE_INDEX_MD,
        render_summary_index(
            "案例机器索引",
            ["[`data/cases/unified-cases.json`](unified-cases.json)", "[`data/cases/unified-cases.jsonl`](unified-cases.jsonl)"],
            case_public,
            ["编号", "中文名称", "状态", "关联函数数", "路径"],
            lambda c: [
                f"[{c['id']}](items/{c['normalized_id']}.md)",
                escape_md(c["title"]),
                escape_md(c["status"]),
                str(len(c["related_functions"])),
                f"items/{c['normalized_id']}.md",
            ],
        ),
    )

    write_text(OUT_REPORT, make_report(func_public, case_public, dangling))

    update_readme(func_public, case_public)

    print(
        json.dumps(
            {
                "functions": len(func_public),
                "cases": len(case_public),
                "dangling_references": len(dangling),
                "function_pages": len(func_public),
                "case_pages": len(case_public),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
