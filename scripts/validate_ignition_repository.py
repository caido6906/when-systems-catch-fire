#!/usr/bin/env python3
"""Validate the Ignition repository's numbered discovery/prediction gate."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


REPO_ROOT = Path("/workspace/when-systems-catch-fire")
READMES = {
    "root": REPO_ROOT / "README.md",
    "discoveries": REPO_ROOT / "DISCOVERIES.md",
    "predictions": REPO_ROOT / "PREDICTIONS.md",
}
DATA = {
    "discoveries": REPO_ROOT / "data/discoveries/unified-discoveries.json",
    "predictions": REPO_ROOT / "data/predictions/unified-predictions.json",
}
ID_RE = {
    "discoveries": re.compile(r"^DISC-\d{4}$"),
    "predictions": re.compile(r"^PRED-\d{4}$"),
}


def read_json(path: Path, default):
    if not path.exists():
        return default
    text = path.read_text(encoding="utf-8").strip()
    return json.loads(text) if text else default


def fail(errors: list[str]) -> int:
    for error in errors:
        print(f"ERROR: {error}")
    return 1 if errors else 0


def check_readme_order(errors: list[str]) -> None:
    text = READMES["root"].read_text(encoding="utf-8")
    markers = [
        "[发现 / Discoveries]",
        "[预测 / Predictions]",
        "[函数表 / Functions]",
        "[案例表 / Cases]",
    ]
    positions = []
    for marker in markers:
        pos = text.find(marker)
        if pos < 0:
            errors.append(f"README.md missing entrance marker {marker}")
        positions.append(pos)
    if all(pos >= 0 for pos in positions) and positions != sorted(positions):
        errors.append("README.md entrance order is incorrect")


def check_layer(layer: str, errors: list[str]) -> dict[str, int]:
    path = DATA[layer]
    items = read_json(path, [])
    stats = {"total": len(items), "novelty_pending": 0, "novelty_passed": 0}

    for item in items:
        item_id = item.get("id", "")
        if not ID_RE[layer].match(item_id):
            errors.append(f"{path.relative_to(REPO_ROOT)} has invalid id format: {item_id}")

        page = item.get("page") or item.get("links", {}).get("human_page")
        if not page:
            errors.append(f"{item_id} missing page reference")
        else:
            page_path = REPO_ROOT / page
            if not page_path.exists():
                errors.append(f"{item_id} page missing: {page}")
            else:
                page_text = page_path.read_text(encoding="utf-8")
                novelty = item.get("academic_novelty")
                if not isinstance(novelty, dict):
                    errors.append(f"{item_id} missing academic_novelty object")
                    continue
                novelty_status = novelty.get("status")
                if not novelty_status:
                    errors.append(f"{item_id} missing academic_novelty.status")
                elif novelty_status == "passed":
                    stats["novelty_passed"] += 1
                else:
                    stats["novelty_pending"] += 1
                if item.get("status") == "active" and novelty_status != "passed":
                    errors.append(f"{item_id} is active but academic_novelty.status is not passed")
                if item.get("status", "").startswith("active") and novelty_status != "passed":
                    page_lower = page_text.lower()
                    if "academic novelty" not in page_lower or "passed" in page_lower:
                        if "pending" not in page_lower and "inconclusive" not in page_lower:
                            errors.append(f"{item_id} page does not reflect pending novelty status")
                if "Academic Novelty Check" not in page_text:
                    errors.append(f"{item_id} page missing Academic Novelty Check section")

    return stats


def check_public_indexes(errors: list[str]) -> None:
    expected = [
        REPO_ROOT / "data/discoveries/index.md",
        REPO_ROOT / "data/discoveries/index.jsonl",
        REPO_ROOT / "data/predictions/index.md",
        REPO_ROOT / "data/predictions/index.jsonl",
        REPO_ROOT / "data/predictions/unified-predictions-index.md",
    ]
    for path in expected:
        if not path.exists():
            errors.append(f"missing generated index: {path.relative_to(REPO_ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    check_readme_order(errors)
    stats_discoveries = check_layer("discoveries", errors)
    stats_predictions = check_layer("predictions", errors)
    check_public_indexes(errors)

    report = {
        "readme_order_ok": not any("README.md" in error for error in errors),
        "discoveries": stats_discoveries,
        "predictions": stats_predictions,
        "errors": errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return fail(errors) if args.check or errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
