#!/usr/bin/env python3
"""Add a prediction record from JSON input.

This helper validates a prediction-shaped JSON payload and can emit a normalized
record to stdout or write it to a file. The bootstrap renderer remains the source
of truth for the curated prediction index.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_FIELDS = [
    "id",
    "title",
    "statement",
    "basis",
    "test_condition",
    "falsification_condition",
    "time_window",
    "categories",
    "related_functions",
    "related_cases",
    "related_discoveries",
    "source_refs",
    "confidence",
    "status",
    "created_at",
    "updated_at",
    "page",
]


def load_payload(path: str | None) -> dict:
    raw = sys.stdin.read() if path in {None, "-"} else Path(path).read_text(encoding="utf-8")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("prediction payload must be a JSON object")
    return payload


def normalize_prediction(payload: dict) -> dict:
    missing = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")
    normalized = dict(payload)
    normalized.setdefault("slug", normalized["id"].lower())
    normalized.setdefault("links", {"human_page": normalized["page"]})
    return normalized


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and emit a prediction JSON record.")
    parser.add_argument("--input", "-i", help="JSON file to read; use '-' or omit to read from stdin.", default="-")
    parser.add_argument("--output", "-o", help="Write the normalized JSON to this file instead of stdout.")
    parser.add_argument("--check", action="store_true", help="Validate the input and exit without writing.")
    args = parser.parse_args()

    payload = normalize_prediction(load_payload(args.input))
    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"

    if args.check:
        return 0

    if args.output:
        Path(args.output).write_text(serialized, encoding="utf-8")
    else:
        sys.stdout.write(serialized)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
