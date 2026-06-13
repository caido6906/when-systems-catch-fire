#!/usr/bin/env python3
"""Validate the Ignition repository's dynamic counts, sorting, and gates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_predictions_from_bootstrap import (
    PREDICTIONS_HUMAN_MD,
    PREDICTION_BLUEPRINTS,
    build_category_defs,
    build_maps,
    build_category_map,
    enrich_prediction,
    render_index as render_prediction_index,
    render_machine_index,
)
from discovery_category_utils import (
    BOOTSTRAP_REPORT_MD,
    CATEGORY_MAP_JSON,
    DISCOVERY_INDEX_MD,
    DISCOVERY_LIST_MD,
    read_json as read_discovery_json,
    render_bootstrap_report,
    render_discoveries_list,
    render_discovery_index_md,
)
from repository_overview_utils import (
    README,
    count_repository_objects,
    readme_overview_matches,
)
from render_human_entry_from_unified_md import (
    CASE_SOURCE,
    DOC_CASE_INDEX,
    DOC_CASE_DIR,
    DOC_FUNC_INDEX,
    DOC_FUNC_DIR,
    FUNC_SOURCE,
    ROOT_CASES,
    ROOT_FUNCTIONS,
    build_relationships,
    parse_case_table,
    parse_function_table,
    render_cases_collection,
    render_functions_collection,
)


REPO_ROOT = Path("/workspace/when-systems-catch-fire")
DISCOVERIES_JSON = REPO_ROOT / "data/discoveries/unified-discoveries.json"
DISCOVERIES_INDEX_JSON = REPO_ROOT / "data/discoveries/unified-discoveries-index.md"
PREDICTIONS_JSON = REPO_ROOT / "data/predictions/unified-predictions.json"
PREDICTIONS_INDEX_JSON = REPO_ROOT / "data/predictions/unified-predictions-index.md"


def fail(errors: list[str]) -> int:
    for error in errors:
        print(f"ERROR: {error}")
    return 1 if errors else 0


def check_readme(errors: list[str]) -> None:
    text = README.read_text(encoding="utf-8")
    required = [
        "[发现 / Discoveries](DISCOVERIES.md)",
        "[预测 / Predictions](PREDICTIONS.md)",
        "[函数表 / Functions](FUNCTIONS.md)",
        "[案例表 / Cases](CASES.md)",
    ]
    positions = []
    for marker in required:
        pos = text.find(marker)
        if pos < 0:
            errors.append(f"README.md missing entrance marker {marker}")
        positions.append(pos)
    if all(pos >= 0 for pos in positions) and positions != sorted(positions):
        errors.append("README.md entrance order is incorrect")
    if not readme_overview_matches(README):
        errors.append("README.md repository overview block is out of date")


def check_discoveries(errors: list[str]) -> dict[str, int]:
    discoveries = read_discovery_json(DISCOVERIES_JSON, [])
    category_map = read_discovery_json(CATEGORY_MAP_JSON, [])
    expected_index = render_discoveries_list(discoveries, category_map)
    current_index = DISCOVERY_LIST_MD.read_text(encoding="utf-8")
    if expected_index != current_index:
        errors.append("DISCOVERIES.md does not match generated discovery index")

    machine_index = render_discovery_index_md(discoveries)
    machine_path = REPO_ROOT / "data/discoveries/unified-discoveries-index.md"
    if machine_index != machine_path.read_text(encoding="utf-8"):
        errors.append("data/discoveries/unified-discoveries-index.md is out of date")

    bootstrap_report = render_bootstrap_report(category_map)
    if bootstrap_report != (REPO_ROOT / "data/discoveries/bootstrap-category-report.md").read_text(encoding="utf-8"):
        errors.append("data/discoveries/bootstrap-category-report.md is out of date")

    return {
        "curated": len(discoveries),
        "leads": sum(len(entry.get("discovery_leads", [])) for entry in category_map),
    }


def check_predictions(errors: list[str]) -> dict[str, int]:
    predictions = read_discovery_json(PREDICTIONS_JSON, [])
    existing_predictions = {item["id"]: item for item in predictions}
    category_defs = build_category_defs()
    functions = read_discovery_json(REPO_ROOT / "data/functions/unified-functions.json", [])
    cases = read_discovery_json(REPO_ROOT / "data/cases/unified-cases.json", [])
    discoveries = read_discovery_json(DISCOVERIES_JSON, [])
    func_map, case_map, disc_map = build_maps(functions, cases, discoveries)
    enriched = [
        enrich_prediction(
            blueprint,
            func_map,
            case_map,
            disc_map,
            category_defs,
            existing_predictions.get(blueprint["id"]),
        )
        for blueprint in PREDICTION_BLUEPRINTS
    ]
    category_map = build_category_map(enriched, category_defs)

    expected_human = render_prediction_index(enriched, category_map)
    current_human = PREDICTIONS_HUMAN_MD.read_text(encoding="utf-8")
    if expected_human != current_human:
        errors.append("PREDICTIONS.md does not match generated prediction index")

    machine_index = render_machine_index(enriched)
    current_machine = (REPO_ROOT / "data/predictions/unified-predictions-index.md").read_text(encoding="utf-8")
    if machine_index != current_machine:
        errors.append("data/predictions/unified-predictions-index.md is out of date")

    return {
        "curated": len(predictions),
        "passed_novelty": sum(1 for pred in predictions if pred.get("academic_novelty", {}).get("status") == "passed"),
        "pending_novelty": sum(1 for pred in predictions if pred.get("academic_novelty", {}).get("status") == "pending"),
        "failed_novelty": sum(1 for pred in predictions if pred.get("academic_novelty", {}).get("status") == "failed"),
    }


def check_functions_cases(errors: list[str]) -> dict[str, int]:
    functions = parse_function_table(FUNC_SOURCE)
    cases = parse_case_table(CASE_SOURCE)
    rel = build_relationships(functions, cases)
    dangling = rel["dangling"]

    function_render = render_functions_collection(functions, ROOT_FUNCTIONS)
    if function_render != ROOT_FUNCTIONS.read_text(encoding="utf-8"):
        errors.append("FUNCTIONS.md does not match generated function collection")

    case_render = render_cases_collection(cases, ROOT_CASES)
    if case_render != ROOT_CASES.read_text(encoding="utf-8"):
        errors.append("CASES.md does not match generated case collection")

    return {
        "functions": len(functions),
        "cases": len(cases),
        "dangling_references": len(dangling),
    }


def check_presence(errors: list[str]) -> None:
    expected = [
        DOC_FUNC_INDEX,
        DOC_CASE_INDEX,
        DISCOVERY_INDEX_MD,
        REPO_ROOT / "data/functions/unified-functions-index.md",
        REPO_ROOT / "data/cases/unified-cases-index.md",
        PREDICTIONS_INDEX_JSON,
        REPO_ROOT / "data/predictions/unified-predictions-index.md",
        REPO_ROOT / "data/discoveries/unified-discoveries-index.md",
        REPO_ROOT / "data/discoveries/bootstrap-category-report.md",
        BOOTSTRAP_REPORT_MD,
    ]
    for path in expected:
        if not path.exists():
            errors.append(f"missing generated file: {path.relative_to(REPO_ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    check_readme(errors)
    discovery_stats = check_discoveries(errors)
    prediction_stats = check_predictions(errors)
    function_stats = check_functions_cases(errors)
    check_presence(errors)

    counts = count_repository_objects()
    report = {
        "readme_ok": readme_overview_matches(README),
        "counts": counts,
        "discoveries": discovery_stats,
        "predictions": prediction_stats,
        "functions": function_stats,
        "errors": errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return fail(errors) if args.check or errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
