#!/usr/bin/env python3
"""Render bilingual human-readable entrances from unified function/case tables.

The source of truth remains the reconstructed Markdown tables:

* data/functions/统一函数总表_470条_源文交叉重建版_v4.md
* data/cases/统一案例总表_578案例_源文交叉重建版_v4.md

This script converts them into:

* bilingual README entrance
* card-style FUNCTIONS.md / CASES.md
* bilingual docs/zh/functions.md / docs/zh/cases.md
* per-item detail pages
* machine-readable JSON / JSONL / minified JSON / markdown indexes
* a render report with counts and dangling references

The English layer is rule-generated with a conservative glossary. It is useful
for browsing and should still be reviewed by a human later.
"""

from __future__ import annotations

import json
import os
import re
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

README = REPO_ROOT / "README.md"
ROOT_FUNCTIONS = REPO_ROOT / "FUNCTIONS.md"
ROOT_CASES = REPO_ROOT / "CASES.md"
ROOT_DISCOVERIES = REPO_ROOT / "DISCOVERIES.md"
DOC_FUNC_INDEX = REPO_ROOT / "docs/zh/functions.md"
DOC_CASE_INDEX = REPO_ROOT / "docs/zh/cases.md"
DOC_FUNC_DIR = REPO_ROOT / "docs/zh/functions/items"
DOC_CASE_DIR = REPO_ROOT / "docs/zh/cases/items"
DOC_DISC_DIR = REPO_ROOT / "docs/zh/discoveries/items"

OUT_DISC_JSON = REPO_ROOT / "data/discoveries/unified-discoveries.json"
OUT_DISC_JSONL = REPO_ROOT / "data/discoveries/unified-discoveries.jsonl"
OUT_DISC_INDEX_MD = REPO_ROOT / "data/discoveries/unified-discoveries-index.md"


STATUS_TRANSLATIONS = {
    "CROSS_VERIFIED": "交叉验证 / Cross-verified",
    "GETNOTE_ONLY": "仅来自原始笔记 / From source notes only",
    "SINGLE_SOURCE": "单源 / Single source",
}

LEVEL_TRANSLATIONS = {
    "公理": "Axiom",
    "定理": "Theorem",
    "推论": "Derived function",
}

COMMON_TRANSLATIONS: list[tuple[str, str]] = [
    ("模拟8步资源投入", "simulate 8-step resource allocation"),
    ("先防守后进攻", "defend first, attack later"),
    ("级联防御", "cascade defense"),
    ("贪心优化", "greedy optimization"),
    ("门槛附近维度", "threshold-near dimension"),
    ("弹性最高维度", "highest-elasticity dimension"),
    ("无需人为切换", "no manual switching required"),
    ("系统状态", "system state"),
    ("第5步跑通但留隐患", "Step 5 validated but leaves a hidden risk"),
    ("第5步跑通", "Step 5 validated"),
    ("第4步跑通", "Step 4 validated"),
    ("第3步未满足", "Step 3 not satisfied"),
    ("第2步未满足", "Step 2 not satisfied"),
    ("第5步延迟300年", "Step 5 delayed by 300 years"),
    ("资源投入", "resource allocation"),
    ("数学必然", "mathematical necessity"),
    ("提议者意识", "proposer awareness"),
    ("提议者姿态的激进程度", "proposer posture aggressiveness"),
    ("应约者感知退出权", "perceived responder exit right"),
    ("应约者退出权", "responder exit right"),
    ("退出权", "exit right"),
    ("感知退出权", "perceived exit right"),
    ("退出概率", "exit probability"),
    ("退出成本", "exit cost"),
    ("遮蔽函数（双源）", "obscuration function (dual-source)"),
    ("遮蔽函数", "obscuration function"),
    ("遮蔽", "obscuration"),
    ("决策维度", "decision dimension"),
    ("点火充要条件", "ignition necessary and sufficient condition"),
    ("乘法归零律", "multiplication zero law"),
    ("ε双向动力学", "epsilon bidirectional dynamics"),
    ("乘法对称变换", "multiplicative symmetry transform"),
    ("凯利公式认知边界", "Kelly-formula cognitive boundary"),
    ("自举激活条件", "bootstrap activation condition"),
    ("好奇心驱动函数", "curiosity-driven function"),
    ("ε相变级联", "epsilon phase-transition cascade"),
    ("自主意识函数", "autonomous consciousness function"),
    ("缓存倒U型", "cache inverted-U curve"),
    ("生存域函数", "survival domain function"),
    ("信息门效率统一", "information-gate efficiency unification"),
    ("三效率冲突三角约束", "three-efficiency conflict triangle constraint"),
    ("自举元函数层级", "bootstrap meta-function hierarchy"),
    ("乘法临界漂移统一", "multiplicative critical-drift unification"),
    ("两个反向单调函数相乘必然生成倒U型", "two oppositely monotone functions multiplied together necessarily generate an inverted-U curve"),
    ("Φ=零温自由能", "Phi = zero-temperature free energy"),
    ("跨域稳定性定理", "cross-domain stability theorem"),
    ("共生外部注入函数", "symbiotic external-injection function"),
    ("权力腐败函数", "power-corruption function"),
    ("物理大统一本质函数", "physical grand-unification essential function"),
    ("门控函数稳定性必要条件", "necessary condition for gate-function stability"),
    ("高斯门控函数", "Gaussian gate function"),
    ("门控函数进化三阶段", "three-stage evolution of gate functions"),
    ("门控-路径积分同构与极小熵原理", "gate / path-integral isomorphism and minimum-entropy principle"),
    ("门控信息熵跃迁函数", "gate information-entropy transition function"),
    ("认知分辨率函数", "cognitive resolution function"),
    ("A-B型门控面冲突函数", "A-B type gate-surface conflict function"),
    ("量子引力Φ框架函数", "quantum-gravity Phi framework function"),
    ("点火", "Ignition"),
    ("跑通", "validated"),
    ("未满足", "not satisfied"),
    ("部分满足", "partially satisfied"),
    ("进行中", "in progress"),
    ("未在当前函数表中找到", "not found in the current function table"),
    ("未在当前案例表中找到", "not found in the current case table"),
    ("退出权信号", "exit-right signal"),
    ("应约者退出的成本", "responder exit cost"),
    ("认知规范破缺函数", "cognitive norm-breaking function"),
]

