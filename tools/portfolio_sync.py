#!/usr/bin/env python3
"""Sync Mosaic bucket/company folders and seed company Markdown files from template."""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path

import pandas as pd
from active_manifest import ManifestEntry, write_active_manifests


REQUIRED_COLUMNS = ["ticker"]


def is_blankish(value: object) -> bool:
    """Return True for empty/NaN-like cell values."""
    if value is None:
        return True
    text = str(value).strip()
    return text == "" or text.lower() in {"nan", "none", "null", "nat"}


def safe_name(value: str) -> str:
    """Return a Windows-safe folder/file token."""
    cleaned = re.sub(r'[<>:"/\\|?*]+', "_", (value or "").strip())
    return cleaned.strip(" .")


def ticker_key(raw_ticker: str) -> str:
    """Map Bloomberg-like ticker text to filesystem key.

    Examples:
    - "DGX US Equity" -> "DGX"
    - "USD Curncy" -> "USD"
    """
    token = (raw_ticker or "").strip().split(" ")[0].upper()
    return safe_name(token)


def bucket_fs(bucket_symbol: str) -> str:
    """Map bucket symbol to filesystem bucket folder."""
    symbol = (bucket_symbol or "").strip()
    if is_blankish(symbol):
        return ""
    if symbol.startswith("."):
        symbol = symbol.lstrip(".")
    if is_blankish(symbol):
        return ""
    return safe_name(symbol)


def resolve_bucket_id(row: pd.Series) -> str:
    """Resolve filesystem bucket id from active_portfolio row."""
    raw_bucket_id = row.get("bucket_id", "")
    if not is_blankish(raw_bucket_id):
        raw_bucket_id = str(raw_bucket_id).strip()
        return safe_name(raw_bucket_id)
    raw_bucket_symbol = str(row.get("bucket_symbol", "") or "").strip()
    return bucket_fs(raw_bucket_symbol)


def is_active_row(row: pd.Series) -> bool:
    """Return whether a portfolio row should be treated as active."""
    for column in ("is_active", "active", "enabled"):
        if column in row.index:
            value = row[column]
            if pd.isna(value):
                return False
            normalized = str(value).strip().lower()
            if normalized in {"1", "true", "yes", "y"}:
                return True
            if normalized in {"0", "false", "no", "n", ""}:
                return False
            # Fallback for unexpected truthy-ish text.
            return normalized not in {"nan", "none", "null"}
    return True


def render_company_markdown(template_text: str, values: dict[str, str]) -> str:
    """Replace template placeholders with row values."""
    rendered = template_text
    for key, value in values.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered


def ensure_dir(path: Path, dry_run: bool) -> None:
    """Create directory when missing."""
    if path.exists():
        return
    if dry_run:
        print(f"[DRY] mkdir -p: {path}")
        return
    path.mkdir(parents=True, exist_ok=True)
    print(f"[APPLY] mkdir -p: {path}")


def create_company_file(md_path: Path, content: str, dry_run: bool) -> bool:
    """Create company markdown file only if missing."""
    if md_path.exists():
        return False
    if dry_run:
        print(f"[DRY] create: {md_path}")
        return True
    md_path.write_text(content, encoding="utf-8")
    print(f"[APPLY] create: {md_path}")
    return True


def create_bucket_thesis_file(md_path: Path, content: str, dry_run: bool) -> bool:
    """Create bucket thesis markdown file only if missing."""
    if md_path.exists():
        return False
    if dry_run:
        print(f"[DRY] create: {md_path}")
        return True
    md_path.write_text(content, encoding="utf-8")
    print(f"[APPLY] create: {md_path}")
    return True


def create_bucket_kpi_file(kpi_path: Path, template_path: Path, dry_run: bool) -> bool:
    """Create bucket KPI workbook from template only if missing."""
    if kpi_path.exists():
        return False
    if dry_run:
        print(f"[DRY] copy: {template_path} -> {kpi_path}")
        return True
    kpi_path.parent.mkdir(parents=True, exist_ok=True)
    kpi_path.write_bytes(template_path.read_bytes())
    print(f"[APPLY] copy: {template_path} -> {kpi_path}")
    return True


def move_path(src: Path, dst: Path, dry_run: bool) -> bool:
    """Move a file/folder only when destination does not exist."""
    if dst.exists():
        print(f"[SKIP] conflict exists: {dst}")
        return False
    if dry_run:
        print(f"[DRY] move: {src} -> {dst}")
        return True
    dst.parent.mkdir(parents=True, exist_ok=True)
    src.rename(dst)
    print(f"[APPLY] move: {src} -> {dst}")
    return True


