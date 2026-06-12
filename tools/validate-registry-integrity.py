#!/usr/bin/env python3
"""Strict validation for unified function and case registry tables.

Read-only: never modifies files.
Exit 0 if all checks pass, exit 1 if any severe issues found.

Rules:
1. No empty function/case ID
2. No empty function/case name
3. No F-unknown-* IDs
4. No C-unknown-* IDs
5. No "—" or "-" as valid ID
6. No duplicate IDs (except C-unknown where we count total)
7. No D-prefixed IDs that are not D-X*
8. No completely empty rows
"""

import csv
import sys
from pathlib import Path
from collections import Counter

REGISTRY_DIR = Path(__file__).parent.parent / "data" / "registry"
FUNC_CSV = REGISTRY_DIR / "统一函数总表.csv"
CASE_CSV = REGISTRY_DIR / "统一案例总表.csv"


def validate_function_table():
    """Validate unified function table."""
    errors = []
    warnings = []

    if not FUNC_CSV.exists():
        errors.append("FATAL: 统一函数总表.csv 不存在")
        return errors, warnings, 0

    rows = list(csv.DictReader(FUNC_CSV.open(encoding="utf-8-sig", newline="")))
    total = len(rows)

    if total == 0:
        errors.append("FATAL: 函数表为空")
        return errors, warnings, total

    # Check for empty IDs
    empty_id = [r for r in rows if not r.get("函数ID", "").strip()]
    if empty_id:
        errors.append(f"SEVERE: 有 {len(empty_id)} 条函数记录 ID 为空")

    # Check for empty names
    empty_name = [r for r in rows if not r.get("函数名称", "").strip()]
    if empty_name:
        errors.append(f"SEVERE: 有 {len(empty_name)} 条函数记录名称为空")

    # Check for F-unknown-*
    f_unknown = [r for r in rows if r.get("函数ID", "").startswith("F-unknown")]
    if f_unknown:
        errors.append(f"SEVERE: 发现 {len(f_unknown)} 条 F-unknown-* 编号")

    # Check for "—" or "-" as ID
    dash_id = [r for r in rows if r.get("函数ID", "").strip() in {"—", "-", "无", "N/A"}]
    if dash_id:
        errors.append(f"SEVERE: 发现 {len(dash_id)} 条以 '{dash_id[0]['函数ID']}' 作为编号的记录")

    # Check for non-D-X* D-prefixed IDs
    bad_d = [r for r in rows if r.get("函数ID", "").startswith("D") and not r.get("functionID", "").startswith("D-X") and not r.get("函数ID", "").startswith("D-X")]
    if bad_d:
        bad_ids = set(r.get("函数ID", "").strip() for r in bad_d)
        errors.append(f"SEVERE: 发现 {len(bad_d)} 条 D-prefixed 但不是 D-X* 格式的编号: {', '.join(sorted(bad_ids))}")

    # Check for duplicate IDs
    id_counter = Counter(r.get("函数ID", "").strip() for r in rows if r.get("函数ID", "").strip())
    dup_ids = {k: v for k, v in id_counter.items() if v > 1 and k}
    if dup_ids:
        errors.append(f"SEVERE: 发现 {len(dup_ids)} 个重复编号: {dup_ids}")

    # Summary
    print(f"=== 统一函数总表诊断 ===")
    print(f"总条目数: {total}")
    print(f"空ID: {len(empty_id)}")
    print(f"空名称: {len(empty_name)}")
    print(f"F-unknown-*: {len(f_unknown)}")
    print(f"非法编号('—','-'): {len(dash_id)}")
    print(f"非D-X*的D-prefixed: {len(bad_d)}")
    print(f"重复编号: {len(dup_ids)}")
    print()

    if errors:
        print(f"❌ 验证失败，发现 {len(errors)} 个严重问题:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("✅ 函数表验证通过")

    return errors, warnings, total


def validate_case_table():
    """Validate unified case table."""
    errors = []
    warnings = []

    if not CASE_CSV.exists():
        errors.append("FATAL: 统一案例总表.csv 不存在")
        return errors, warnings, 0

    rows = list(csv.DictReader(CASE_CSV.open(encoding="utf-8-sig", newline="")))
    total = len(rows)

    if total == 0:
        errors.append("FATAL: 案例表为空")
        return errors, warnings, total

    # Check for empty IDs
    empty_id = [r for r in rows if not r.get("案例ID", "").strip()]
    if empty_id:
        errors.append(f"SEVERE: 有 {len(empty_id)} 条案例记录 ID 为空")

    # Check for empty names
    empty_name = [r for r in rows if not r.get("案例名称", "").strip()]
    if empty_name:
        errors.append(f"SEVERE: 有 {len(empty_name)} 条案例记录名称为空")

    # Check for C-unknown-*
    c_unknown = [r for r in rows if r.get("案例ID", "").startswith("C-unknown")]
    if c_unknown:
        errors.append(f"SEVERE: 发现 {len(c_unknown)} 条 C-unknown-* 编号")

    # Check for completely empty rows (all fields empty)
    empty_rows = [r for r in rows if not any(v.strip() for v in r.values() if v)]
    if empty_rows:
        errors.append(f"SEVERE: 发现 {len(empty_rows)} 条完全空的记录行")

    # Check for duplicate IDs
    id_counter = Counter(r.get("案例ID", "").strip() for r in rows if r.get("案例ID", "").strip())
    dup_ids = {k: v for k, v in id_counter.items() if v > 1 and k and not k.startswith("C-unknown")}
    if dup_ids:
        errors.append(f"WARNING: 发现 {len(dup_ids)} 个重复编号（不含 C-unknown）: 最大重复数={max(dup_ids.values())}")

    # Check for CSV misalignment (too many/few fields)
    # Read raw lines to check
    with open(CASE_CSV, encoding="utf-8-sig") as f:
        raw_lines = f.readlines()
    header_fields = len(raw_lines[0].strip().split(",")) if raw_lines else 0
    misaligned = 0
    for i, line in enumerate(raw_lines[1:], 2):
        # Simple check: count commas vs header
        line_commas = line.count(",")
        if line_commas != header_fields - 1:
            misaligned += 1
    if misaligned > 0:
        warnings.append(f"WARNING: 发现 {misaligned} 行字段数量与表头不一致（可能是CSV错列）")

    print(f"=== 统一案例总表诊断 ===")
    print(f"总条目数: {total}")
    print(f"空ID: {len(empty_id)}")
    print(f"空名称: {len(empty_name)}")
    print(f"C-unknown-*: {len(c_unknown)}")
    print(f"完全空行: {len(empty_rows)}")
    print(f"重复编号: {len(dup_ids)}")
    print(f"CSV错列行: {misaligned}")
    print()

    if errors:
        print(f"❌ 验证失败，发现 {len(errors)} 个严重问题:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("✅ 案例表验证通过")

    return errors, warnings, total


def main():
    print("=" * 60)
    print("Registry 完整性验证 - GRS-10")
    print("=" * 60)
    print()

    func_errors, func_warnings, func_total = validate_function_table()
    print()
    case_errors, case_warnings, case_total = validate_case_table()

    print()
    print("=" * 60)
    print("汇总")
    print("=" * 60)
    print(f"函数表: {func_total} 条 | 严重问题: {len(func_errors)} | 警告: {len(func_warnings)}")
    print(f"案例表: {case_total} 条 | 严重问题: {len(case_errors)} | 警告: {len(case_warnings)}")

    all_errors = func_errors + case_errors
    all_warnings = func_warnings + case_warnings

    if all_errors:
        print(f"\n❌ Registry 验证不通过！共 {len(all_errors)} 个严重问题。")
        print("在修复前不应启用 collector/worker cron。")
        sys.exit(1)
    else:
        print(f"\n✅ Registry 验证通过。")
        if all_warnings:
            print(f"注意: {len(all_warnings)} 个警告，建议检查。")
        sys.exit(0)


if __name__ == "__main__":
    main()
