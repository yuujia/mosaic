#!/usr/bin/env python3
"""Generate deterministic active manifest files from active portfolio rows."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re

MANUAL_BEGIN = "<!-- MOSAIC:BEGIN:MANUAL -->"
MANUAL_END = "<!-- MOSAIC:END:MANUAL -->"
AUTO_BUCKETS_BEGIN = "<!-- BEGIN AUTO:BUCKETS -->"
AUTO_BUCKETS_END = "<!-- END AUTO:BUCKETS -->"
AUTO_GLOBAL_BEGIN = "<!-- BEGIN AUTO:GLOBAL_COMPANY_INDEX -->"
AUTO_GLOBAL_END = "<!-- END AUTO:GLOBAL_COMPANY_INDEX -->"

AGENT_ENTRY_POINTS_SECTION = """## Agent Entry Points
Primary workflow entry point for Mosaic agents.

Steps:
1. Open this file (active_manifest.md).
2. Find the requested bucket section under "## Buckets".
3. Open the listed bucket_thesis_file.
4. Open each company_file listed in the bucket.
5. Apply extraction/scanning rules defined in: agents/skills/analyst.md

- Agents must not assume directory listing is available; they should use manifest paths.
"""


@dataclass(frozen=True)
class ManifestEntry:
    """One active company row in the manifest."""

    bucket_id: str
    bucket_symbol: str
    ticker: str
    side: str
    is_active: bool


def _relpath(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _first_existing(root: Path, candidates: list[Path]) -> Path | None:
    for candidate in candidates:
        if (root / candidate).exists():
            return candidate
    return None


def _load_manual_block(md_path: Path) -> list[str]:
    """Return preserved manual block lines, including marker lines."""
    if not md_path.exists():
        return [MANUAL_BEGIN, "_Add manual notes here. This block is preserved by sync._", MANUAL_END]

    lines = md_path.read_text(encoding="utf-8").splitlines()
    start_idx = -1
    end_idx = -1
    for idx, line in enumerate(lines):
        if line.strip() == MANUAL_BEGIN:
            start_idx = idx
            break
    if start_idx >= 0:
        for idx in range(start_idx + 1, len(lines)):
            if lines[idx].strip() == MANUAL_END:
                end_idx = idx
                break
    if start_idx >= 0 and end_idx > start_idx:
        return lines[start_idx : end_idx + 1]
    return [MANUAL_BEGIN, "_Add manual notes here. This block is preserved by sync._", MANUAL_END]


def _ensure_header_line(text: str, key: str, value: str, after_key: str) -> str:
    key_pattern = re.compile(rf"(?m)^{re.escape(key)}:\s*.*$")
    if key_pattern.search(text):
        return text
    after_pattern = re.compile(rf"(?m)^{re.escape(after_key)}:\s*.*$")
    match = after_pattern.search(text)
    if match:
        insert_at = match.end()
        return text[:insert_at] + f"\n{key}: {value}" + text[insert_at:]
    header_match = re.search(r"(?m)^## Header\s*$", text)
    if header_match:
        insert_at = header_match.end()
        return text[:insert_at] + f"\n{key}: {value}" + text[insert_at:]
    return f"## Header\n{key}: {value}\n\n{text}"


def _upsert_generated_on(text: str, today: str) -> str:
    pattern = re.compile(r"(?m)^generated_on:\s*.*$")
    if pattern.search(text):
        return pattern.sub(f"generated_on: {today}", text, count=1)
    return _ensure_header_line(text, "generated_on", today, after_key="mosaic_schema_version")


def _ensure_agent_entry_points(text: str) -> str:
    if re.search(r"(?m)^## Agent Entry Points\s*$", text):
        return text
    conventions_match = re.search(r"(?m)^## Conventions\s*$", text)
    if conventions_match:
        return text[:conventions_match.start()] + AGENT_ENTRY_POINTS_SECTION + "\n" + text[conventions_match.start():]
    return text.rstrip() + "\n\n" + AGENT_ENTRY_POINTS_SECTION + "\n"


def _ensure_section_heading(text: str, heading: str) -> str:
    if re.search(rf"(?m)^## {re.escape(heading)}\s*$", text):
        return text
    return text.rstrip() + f"\n\n## {heading}\n"


def _section_span(text: str, heading: str) -> tuple[int, int] | None:
    heading_match = re.search(rf"(?m)^## {re.escape(heading)}\s*$", text)
    if not heading_match:
        return None
    body_start = heading_match.end()
    next_section = re.search(r"(?m)^## [^\n]+$", text[body_start:])
    if next_section:
        body_end = body_start + next_section.start()
    else:
        body_end = len(text)
    return (body_start, body_end)


def _ensure_auto_markers(text: str, heading: str, begin_marker: str, end_marker: str) -> str:
    span = _section_span(text, heading)
    if span is None:
        return text
    body_start, body_end = span
    body = text[body_start:body_end]
    if begin_marker in body and end_marker in body:
        return text
    preserved = body.strip("\n")
    wrapped = "\n\n" + begin_marker + "\n"
    if preserved:
        wrapped += preserved + "\n"
    wrapped += end_marker + "\n"
    return text[:body_start] + wrapped + text[body_end:]


def _replace_auto_block(text: str, begin_marker: str, end_marker: str, replacement: str) -> str:
    pattern = re.compile(rf"(?s)({re.escape(begin_marker)}\n)(.*?)(\n{re.escape(end_marker)})")
    if not pattern.search(text):
        return text
    block_text = replacement.rstrip("\n")
    return pattern.sub(rf"\1{block_text}\3", text, count=1)


def _render_buckets_block(
    buckets: dict[str, dict[str, object]],
) -> str:
    lines: list[str] = []
    first = True
    for bucket_id in sorted(buckets.keys(), key=str.upper):
        bucket_data = buckets[bucket_id]
        bucket_symbol = str(bucket_data["bucket_symbol"] or "")
        bucket_thesis_file = str(bucket_data["bucket_thesis_file"] or "")
        companies = sorted(bucket_data["companies"], key=lambda item: str(item["ticker"]).upper())

        if not first:
            lines.append("")
        first = False
        lines.extend(
            [
                f"### {bucket_id}",
                f"- bucket_id: `{bucket_id}`",
                f"- bucket_symbol: `{bucket_symbol}`",
                f"- bucket_path: `buckets/{bucket_id}/`",
                f"- bucket_thesis_file: `{bucket_thesis_file}`",
                "",
                "| ticker | side | company_file |",
                "|---|---|---|",
            ]
        )
        for company in companies:
            lines.append(f"| {company['ticker']} | {company['side']} | {company['company_file']} |")
    return "\n".join(lines)


def _render_global_index_block(global_rows: list[tuple[str, str, str]]) -> str:
    lines = [
        "| ticker | company_file | bucket_id |",
        "|---|---|---|",
    ]
    for ticker, company_file, bucket_id in sorted(global_rows, key=lambda row: (row[0].upper(), row[2].upper())):
        lines.append(f"| {ticker} | {company_file} | {bucket_id} |")
    return "\n".join(lines)


def _bucket_thesis_path(root: Path, bucket_id: str) -> tuple[str, str]:
    candidates: list[tuple[Path, str]] = [
        (Path("buckets") / bucket_id / f"{bucket_id}_bucket_thesis.md", "buckets/<BUCKET_ID>/<BUCKET_ID>_bucket_thesis.md"),
        (Path("buckets") / bucket_id / "bucket_thesis.md", "buckets/<BUCKET_ID>/bucket_thesis.md"),
        (Path("buckets") / bucket_id / f"{bucket_id}.md", "buckets/<BUCKET_ID>/<BUCKET_ID>.md"),
    ]
    existing = _first_existing(root, [p for p, _ in candidates])
    if existing is not None:
        for path, label in candidates:
            if path == existing:
                return (existing.as_posix(), label)
    fallback, label = candidates[0]
    return (fallback.as_posix(), label)


def _company_file_path(root: Path, bucket_id: str, ticker: str) -> tuple[str, str]:
    candidates: list[tuple[Path, str]] = [
        (Path("buckets") / bucket_id / ticker / f"{ticker}.md", "buckets/<BUCKET_ID>/<TICKER>/<TICKER>.md"),
        (Path("buckets") / bucket_id / "companies" / f"{ticker}.md", "buckets/<BUCKET_ID>/companies/<TICKER>.md"),
        (Path("buckets") / bucket_id / f"{ticker}.md", "buckets/<BUCKET_ID>/<TICKER>.md"),
    ]
    existing = _first_existing(root, [p for p, _ in candidates])
    if existing is not None:
        for path, label in candidates:
            if path == existing:
                return (existing.as_posix(), label)
    fallback, label = candidates[0]
    return (fallback.as_posix(), label)


def write_active_manifests(
    mosaic_root: Path,
    entries: list[ManifestEntry],
    dry_run: bool,
) -> tuple[Path, Path]:
    """Write active manifest markdown + csv in 00_config."""
    md_path = mosaic_root / "00_config" / "active_manifest.md"
    csv_path = mosaic_root / "00_config" / "active_manifest.csv"
    manual_block = _load_manual_block(md_path)

    deduped: dict[tuple[str, str], ManifestEntry] = {}
    for entry in entries:
        deduped[(entry.bucket_id, entry.ticker)] = entry
    ordered = sorted(deduped.values(), key=lambda item: (item.bucket_id.upper(), item.ticker.upper()))

    buckets: dict[str, dict[str, object]] = {}
    thesis_conventions: set[str] = set()
    company_conventions: set[str] = set()
    global_rows: list[tuple[str, str, str]] = []
    csv_rows: list[list[str]] = []

    for entry in ordered:
        thesis_file, thesis_convention = _bucket_thesis_path(mosaic_root, entry.bucket_id)
        company_file, company_convention = _company_file_path(mosaic_root, entry.bucket_id, entry.ticker)
        thesis_conventions.add(thesis_convention)
        company_conventions.add(company_convention)

        bucket_data = buckets.setdefault(
            entry.bucket_id,
            {
                "bucket_symbol": entry.bucket_symbol,
                "bucket_thesis_file": thesis_file,
                "companies": [],
            },
        )
        if not bucket_data["bucket_symbol"] and entry.bucket_symbol:
            bucket_data["bucket_symbol"] = entry.bucket_symbol

        bucket_companies = bucket_data["companies"]
        assert isinstance(bucket_companies, list)
        bucket_companies.append(
            {
                "ticker": entry.ticker,
                "side": entry.side,
                "company_file": company_file,
            }
        )

        global_rows.append((entry.ticker, company_file, entry.bucket_id))
        csv_rows.append(
            [
                entry.bucket_id,
                entry.bucket_symbol,
                entry.ticker,
                entry.side,
                "true" if entry.is_active else "false",
                thesis_file,
                company_file,
            ]
        )

    header_date = date.today().isoformat()

    if len(thesis_conventions) == 1:
        thesis_convention_text = next(iter(thesis_conventions))
    elif thesis_conventions:
        thesis_convention_text = "mixed existing paths (" + ", ".join(sorted(thesis_conventions)) + ")"
    else:
        thesis_convention_text = "buckets/<BUCKET_ID>/<BUCKET_ID>_bucket_thesis.md"

    if len(company_conventions) == 1:
        company_convention_text = next(iter(company_conventions))
    elif company_conventions:
        company_convention_text = "mixed existing paths (" + ", ".join(sorted(company_conventions)) + ")"
    else:
        company_convention_text = "buckets/<BUCKET_ID>/<TICKER>/<TICKER>.md"

    buckets_block = _render_buckets_block(buckets)
    global_index_block = _render_global_index_block(global_rows)

    if md_path.exists():
        md_content = md_path.read_text(encoding="utf-8")
    else:
        lines: list[str] = [
            "## Header",
            "mosaic_anchor: ACTIVE_MANIFEST",
            "mosaic_project: Mosaic",
            "mosaic_schema_version: 1",
            f"generated_on: {header_date}",
            "source_file: 00_config/active_portfolio.xlsx",
            "",
            AGENT_ENTRY_POINTS_SECTION.rstrip("\n"),
            "",
            "## Conventions",
            "- Paths are relative to the Mosaic root.",
            f"- Bucket thesis convention: `{thesis_convention_text}`",
            f"- Company file convention: `{company_convention_text}`",
            "- Buckets are sorted A->Z and tickers are sorted A->Z.",
            "",
            "## Buckets",
            "",
            AUTO_BUCKETS_BEGIN,
            AUTO_BUCKETS_END,
            "",
            "## Global Company Index",
            "",
            AUTO_GLOBAL_BEGIN,
            AUTO_GLOBAL_END,
            "",
            "## Manual Sections",
            "",
            "Content inside the block below is user-owned and preserved on sync runs.",
            "",
        ]
        lines.extend(manual_block)
        md_content = "\n".join(lines).rstrip() + "\n"

    md_content = _ensure_header_line(md_content, "mosaic_anchor", "ACTIVE_MANIFEST", after_key="## Header")
    md_content = _ensure_header_line(md_content, "mosaic_project", "Mosaic", after_key="mosaic_anchor")
    md_content = _ensure_header_line(md_content, "mosaic_schema_version", "1", after_key="mosaic_project")
    md_content = _upsert_generated_on(md_content, header_date)
    md_content = _ensure_header_line(md_content, "source_file", "00_config/active_portfolio.xlsx", after_key="generated_on")
    md_content = _ensure_agent_entry_points(md_content)
    md_content = _ensure_section_heading(md_content, "Buckets")
    md_content = _ensure_section_heading(md_content, "Global Company Index")
    md_content = _ensure_auto_markers(md_content, "Buckets", AUTO_BUCKETS_BEGIN, AUTO_BUCKETS_END)
    md_content = _ensure_auto_markers(md_content, "Global Company Index", AUTO_GLOBAL_BEGIN, AUTO_GLOBAL_END)
    md_content = _replace_auto_block(md_content, AUTO_BUCKETS_BEGIN, AUTO_BUCKETS_END, buckets_block)
    md_content = _replace_auto_block(md_content, AUTO_GLOBAL_BEGIN, AUTO_GLOBAL_END, global_index_block)
    md_content = md_content.rstrip() + "\n"

    csv_header = [
        "bucket_id",
        "bucket_symbol",
        "ticker",
        "side",
        "is_active",
        "bucket_thesis_file",
        "company_file",
    ]
    csv_rows_sorted = sorted(csv_rows, key=lambda row: (row[0].upper(), row[2].upper()))

    if dry_run:
        print(f"[DRY] write: {_relpath(md_path, mosaic_root)}")
        print(f"[DRY] write: {_relpath(csv_path, mosaic_root)}")
        return (md_path, csv_path)

    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(md_content, encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(csv_header)
        writer.writerows(csv_rows_sorted)
    print(f"[APPLY] write: {_relpath(md_path, mosaic_root)}")
    print(f"[APPLY] write: {_relpath(csv_path, mosaic_root)}")
    return (md_path, csv_path)
