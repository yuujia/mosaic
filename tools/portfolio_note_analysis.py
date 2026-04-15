"""Summarize active-portfolio note coverage and latest thesis evidence."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


SECTION_HEADERS = [
    "Major Announcements and Changes",
    "KPI Assessment",
    "Quarterly KPI Assessment",
    "Thesis On Track",
    "Thesis Off Track",
    "Upside Drivers",
    "Risk Factors (Macro, Execution, Structural)",
    "Idiosyncratic Issues",
    "Thematic Color",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize active-portfolio note coverage plus portfolio-level upside drivers and downside risks."
    )
    parser.add_argument(
        "--manifest",
        default="00_config/active_manifest.md",
        help="Path to the active manifest markdown file.",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="Output format.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=8,
        help="Number of repeated upside/downside themes to show.",
    )
    parser.add_argument(
        "--include-blank-names",
        action="store_true",
        help="Include the list of active positions whose latest company note is still blank.",
    )
    parser.add_argument(
        "--exclude-cash",
        action="store_true",
        help="Exclude the Cash bucket from portfolio coverage calculations.",
    )
    parser.add_argument(
        "--exclude-bucket",
        action="append",
        default=[],
        help="Bucket id to exclude. Repeatable.",
    )
    return parser.parse_args()


def parse_manifest(manifest_path: Path) -> list[dict[str, str]]:
    text = manifest_path.read_text(encoding="utf-8")
    companies: list[dict[str, str]] = []
    current_bucket: str | None = None
    pattern = re.compile(r"\|\s*([A-Z0-9_]+)\s*\|\s*(Long|Short)\s*\|\s*([^|]+)\|")

    for line in text.splitlines():
        if line.startswith("### "):
            current_bucket = line[4:].strip()
            continue

        match = pattern.match(line)
        if match and current_bucket:
            ticker, side, company_file = match.groups()
            companies.append(
                {
                    "bucket": current_bucket,
                    "ticker": ticker,
                    "side": side,
                    "path": company_file.strip(),
                }
            )

    return companies


def extract_latest_block(text: str) -> tuple[str | None, str | None]:
    quarter_headers = list(re.finditer(r"^##\s+(20\d{2}\s+Q[1-4])\s*$", text, flags=re.M))
    if not quarter_headers:
        return None, None

    start = quarter_headers[0].start()
    end = quarter_headers[1].start() if len(quarter_headers) > 1 else len(text)
    return quarter_headers[0].group(1), text[start:end]


def extract_section(block: str | None, header: str) -> list[str]:
    if not block:
        return []

    match = re.search(
        rf"^###\s+{re.escape(header)}\s*$\n(.*?)(?=^###\s+|^##\s+|\Z)",
        block,
        flags=re.M | re.S,
    )
    if not match:
        return []

    values: list[str] = []
    for raw_line in match.group(1).splitlines():
        line = raw_line.strip()
        if not line or line in {"-", "--"}:
            continue
        if line.startswith("- "):
            line = line[2:].strip()
        values.append(line)

    return values


def normalize_theme(text: str) -> str:
    collapsed = " ".join(text.split())
    return collapsed.rstrip(".")


def is_filled(block: str | None) -> bool:
    return any(extract_section(block, header) for header in SECTION_HEADERS)


def analyze(
    companies: list[dict[str, str]],
    exclude_cash: bool,
    exclude_buckets: list[str],
) -> dict[str, object]:
    excluded = set(exclude_buckets)
    selected = [
        c
        for c in companies
        if not (exclude_cash and c["bucket"] == "Cash") and c["bucket"] not in excluded
    ]

    by_bucket: dict[str, Counter[str]] = defaultdict(Counter)
    by_side: dict[str, Counter[str]] = defaultdict(Counter)
    signals = Counter()
    upside_drivers = Counter()
    downside_risks = Counter()
    blank_names: list[str] = []

    for company in selected:
        text = Path(company["path"]).read_text(encoding="utf-8")
        latest_quarter, latest_block = extract_latest_block(text)
        company["latest_quarter"] = latest_quarter or ""

        by_bucket[company["bucket"]]["total"] += 1
        by_side[company["side"]]["total"] += 1

        if not is_filled(latest_block):
            by_bucket[company["bucket"]]["blank"] += 1
            by_side[company["side"]]["blank"] += 1
            blank_names.append(f'{company["bucket"]}/{company["ticker"]}')
            continue

        by_bucket[company["bucket"]]["filled"] += 1
        by_side[company["side"]]["filled"] += 1

        signal_match = re.search(r"^signal:\s*([^#\n]+)", latest_block or "", flags=re.M)
        if signal_match:
            signals[signal_match.group(1).strip()] += 1

        upside_bullets = extract_section(latest_block, "Thesis On Track") or extract_section(
            latest_block, "Upside Drivers"
        )
        for bullet in upside_bullets:
            upside_drivers[normalize_theme(bullet)] += 1

        downside_bullets = extract_section(latest_block, "Thesis Off Track") or extract_section(
            latest_block, "Risk Factors (Macro, Execution, Structural)"
        )
        for bullet in downside_bullets:
            downside_risks[normalize_theme(bullet)] += 1

    total = len(selected)
    blank = sum(counter["blank"] for counter in by_bucket.values())
    filled = sum(counter["filled"] for counter in by_bucket.values())
    side_totals = Counter(company["side"] for company in selected)

    by_bucket_side_gross: dict[str, dict[str, float]] = {}
    for bucket, counter in sorted(by_bucket.items()):
        bucket_companies = [company for company in selected if company["bucket"] == bucket]
        long_count = sum(1 for company in bucket_companies if company["side"] == "Long")
        short_count = sum(1 for company in bucket_companies if company["side"] == "Short")
        by_bucket_side_gross[bucket] = {
            "long_positions": long_count,
            "short_positions": short_count,
            "long_gross_pct": (long_count / side_totals["Long"] * 100) if side_totals["Long"] else 0.0,
            "short_gross_pct": (short_count / side_totals["Short"] * 100) if side_totals["Short"] else 0.0,
        }

    return {
        "total_positions": total,
        "filled_positions": filled,
        "blank_positions": blank,
        "blank_pct": (blank / total * 100) if total else 0.0,
        "coverage_pct": (filled / total * 100) if total else 0.0,
        "by_bucket": {bucket: dict(counter) for bucket, counter in sorted(by_bucket.items())},
        "by_side": {side: dict(counter) for side, counter in sorted(by_side.items())},
        "by_bucket_side_gross": by_bucket_side_gross,
        "signals": dict(signals),
        "upside_drivers": upside_drivers.most_common(),
        "downside_risks": downside_risks.most_common(),
        "blank_names": blank_names,
    }


def render_markdown(result: dict[str, object], top_n: int, include_blank_names: bool) -> str:
    lines: list[str] = []
    lines.append("# Portfolio Note Analysis")
    lines.append("")
    lines.append("## Coverage")
    lines.append(
        f"- Active positions analyzed: {result['total_positions']}"
    )
    lines.append(
        f"- Positions with authored latest-note content: {result['filled_positions']} ({result['coverage_pct']:.1f}%)"
    )
    lines.append(
        f"- Positions still blank: {result['blank_positions']} ({result['blank_pct']:.1f}%)"
    )
    lines.append("")
    lines.append("## Coverage By Side")
    for side, counter in result["by_side"].items():
        filled = counter.get("filled", 0)
        total = counter.get("total", 0)
        blank = counter.get("blank", 0)
        pct = (filled / total * 100) if total else 0.0
        lines.append(f"- {side}: {filled}/{total} filled ({pct:.1f}%), {blank} blank")
    lines.append("")
    lines.append("## Side-Gross Exposure By Bucket")
    for bucket, exposure in sorted(
        result["by_bucket_side_gross"].items(),
        key=lambda item: (-(item[1].get("long_gross_pct", 0) + item[1].get("short_gross_pct", 0)), item[0]),
    ):
        long_pct = exposure.get("long_gross_pct", 0)
        short_pct = exposure.get("short_gross_pct", 0)
        if long_pct == 0 and short_pct == 0:
            continue
        parts = []
        if long_pct:
            parts.append(f"{long_pct:.1f}% of long gross")
        if short_pct:
            parts.append(f"{short_pct:.1f}% of short gross")
        lines.append(f"- {bucket}: {', '.join(parts)}")
    lines.append("")
    lines.append("## Coverage By Bucket")
    for bucket, counter in sorted(
        result["by_bucket"].items(),
        key=lambda item: (-item[1].get("filled", 0), item[0]),
    ):
        total = counter.get("total", 0)
        filled = counter.get("filled", 0)
        blank = counter.get("blank", 0)
        if filled == 0:
            continue
        lines.append(f"- {bucket}: {filled}/{total} filled, {blank} blank")
    lines.append("")
    lines.append("## Portfolio Upside Drivers")
    top_upside = result["upside_drivers"][:top_n]
    if top_upside:
        for text, count in top_upside:
            lines.append(f"- {count}x: {text}")
    else:
        lines.append("- No authored `Thesis On Track` bullets found in latest notes.")
    lines.append("")
    lines.append("## Portfolio Downside Risks")
    top_downside = result["downside_risks"][:top_n]
    if top_downside:
        for text, count in top_downside:
            lines.append(f"- {count}x: {text}")
    else:
        lines.append("- No authored `Thesis Off Track` bullets found in latest notes.")

    if include_blank_names:
        lines.append("")
        lines.append("## Blank Active Positions")
        for name in result["blank_names"]:
            lines.append(f"- {name}")

    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    manifest_path = Path(args.manifest)
    companies = parse_manifest(manifest_path)
    result = analyze(
        companies,
        exclude_cash=args.exclude_cash,
        exclude_buckets=args.exclude_bucket,
    )

    if args.format == "json":
        print(json.dumps(result, indent=2))
        return

    print(render_markdown(result, top_n=args.top, include_blank_names=args.include_blank_names))


if __name__ == "__main__":
    main()