CJK_RE = re.compile(r"[\u4e00-\u9fff]")


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


def rel_link(from_path: Path, to_path: Path) -> str:
    return os.path.relpath(to_path, from_path.parent).replace(os.sep, "/")


def is_row(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith("|") and not stripped.startswith("|---")


def normalize_pipe_literals(text: str) -> str:
    return text.replace("\\|", "[[PIPE]]")


def restore_pipe_literals(text: str) -> str:
    return text.replace("[[PIPE]]", "|")


def split_row(line: str) -> List[str]:
    safe = normalize_pipe_literals(line.strip())
    parts = [part.strip() for part in safe.split("|")]
    return [restore_pipe_literals(part) for part in parts]


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


def clean_title(text: str) -> str:
    text = restore_pipe_literals(text).strip()
    text = re.sub(r"[，,。．.\s]+$", "", text)
    return text.strip()


def normalize_signature(text: str) -> str:
    chars: list[str] = []
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


def strip_formula_prefix(text: str) -> str:
    stripped = re.sub(r"^[A-Za-zΦΨΩμσΔεθρλγβ0-9_(),\s]+", "", text).strip()
    return stripped or text.strip()


def translate_text(text: str) -> str:
    if not text:
        return ""

    result = text
    # Longer phrases first.
    for zh, en in sorted(COMMON_TRANSLATIONS, key=lambda item: len(item[0]), reverse=True):
        result = result.replace(zh, en)

    replacements = {
        "（": "(",
        "）": ")",
        "：": ": ",
        "；": "; ",
        "、": ", ",
        "。": ". ",
        "，": ", ",
        "—": " - ",
        "→": " -> ",
        "×": " x ",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "／": "/",
        "｜": "|",
        "\u3000": " ",
    }
    for src, dst in replacements.items():
        result = result.replace(src, dst)

    result = re.sub(r"\s+", " ", result)
    result = result.replace(" ,", ",").replace(" .", ".").replace(" :", ":")
    return result.strip()


def safe_english(text: str) -> str:
    """Return a conservative English rendering with no Chinese characters."""
    if not text:
        return ""
    if CJK_RE.search(text):
        return "Rule-based English rendering pending human review."
    return text


def translate_level(level: str) -> str:
    if level in LEVEL_TRANSLATIONS:
        return LEVEL_TRANSLATIONS[level]
    translated = translate_text(level)
    translated = translated.replace("格 ", "Tier ")
    translated = translated.replace("Tier  ", "Tier ")
    return translated


def translate_status(status: str) -> str:
    return STATUS_TRANSLATIONS.get(status, translate_text(status))


def render_bilingual(zh: str, en: str, label_zh: str = "中文", label_en: str = "English") -> str:
    lines = [f"{label_zh}：{zh or '—'}", f"{label_en}: {en or '—'}"]
    return "\n".join(lines)


def format_bilingual_title(zh: str, en: str) -> str:
    if en and en != zh:
        return f"{zh} / {en}"
    return zh


def parse_function_middle(middle_parts: List[str]) -> tuple[str, str]:
    blob = " | ".join(middle_parts).strip()
    blob = restore_pipe_literals(blob)
    if not blob:
        return "", ""

    if "—" in blob:
        left, right = blob.split("—", 1)
        title = clean_title(normalize_signature(left).strip())
        content = right.strip()
        return title, content

    assign = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*=", blob)
    if assign:
        left = blob[: assign.start()].strip()
        var = assign.group(1)
        right = blob[assign.start():].strip()
        title = clean_title(normalize_signature(left).strip())
        content = right
        if title.endswith(var):
            title = title[: -len(var)].rstrip(" ，,")
        return title, content

    title = clean_title(normalize_signature(blob).strip())
    return title, ""


def parse_case_middle(middle_parts: List[str]) -> tuple[str, str, str]:
    blob = " | ".join(middle_parts).strip()
    blob = restore_pipe_literals(blob)
    if not blob:
        return "", "", ""

    if "—" in blob:
        left, right = blob.split("—", 1)
        title = clean_title(normalize_signature(left).strip())
        content = right.strip()
        return title, content, ""

    assign = re.search(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*=", blob)
    if assign:
        left = blob[: assign.start()].strip()
        var = assign.group(1)
        right = blob[assign.start():].strip()
        title = clean_title(normalize_signature(left).strip())
        if title.endswith(var):
            title = title[: -len(var)].rstrip(" ，,")
        return title, right, ""

    title = clean_title(normalize_signature(blob).strip())
    return title, "", ""


def parse_function_table(path: Path) -> List[dict]:
    lines = read_lines(path)
    header_idx = next((i for i, line in enumerate(lines) if "| 序 | 函数ID |" in line), None)
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
        if len(parts) < 10:
            raise RuntimeError(f"Malformed function row at {path}:{lineno}: {line}")

        seq = parts[1]
        fid = parts[2]
        level_zh = parts[3]
        middle_parts = parts[4:-4]
        source_ref = parts[-4]
        source_type = parts[-3]
        status = parts[-2]

        if len(middle_parts) == 1:
            title_zh = normalize_signature(middle_parts[0]).strip()
            content_zh = ""
        elif len(middle_parts) == 2:
            if not middle_parts[1].strip():
                title_zh = clean_title(normalize_signature(middle_parts[0]).strip())
                content_zh = ""
            elif ("=" in middle_parts[0]) or (middle_parts[0].count("(") > middle_parts[0].count(")")) or middle_parts[0].endswith("("):
                title_zh, content_zh = parse_function_middle(middle_parts)
            else:
                title_zh = clean_title(normalize_signature(middle_parts[0]).strip())
                content_zh = restore_pipe_literals(middle_parts[1].strip())
        else:
            title_zh, content_zh = parse_function_middle(middle_parts)

        if not title_zh.strip():
            title_zh = fid

        concept_zh = strip_formula_prefix(title_zh)
        explanation_zh = (
            f"该函数通过 {content_zh} 描述 {concept_zh}。"
            if content_zh
            else f"该函数用于刻画 {concept_zh}。"
        )

        record = {
            "id": fid,
            "normalized_id": fid,
            "title": {
                "zh": title_zh,
                "en": translate_text(title_zh),
            },
            "title_text": title_zh,
            "level": {
                "zh": level_zh,
                "en": translate_level(level_zh),
            },
            "level_text": level_zh,
            "status": status,
            "status_text": translate_status(status),
            "content": {
                "zh": content_zh,
                "en": translate_text(content_zh) if content_zh else "",
            },
            "explanation": {
                "zh": explanation_zh,
                "en": translate_text(explanation_zh),
            },
            "source": {
                "source_table": str(path.relative_to(REPO_ROOT)),
                "source_line": lineno,
                "source_note_id": source_ref_to_note_id(source_ref),
                "source_file": source_ref_to_file(source_ref),
                "source_reference": source_ref,
                "source_type": source_type,
                "raw_excerpt": line.strip(),
            },
            "links": {
                "human_page": f"docs/zh/functions/items/{fid}.md",
            },
            "_seq": int(seq),
            "_source_middle": " | ".join(middle_parts).strip(),
        }
        records.append(record)

    if len(records) != 470:
        raise RuntimeError(f"Expected 470 functions, parsed {len(records)} from {path}")

    seen = set()
    for record in records:
        if record["id"] in seen:
            raise RuntimeError(f"Duplicate function ID detected: {record['id']}")
        seen.add(record["id"])
        if not record["title"]["zh"].strip():
            raise RuntimeError(f"Empty function title for {record['id']}")
    return records


def parse_case_table(path: Path) -> List[dict]:
    lines = read_lines(path)
    header_idx = next((i for i, line in enumerate(lines) if "| 序 | 案例ID |" in line), None)
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
        if len(parts) < 11:
            raise RuntimeError(f"Malformed case row at {path}:{lineno}: {line}")

        seq = parts[1]
        cid = parts[2]
        title_zh = normalize_signature(parts[3]).strip() or cid
        level_zh = parts[4]
        middle_parts = parts[5:-3]
        source_ref = parts[-3]
        status = parts[-2]

        core_functions_raw = middle_parts[0].strip() if len(middle_parts) >= 1 else ""
        case_description_raw = middle_parts[1].strip() if len(middle_parts) >= 2 else ""
        key_discovery_raw = " | ".join(part.strip() for part in middle_parts[2:]).strip()

        content_lines_zh: list[str] = []
        if case_description_raw:
            content_lines_zh.append(f"案例说明：{case_description_raw}")
        if key_discovery_raw:
            content_lines_zh.append(f"关键发现：{key_discovery_raw}")
        content_zh = "\n".join(content_lines_zh)

        content_lines_en: list[str] = []
        if case_description_raw:
            content_lines_en.append(f"Case description: {translate_text(case_description_raw)}")
        if key_discovery_raw:
            content_lines_en.append(f"Key discovery: {translate_text(key_discovery_raw)}")
        content_en = "\n".join(content_lines_en)

        explanation_zh = key_discovery_raw or case_description_raw or f"该案例围绕 {strip_formula_prefix(title_zh)} 展开。"
        explanation_en = translate_text(explanation_zh)

        numeric_match = re.search(r"#(\d+)", cid)
        numeric = int(numeric_match.group(1)) if numeric_match else 0
        normalized = f"C-{numeric:04d}"

        record = {
            "id": cid,
            "normalized_id": normalized,
            "title": {
                "zh": title_zh,
                "en": translate_text(title_zh),
            },
            "title_text": title_zh,
            "level": {
                "zh": level_zh,
                "en": translate_level(level_zh),
            },
            "level_text": level_zh,
            "status": status,
            "status_text": translate_status(status),
            "content": {
                "zh": content_zh,
                "en": content_en,
            },
            "explanation": {
                "zh": explanation_zh,
                "en": explanation_en,
            },
            "source": {
                "source_table": str(path.relative_to(REPO_ROOT)),
                "source_line": lineno,
                "source_note_id": source_ref_to_note_id(source_ref),
                "source_file": source_ref_to_file(source_ref),
                "source_reference": source_ref,
                "core_functions_raw": core_functions_raw,
                "case_description_raw": case_description_raw,
                "key_discovery_raw": key_discovery_raw,
                "raw_excerpt": line.strip(),
            },
            "links": {
                "human_page": f"docs/zh/cases/items/{normalized}.md",
            },
            "_seq": int(seq),
            "_source_middle": " | ".join(middle_parts).strip(),
        }
        records.append(record)

    if len(records) != 578:
        raise RuntimeError(f"Expected 578 cases, parsed {len(records)} from {path}")

    seen = set()
    for record in records:
        if record["normalized_id"] in seen:
            raise RuntimeError(f"Duplicate case ID detected: {record['normalized_id']}")
        seen.add(record["normalized_id"])
        if not record["title"]["zh"].strip():
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


def dedupe(seq: Iterable[str]) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in seq:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def build_relationships(functions: List[dict], cases: List[dict]) -> dict:
    function_map = {f["id"]: f for f in functions}
    case_map = {c["normalized_id"]: c for c in cases}
    dangling: List[dict] = []

    for case in cases:
        raw_text = " ".join(
            [
                case["title"]["zh"],
                case["source"].get("core_functions_raw", ""),
                case["source"].get("case_description_raw", ""),
                case["source"].get("key_discovery_raw", ""),
            ]
        )
        related_ids = dedupe(extract_function_refs(raw_text))
        case["related_function_ids"] = related_ids
        related_objects = []
        for ref in related_ids:
            if ref in function_map:
                func = function_map[ref]
                related_objects.append(
                    {
                        "id": func["id"],
                        "normalized_id": func["normalized_id"],
                        "title": func["title"],
                        "page": f"docs/zh/functions/items/{func['id']}.md",
                        "found": True,
                    }
                )
            else:
                dangling.append(
                    {
                        "case": case["normalized_id"],
                        "case_title": case["title"]["zh"],
                        "ref": ref,
                        "source_line": case["source"]["source_line"],
                        "source_excerpt": case["source"]["raw_excerpt"],
                    }
                )
                related_objects.append(
                    {
                        "id": ref,
                        "normalized_id": ref,
                        "title": {
                            "zh": f"{ref}（未在当前函数表中找到）",
                            "en": f"{ref} (not found in the current function table)",
                        },
                        "page": None,
                        "found": False,
                    }
                )
        case["related_functions"] = related_objects

    for func in functions:
        related_cases = []
        for case in cases:
            if func["id"] in case.get("related_function_ids", []):
                related_cases.append(
                    {
                        "id": case["id"],
                        "normalized_id": case["normalized_id"],
                        "title": case["title"],
                        "page": f"docs/zh/cases/items/{case['normalized_id']}.md",
                        "found": True,
                    }
                )
        func["related_cases"] = related_cases

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
            "level": f["level"],
            "status": f["status"],
            "related_case_count": len(f.get("related_cases", [])),
            "page": f["links"]["human_page"],
        }
        for f in functions
    ]


