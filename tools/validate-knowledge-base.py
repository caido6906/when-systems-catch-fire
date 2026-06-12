#!/usr/bin/env python3
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def jsonl_count(path):
    if not path.exists():
        return -1
    with path.open("r", encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def csv_count(path):
    if not path.exists():
        return -1
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def bad_id(value):
    if not value or not str(value).strip():
        return True
    lowered = str(value).lower()
    return lowered in {"f-unknown", "c-unknown", "unknown"} or "unknown" in lowered


def path_ok(relation):
    if relation.get("unresolved"):
        return True
    rel_path = relation.get("path")
    if not rel_path:
        return True
    return (ROOT / rel_path).exists()


def check_counts(errors, base_dir):
    item_count = len(list((ROOT / base_dir / "items").glob("*.json")))
    index_jsonl = ROOT / base_dir / "index.jsonl"
    index_csv = ROOT / base_dir / "index.csv"
    if jsonl_count(index_jsonl) != item_count:
        errors.append(f"{index_jsonl.relative_to(ROOT)} line count does not match items count")
    if csv_count(index_csv) != item_count:
        errors.append(f"{index_csv.relative_to(ROOT)} row count does not match items count")


def validate_functions(errors):
    for path in sorted((ROOT / "data/functions/items").glob("*.json")):
        item = load_json(path)
        if bad_id(item.get("id")):
            errors.append(f"{path.relative_to(ROOT)} has invalid id")
        if not item.get("title", {}).get("zh"):
            errors.append(f"{path.relative_to(ROOT)} is missing title.zh")
        if "short_definition" not in item and "mechanism" not in item:
            errors.append(f"{path.relative_to(ROOT)} is missing short_definition or mechanism")
        for relation in item.get("related_cases", []):
            if not path_ok(relation):
                errors.append(f"{path.relative_to(ROOT)} has missing related case path: {relation.get('path')}")


def validate_cases(errors):
    for path in sorted((ROOT / "data/cases/items").glob("*.json")):
        item = load_json(path)
        if bad_id(item.get("id")):
            errors.append(f"{path.relative_to(ROOT)} has invalid id")
        if not item.get("title", {}).get("zh"):
            errors.append(f"{path.relative_to(ROOT)} is missing title.zh")
        if "related_functions" not in item:
            errors.append(f"{path.relative_to(ROOT)} is missing related_functions")
        for relation in item.get("related_functions", []):
            if not path_ok(relation):
                errors.append(f"{path.relative_to(ROOT)} has missing related function path: {relation.get('path')}")


def validate_discoveries(errors):
    for path in sorted((ROOT / "data/discoveries/items").glob("*.json")):
        item = load_json(path)
        for relation in item.get("related_functions", []):
            if not path_ok(relation):
                errors.append(f"{path.relative_to(ROOT)} has missing related function path: {relation.get('path')}")
        for relation in item.get("related_cases", []):
            if not path_ok(relation):
                errors.append(f"{path.relative_to(ROOT)} has missing related case path: {relation.get('path')}")


def validate_routing(errors):
    if (ROOT / "book").exists():
        errors.append("book/ still exists in the repository root")
    if (ROOT / "SUMMARY.md").exists():
        errors.append("SUMMARY.md still exists in the repository root")
    if not (ROOT / "archive/book-legacy").exists():
        errors.append("archive/book-legacy/ is missing")
    for path in (ROOT / "data/functions/items").glob("*.json"):
        if "dianhuo/originals" in path.as_posix():
            errors.append(f"raw original is being used as a function item: {path.relative_to(ROOT)}")
    for path in (ROOT / "data/cases/items").glob("*.json"):
        if "dianhuo/originals" in path.as_posix():
            errors.append(f"raw original is being used as a case item: {path.relative_to(ROOT)}")


def main():
    errors = []
    validate_functions(errors)
    validate_cases(errors)
    validate_discoveries(errors)
    check_counts(errors, "data/functions")
    check_counts(errors, "data/cases")
    check_counts(errors, "data/discoveries")
    validate_routing(errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("knowledge base validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
