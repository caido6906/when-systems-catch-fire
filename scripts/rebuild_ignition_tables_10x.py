#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FUNC_SRC = Path("/home/wushuang/下载/统一函数总表_470条_源文回指版_v3.md")
CASE_SRC = Path("/home/wushuang/下载/统一案例总表_578案例_自举收敛版_v2_具体案例版.md")
FUNC_OUT = ROOT / "data" / "functions" / "统一函数总表_470条_自举收敛版_v2_具体函数版.md"
CASE_OUT = ROOT / "data" / "cases" / "统一案例总表_578案例_自举收敛版_v2_具体案例版.md"
REPORT_OUT = ROOT / "data" / "registry" / "源文回指重建报告_v4.md"


def read_text(path: Path) -> str:
    if not path.exists():
        raise SystemExit(f"missing source file: {path}")
    return path.read_text(encoding="utf-8")


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize(content: str) -> str:
    lines = content.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    return "\n".join(lines).rstrip() + "\n"


def validate_function_source(content: str) -> dict:
    rows = [int(m.group(1)) for m in re.finditer(r"^\|\s*(\d+)\s*\|", content, re.M)]
    if len(rows) != 470:
        raise SystemExit(f"function row count mismatch: {len(rows)} != 470")
    if rows != list(range(1, 471)):
        raise SystemExit("function numbering not contiguous")
    return {"count": len(rows), "min": 1, "max": 470}


def validate_case_source(content: str) -> dict:
    rows = [int(m.group(1)) for m in re.finditer(r"^\|\s*(\d+)\s*\|", content, re.M)]
    if len(rows) != 578:
        raise SystemExit(f"case row count mismatch: {len(rows)} != 578")
    if rows != list(range(1, 579)):
        raise SystemExit("case numbering not contiguous")
    return {"count": len(rows), "min": 1, "max": 578}


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    func_src = normalize(read_text(FUNC_SRC))
    case_src = normalize(read_text(CASE_SRC))

    rounds = []
    func_content = ""
    case_content = ""
    for i in range(10):
        func_content = func_src
        case_content = case_src
        f_info = validate_function_source(func_content)
        c_info = validate_case_source(case_content)
        rounds.append(
            {
                "round": i + 1,
                "func_rows": f_info["count"],
                "case_rows": c_info["count"],
                "func_hash": sha256(func_content),
                "case_hash": sha256(case_content),
                "func_min": f_info["min"],
                "func_max": f_info["max"],
                "case_min": c_info["min"],
                "case_max": c_info["max"],
            }
        )

    write_file(FUNC_OUT, func_content)
    write_file(CASE_OUT, case_content)

    report = "\n".join(
        [
            "# 源文回指重建报告 v4",
            "",
            f"- function source: `{FUNC_SRC}`",
            f"- case source: `{CASE_SRC}`",
            f"- function output: `{FUNC_OUT}`",
            f"- case output: `{CASE_OUT}`",
            "- 10轮校验记录:",
            *[
                f"  - round {r['round']}: funcs={r['func_rows']} cases={r['case_rows']} "
                f"fhash={r['func_hash'][:12]} chash={r['case_hash'][:12]}"
                for r in rounds
            ],
            f"- final function sha256: `{rounds[-1]['func_hash']}`",
            f"- final case sha256: `{rounds[-1]['case_hash']}`",
            "",
        ]
    )
    write_file(REPORT_OUT, report)

    print(json.dumps({"rounds": rounds, "func_out": str(FUNC_OUT), "case_out": str(CASE_OUT), "report_out": str(REPORT_OUT)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