def minimal_cases(cases: List[dict]) -> List[dict]:
    return [
        {
            "id": c["id"],
            "normalized_id": c["normalized_id"],
            "title": c["title"],
            "level": c["level"],
            "status": c["status"],
            "related_function_count": len(c.get("related_functions", [])),
            "page": c["links"]["human_page"],
        }
        for c in cases
    ]


def render_markdown_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def render_root_intro(title_zh: str, title_en: str, intro_zh: str, intro_en: str, quick_lines: list[str]) -> str:
    return "\n".join(
        [
            f"# {title_zh} / {title_en}",
            "",
            f"{intro_zh}",
            f"{intro_en}",
            "",
            "## 快速入口 / Quick Entry",
            "",
            *quick_lines,
            "",
        ]
    )


def render_function_detail_link(func: dict) -> str:
    return f"[{format_bilingual_title(func['title']['zh'], func['title']['en'])}]({func['links']['human_page']})"


def render_case_detail_link(case: dict) -> str:
    return f"[{format_bilingual_title(case['title']['zh'], case['title']['en'])}]({case['links']['human_page']})"


def render_related_functions_block(case: dict, current_path: Path, limit: int | None = None) -> str:
    lines: list[str] = []
    for item in case.get("related_functions", [])[: limit or None]:
        if item.get("found"):
            link = rel_link(current_path, REPO_ROOT / item["page"])
            lines.append(f"- [{format_bilingual_title(item['title']['zh'], item['title']['en'])}]({link})")
        else:
            lines.append(f"- {item['title']['zh']} / {item['title']['en']}")
    if not lines:
        lines.append("- 暂无明确关联函数 / No explicit related functions yet.")
    return "\n".join(lines)


