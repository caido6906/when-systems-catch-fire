#!/usr/bin/env python3
"""Rebuild unified function and case tables from original note files.

This script:
1. Scans dianhuo/originals/ for files containing unified function/case tables
2. Parses Markdown tables from those files
3. Filters entries: only keeps rows with valid ID and valid name
4. Writes quarantine report for rejected rows
5. Overwrites 统一函数总表.csv and 统一案例总表.csv
6. Does NOT touch canonical or any other files

Usage:
    python3 tools/rebuild-unified-registry.py --repo-root .
    python3 tools/rebuild-unified-registry.py --repo-root . --dry-run
"""

import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict


# ── Config ──────────────────────────────────────────────────────────────────

DEFAULT_DATA_DIR = "data/registry"
DEFAULT_NOTES_DIR = "dianhuo/originals"

UNIFIED_FUNC_CSV = os.path.join(DEFAULT_DATA_DIR, "统一函数总表.csv")
UNIFIED_CASE_CSV = os.path.join(DEFAULT_DATA_DIR, "统一案例总表.csv")
PROCESSED_FILE = os.path.join(DEFAULT_DATA_DIR, "processed-notes.jsonl")

UNIFIED_FUNC_HEADER = [
    "函数ID", "函数名称", "函数类型", "输入变量", "输出判断", "规则摘要", "操作用途", "关联案例",
    "来源笔记ID", "来源文件", "来源哈希", "首次发现时间", "最后更新时间", "状态", "置信度", "备注",
]

UNIFIED_CASE_HEADER = [
    "案例ID", "案例名称", "案例类型", "框架位置", "关联函数ID", "事件层级", "参与者规模",
    "验证状态", "状态", "交叉引用", "摘要", "来源笔记ID", "来源文件", "来源哈希",
    "首次发现时间", "最后更新时间", "备注",
]

# Aliases for column matching in markdown tables
_FUNC_ALIASES = {
    "函数ID": ["函数ID", "编号", "func_id", "ID", "序号"],
    "函数名称": ["函数名称", "名称", "函数名", "func_label", "label"],
    "函数类型": ["函数类型", "类型", "func_type"],
    "输入变量": ["输入变量", "输入", "inputs", "input"],
    "输出判断": ["输出判断", "输出", "output"],
    "规则摘要": ["规则摘要", "规则", "判断逻辑", "rule_summary", "rule"],
    "操作用途": ["操作用途", "用途", "operational_use"],
    "关联案例": ["关联案例", "关联函数", "related_case", "cross_refs"],
    "状态": ["状态", "status"],
    "置信度": ["置信度", "confidence"],
    "备注": ["备注", "note"],
}

_CASE_ALIASES = {
    "案例ID": ["案例ID", "编号", "case_id", "ID", "序号"],
    "案例名称": ["案例名称", "名称", "案例", "case_name", "label"],
    "案例类型": ["案例类型", "类型", "case_type"],
    "框架位置": ["框架位置", "框架", "framework_location", "location"],
    "关联函数ID": ["关联函数ID", "关联函数", "function_ref", "func_ref"],
    "事件层级": ["事件层级", "层级", "event_layer"],
    "参与者规模": ["参与者规模", "规模", "participant_scale", "scale"],
    "验证状态": ["验证状态", "验证", "verification_status", "vstatus"],
    "状态": ["状态", "status"],
    "交叉引用": ["交叉引用", "cross_refs", "refs"],
    "摘要": ["摘要", "summary", "desc"],
    "备注": ["备注", "note"],
}


# ── Markdown table parser ──────────────────────────────────────────────────

def parse_markdown_tables(text):
    """Parse markdown tables from text. Returns list of (header_cells, data_rows)."""
    tables = []
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if "|" in line and not line.startswith("|-") and not line.startswith("-|") and not line.startswith("---"):
            header_cells = [c.strip() for c in line.split("|")[1:-1]]
            if header_cells and any(h for h in header_cells):
                data_rows = []
                i += 1
                while i < len(lines):
                    sep = lines[i].strip()
                    if re.match(r'^\|?[\s:|-]*\|?$', sep) and "---" in sep.replace(" ", "").replace(":", ""):
                        i += 1
                        continue
                    if "|" in sep:
                        cells = [c.strip() for c in sep.split("|")[1:-1]]
                        if any(c for c in cells):  # skip empty separator-like rows
                            # Pad or truncate to header length
                            if len(cells) < len(header_cells):
                                cells += [""] * (len(header_cells) - len(cells))
                            elif len(cells) > len(header_cells):
                                cells = cells[:len(header_cells)]
                            data_rows.append(cells)
                        i += 1
                    else:
                        break
                if data_rows:
                    tables.append((header_cells, data_rows))
            else:
                i += 1
        else:
            i += 1
    return tables


