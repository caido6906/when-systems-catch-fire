#!/usr/bin/env python3
"""Incremental extractor for function and case registries from GetNote originals.

Operational design:
- Reads raw note files from dianhuo/originals/
- Extracts function candidates (D-X* patterns, "函数", etc.)
- Extracts case candidates (案例, 政策, 公司, 国家, etc.)
- Appends/merges into CSV registries
- Tracks processed files via sha256 in processed-notes.jsonl
- Safe: never rewrites existing canonical tables, never deletes

Usage:
    python3 tools/extract-registry.py --repo-root . --notes-dir dianhuo/originals --verbose
    python3 tools/extract-registry.py --dry-run --limit 5
    python3 tools/extract-registry.py --since-unprocessed --verbose
"""

import argparse
import csv
import hashlib
import io
import json
import os
import re
import sys
from datetime import datetime, timezone


# ── Config ──────────────────────────────────────────────────────────────────

FUNCTION_KEYWORDS = [
    "函数", "函数表", "输入", "输出", "规则", "判断",
    "派生", "方程", "阈值", "压缩", "映射", "干预",
    "级联", "阻尼", "衰减", "免疫", "遮蔽", "退化",
]

CASE_KEYWORDS = [
    "案例", "政策", "公司", "国家", "事件", "监管",
    "财政", "改革", "制度", "基金", "税收", "债务",
    "都市圈", "转移支付", "分税制", "自给率",
]

FUNC_ID_PATTERN = re.compile(r'(D-X\d+|F-\d{8}-\d+)')
NOTE_ID_PATTERN = re.compile(r'^(\d{19})_')

CSV_FIELD_SIZE = 100000  # Increase limit for large CSV fields

# Default paths (relative to repo root)
DEFAULT_DATA_DIR = "data/registry"
DEFAULT_NOTES_DIR = "dianhuo/originals"
DEFAULT_FUNC_CSV = os.path.join(DEFAULT_DATA_DIR, "ignition-function-registry.csv")
DEFAULT_CASE_CSV = os.path.join(DEFAULT_DATA_DIR, "ignition-case-registry.csv")
DEFAULT_PROCESSED = os.path.join(DEFAULT_DATA_DIR, "processed-notes.jsonl")

FUNC_HEADER = [
    "func_id", "func_label", "func_type", "source_note_id", "source_file",
    "domain_layer", "formula_or_rule", "inputs", "output",
    "decision_logic", "confidence", "status",
    "collides_with_existing", "cross_refs",
    "created_at", "updated_at",
]

CASE_HEADER = [
    "case_id", "case_name", "source_note_id", "source_file",
    "case_type", "framework_location", "function_ref",
    "event_layer", "participant_scale",
    "verification_status", "status", "cross_refs",
    "summary", "created_at", "updated_at",
]


# ── Helpers ─────────────────────────────────────────────────────────────────