def remove_dir_if_empty(path: Path, dry_run: bool) -> bool:
    """Remove directory if it is empty."""
    if not path.is_dir():
        return False
    try:
        next(path.iterdir())
        return False
    except StopIteration:
        if dry_run:
            print(f"[DRY] rmdir: {path}")
            return True
        try:
            path.rmdir()
        except OSError as exc:
            print(f"[SKIP] rmdir failed: {path} ({exc})")
            return False
        print(f"[APPLY] rmdir: {path}")
        return True


def migrate_legacy_companies_wrapper(bucket_dir: Path, dry_run: bool) -> tuple[int, int]:
    """Migrate legacy bucket/companies/* layout into canonical bucket/* layout."""
    legacy_root = bucket_dir / "companies"
    if not legacy_root.is_dir():
        return (0, 0)

    moved = 0
    conflicts = 0
    for legacy_company_dir in sorted((p for p in legacy_root.iterdir() if p.is_dir()), key=lambda p: p.name.lower()):
        canonical_company_dir = bucket_dir / safe_name(legacy_company_dir.name)
        ensure_dir(canonical_company_dir, dry_run=dry_run)
        for child in sorted(legacy_company_dir.iterdir(), key=lambda p: p.name.lower()):
            dst = canonical_company_dir / child.name
            if move_path(child, dst, dry_run=dry_run):
                moved += 1
            else:
                conflicts += 1
        remove_dir_if_empty(legacy_company_dir, dry_run=dry_run)

    remove_dir_if_empty(legacy_root, dry_run=dry_run)
    return (moved, conflicts)


def archive_stale_buckets(
    buckets_root: Path, active_buckets: set[str], dry_run: bool
) -> tuple[int, int, int]:
    """Archive top-level bucket folders not present in active portfolio."""
    archive_root = buckets_root / "_archive" / "buckets"
    stale_detected = 0
    archived = 0
    conflicts = 0

    for bucket_dir in sorted((p for p in buckets_root.iterdir() if p.is_dir()), key=lambda p: p.name.lower()):
        bucket_name = bucket_dir.name
        if bucket_name == "_archive":
            continue
        if bucket_name in active_buckets:
            continue

        stale_detected += 1
        archive_target = archive_root / bucket_name
        if archive_target.exists():
            print(f"[SKIP] stale archive conflict exists: {archive_target}")
            conflicts += 1
            continue

        if dry_run:
            print(f"[DRY] move stale bucket: {bucket_dir} -> {archive_target}")
            archived += 1
            continue

        archive_target.parent.mkdir(parents=True, exist_ok=True)
        bucket_dir.rename(archive_target)
        print(f"[APPLY] move stale bucket: {bucket_dir} -> {archive_target}")
        archived += 1

    return (stale_detected, archived, conflicts)