def _build_col_map(header_cells, aliases):
    """Build {target_header: column_index} mapping."""
    col_map = {}
    for target, aliases_list in aliases.items():
        lower_aliases = [a.lower() for a in aliases_list]
        for idx, cell in enumerate(header_cells):
            if cell.lower() in lower_aliases:
                col_map[target] = idx
                break
    return col_map


def _row_to_dict(row_cells, col_map):
    """Map row cells to dict."""
    d = {}
    for target, idx in col_map.items():
        if idx < len(row_cells):
            d[target] = row_cells[idx].strip()
        else:
            d[target] = ""
    return d


# ── Validation ──────────────────────────────────────────────────────────────

def is_valid_func_id(fid):
    """Check if function ID is valid (non-empty, D-X* format, not dash)."""
    fid = (fid or "").strip()
    if not fid:
        return False
    if fid in {"—", "-", "无", "N/A"}:
        return False
    if fid.startswith("D-X"):
        return True
    # Accept other known ID formats: D74 etc if they come from source with names
    # But only if they match expected pattern (single letter + digits)
    if re.match(r'^[A-Z]\d+$', fid):
        return True
    return False


def is_valid_case_id(cid):
    """Check if case ID is valid (non-empty, not unknown, not dash)."""
    cid = (cid or "").strip()
    if not cid:
        return False
    if cid.startswith("C-unknown"):
        return False
    if cid in {"—", "-", "无", "N/A"}:
        return False
    return True


def has_valid_name(entry, key="函数名称"):
    """Check if entry has a non-empty name."""
    return bool((entry.get(key, "") or "").strip())


# ── Detection ───────────────────────────────────────────────────────────────

def detect_table_type(filepath):
    """Detect if a file contains unified function table or case table."""
    name = os.path.basename(filepath)
    first_lines = ""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            first_lines = "\n".join(f.readlines()[:5])
    except (OSError, UnicodeDecodeError):
        pass
    haystack = f"{name}\n{first_lines}"
    if "统一函数总表" in haystack:
        return "function"
    if "统一案例总表" in haystack:
        return "case"
    return None


# ── Processing ──────────────────────────────────────────────────────────────

def sha256_file(filepath):
    h = __import__('hashlib').sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
    except (OSError, IOError):
        return None
    return h.hexdigest()


def extract_note_id(filename):
    m = re.match(r'^(\d{19})_', os.path.basename(filename))
    return m.group(1) if m else ""


def generate_func_id(note_id, note_hash, idx):
    return f"D-auto-{note_id}-{idx}"


def generate_case_id(note_id, note_hash, idx):
    return f"C-auto-{note_id}-{idx}"