def sha256_file(filepath):
    """Compute SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
    except (OSError, IOError):
        return None
    return h.hexdigest()


def extract_note_id(filename):
    """Extract note ID from filename prefix."""
    m = NOTE_ID_PATTERN.match(os.path.basename(filename))
    if m:
        return m.group(1)
    return ""


def extract_func_id(text):
    """Find D-X* style function IDs in text."""
    matches = FUNC_ID_PATTERN.findall(text)
    return matches


def classify_func_type(text):
    """Classify function type based on content hints."""
    text_lower = text.lower()
    if any(k in text for k in ["函数表", "function_table"]):
        return "function_table"
    if any(k in text for k in ["预测", "prediction"]):
        return "prediction_function"
    if any(k in text for k in ["诊断", "diagnostic"]):
        return "diagnostic_function"
    if any(k in text for k in ["警告", "warning"]):
        return "warning_function"
    if any(k in text for k in ["案例映射", "case_mapping"]):
        return "case_mapping_function"
    return "candidate"


def classify_domain_layer(text, source_file):
    """Classify which layer the function belongs to."""
    text_lower = text.lower()
    source_lower = source_file.lower()
    if "碰撞" in text or "碰撞层" in text or "collision" in text_lower:
        return "collision_layer"
    if "事件条件" in text or "event_condition" in text_lower:
        return "event_condition"
    if "案例" in text or "case" in text_lower:
        return "case_validation"
    if any(k in source_lower for k in ["政策", "policy", "财政", "基金"]):
        return "policy_case"
    return "unknown"


def classify_case_type(text, source_file):
    """Classify case type based on content hints."""
    text_lower = text.lower()
    source_lower = source_file.lower()
    if "历史" in text or any(c in text for c in ["周公", "秦", "唐", "汉", "宋", "明", "清"]):
        return "historical_case"
    if "政策" in text or "政策" in source_lower or "政策" in text_lower:
        return "policy_case"
    if "公司" in text or any(k in text_lower for k in ["公司", "企业", "基金", "投资"]):
        return "company_case"
    if "人际" in text or "人际" in text_lower:
        return "interpersonal_case"
    if "预测" in text:
        return "prediction_case"
    if "边界" in text:
        return "boundary_case"
    return "candidate"


def classify_framework_location(text):
    """Guess the framework location for a case."""
    text_lower = text.lower()
    if "事件条件矩阵" in text or "event_condition" in text_lower or "matrix" in text_lower:
        return "event_condition_matrix"
    if "negat" in text_lower or "negative_time" in text_lower or "负时间" in text:
        return "negative_time_gap"
    if "proposal" in text_lower or "提议" in text:
        return "proposal_miscarriage"
    if "退出权" in text or "exit" in text_lower:
        return "exit_rights_layer"
    return "unknown"


def guess_event_layer(text):
    """Guess event layer from text."""
    text_lower = text.lower()
    if "人际" in text or "interpersonal" in text_lower or "dyadic" in text_lower:
        return "interpersonal"
    if "团队" in text or "小团队" in text or "small_team" in text_lower:
        return "team"
    if "公司" in text or "company" in text_lower or "企业" in text:
        # Only mark as company if text is about a specific company, not general policy
        if "公司" in text and not any(kw in text for kw in ["政策", "监管", "国务院", "国办", "财政", "税"]):
            return "company"
    if "国家" in text or "national" in text_lower or "policy" in text_lower or "财政" in text or "监管" in text or "国务院" in text:
        return "policy"
    if "文明" in text or "civilizational" in text_lower or "civilization" in text_lower:
        return "civilization"
    return "unknown"


def guess_participant_scale(text):
    """Guess participant scale from text."""
    text_lower = text.lower()
    if "dyadic" in text_lower or "双人" in text or "两个人" in text:
        return "dyadic"
    if "small_group" in text_lower or "小群体" in text or "小团队" in text:
        return "small_group"
    if "large_group" in text_lower or "大群体" in text:
        return "large_group"
    if "civilizational" in text_lower or "civilization" in text_lower or "文明" in text:
        return "civilizational_population"
    return "unknown"


def extract_formula_block(text):
    """Extract formula/rule block from text. Looks for lines with math-like content."""
    lines = text.split("\n")
    formulas = []
    for line in lines:
        line = line.strip()
        # Match lines with math notation: Greek letters, equations, function defs
        if re.search(r'(σ|ε|α|β|π|λ|μ|ν|ρ|σ\(|=.*\(|d[A-Z]/dt|≈)', line):
            if any(kw in line for kw in ["=", "函数", "公式", "方程", "定义", "派生"]):
                formulas.append(line)
        elif re.search(r'【|】|【公式】|【定义】', line):
            # Skip purely structural markers without content
            pass
    return " | ".join(formulas[:5])  # Limit to first 5 formula lines


def extract_summary(text, max_len=200):
    """Extract a one-sentence summary from the first meaningful paragraph."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    for p in paragraphs:
        # Skip headers
        if p.startswith("#"):
            continue
        # Skip very short lines
        if len(p) < 10:
            continue
        # Take first meaningful paragraph
        summary = p[:max_len]
        if len(p) > max_len:
            summary += "…"
        return summary
    return text[:max_len]