def run_sync(mosaic_root: Path, apply: bool, archive_stale_buckets_flag: bool) -> None:
    """Run portfolio-driven directory and Markdown seeding sync."""
    dry_run = not apply

    config_file = mosaic_root / "00_config" / "active_portfolio.xlsx"
    company_template_file = mosaic_root / "tools" / "templates" / "COMPANY_TEMPLATE.md"
    bucket_thesis_template_file = mosaic_root / "tools" / "templates" / "BUCKET_THESIS_TEMPLATE.md"
    bucket_kpi_template_candidates = [
        mosaic_root / "tools" / "templates" / "BUCKET_kpi_template.xlsx",
        mosaic_root / "tools" / "templates" / "BUCKET_kpi_TEMPLATE.xlsx",
    ]
    buckets_root = mosaic_root / "buckets"
    bucket_kpi_template_file = next((p for p in bucket_kpi_template_candidates if p.exists()), None)

    if not config_file.exists():
        raise FileNotFoundError(f"Missing portfolio file: {config_file}")
    if not company_template_file.exists():
        raise FileNotFoundError(f"Missing template file: {company_template_file}")
    if not bucket_thesis_template_file.exists():
        raise FileNotFoundError(f"Missing template file: {bucket_thesis_template_file}")
    if bucket_kpi_template_file is None:
        expected = " or ".join(str(p) for p in bucket_kpi_template_candidates)
        raise FileNotFoundError(f"Missing template file: {expected}")

    company_template_text = company_template_file.read_text(encoding="utf-8")
    bucket_thesis_template_text = bucket_thesis_template_file.read_text(encoding="utf-8")
    df = pd.read_excel(config_file)

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns in active_portfolio.xlsx: {', '.join(missing_columns)}")
    if "bucket_id" not in df.columns and "bucket_symbol" not in df.columns:
        raise ValueError("Missing required bucket column: expected one of bucket_id or bucket_symbol")

    ensure_dir(buckets_root, dry_run=dry_run)

    today = date.today().isoformat()
    created_count = 0
    bucket_thesis_created_count = 0
    bucket_kpi_created_count = 0
    moved_count = 0
    conflict_count = 0
    stale_detected_count = 0
    stale_archived_count = 0
    stale_conflict_count = 0
    migrated_buckets: set[Path] = set()
    active_buckets: set[str] = set()
    manifest_entries: list[ManifestEntry] = []

    for _, row in df.iterrows():
        if not is_active_row(row):
            continue

        raw_ticker = str(row["ticker"] or "").strip()
        raw_bucket_symbol = str(row.get("bucket_symbol", "") or "").strip()
        resolved_bucket_id = resolve_bucket_id(row)
        if is_blankish(raw_ticker):
            continue
        if not resolved_bucket_id:
            continue

        key = ticker_key(raw_ticker)
        fs_bucket = resolved_bucket_id
        if not key or not fs_bucket:
            continue
        active_buckets.add(fs_bucket)

        company_name = str(row.get("name", "") or "").strip()
        side = str(row.get("side", "") or "").strip()
        bucket_name = str(row.get("bucket_name", "") or "").strip()
        bucket_dir = buckets_root / fs_bucket

        ensure_dir(bucket_dir, dry_run=dry_run)
        if bucket_dir not in migrated_buckets:
            moved, conflicts = migrate_legacy_companies_wrapper(bucket_dir, dry_run=dry_run)
            moved_count += moved
            conflict_count += conflicts
            thesis_path = bucket_dir / f"{fs_bucket}_bucket_thesis.md"
            thesis_text = render_company_markdown(
                bucket_thesis_template_text,
                {
                    "bucket_symbol": raw_bucket_symbol,
                    "bucket_fs": fs_bucket,
                    "bucket_name": bucket_name,
                    "last_updated": today,
                },
            ).replace("YYYY-MM-DD", today)
            if create_bucket_thesis_file(thesis_path, thesis_text, dry_run=dry_run):
                bucket_thesis_created_count += 1
            bucket_kpi_path = bucket_dir / f"{fs_bucket}_kpi.xlsx"
            if create_bucket_kpi_file(bucket_kpi_path, bucket_kpi_template_file, dry_run=dry_run):
                bucket_kpi_created_count += 1
            migrated_buckets.add(bucket_dir)

        company_dir = bucket_dir / key
        md_path = company_dir / f"{key}.md"
        source_dir = company_dir / "source"

        ensure_dir(company_dir, dry_run=dry_run)
        ensure_dir(source_dir, dry_run=dry_run)

        rendered = render_company_markdown(
            company_template_text,
            {
                "bucket_symbol": raw_bucket_symbol,
                "bucket_name": bucket_name,
                "ticker": key,
                "company_name": company_name,
                "side": side,
                "last_updated": today,
            },
        )
        if create_company_file(md_path, rendered, dry_run=dry_run):
            created_count += 1

        manifest_entries.append(
            ManifestEntry(
                bucket_id=fs_bucket,
                bucket_symbol=raw_bucket_symbol,
                ticker=key,
                side=side,
                is_active=True,
            )
        )

    if archive_stale_buckets_flag:
        stale_detected_count, stale_archived_count, stale_conflict_count = archive_stale_buckets(
            buckets_root=buckets_root,
            active_buckets=active_buckets,
            dry_run=dry_run,
        )

    write_active_manifests(
        mosaic_root=mosaic_root,
        entries=manifest_entries,
        dry_run=dry_run,
    )

    print("Done.")
    if dry_run:
        print("NOTE: Dry-run mode (no changes). Re-run with --apply to apply changes.")
    print(f"Markdown files created: {created_count}")
    print(f"Bucket thesis files created: {bucket_thesis_created_count}")
    print(f"Bucket KPI files created: {bucket_kpi_created_count}")
    print(f"Legacy paths migrated: {moved_count}")
    print(f"Migration conflicts: {conflict_count}")
    if archive_stale_buckets_flag:
        print(f"Stale buckets detected: {stale_detected_count}")
        print(f"Stale buckets archived: {stale_archived_count}")
        print(f"Stale archive conflicts: {stale_conflict_count}")


def parse_args() -> argparse.Namespace:
    """Parse CLI args."""
    parser = argparse.ArgumentParser(
        description="Mosaic: sync portfolio folders and seed company markdown files from template."
    )
    parser.add_argument(
        "--mosaic-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Path to Mosaic root folder (contains 00_config/, buckets/, tools/).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes. Without this flag, runs in dry-run mode.",
    )
    parser.add_argument(
        "--archive-stale-buckets",
        action="store_true",
        help="Archive top-level bucket folders not present in active_portfolio.xlsx into buckets/_archive/buckets/.",
    )
    return parser.parse_args()


def main() -> None:
    """CLI entrypoint."""
    args = parse_args()
    run_sync(
        mosaic_root=args.mosaic_root.resolve(),
        apply=args.apply,
        archive_stale_buckets_flag=args.archive_stale_buckets,
    )


if __name__ == "__main__":
    main()