def process_function_table(source_dir, dry_run=False):
    """Process unified function table notes and rebuild."""
    now = datetime.now(timezone.utc).isoformat()
    valid_funcs = []
    quarantined = []
    source_files_processed = []
    seen_ids = set()

    for fname in sorted(os.listdir(source_dir)):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(source_dir, fname)
        if not os.path.isfile(fpath):
            continue
        table_type = detect_table_type(fpath)
        if table_type != "function":
            continue

        rel_path = os.path.relpath(fpath, source_dir)
        with open(fpath, "r", encoding="utf-8") as f:
            text = f.read()

        note_id = extract_note_id(fname)
        file_hash = sha256_file(fpath)
        tables = parse_markdown_tables(text)

        for header_cells, data_rows in tables:
            col_map = _build_col_map(header_cells, _FUNC_ALIASES)
            if not col_map:
                continue

            for row_cells in data_rows:
                entry = _row_to_dict(row_cells, col_map)
                fid = entry.get("函数ID", "").strip()
                name = entry.get("函数名称", "").strip()

                # Validate
                if not fid or not name:
                    quarantined.append({
                        "source_file": rel_path,
                        "function_id": fid,
                        "function_name": name,
                        "reason": "empty ID or name",
                        "all_fields": entry,
                    })
                    continue

                if not is_valid_func_id(fid):
                    # Try to generate a new valid ID from name
                    if len(quarantined) < 100:  # limit quarantine dump
                        quarantined.append({
                            "source_file": rel_path,
                            "function_id": fid,
                            "function_name": name,
                            "reason": f"invalid function ID format: {fid}",
                            "all_fields": entry,
                        })
                    continue

                if fid in seen_ids:
                    quarantined.append({
                        "source_file": rel_path,
                        "function_id": fid,
                        "function_name": name,
                        "reason": "duplicate ID",
                        "all_fields": entry,
                    })
                    continue

                seen_ids.add(fid)
                entry["来源笔记ID"] = note_id
                entry["来源文件"] = rel_path
                entry["来源哈希"] = file_hash or ""
                entry["首次发现时间"] = now
                entry["最后更新时间"] = now
                entry.setdefault("状态", "fact_checked")
                entry.setdefault("置信度", "high")

                # Ensure all header fields exist
                for h in UNIFIED_FUNC_HEADER:
                    if h not in entry:
                        entry[h] = ""

                valid_funcs.append(entry)

        source_files_processed.append(rel_path)

    # Sort by function ID
    valid_funcs.sort(key=lambda x: x.get("函数ID", ""))

    if not dry_run:
        # Write valid CSV
        with open(os.path.join(source_dir, "..", "..", UNIFIED_FUNC_CSV), "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=UNIFIED_FUNC_HEADER, lineterminator="\n")
            writer.writeheader()
            for entry in valid_funcs:
                writer.writerow({h: entry.get(h, "") for h in UNIFIED_FUNC_HEADER})

        # Write quarantine CSV
        if quarantined:
            quarantine_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..", "projects", "when-systems-catch-fire", "grs-10", "reports", "quarantined-functions.csv"
            )
            quarantine_dir = os.path.dirname(quarantine_path)
            os.makedirs(quarantine_dir, exist_ok=True)
            with open(quarantine_path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["source_file", "function_id", "function_name", "reason", "all_fields"], lineterminator="\n")
                writer.writeheader()
                for q in quarantined:
                    writer.writerow({
                        "source_file": q["source_file"],
                        "function_id": q["function_id"],
                        "function_name": q["function_name"],
                        "reason": q["reason"],
                        "all_fields": json.dumps(q["all_fields"], ensure_ascii=False),
                    })

    return valid_funcs, quarantined, source_files_processed


