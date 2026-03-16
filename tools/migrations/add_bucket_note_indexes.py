#!/usr/bin/env python3
"""Generate managed bucket note indexes via portfolio sync."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

TOOLS_DIR = Path(__file__).resolve().parents[1]
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from portfolio_sync import run_sync


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate managed {BUCKET_FS}_note_index.md files and refresh manifests. "
            "Dry-run by default."
        )
    )
    parser.add_argument(
        "--mosaic-root",
        type=Path,
        default=Path(__file__).resolve().parents[2],
        help="Path to Mosaic root folder.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes. Without this flag, runs in dry-run mode.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_sync(
        mosaic_root=args.mosaic_root.resolve(),
        apply=args.apply,
        archive_stale_buckets_flag=False,
    )


if __name__ == "__main__":
    main()