def render_related_cases_block(func: dict, current_path: Path, limit: int | None = None) -> str:
    lines: list[str] = []
    for item in func.get("related_cases", [])[: limit or None]:
        link = rel_link(current_path, REPO_ROOT / item["page"])
        lines.append(f"- [{format_bilingual_title(item['title']['zh'], item['title']['en'])}]({link})")
    if not lines:
        lines.append("- 暂无明确关联案例 / No explicit related cases yet.")
    return "\n".join(lines)


def render_function_card(func: dict, current_path: Path, related_limit: int = 5) -> str:
    title = format_bilingual_title(func["title"]["zh"], func["title"]["en"])
    detail_link = rel_link(current_path, REPO_ROOT / func["links"]["human_page"])
    content = func["content"]["zh"] or "暂无内容 / No content"
    content_en = safe_english(func["content"]["en"] or translate_text(content))
    explanation = func["explanation"]["zh"]
    explanation_en = safe_english(func["explanation"]["en"] or translate_text(explanation))
    related_block = render_related_cases_block(func, current_path, limit=related_limit)
    more_line = ""
    if len(func.get("related_cases", [])) > related_limit:
        more_line = f"- 更多 / More: [查看函数详情 / View function page]({detail_link})"

    return "\n".join(
        [
            f"### [{func['id']}｜{title}]({detail_link})",
            "",
            "**函数内容 / Function Content**",
            f"中文：{content}",
            f"English: {content_en}",
            "",
            "**说明 / Explanation**",
            f"中文：{explanation}",
            f"English: {explanation_en}",
            "",
            "**关联案例 / Related Cases**",
            related_block,
            *(["", more_line] if more_line else []),
            "",
        ]
    )