def process_case_table(source_dir, dry_run=False):
    """Process unified case table notes and rebuild."""
    now = datetime.now(timezone.utc).isoformat()
    valid_cases = []
    quarantined = []
    source_files_processed = []
    seen_ids = set()

    for fname in sorted(os.listdir(source_dir)):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(source_dir, fname)
        if not os.path.isfile(fpath):
            continue
        table_type = detect_table_type(fpath)
        if table_type != "case":
            continue

        rel_path = os.path.relpath(fpath, source_dir)
        with open(fpath, "r", encoding="utf-8") as f:
            text = f.read()

        note_id = extract_note_id(fname)
        file_hash = sha256_file(fpath)
        tables = parse_markdown_tables(text)

        for header_cells, data_rows in tables:
            col_map = _build_col_map(header_cells, _CASE_ALIASES)
            if not col_map:
                continue

            # Check if this is a "summary" row (e.g., case table by layer)
            # These have IDs like "84,89,90" or "1-18" which are summary references
            # Not individual cases - skip them
            first_id = ""
            col_idx = col_map.get("案例ID")
            for row in data_rows[:3]:
                fid_cell = row[col_idx] if col_idx is not None and col_idx < len(row) else ""
                if fid_cell:
                    first_id = fid_cell
                    break

            # Detect summary/compact table format:
            # Format A: "序号 | 案例 | 8格 | 方向 | 状态 | ..." (case name in col 1, seq num in col 0)
            # Format B: "案例ID | 案例名称 | 案例类型 | ..." (proper ID column)
            # Format C: IDs like "84,89,90" (layer summary referencing multiple cases)
            is_summary_table = False
            if col_idx is not None:
                # Check if first_id looks like a layer summary (comma-separated)
                if "," in first_id or "→" in first_id:
                    is_summary_table = True
                # Check if the table has a "案例" column but no "案例名称" column
                # (meaning "案例" is the name column, and "序号"/"案例ID" maps to seq number)
                elif "案例名称" not in col_map and "案例" in header_cells:
                    is_summary_table = True
                # Also check if case_id values are pure digits
                elif re.match(r'^\d+$', first_id.strip()):
                    is_summary_table = True

            if is_summary_table:
                # Summary table: "序号 | 案例 | 8格 | 方向 | 状态 | ..."
                # The "序号" column has numbers like 1, 2, 3...
                # The "案例" column has case names like 周公制礼, 孔子作春秋...
                # We need to map differently
                seq_idx = None
                name_idx = None

                # Try to find the "序号" and "案例" columns
                for idx, cell in enumerate(header_cells):
                    if cell in ("序号", "编号", "No.", "#"):
                        seq_idx = idx
                    if cell in ("案例", "案例名称", "Name", "name"):
                        name_idx = idx

                if seq_idx is not None and name_idx is not None:
                    # This is a case table with 序号|案例 columns
                    # Generate proper C-XXX IDs from sequence numbers
                    used_seq = set()
                    for row in data_rows:
                        if seq_idx >= len(row) or name_idx >= len(row):
                            continue
                        seq_num = row[seq_idx].strip()
                        case_name = row[name_idx].strip()

                        # Skip empty rows
                        if not seq_num or not case_name:
                            continue

                        # Try to parse sequence number
                        try:
                            seq_int = int(seq_num)
                        except ValueError:
                            # Non-numeric sequences (like summary rows referencing ranges) - skip
                            continue

                        if seq_int in used_seq:
                            continue
                        used_seq.add(seq_int)

                        case_id = f"C-{seq_int:03d}"
                        if case_id in seen_ids:
                            continue

                        seen_ids.add(case_id)
                        entry = _row_to_dict(row, col_map)
                        entry["案例ID"] = case_id
                        entry["案例名称"] = case_name
                        entry["来源笔记ID"] = note_id
                        entry["来源文件"] = rel_path
                        entry["来源哈希"] = file_hash or ""
                        entry["首次发现时间"] = now
                        entry["最后更新时间"] = now
                        entry.setdefault("状态", "fact_checked")

                        for h in UNIFIED_CASE_HEADER:
                            if h not in entry:
                                entry[h] = ""

                        valid_cases.append(entry)
                else:
                    # Can't find proper columns - quarantine all rows
                    for row in data_rows:
                        quarantined.append({
                            "source_file": rel_path,
                            "reason": f"summary table without identifiable ID/name columns (headers: {','.join(header_cells[:10])})",
                            "all_fields": ",".join(row),
                        })
            else:
                # Regular case table with proper ID column
                for row in data_rows:
                    entry = _row_to_dict(row, col_map)
                    cid = entry.get("案例ID", "").strip()
                    cname = entry.get("案例名称", "").strip()

                    if not cid or not cname:
                        quarantined.append({
                            "source_file": rel_path,
                            "case_id": cid,
                            "case_name": cname,
                            "reason": "empty ID or name",
                            "all_fields": json.dumps(entry, ensure_ascii=False),
                        })
                        continue

                    if not is_valid_case_id(cid):
                        quarantined.append({
                            "source_file": rel_path,
                            "case_id": cid,
                            "case_name": cname,
                            "reason": f"invalid case ID: {cid}",
                            "all_fields": json.dumps(entry, ensure_ascii=False),
                        })
                        continue

                    if cid in seen_ids:
                        quarantined.append({
                            "source_file": rel_path,
                            "case_id": cid,
                            "case_name": cname,
                            "reason": "duplicate ID",
                            "all_fields": json.dumps(entry, ensure_ascii=False),
                        })
                        continue

                    seen_ids.add(cid)
                    entry["来源笔记ID"] = note_id
                    entry["来源文件"] = rel_path
                    entry["来源哈希"] = file_hash or ""
                    entry["首次发现时间"] = now
                    entry["最后更新时间"] = now
                    entry.setdefault("状态", "fact_checked")

                    for h in UNIFIED_CASE_HEADER:
                        if h not in entry:
                            entry[h] = ""

                    valid_cases.append(entry)

        source_files_processed.append(rel_path)

    # Sort by case ID
    valid_cases.sort(key=lambda x: x.get("案例ID", ""))

    if not dry_run:
        # Write valid CSV
        with open(os.path.join(source_dir, "..", "..", UNIFIED_CASE_CSV), "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=UNIFIED_CASE_HEADER, lineterminator="\n")
            writer.writeheader()
            for entry in valid_cases:
                writer.writerow({h: entry.get(h, "") for h in UNIFIED_CASE_HEADER})

        # Write quarantine CSV
        if quarantined:
            quarantine_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "..", "projects", "when-systems-catch-fire", "grs-10", "reports", "quarantined-cases.csv"
            )
            quarantine_dir = os.path.dirname(quarantine_path)
            os.makedirs(quarantine_dir, exist_ok=True)
            with open(quarantine_path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["source_file", "case_id", "case_name", "reason", "all_fields"], lineterminator="\n")
                writer.writeheader()
                for q in quarantined:
                    writer.writerow({
                        "source_file": q["source_file"],
                        "case_id": q.get("case_id", ""),
                        "case_name": q.get("case_name", ""),
                        "reason": q["reason"],
                        "all_fields": q.get("all_fields", ""),
                    })

    return valid_cases, quarantined, source_files_processed


