#!/usr/bin/env python3
"""One-time migration to drop leading dots from bucket folders and normalize thesis filenames."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path


SKIP_DOT_DIRS = {".git", ".github", ".vscode"}


def is_bucket_dir(path: Path) -> bool:
    if not path.is_dir():
        return False
    if (path / "companies").is_dir():
        return True
    legacy_candidates = [
        path / "bucket_thesis.md",
        path / f".{path.name}_bucket_thesis.md",
        path / f"{path.name}_bucket_thesis.md",
        path / f"_{path.name}_bucket_thesis.md",
    ]
    return any(p.is_file() for p in legacy_candidates)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Migrate buckets by removing leading dots from folder names and renaming legacy thesis files."
    )
    parser.add_argument(
        "--mosaic-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Path to Mosaic root (contains buckets/ and 00_config/).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes. Without this flag, performs a dry-run.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.mosaic_root.resolve()
    dry_run = not args.apply

    buckets_root = root / "buckets"
    log_path = root / "00_config" / "migrations" / "migrate_drop_dot_buckets.log"

    folders_renamed: list[tuple[Path, Path]] = []
    thesis_renamed: list[tuple[Path, Path]] = []
    skipped_dot_dirs: list[Path] = []
    conflicts: list[str] = []

    if not buckets_root.is_dir():
        raise FileNotFoundError(f"Missing buckets directory: {buckets_root}")

    bucket_dirs: list[Path] = []
    for child in sorted(buckets_root.iterdir(), key=lambda p: p.name.lower()):
        if not child.is_dir():
            continue
        if child.name.startswith("."):
            if child.name in SKIP_DOT_DIRS:
                skipped_dot_dirs.append(child)
                continue
            if not is_bucket_dir(child):
                skipped_dot_dirs.append(child)
                continue
            target = child.with_name(child.name[1:])
            if target.exists():
                conflicts.append(f"folder conflict: {child} -> {target} (destination exists)")
                bucket_dirs.append(target)
                continue
            folders_renamed.append((child, target))
            bucket_dirs.append(target)
            if dry_run:
                continue
            child.rename(target)
        else:
            bucket_dirs.append(child)

    for bucket in bucket_dirs:
        if not bucket.is_dir():
            continue
        stable = bucket / f"{bucket.name}_bucket_thesis.md"
        legacy_candidates = [
            bucket / "bucket_thesis.md",
            bucket / f".{bucket.name}_bucket_thesis.md",
            bucket / f"{bucket.name}_bucket_thesis.md",
            bucket / f"_{bucket.name}_bucket_thesis.md",
        ]
        existing_legacy = [p for p in legacy_candidates if p.is_file()]
        if not existing_legacy:
            continue
        if stable.exists():
            for legacy in existing_legacy:
                conflicts.append(f"thesis conflict: {legacy} -> {stable} (destination exists)")
            continue
        legacy_to_rename = existing_legacy[0]
        thesis_renamed.append((legacy_to_rename, stable))
        if not dry_run:
            legacy_to_rename.rename(stable)
        for extra_legacy in existing_legacy[1:]:
            conflicts.append(f"thesis conflict: {extra_legacy} -> {stable} (multiple legacy files)")

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    log_lines = [
        f"[{timestamp}] mode={'DRY_RUN' if dry_run else 'APPLY'} root={root}",
        f"folders_renamed={len(folders_renamed)}",
        f"thesis_renamed={len(thesis_renamed)}",
        f"conflicts={len(conflicts)}",
    ]
    for src, dst in folders_renamed:
        log_lines.append(f"rename_folder: {src} -> {dst}")
    for src, dst in thesis_renamed:
        log_lines.append(f"rename_thesis: {src} -> {dst}")
    for msg in conflicts:
        log_lines.append(f"conflict: {msg}")
    for path in skipped_dot_dirs:
        log_lines.append(f"skip_dot_dir: {path}")

    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write("\n".join(log_lines) + "\n")

    print(f"Mode: {'DRY-RUN' if dry_run else 'APPLY'}")
    print(f"Buckets root: {buckets_root}")
    print(f"Folders renamed: {len(folders_renamed)}")
    print(f"Thesis files renamed: {len(thesis_renamed)}")
    print(f"Conflicts: {len(conflicts)}")
    print(f"Skipped dot dirs: {len(skipped_dot_dirs)}")
    for src, dst in folders_renamed:
        print(f" - folder: {src.name} -> {dst.name}")
    for src, dst in thesis_renamed:
        print(f" - thesis: {src.name} -> {dst.name}")
    for msg in conflicts:
        print(f" - conflict: {msg}")
    for path in skipped_dot_dirs:
        print(f" - skipped: {path.name}")
    if dry_run:
        print("Dry-run only. Re-run with --apply to apply changes.")
    print(f"Log written to: {log_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
