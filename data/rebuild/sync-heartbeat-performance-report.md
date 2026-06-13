# Sync / Heartbeat Performance Report

- generated_at: 2026-06-13T13:16:30.130383+00:00
- sync_dry_run_total_s: 31.122
- heartbeat_once_dry_run_total_s: 31.185
- validate_quick_duration_s: 0.261
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