def main():
    parser = argparse.ArgumentParser(description="Rebuild unified registry from original notes")
    parser.add_argument("--repo-root", default=".", help="Repository root directory")
    parser.add_argument("--notes-dir", default=None, help="Notes directory (default: <repo>/dianhuo/originals)")
    parser.add_argument("--data-dir", default=None, help="Data directory (default: <repo>/data/registry)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without modifying files")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    notes_dir = Path(args.notes_dir) if args.notes_dir else repo_root / "dianhuo" / "originals"
    data_dir = Path(args.data_dir) if args.data_dir else repo_root / "data" / "registry"

    if not notes_dir.exists():
        print(f"ERROR: Notes directory not found: {notes_dir}")
        sys.exit(1)

    print(f"Notes directory: {notes_dir}")
    print(f"Data directory: {data_dir}")
    print()

    # Process function table
    print("=" * 60)
    print("处理统一函数总表")
    print("=" * 60)
    func_valid, func_quarantined, func_sources = process_function_table(str(notes_dir), dry_run=args.dry_run)
    print(f"有效函数条目: {len(func_valid)}")
    print(f"隔离条目: {len(func_quarantined)}")
    print(f"来源文件: {len(func_sources)}")
    if func_sources:
        for s in func_sources[:5]:
            print(f"  - {s}")
    if len(func_sources) > 5:
        print(f"  ... and {len(func_sources) - 5} more")
    print()

    # Process case table
    print("=" * 60)
    print("处理统一案例总表")
    print("=" * 60)
    case_valid, case_quarantined, case_sources = process_case_table(str(notes_dir), dry_run=args.dry_run)
    print(f"有效案例条目: {len(case_valid)}")
    print(f"隔离条目: {len(case_quarantined)}")
    print(f"来源文件: {len(case_sources)}")
    if case_sources:
        for s in case_sources[:5]:
            print(f"  - {s}")
    if len(case_sources) > 5:
        print(f"  ... and {len(case_sources) - 5} more")
    print()

    # Summary
    print("=" * 60)
    print("重建摘要")
    print("=" * 60)
    print(f"函数表: {len(func_valid)} 有效 | {len(func_quarantined)} 隔离")
    print(f"案例表: {len(case_valid)} 有效 | {len(case_quarantined)} 隔离")

    if args.dry_run:
        print("\n[DRY RUN] 未修改任何文件。去除此标志以应用更改。")
    else:
        print("\n✅ 重建完成。请运行 validate-registry-integrity.py 验证。")


if __name__ == "__main__":
    main()