def render_case_card(case: dict, current_path: Path, related_limit: int = 5) -> str:
    title = format_bilingual_title(case["title"]["zh"], case["title"]["en"])
    detail_link = rel_link(current_path, REPO_ROOT / case["links"]["human_page"])
    content = case["content"]["zh"] or "暂无内容 / No content"
    content_en = safe_english(case["content"]["en"] or translate_text(content))
    explanation = case["explanation"]["zh"]
    explanation_en = safe_english(case["explanation"]["en"] or translate_text(explanation))
    related_block = render_related_functions_block(case, current_path, limit=related_limit)
    more_line = ""
    if len(case.get("related_functions", [])) > related_limit:
        more_line = f"- 更多 / More: [查看案例详情 / View case page]({detail_link})"

    return "\n".join(
        [
            f"### [{case['id']}｜{title}]({detail_link})",
            "",
            "**案例内容 / Case Content**",
            f"中文：{content}",
            f"English: {content_en}",
            "",
            "**它说明了什么 / What It Shows**",
            f"中文：{explanation}",
            f"English: {explanation_en}",
            "",
            "**关联函数 / Related Functions**",
            related_block,
            *(["", more_line] if more_line else []),
            "",
        ]
    )


def render_detail_function_page(func: dict) -> str:
    current_path = DOC_FUNC_DIR / f"{func['id']}.md"
    back_to_list = rel_link(current_path, DOC_FUNC_INDEX)
    back_to_root = rel_link(current_path, README)
    title = format_bilingual_title(func["title"]["zh"], func["title"]["en"])

    related_lines: list[str] = []
    for item in func.get("related_cases", []):
        link = rel_link(current_path, REPO_ROOT / item["page"])
        relation_zh = "该案例在源表中引用了该函数。"
        relation_en = "The source table links this case to the function."
        related_lines.append(
            "\n".join(
                [
                    f"- [{format_bilingual_title(item['title']['zh'], item['title']['en'])}]({link})",
                    f"  中文：{relation_zh}",
                    f"  English: {relation_en}",
                ]
            )
        )
    if not related_lines:
        related_lines.append("暂无明确关联案例。\nNo explicit related cases yet.")

    return "\n".join(
        [
            f"# {func['id']}｜{title}",
            "",
            f"[← 返回函数表 / Back to Functions]({back_to_list})",
            f"[返回仓库首页 / Back to Repository Home]({back_to_root})",
            "",
            "## 函数内容 / Function Content",
            "",
            "中文：",
            func["content"]["zh"] or "—",
            "",
            "English:",
            safe_english(func["content"]["en"] or translate_text(func["content"]["zh"])),
            "",
            "## 它解决的问题 / Problem It Addresses",
            "",
            "中文：",
            func["explanation"]["zh"],
            "",
            "English:",
            safe_english(func["explanation"]["en"] or translate_text(func["explanation"]["zh"])),
            "",
            "## 关联案例 / Related Cases",
            "",
            *related_lines,
            "",
            "## 来源回指 / Source Reference",
            "",
            f"- 源总表 / Source table：`{func['source']['source_table']}`",
            f"- 源行 / Source line：{func['source']['source_line']}",
            f"- 来源笔记ID / Source note ID：`{func['source']['source_note_id']}`",
            f"- 来源文件 / Source file：`{func['source']['source_file']}`",
            "",
        ]
    )


def render_detail_case_page(case: dict) -> str:
    current_path = DOC_CASE_DIR / f"{case['normalized_id']}.md"
    back_to_list = rel_link(current_path, DOC_CASE_INDEX)
    back_to_root = rel_link(current_path, README)
    title = format_bilingual_title(case["title"]["zh"], case["title"]["en"])

    related_lines: list[str] = []
    for item in case.get("related_functions", []):
        if item.get("found"):
            link = rel_link(current_path, REPO_ROOT / item["page"])
            relation_zh = "该函数在源表中帮助解释本案例。"
            relation_en = "The function helps explain this case in the source table."
            related_lines.append(
                "\n".join(
                    [
                        f"- [{format_bilingual_title(item['title']['zh'], item['title']['en'])}]({link})",
                        f"  中文：{relation_zh}",
                        f"  English: {relation_en}",
                    ]
                )
            )
        else:
            related_lines.append(
                "\n".join(
                    [
                        f"- {item['title']['zh']}",
                        f"  中文：未在当前函数表中找到。",
                        f"  English: Not found in the current function table.",
                    ]
                )
            )
    if not related_lines:
        related_lines.append("暂无明确关联函数。\nNo explicit related functions yet.")

    return "\n".join(
        [
            f"# {case['normalized_id']}｜{title}",
            "",
            f"[← 返回案例表 / Back to Cases]({back_to_list})",
            f"[返回仓库首页 / Back to Repository Home]({back_to_root})",
            "",
            "## 案例内容 / Case Content",
            "",
            "中文：",
            case["content"]["zh"] or "—",
            "",
            "English:",
            safe_english(case["content"]["en"] or translate_text(case["content"]["zh"])),
            "",
            "## 它说明了什么 / What It Shows",
            "",
            "中文：",
            case["explanation"]["zh"],
            "",
            "English:",
            safe_english(case["explanation"]["en"] or translate_text(case["explanation"]["zh"])),
            "",
            "## 关联函数 / Related Functions",
            "",
            *related_lines,
            "",
            "## 来源回指 / Source Reference",
            "",
            f"- 源总表 / Source table：`{case['source']['source_table']}`",
            f"- 源行 / Source line：{case['source']['source_line']}",
            f"- 来源笔记ID / Source note ID：`{case['source']['source_note_id']}`",
            f"- 来源文件 / Source file：`{case['source']['source_file']}`",
            "",
        ]
    )


