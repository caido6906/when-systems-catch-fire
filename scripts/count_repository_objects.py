#!/usr/bin/env python3
"""Count repository objects across the four knowledge layers."""

from __future__ import annotations

import argparse
import json

from repository_overview_utils import count_repository_objects, readme_overview_matches


def main() -> int:
    parser = argparse.ArgumentParser(description="Count repository objects and validate the README overview block.")
    parser.add_argument("--check", action="store_true", help="Validate the current README overview block.")
    args = parser.parse_args()

    counts = count_repository_objects()
    print(json.dumps(counts, ensure_ascii=False, indent=2))

    if args.check:
        if not readme_overview_matches():
            print("README overview block is out of date")
            return 1
        print("README overview block is up to date")
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