def detect_collisions(existing_funcs, new_func):
    """Check if a new function might collide with existing ones."""
    if not existing_funcs:
        return False
    new_id = new_func.get("func_id", "")
    new_label = new_func.get("func_label", "")
    # Exact func_id match
    if new_id and any(e.get("func_id") == new_id for e in existing_funcs if e.get("func_id")):
        return True
    # Similar label (simplified: contains same key terms)
    if new_label:
        new_terms = set(re.findall(r'[\u4e00-\u9fff]{2,}', new_label))
        for e in existing_funcs:
            e_label = e.get("func_label", "")
            if e_label:
                e_terms = set(re.findall(r'[\u4e00-\u9fff]{2,}', e_label))
                if new_terms & e_terms and len(new_terms) > 3:
                    overlap_ratio = len(new_terms & e_terms) / max(len(new_terms), len(e_terms))
                    if overlap_ratio > 0.5:
                        return True
    return False


# ── CSV I/O ─────────────────────────────────────────────────────────────────

def load_existing_csv(filepath, header):
    """Load existing CSV entries into a list of dicts."""
    entries = []
    if not os.path.exists(filepath):
        return entries
    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames:
                for row in reader:
                    entries.append(row)
    except (OSError, csv.Error) as e:
        print(f"  ⚠️  Warning: could not read {filepath}: {e}", file=sys.stderr)
    return entries


def save_csv(filepath, header, entries):
    """Append entries to CSV file, creating it with header if needed."""
    write_header = not os.path.exists(filepath)
    with open(filepath, "a", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header, lineterminator="\n")
        if write_header:
            writer.writeheader()
        for entry in entries:
            writer.writerow({h: entry.get(h, "") for h in header})


def load_processed_index(filepath):
    """Load processed notes index (JSONL format)."""
    if not os.path.exists(filepath):
        return []
    entries = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if isinstance(obj, dict):
                        entries.append(obj)
                except json.JSONDecodeError:
                    continue
    except OSError:
        pass
    return entries


def append_processed_entry(filepath, entry):
    """Append a processed note entry to the JSONL index."""
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ── Extraction ──────────────────────────────────────────────────────────────