def group_functions(functions: List[dict]) -> list[tuple[str, list[dict], bool]]:
    order = ["公理", "定理", "推论"]
    grouped: list[tuple[str, list[dict], bool]] = []
    for level in order:
        items = [f for f in functions if f["level"]["zh"] == level]
        if items:
            grouped.append((level, items, level == "公理"))
    other_levels = [lvl for lvl in sorted({f["level"]["zh"] for f in functions}) if lvl not in order]
    for level in other_levels:
        items = [f for f in functions if f["level"]["zh"] == level]
        if items:
            grouped.append((level, items, False))
    return grouped


def group_cases(cases: List[dict]) -> list[tuple[str, list[dict], bool]]:
    grouped: list[tuple[str, list[dict], bool]] = []
    for start in range(1, 579, 100):
        end = min(start + 99, 578)
        items = [c for c in cases if start <= c["_seq"] <= end]
        if items:
            grouped.append((f"#{start}–#{end}", items, start == 1))
    return grouped


def render_functions_collection(functions: List[dict], current_path: Path) -> str:
    quick_lines = [
        f"- 公理层 / Axioms：{sum(1 for f in functions if f['level']['zh'] == '公理')} 条 / {sum(1 for f in functions if f['level']['zh'] == '公理')} entries",
        f"- 定理层 / Theorems：{sum(1 for f in functions if f['level']['zh'] == '定理')} 条 / {sum(1 for f in functions if f['level']['zh'] == '定理')} entries",
        f"- 推论层 / Derived functions：{sum(1 for f in functions if f['level']['zh'] == '推论')} 条 / {sum(1 for f in functions if f['level']['zh'] == '推论')} entries",
        f"- 机器数据 / Machine data：[`data/functions/unified-functions.json`](data/functions/unified-functions.json)",
        f"- JSONL：[`data/functions/unified-functions.jsonl`](data/functions/unified-functions.jsonl)",
        f"- 重建审计 / Rebuild audit：[`data/rebuild/human-entry-render-report.md`](data/rebuild/human-entry-render-report.md)",
    ]
    parts = [
        render_root_intro(
            "统一函数总表",
            "Unified Function Table",
            "本表收录 470 条点火函数。每条函数都包含编号、名称、函数内容、关联案例和来源回指。",
            "This table contains 470 ignition functions. Each function includes its ID, title, content, related cases, and source reference.",
            quick_lines,
        ),
    ]
    for level, items, open_flag in group_functions(functions):
        parts.extend(
            [
                f"<details{' open' if open_flag else ''}>",
                f"<summary>{level} / {translate_level(level)} ({len(items)})</summary>",
                "",
            ]
        )
        for func in items:
            parts.append(render_function_card(func, current_path))
        parts.append("</details>")
        parts.append("")
    return "\n".join(parts)


def render_cases_collection(cases: List[dict], current_path: Path) -> str:
    quick_lines = [
        f"- #1–#100",
        f"- #101–#200",
        f"- #201–#300",
        f"- #301–#400",
        f"- #401–#500",
        f"- #501–#578",
        f"- 机器数据 / Machine data：[`data/cases/unified-cases.json`](data/cases/unified-cases.json)",
        f"- JSONL：[`data/cases/unified-cases.jsonl`](data/cases/unified-cases.jsonl)",
        f"- 重建审计 / Rebuild audit：[`data/rebuild/human-entry-render-report.md`](data/rebuild/human-entry-render-report.md)",
    ]
    parts = [
        render_root_intro(
            "统一案例总表",
            "Unified Case Table",
            "本表收录 578 个点火案例。每个案例都包含编号、案例内容、关联函数和来源回指。",
            "This table contains 578 ignition cases. Each case includes its ID, content, related functions, and source reference.",
            quick_lines,
        ),
    ]
    for label, items, open_flag in group_cases(cases):
        parts.extend(
            [
                f"<details{' open' if open_flag else ''}>",
                f"<summary>{label} / {label}</summary>",
                "",
            ]
        )
        for case in items:
            parts.append(render_case_card(case, current_path))
        parts.append("</details>")
        parts.append("")
    return "\n".join(parts)


def render_index_page(
    title_zh: str,
    title_en: str,
    intro_zh: str,
    intro_en: str,
    links: list[str],
    headers: Sequence[str],
    rows: Sequence[Sequence[str]],
) -> str:
    parts = [
        f"# {title_zh} / {title_en}",
        "",
        intro_zh,
        intro_en,
        "",
        *links,
        "",
        render_markdown_table(headers, rows),
        "",
    ]
    return "\n".join(parts)


