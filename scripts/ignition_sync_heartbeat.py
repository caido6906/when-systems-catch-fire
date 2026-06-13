#!/usr/bin/env python3
"""Heartbeat wrapper for the Ignition sync dry-run flow."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess


REPO_ROOT = Path("/workspace/when-systems-catch-fire")
LOCK_FILE = REPO_ROOT / "data/sync/.ignition-maintenance.lock"
STATE_FILE = REPO_ROOT / "data/sync/heartbeat-state.json"
REPORT_MD = REPO_ROOT / "data/sync/heartbeat-dry-run-report.md"
REPORT_JSON = REPO_ROOT / "data/sync/heartbeat-dry-run-report.json"


def read_json(path: Path, default):
    if not path.exists():
        return default
    text = path.read_text(encoding="utf-8").strip()
    return json.loads(text) if text else default


def write_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def run(cmd: list[str]) -> dict:
    proc = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    return {"cmd": cmd, "returncode": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr, "ok": proc.returncode == 0}


def write_reports(payload: dict) -> None:
    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    lines = [
        "# Ignition Heartbeat Dry Run Report",
        "",
        f"- generated_at: {payload['generated_at']}",
        f"- lock_present: {payload['lock_present']}",
        f"- validate_ok: {payload['validate_ok']}",
        "",
    ]
    lines.append("## Commands")
    lines.append("")
    for result in payload["commands"]:
        lines.append(f"- {' '.join(result['cmd'])}: {result['returncode']}")
    lines.append("")
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    state = read_json(STATE_FILE, {})
    if args.status and not args.once:
        payload = {
            "lock_present": LOCK_FILE.exists(),
            "state": state,
            "report_md": str(REPORT_MD.relative_to(REPO_ROOT)),
            "report_json": str(REPORT_JSON.relative_to(REPO_ROOT)),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    commands = []
    if args.once and args.dry_run:
        commands.append(run(["python3", "scripts/sync_ignition_knowledge_base.py", "--dry-run"]))
        commands.append(run(["python3", "scripts/validate_ignition_repository.py", "--check"]))
        commands.append(run(["python3", "scripts/render_answer_index.py", "--check"]))
        payload = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "lock_present": LOCK_FILE.exists(),
            "state": {
                "last_run_at": datetime.now(timezone.utc).isoformat(),
                "last_run_mode": "dry-run",
                "validate_ok": all(result["ok"] for result in commands),
            },
            "commands": commands,
            "validate_ok": all(result["ok"] for result in commands),
        }
        write_json(STATE_FILE, payload["state"])
        write_reports(payload)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload["validate_ok"] else 1

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "lock_present": LOCK_FILE.exists(),
        "commands": [],
        "validate_ok": False,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