def extract_functions_from_text(text, note_id, source_file):
    """Extract function candidates from raw note text."""
    functions = []

    # Strategy 1: Extract D-X* numbered items (most reliable)
    # Find "新增碰撞层派生 D-X16：..." blocks
    func_pattern = re.compile(
        r'新增.*?派生\s+(D-X\d+)[：:]\s*([^\n]+)',
        re.MULTILINE
    )
    for m in func_pattern.finditer(text):
        fid = m.group(1)
        label = m.group(2).strip()
        # Strip trailing markdown bold markers
        label = re.sub(r'\*+$', '', label).strip()
        # Get formula/context around this function
        start = m.start()
        context = text[start:start + 500]
        formula = extract_formula_block(context)
        func_type = classify_func_type(context)
        domain = classify_domain_layer(context, source_file)

        func = {
            "func_id": fid,
            "func_label": label,
            "func_type": func_type,
            "source_note_id": note_id,
            "source_file": source_file,
            "domain_layer": domain,
            "formula_or_rule": formula,
            "inputs": "unknown",
            "output": "unknown",
            "decision_logic": "",
            "confidence": "medium",
            "status": "candidate",
            "collides_with_existing": "",
            "cross_refs": "",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        functions.append(func)

    # Strategy 2: Extract explicit "函数" definitions without D-X* numbering
    if not any(f["func_id"] for f in functions):
        # Look for patterns like "X(t) = ..." or "k = ..." in a function context
        explicit_formula_lines = []
        in_func_block = False
        current_block = []

        for line in text.split("\n"):
            line_s = line.strip()
            # Detect start of a function block
            if any(kw in line_s for kw in ["函数定义", "函数表达式", "完整形式", "完整方程"]):
                in_func_block = True
                current_block = [line_s]
                continue

            if in_func_block:
                current_block.append(line_s)
                # End of block or start of next section
                if re.match(r'^(##|[0-9]、|\n{2,}|来源：)', line_s):
                    block_text = " ".join(current_block)
                    if "=" in block_text or "(" in block_text:
                        explicit_formula_lines.append(block_text)
                    in_func_block = False
                    current_block = []

        for block in explicit_formula_lines:
            if any(kw in block for kw in FUNCTION_KEYWORDS):
                func_type = classify_func_type(block)
                formula = extract_formula_block(block)
                if formula:
                    # Try to extract label from context
                    label_match = re.search(r'([^\n=]+(?:函数|公式|方程))', block)
                    label = label_match.group(1).strip() if label_match else "unnamed_function"

                    func = {
                        "func_id": "",
                        "func_label": label,
                        "func_type": func_type,
                        "source_note_id": note_id,
                        "source_file": source_file,
                        "domain_layer": classify_domain_layer(block, source_file),
                        "formula_or_rule": formula,
                        "inputs": "unknown",
                        "output": "unknown",
                        "decision_logic": "",
                        "confidence": "low",
                        "status": "needs_review",
                        "collides_with_existing": "",
                        "cross_refs": "",
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "updated_at": datetime.now(timezone.utc).isoformat(),
                    }
                    functions.append(func)

    return functions


def extract_cases_from_text(text, note_id, source_file):
    """Extract case candidates from raw note text."""
    cases = []

    # Strategy 1: Look for explicit "案例" sections
    # Pattern: "**案例**：..." or "案例：" or "案例一：" etc.
    case_patterns = [
        re.compile(r'\*\*案例\*\*[：:]\s*(.+?)(?=\n\n|\*\*[^\*]+\*\*[：:]|---|$)', re.MULTILINE),
        re.compile(r'案例[一二三四五六七八九十\d]*[：:]\s*(.+?)(?=\n\n|\*\*|---|$)', re.MULTILINE),
        re.compile(r'案例\s*#\d+[：:]\s*(.+?)(?=\n\n|\*\*|---|$)', re.MULTILINE),
    ]

    for pattern in case_patterns:
        for m in pattern.finditer(text):
            case_text = m.group(1).strip()
            if len(case_text) < 5:
                continue
            case_type = classify_case_type(case_text, source_file)
            framework = classify_framework_location(case_text)
            event_layer = guess_event_layer(case_text)
            scale = guess_participant_scale(case_text)

            case = {
                "case_id": "",
                "case_name": case_text[:80],
                "source_note_id": note_id,
                "source_file": source_file,
                "case_type": case_type,
                "framework_location": framework,
                "function_ref": "",
                "event_layer": event_layer,
                "participant_scale": scale,
                "verification_status": "working_hypothesis",
                "status": "candidate",
                "cross_refs": "",
                "summary": extract_summary(case_text, 200),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            cases.append(case)

    # Strategy 2: Look for policy/news items with clear "事件" markers
    if not cases:
        # Check if the entire note is about a policy/news event
        policy_indicators = ["政策", "监管", "国务院", "财政部", "证监会", "指导意见", "通知", "国办", "文件"]
        if any(kw in text for kw in policy_indicators):
            summary = extract_summary(text, 200)
            # Extract a short case name from the filename (remove note ID prefix)
            short_name = os.path.basename(source_file)
            short_name = re.sub(r'^\d{19}_', '', short_name)
            short_name = re.sub(r'\.md$', '', short_name)
            case = {
                "case_id": "",
                "case_name": short_name[:80],
                "source_note_id": note_id,
                "source_file": source_file,
                "case_type": "policy_case",
                "framework_location": "unknown",
                "function_ref": "",
                "event_layer": guess_event_layer(text),
                "participant_scale": guess_participant_scale(text),
                "verification_status": "unknown",
                "status": "candidate",
                "cross_refs": "",
                "summary": summary,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            cases.append(case)

    return cases


# ── Dedup & Merge ──────────────────────────────────────────────────────────

def func_key(entry):
    """Generate dedup key for a function entry."""
    if entry.get("func_id"):
        return f"id:{entry['func_id']}"
    return f"label:{entry.get('func_label', '')}|source:{entry.get('source_note_id', '')}"


def case_key(entry):
    """Generate dedup key for a case entry."""
    name = entry.get("case_name", "")
    source = entry.get("source_note_id", "")
    return f"{name}|{source}"


def merge_entries(existing, new_entries, key_fn):
    """Merge new entries into existing, dedup by key_fn. Return (merged, new_only)."""
    existing_keys = set()
    existing_by_key = {}
    for e in existing:
        k = key_fn(e)
        existing_keys.add(k)
        existing_by_key[k] = e

    new_only = []
    merged = list(existing)
    for ne in new_entries:
        k = key_fn(ne)
        if k in existing_keys:
            # Merge: update timestamps, keep existing data
            if k in existing_by_key:
                existing_by_key[k]["updated_at"] = datetime.now(timezone.utc).isoformat()
        else:
            new_only.append(ne)
            merged.append(ne)

    return merged, new_only


# ── Main Logic ──────────────────────────────────────────────────────────────

def process_file(filepath, notes_dir, dry_run, verbose):
    """Process a single raw note file."""
    rel_path = os.path.relpath(filepath, notes_dir)
    note_id = extract_note_id(filepath)
    file_sha = sha256_file(filepath)

    if file_sha is None:
        if verbose:
            print(f"  ⚠️  Cannot read: {rel_path}", file=sys.stderr)
        return None, 0, 0

    # Read file content
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError) as e:
        print(f"  ⚠️  Cannot read {rel_path}: {e}", file=sys.stderr)
        return rel_path, 0, 0

    # Extract (always extract, even in dry-run — just don't write in dry-run)
    functions = extract_functions_from_text(text, note_id, rel_path)
    cases = extract_cases_from_text(text, note_id, rel_path)

    if verbose:
        n_funcs = len(functions)
        n_cases = len(cases)
        print(f"  📄 {rel_path}")
        if n_funcs:
            print(f"    → {n_funcs} function(s) extracted:")
            for fn in functions:
                fid = fn['func_id'] or "(unnamed)"
                print(f"      {fid}: {fn['func_label'][:60]}")
        if n_cases:
            print(f"    → {n_cases} case(s) extracted:")
            for cs in cases:
                print(f"      {cs['case_name'][:60]}")

    # Update processed index entry
    processed_entry = {
        "source_file": rel_path,
        "source_note_id": note_id,
        "sha256": file_sha,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "functions_added": len(functions),
        "cases_added": len(cases),
        "status": "processed",
    }

    # Always return a consistent 6-tuple:
    # (rel_path, n_functions, n_cases, processed_entry_or_None, functions_or_None, cases_or_None)
    return rel_path, len(functions), len(cases), processed_entry, functions, cases


def main():
    parser = argparse.ArgumentParser(
        description="Incremental extractor for function and case registries from GetNote originals"
    )
    parser.add_argument("--repo-root", default=".", help="Repository root directory")
    parser.add_argument("--notes-dir", default=None, help="Raw notes directory (default: dianhuo/originals)")
    parser.add_argument("--limit", type=int, default=0, help="Max files to process (0=all)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be extracted without writing")
    parser.add_argument("--since-unprocessed", action="store_true", help="Only process unprocessed files")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    notes_dir = os.path.join(repo_root, args.notes_dir if args.notes_dir else DEFAULT_NOTES_DIR)
    data_dir = os.path.join(repo_root, DEFAULT_DATA_DIR)
    func_csv = os.path.join(data_dir, "ignition-function-registry.csv")
    case_csv = os.path.join(data_dir, "ignition-case-registry.csv")
    processed_file = os.path.join(data_dir, "processed-notes.jsonl")

    # Validate
    if not os.path.isdir(notes_dir):
        print(f"❌ Notes directory not found: {notes_dir}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(data_dir, exist_ok=True)

    # Load processed index
    processed_index = load_processed_index(processed_file)
    processed_map = {
        e["source_file"]: e for e in processed_index
    }

    # Load existing registries
    existing_funcs = load_existing_csv(func_csv, FUNC_HEADER)
    existing_cases = load_existing_csv(case_csv, CASE_HEADER)

    # Discover files — sort by mtime (newest first) so --limit targets recent notes
    all_files = []
    for fname in os.listdir(notes_dir):
        if fname.endswith((".md", ".txt")):
            all_files.append(os.path.join(notes_dir, fname))
    all_files.sort(key=lambda p: os.path.getmtime(p), reverse=True)

    if not all_files:
        print("⚠️  No files found in notes directory")
        sys.exit(0)

    # Filter: only unprocessed if --since-unprocessed
    if args.since_unprocessed:
        filtered = []
        for f in all_files:
            rel = os.path.relpath(f, notes_dir)
            if rel not in processed_map:
                filtered.append(f)
            else:
                old_sha = processed_map[rel].get("sha256", "")
                cur_sha = sha256_file(f)
                if old_sha != cur_sha:
                    if args.verbose:
                        print(f"  🔄 Changed: {rel}")
                    filtered.append(f)
                elif args.verbose:
                    print(f"  ⏭️  Skip (unchanged): {rel}")
        all_files = filtered or all_files  # fallback to all if none changed

    # Limit
    if args.limit > 0:
        all_files = all_files[:args.limit]

    if not all_files:
        print("✅ Nothing to process")
        sys.exit(0)

    if args.dry_run:
        print(f"🔍 DRY RUN: would process {len(all_files)} files")
        print("=" * 60)

    total_funcs = 0
    total_cases = 0
    new_entries = []
    processed_entries = []

    for filepath in all_files:
        result = process_file(filepath, notes_dir, args.dry_run, args.verbose)
        if result is None:
            continue

        if args.dry_run:
            rel_path, nf, nc = result[:3]
            total_funcs += nf
            total_cases += nc
            continue

        rel_path, nf, nc = result[:3]

        # Only update index if we extracted something
        if nf > 0 or nc > 0:
            processed_entry = result[3]
            new_entries.append((rel_path, nf, nc, processed_entry))
            total_funcs += nf
            total_cases += nc

    if args.dry_run:
        print("=" * 60)
        print(f"Would extract: {total_funcs} function(s), {total_cases} case(s) from {len(all_files)} file(s)")
        return

    # If no new extractions, we're done
    if total_funcs == 0 and total_cases == 0:
        print(f"✅ Processed {len(all_files)} files, 0 new functions and 0 new cases")
        return

    # Merge functions
    new_funcs = []
    for item in new_entries:
        # We need the actual extracted functions; re-read isn't possible from result
        # So we store them during process_file. Let's adjust: re-extract for merging
        pass

    # Actually, let's restructure: re-extract from files that had new entries
    # This is simpler and ensures we have the full data for merging
    files_to_merge = [item[0] for item in new_entries]  # rel_path list

    all_new_funcs = []
    all_new_cases = []
    all_processed = []

    for rel_path, nf, nc, processed_entry in new_entries:
        full_path = os.path.join(notes_dir, rel_path)
        note_id = extract_note_id(full_path)
        funcs = extract_functions_from_text(open(full_path, "r", encoding="utf-8").read(), note_id, rel_path)
        cases = extract_cases_from_text(open(full_path, "r", encoding="utf-8").read(), note_id, rel_path)
        all_new_funcs.extend(funcs)
        all_new_cases.extend(cases)
        all_processed.append(processed_entry)

    # Dedup and merge
    merged_funcs, just_new_funcs = merge_entries(existing_funcs, all_new_funcs, func_key)
    merged_cases, just_new_cases = merge_entries(existing_cases, all_new_cases, case_key)

    # Save
    save_csv(func_csv, FUNC_HEADER, just_new_funcs)
    save_csv(case_csv, CASE_HEADER, just_new_cases)

    # Update processed index
    for pe in all_processed:
        # Remove old entry if exists, add updated
        processed_index = [e for e in processed_index if e.get("source_file") != pe["source_file"]]
        append_processed_entry(processed_file, pe)

    print(f"✅ Done: {len(all_files)} files processed")
    print(f"   Functions: {total_funcs} extracted, {len(just_new_funcs)} new entries added")
    print(f"   Cases:     {total_cases} extracted, {len(just_new_cases)} new entries added")
    print(f"   Registries: {func_csv}, {case_csv}")
    print(f"   Index: {processed_file}")

    if args.verbose:
        print()
        if just_new_funcs:
            print("New functions:")
            for f in just_new_funcs:
                print(f"  {f['func_id'] or '(unnamed)'}: {f['func_label'][:50]}")
        if just_new_cases:
            print("New cases:")
            for c in just_new_cases:
                print(f"  {c['case_name'][:50]}")


if __name__ == "__main__":
    main()