def update_readme() -> None:
    text = README.read_text(encoding="utf-8")
    top_intro = "\n".join(
        [
            "# When Systems Catch Fire / 点火",
            "",
            "《点火》不是一本固定成书，而是一个开放维护的函数与案例知识库。",
            "When Systems Catch Fire is not a fixed book, but an open and maintained knowledge base of functions and cases.",
            "",
            "## 入口 / Entrance",
            "",
            "| 区域 / Area | 内容 / Content |",
            "|---|---|",
            "| [发现 / Discoveries](DISCOVERIES.md) | 从函数与案例的自举循环中产生的新发现。每条发现都可连接到相关函数、案例和来源。 / New discoveries generated from bootstrap cycles between functions and cases. Each discovery links to related functions, cases, and sources. |",
            "| [预测 / Predictions](PREDICTIONS.md) | 由函数、案例、发现与自举循环推出的可检验未来判断。 / Testable future judgments derived from functions, cases, discoveries, and bootstrap cycles. |",
            "| [函数表 / Functions](FUNCTIONS.md) | 470 条函数。每条函数都可查看定义、公式、来源与关联案例。 / 470 functions. Each function links to its definition, expression, source, and related cases. |",
            "| [案例表 / Cases](CASES.md) | 578 个案例。每个案例都可查看内容、来源与关联函数。 / 578 cases. Each case links to its content, source, and related functions. |",
            "",
        ]
    )

    current_block = "\n".join(
        [
            "## Current Structure / 当前结构",
            "",
            "| Layer | 中文说明 | 主要文件 / Files |",
            "| --- | --- | --- |",
            "| Functions | 点火函数层，保存 D-X 函数及其结构化字段 | `data/functions/unified-functions.json`, `data/functions/unified-functions.jsonl`, `data/functions/items/` |",
            "| Cases | 案例层，保存案例与函数关系 | `data/cases/unified-cases.json`, `data/cases/unified-cases.jsonl`, `data/cases/items/` |",
            "| Discoveries | 新发现说明层，面向人类阅读和传播 | `DISCOVERIES.md`, `data/discoveries/unified-discoveries.json`, `data/discoveries/unified-discoveries.jsonl`, `docs/zh/discoveries/items/` |",
            "| Predictions | 预测说明层，面向人类阅读和验证 | `PREDICTIONS.md`, `data/predictions/unified-predictions.json`, `data/predictions/unified-predictions.jsonl`, `docs/zh/predictions/items/` |",
            "| Registry | 原始统一总表，作为生成 JSON 的来源 | `data/registry/统一函数总表.csv`, `data/registry/统一案例总表.csv` |",
            "| Legacy Book | 旧书籍结构，保留为历史材料 | `archive/book-legacy/` |",
            "| Raw Notes | 原始笔记与来源材料，不作为 canonical item | `dianhuo/originals/` |",
            "",
        ]
    )

    agents_block = "\n".join(
        [
            "## For AI Agents / 给 AI Agent",
            "",
            "1. Read `llms.txt`.",
            "2. Read `AGENT_ENTRY.md`.",
            "3. Use `data/functions/unified-functions.jsonl` for function lookup.",
            "4. Use `data/cases/unified-cases.jsonl` for case lookup.",
            "5. Use `data/discoveries/unified-discoveries.jsonl` for structured discovery entries.",
            "6. Use `data/predictions/unified-predictions.jsonl` for structured prediction entries.",
            "7. Use `data/functions/items/*.json` and `data/cases/items/*.json` as canonical machine-readable records.",
            "",
            "Do not treat raw notes as canonical. Raw notes are sources. Current structured entries live under `data/functions/`, `data/cases/`, `data/discoveries/`, and `data/predictions/`.",
            "",
        ]
    )

    human_block = "\n".join(
        [
            "## Human Reading / 人类阅读入口",
            "",
            "- 中文函数入口 / Chinese functions: `FUNCTIONS.md`, `docs/zh/functions.md`",
            "- 中文案例入口 / Chinese cases: `CASES.md`, `docs/zh/cases.md`",
            "- 中文发现入口 / Chinese discoveries: `DISCOVERIES.md`, `docs/zh/discoveries/items/`",
            "- 中文预测入口 / Chinese predictions: `PREDICTIONS.md`, `docs/zh/predictions/items/`",
            "",
        ]
    )

    current_idx = text.find("## Current Structure / 当前结构")
    data_policy_idx = text.find("## Data Policy / 数据原则")
    if current_idx == -1 or data_policy_idx == -1:
        write_text(README, top_intro + text)
        return

    tail = text[data_policy_idx:]
    write_text(README, top_intro + "\n" + current_block + "\n" + agents_block + "\n" + human_block + tail)


def make_report(functions: List[dict], cases: List[dict], dangling: List[dict]) -> str:
    func_cases = sum(len(f.get("related_cases", [])) for f in functions)
    case_funcs = sum(len(c.get("related_functions", [])) for c in cases)
    dangling_lines = [
        f"- {item['case']} → {item['ref']} (line {item['source_line']})"
        for item in dangling[:30]
    ]
    if not dangling_lines:
        dangling_lines = ["- 无 / None"]
    elif len(dangling) > 30:
        dangling_lines.append(f"- … 还有 {len(dangling) - 30} 条 / {len(dangling) - 30} more")

    return "\n".join(
        [
            "# Human Entry Render Report / 人类入口渲染报告",
            "",
            "## Source Tables / 源表",
            "",
            f"- `{FUNC_SOURCE.relative_to(REPO_ROOT)}`",
            f"- `{CASE_SOURCE.relative_to(REPO_ROOT)}`",
            "",
            "## Counts / 数量",
            "",
            f"- 函数 / Functions：{len(functions)}",
            f"- 案例 / Cases：{len(cases)}",
            f"- 函数关联案例总数 / Function-related cases：{func_cases}",
            f"- 案例关联函数总数 / Case-related functions：{case_funcs}",
            f"- dangling references：{len(dangling)}",
            "",
            "## Dangling References / 悬空引用",
            "",
            *dangling_lines,
            "",
            "## Translation Note / 翻译说明",
            "",
            "English text was rule-generated and needs later human review.",
            "英文为规则翻译，后续仍需人工校订。",
            "",
            "## English Status / 英文状态",
            "",
            "中文：当前英文层为规则翻译，已去除明显中英混杂句，但仍需要后续人工校订。",
            "English: The current English layer is rule-generated. Obvious Chinese-English mixed sentences have been removed, but later human review is still required.",
            "",
        ]
    )


