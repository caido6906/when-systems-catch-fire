# Sync / Heartbeat Performance Report

- generated_at: 2026-06-13T12:40:01.879649+00:00
- sync_dry_run_total_s: 31.388
- heartbeat_once_dry_run_total_s: 31.465
- validate_quick_duration_s: 0.233
- within_60s: True
- recommended_long_heartbeat: False

## Skipped Steps

- academic_novelty_check.py --all-answers --dry-run
- render_discovery_index.py --check
- render_prediction_index.py --check

## Core Steps

- sync_ignition_knowledge_base.py --dry-run --quick
- validate_ignition_repository.py --quick
- render_answer_index.py --check
