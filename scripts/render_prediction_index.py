#!/usr/bin/env python3
"""Render the prediction index and generated prediction pages.

This is a thin CLI wrapper around the bootstrap prediction builder so other
automation can call a dedicated entrypoint.
"""

from __future__ import annotations

import sys

from build_predictions_from_bootstrap import main as build_main


if __name__ == "__main__":
    raise SystemExit(build_main())