def write_outputs(functions: List[dict], cases: List[dict], dangling: List[dict]) -> None:
    ensure_dir(DOC_FUNC_DIR)
    ensure_dir(DOC_CASE_DIR)
    ensure_dir(OUT_REPORT.parent)

    for func in functions:
        write_text(DOC_FUNC_DIR / f"{func['id']}.md", render_detail_function_page(func))
    for case in cases:
        write_text(DOC_CASE_DIR / f"{case['normalized_id']}.md", render_detail_case_page(case))

    write_text(ROOT_FUNCTIONS, render_functions_collection(functions, ROOT_FUNCTIONS))
    write_text(ROOT_CASES, render_cases_collection(cases, ROOT_CASES))
    write_text(DOC_FUNC_INDEX, render_functions_collection(functions, DOC_FUNC_INDEX))
    write_text(DOC_CASE_INDEX, render_cases_collection(cases, DOC_CASE_INDEX))

    func_public = [{k: v for k, v in f.items() if not k.startswith("_")} for f in functions]
    case_public = [{k: v for k, v in c.items() if not k.startswith("_")} for c in cases]

    write_json(OUT_FUNC_JSON, func_public)
    write_jsonl(OUT_FUNC_JSONL, func_public)
    write_json(OUT_FUNC_MIN_JSON, minimal_functions(func_public))

    func_rows = [
        [
            f"[{f['id']}]({f['links']['human_page']})",
            format_bilingual_title(f["title"]["zh"], f["title"]["en"]),
            f"{f['level']['zh']} / {f['level']['en']}",
            f["status_text"],
            str(len(f.get("related_cases", []))),
        ]
        for f in func_public
    ]
    write_text(
        OUT_FUNC_INDEX_MD,
        render_index_page(
            "函数机器索引",
            "Function Machine Index",
            "机器可读索引，保留中文标题、英文标题、层级、状态和关联计数。",
            "Machine-readable index that keeps Chinese titles, English titles, levels, status, and relation counts.",
            [
                "- [`data/functions/unified-functions.json`](unified-functions.json)",
                "- [`data/functions/unified-functions.jsonl`](unified-functions.jsonl)",
            ],
            ["编号 / ID", "名称 / Title", "层级 / Level", "状态 / Status", "关联案例 / Related cases"],
            func_rows,
        ),
    )

    write_json(OUT_CASE_JSON, case_public)
    write_jsonl(OUT_CASE_JSONL, case_public)
    write_json(OUT_CASE_MIN_JSON, minimal_cases(case_public))

    case_rows = [
        [
            f"[{c['id']}]({c['links']['human_page']})",
            format_bilingual_title(c["title"]["zh"], c["title"]["en"]),
            f"{c['level']['zh']} / {c['level']['en']}",
            c["status_text"],
            str(len(c.get("related_functions", []))),
        ]
        for c in case_public
    ]
    write_text(
        OUT_CASE_INDEX_MD,
        render_index_page(
            "案例机器索引",
            "Case Machine Index",
            "机器可读索引，保留中文标题、英文标题、层级、状态和关联计数。",
            "Machine-readable index that keeps Chinese titles, English titles, levels, status, and relation counts.",
            [
                "- [`data/cases/unified-cases.json`](unified-cases.json)",
                "- [`data/cases/unified-cases.jsonl`](unified-cases.jsonl)",
            ],
            ["编号 / ID", "名称 / Title", "层级 / Level", "状态 / Status", "关联函数 / Related functions"],
            case_rows,
        ),
    )

    write_text(OUT_REPORT, make_report(func_public, case_public, dangling))
    update_readme()

    print(
        json.dumps(
            {
                "functions": len(func_public),
                "cases": len(case_public),
                "function_pages": len(list(DOC_FUNC_DIR.glob("*.md"))),
                "case_pages": len(list(DOC_CASE_DIR.glob("*.md"))),
                "dangling_references": len(dangling),
            },
            ensure_ascii=False,
        )
    )


def validate_outputs(functions: List[dict], cases: List[dict]) -> None:
    assert len(functions) == 470, len(functions)
    assert len(cases) == 578, len(cases)
    assert len({f["id"] for f in functions}) == len(functions)
    assert len({c["normalized_id"] for c in cases}) == len(cases)
    assert all(f["title"]["zh"].strip() for f in functions)
    assert all(c["title"]["zh"].strip() for c in cases)
    assert all(f["source"]["source_table"] and f["source"]["source_line"] for f in functions)
    assert all(c["source"]["source_table"] and c["source"]["source_line"] for c in cases)


def main() -> None:
    functions = parse_function_table(FUNC_SOURCE)
    cases = parse_case_table(CASE_SOURCE)
    rel = build_relationships(functions, cases)
    dangling = rel["dangling"]

    validate_outputs(functions, cases)
    write_outputs(functions, cases, dangling)

    # Lightweight post-write checks.
    func_pages = list(DOC_FUNC_DIR.glob("*.md"))
    case_pages = list(DOC_CASE_DIR.glob("*.md"))
    assert len(func_pages) == 470, len(func_pages)
    assert len(case_pages) == 578, len(case_pages)
    assert ROOT_FUNCTIONS.exists()
    assert ROOT_CASES.exists()
    assert DOC_FUNC_INDEX.exists()
    assert DOC_CASE_INDEX.exists()


if __name__ == "__main__":
    main()
