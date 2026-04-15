#!/usr/bin/env python3
"""Build a standalone HTML dashboard for a Mosaic bucket."""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[1]
KPI_EXPORT_DIR = ROOT / "00_config" / "kpi_exports"
BUCKETS_DIR = ROOT / "buckets"


CANONICAL_KPIS = ("revenue", "gross_margin_gaap", "operating_margin_gaap")
ESTIMATE_TYPE_TOKENS = {"consensus", "estimate", "estimates", "forecast", "forward", "guidance", "guide", "ntm"}
NON_DIRECTIONAL_TYPE_TOKENS = {"canonical", "custom"}
ACTUAL_STATUS_TOKENS = {"actual", "reported", "historical"}


def quarter_label(iso_date: str) -> str:
    year, month, _ = iso_date.split("-")
    quarter = {"03": "Q1", "06": "Q2", "09": "Q3", "12": "Q4"}[month]
    return f"{quarter} {year}"


def period_sort_key(label: str) -> tuple[int, int]:
    match = re.search(r"(\d{4})\s+Q([1-4])", label)
    if match:
        return int(match.group(1)), int(match.group(2))
    return (0, 0)


def prior_periods(label: str, count: int) -> list[str]:
    year, quarter = period_sort_key(label)
    if not year or not quarter:
        return []
    periods = []
    for _ in range(count):
        periods.append(f"{year} Q{quarter}")
        quarter -= 1
        if quarter == 0:
            year -= 1
            quarter = 4
    return list(reversed(periods))


def pct_text(value: float | None) -> str:
    return "na" if value is None else f"{value * 100:.1f}%"


def margin_text(value: float | None) -> str:
    return "na" if value is None else f"{value:.1f}%"


def bps_text(value: float | None) -> str:
    return "na" if value is None else f"{value:.0f} bps"


def read_kpi_csv(bucket: str) -> list[dict[str, str]]:
    path = KPI_EXPORT_DIR / f"{bucket}_kpi.csv"
    if not path.exists():
        try:
            rel_path = path.relative_to(ROOT)
        except ValueError:
            rel_path = path
        print(f"Missing KPI export: {rel_path}")
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def quarter_end_is_future(quarter_text: str | None) -> bool:
    if not quarter_text:
        return False
    try:
        return date.fromisoformat(quarter_text[:10]) > date.today()
    except ValueError:
        return False


def normalize_row_kind(
    period_status: str | None = None,
    row_type: str | None = None,
    quarter_text: str | None = None,
) -> str:
    status_text = (period_status or "").strip().lower()
    if status_text:
        status_tokens = {token for token in re.split(r"[^a-z0-9]+", status_text) if token}
        if status_tokens & ESTIMATE_TYPE_TOKENS:
            return "estimate"
        if status_tokens & ACTUAL_STATUS_TOKENS:
            return "actual"

    text = (row_type or "").strip().lower()
    if not text:
        return "estimate" if quarter_end_is_future(quarter_text) else "actual"
    tokens = {token for token in re.split(r"[^a-z0-9]+", text) if token}
    if tokens & ESTIMATE_TYPE_TOKENS:
        return "estimate"
    if tokens <= NON_DIRECTIONAL_TYPE_TOKENS and quarter_end_is_future(quarter_text):
        return "estimate"
    return "actual"


def read_bucket_note_index(bucket: str) -> str:
    return (BUCKETS_DIR / bucket / f"{bucket}_note_index.md").read_text(encoding="utf-8", errors="ignore")


def parse_company_file(bucket: str, ticker: str) -> str:
    return (BUCKETS_DIR / bucket / ticker / f"{ticker}.md").read_text(encoding="utf-8", errors="ignore")


def parse_note_sections(text: str) -> list[tuple[str, str]]:
    parts = re.split(r"(^##\s+.+$)", text, flags=re.M)
    sections: list[tuple[str, str]] = []
    for idx in range(1, len(parts), 2):
        header = parts[idx].strip()[3:].strip()
        body = parts[idx + 1]
        sections.append((header, body))
    return sections


def extract_bullets(body: str, heading: str) -> list[str]:
    match = re.search(rf"^### {re.escape(heading)}\s*\n(.*?)(?=^### |\Z)", body, flags=re.S | re.M)
    if not match:
        return []
    bullets = []
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            bullet = stripped[2:].strip()
            if bullet:
                bullets.append(bullet)
    return bullets


def extract_thesis_progress(body: str) -> tuple[str | None, str | None]:
    match = re.search(
        r"^### Thesis Progress\s*\n(?:.*\n)*?signal:\s*([A-Za-z-]+)\s*(?:#.*)?\n(?:.*\n)*?rationale:\s*(.+)$",
        body,
        flags=re.M,
    )
    if match:
        return match.group(1).strip(), match.group(2).strip()
    signal_match = re.search(r"^### Thesis Progress\s*\n(?:.*\n)*?signal:\s*([A-Za-z-]+)", body, flags=re.M)
    if signal_match:
        return signal_match.group(1).strip(), None
    return None, None


def parse_note_index_tickers(note_index_text: str) -> list[str]:
    return re.findall(r"^### ([A-Z0-9_]+)$", note_index_text, flags=re.M)


def build_kpi_payload(rows: list[dict[str, str]]) -> dict[str, object]:
    by_company: dict[str, dict[str, dict[str, dict[str, float | None]]]] = defaultdict(lambda: defaultdict(dict))
    estimate_by_company: dict[str, dict[str, dict[str, dict[str, float | None]]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    for row in rows:
        if row["kpi"] not in CANONICAL_KPIS:
            continue
        try:
            value = float(row["value"])
        except ValueError:
            value = None
        try:
            yoy = float(row["yoy"])
        except ValueError:
            yoy = None
        try:
            yoy_vs_last_q = float(row["yoy_vs_last_q"])
        except ValueError:
            yoy_vs_last_q = None
        quarter = row["calendar_quarter"]
        parsed_row = {
            "value": value,
            "yoy": yoy,
            "yoy_vs_last_q": yoy_vs_last_q,
        }
        target = (
            estimate_by_company
            if normalize_row_kind(row.get("period_status"), row.get("type"), quarter) == "estimate"
            else by_company
        )
        target[row["sheet"]][row["kpi"]][quarter] = parsed_row

    company_order = []
    for ticker, kpis in by_company.items():
        rev_quarters = sorted(kpis["revenue"])
        if len(rev_quarters) < 2:
            continue
        ltm_quarters = rev_quarters[-4:]
        ltm_revenue = sum(kpis["revenue"][quarter]["value"] or 0.0 for quarter in ltm_quarters)
        company_order.append((ticker, ltm_revenue, rev_quarters))
    company_order.sort(key=lambda item: item[1], reverse=True)

    quarter_coverage = Counter(
        quarter
        for ticker, _, _ in company_order
        for quarter in by_company[ticker]["revenue"].keys()
        if quarter.startswith("202")
    )
    if not quarter_coverage:
        latest_common_quarters = []
    else:
        max_coverage = max(quarter_coverage.values())
        # Roll forward once a majority of covered companies have reported.
        coverage_floor = max(2, (max_coverage // 2) + 1)
        latest_common_quarters = sorted(
            quarter for quarter, count in quarter_coverage.items() if count >= coverage_floor
        )[-4:]

    bucket_table = []
    metric_rows = {
        "Revenue YoY Growth": [],
        "Revenue YoYΔ": [],
        "Gross Margin": [],
        "Gross Margin YoYΔ": [],
        "Operating Margin": [],
        "Operating Margin YoYΔ": [],
    }
    for quarter in latest_common_quarters:
        rev_yoys = []
        gm_values = []
        gm_yoys = []
        op_values = []
        op_yoys = []
        rev_yoy_deltas = []
        for ticker, _, _ in company_order:
            rev_row = by_company[ticker]["revenue"].get(quarter)
            gm_row = by_company[ticker]["gross_margin_gaap"].get(quarter)
            op_row = by_company[ticker]["operating_margin_gaap"].get(quarter)
            if rev_row and rev_row["yoy"] is not None:
                rev_yoys.append(float(rev_row["yoy"]))
            if rev_row and rev_row["yoy_vs_last_q"] is not None:
                rev_yoy_deltas.append(float(rev_row["yoy_vs_last_q"]))
            if gm_row and gm_row["value"] is not None:
                gm_values.append(float(gm_row["value"]))
            if gm_row and gm_row["yoy"] is not None:
                gm_yoys.append(float(gm_row["yoy"]))
            if op_row and op_row["value"] is not None:
                op_values.append(float(op_row["value"]))
            if op_row and op_row["yoy"] is not None:
                op_yoys.append(float(op_row["yoy"]))
        metric_rows["Revenue YoY Growth"].append(mean(rev_yoys) if rev_yoys else None)
        metric_rows["Revenue YoYΔ"].append(mean(rev_yoy_deltas) if rev_yoy_deltas else None)
        metric_rows["Gross Margin"].append(mean(gm_values) if gm_values else None)
        metric_rows["Gross Margin YoYΔ"].append(mean(gm_yoys) if gm_yoys else None)
        metric_rows["Operating Margin"].append(mean(op_values) if op_values else None)
        metric_rows["Operating Margin YoYΔ"].append(mean(op_yoys) if op_yoys else None)

    for metric, values in metric_rows.items():
        bucket_table.append({"metric": metric, "values": values})

    revenue_counts = {"accelerating": 0, "decelerating": 0}
    gm_counts = {"expanding": 0, "contracting": 0}
    op_counts = {"expanding": 0, "contracting": 0}
    member_rows = []
    distribution_rows = {
        "Revenue YoY Growth": [],
        "Revenue YoYΔ": [],
        "Gross Margin": [],
        "Gross Margin YoYΔ": [],
        "Operating Margin": [],
        "Operating Margin YoYΔ": [],
    }

    for ticker, ltm_revenue, rev_quarters in company_order:
        quarters = rev_quarters[-4:]
        latest_actual_quarter = quarters[-1] if quarters else None
        forward_estimate_quarters = []
        for quarter in sorted(estimate_by_company[ticker]["revenue"]):
            if latest_actual_quarter is None or quarter > latest_actual_quarter:
                forward_estimate_quarters.append(quarter)
        rev_yoys = [by_company[ticker]["revenue"].get(quarter, {}).get("yoy") for quarter in quarters]
        rev_yoy_deltas = [by_company[ticker]["revenue"].get(quarter, {}).get("yoy_vs_last_q") for quarter in quarters]
        gm_values = [by_company[ticker]["gross_margin_gaap"].get(quarter, {}).get("value") for quarter in quarters]
        gm_yoys = [by_company[ticker]["gross_margin_gaap"].get(quarter, {}).get("yoy") for quarter in quarters]
        op_values = [by_company[ticker]["operating_margin_gaap"].get(quarter, {}).get("value") for quarter in quarters]
        op_yoys = [by_company[ticker]["operating_margin_gaap"].get(quarter, {}).get("yoy") for quarter in quarters]
        if len(rev_yoys) >= 2 and rev_yoys[-1] is not None and rev_yoys[-2] is not None:
            if rev_yoys[-1] > rev_yoys[-2]:
                revenue_counts["accelerating"] += 1
            elif rev_yoys[-1] < rev_yoys[-2]:
                revenue_counts["decelerating"] += 1
        latest_bucket_quarter = latest_common_quarters[-1] if latest_common_quarters else None
        latest_rev_row = by_company[ticker]["revenue"].get(latest_bucket_quarter, {}) if latest_bucket_quarter else {}
        latest_gm_row = by_company[ticker]["gross_margin_gaap"].get(latest_bucket_quarter, {}) if latest_bucket_quarter else {}
        latest_op_row = by_company[ticker]["operating_margin_gaap"].get(latest_bucket_quarter, {}) if latest_bucket_quarter else {}

        if gm_yoys and gm_yoys[-1] is not None:
            if gm_yoys[-1] > 0:
                gm_counts["expanding"] += 1
            elif gm_yoys[-1] < 0:
                gm_counts["contracting"] += 1
        if op_yoys and op_yoys[-1] is not None:
            if op_yoys[-1] > 0:
                op_counts["expanding"] += 1
            elif op_yoys[-1] < 0:
                op_counts["contracting"] += 1

        if latest_rev_row.get("yoy") is not None:
            latest_rev = float(latest_rev_row["yoy"])
            distribution_rows["Revenue YoY Growth"].append(
                {"ticker": ticker, "value": latest_rev * 100, "display": pct_text(latest_rev)}
            )
        if latest_rev_row.get("yoy_vs_last_q") is not None:
            latest_rev_delta = float(latest_rev_row["yoy_vs_last_q"])
            distribution_rows["Revenue YoYΔ"].append(
                {"ticker": ticker, "value": latest_rev_delta, "display": bps_text(latest_rev_delta)}
            )
        if latest_gm_row.get("yoy") is not None:
            latest_gm = float(latest_gm_row["yoy"])
            distribution_rows["Gross Margin YoYΔ"].append(
                {"ticker": ticker, "value": latest_gm, "display": bps_text(latest_gm)}
            )
        if latest_gm_row.get("value") is not None:
            latest_gm_value = float(latest_gm_row["value"])
            distribution_rows["Gross Margin"].append(
                {"ticker": ticker, "value": latest_gm_value, "display": margin_text(latest_gm_value)}
            )
        if latest_op_row.get("yoy") is not None:
            latest_op = float(latest_op_row["yoy"])
            distribution_rows["Operating Margin YoYΔ"].append(
                {"ticker": ticker, "value": latest_op, "display": bps_text(latest_op)}
            )
        if latest_op_row.get("value") is not None:
            latest_op_value = float(latest_op_row["value"])
            distribution_rows["Operating Margin"].append(
                {"ticker": ticker, "value": latest_op_value, "display": margin_text(latest_op_value)}
            )
        member_rows.append(
            {
                "ticker": ticker,
                "ltmRevenue": round(ltm_revenue, 1),
                "quarters": [quarter_label(q) for q in quarters],
                "revenueYoy": [pct_text(v) for v in rev_yoys],
                "revenueYoyDelta": [bps_text(v) for v in rev_yoy_deltas],
                "grossMargin": [margin_text(v) for v in gm_values],
                "grossMarginYoyDelta": [bps_text(v) for v in gm_yoys],
                "operatingMargin": [margin_text(v) for v in op_values],
                "operatingMarginYoyDelta": [bps_text(v) for v in op_yoys],
                "forwardRevenueEstimateQuarters": [quarter_label(q) for q in forward_estimate_quarters],
                "forwardRevenueEstimateYoy": [
                    pct_text(estimate_by_company[ticker]["revenue"].get(quarter, {}).get("yoy"))
                    for quarter in forward_estimate_quarters
                ],
            }
        )

    estimate_coverage = Counter(
        quarter
        for ticker in estimate_by_company
        for quarter in estimate_by_company[ticker]["revenue"].keys()
        if quarter.startswith("202")
    )
    forecast_rows = []
    for ticker, _, _ in company_order:
        coverage = sorted(estimate_by_company[ticker]["revenue"].keys())
        if not coverage:
            continue
        forecast_rows.append(
            {
                "ticker": ticker,
                "quarters": [quarter_label(q) for q in coverage],
                "revenueYoy": [
                    pct_text(estimate_by_company[ticker]["revenue"].get(quarter, {}).get("yoy"))
                    for quarter in coverage
                ],
            }
        )

    return {
        "quarters": [quarter_label(q) for q in latest_common_quarters],
        "latestDistributionQuarter": quarter_label(latest_common_quarters[-1]) if latest_common_quarters else "",
        "bucketTable": bucket_table,
        "breadth": {
            "revenue": revenue_counts,
            "grossMargin": gm_counts,
            "operatingMargin": op_counts,
        },
        "distribution": {
            metric: sorted(values, key=lambda item: item["value"], reverse=True)
            for metric, values in distribution_rows.items()
        },
        "estimateCoverage": [
            {"quarter": quarter_label(quarter), "count": count}
            for quarter, count in sorted(estimate_coverage.items())
        ],
        "forecastRows": forecast_rows,
        "memberRows": member_rows,
    }


def build_note_payload(bucket: str, tickers: list[str]) -> dict[str, object]:
    latest_confirming = []
    latest_disconfirming = []
    latest_thematic = []
    trend_counts: dict[str, Counter[str]] = defaultdict(Counter)
    latest_quarter_notes = []
    current_signal_counts = Counter()

    for ticker in tickers:
        text = parse_company_file(bucket, ticker)
        sections = parse_note_sections(text)
        for header, body in sections:
            signal, _ = extract_thesis_progress(body)
            if signal:
                trend_counts[header][signal] += 1
        if not sections:
            continue
        latest_header, latest_body = sections[0]
        signal, rationale = extract_thesis_progress(latest_body)
        if signal:
            current_signal_counts[signal] += 1
        confirming = extract_bullets(latest_body, "Thesis On Track")
        disconfirming = extract_bullets(latest_body, "Thesis Off Track")
        thematic = extract_bullets(latest_body, "Thematic Color")
        latest_confirming.extend({"ticker": ticker, "text": bullet} for bullet in confirming)
        latest_disconfirming.extend({"ticker": ticker, "text": bullet} for bullet in disconfirming)
        latest_thematic.extend({"ticker": ticker, "text": bullet} for bullet in thematic)
        latest_quarter_notes.append(
            {
                "ticker": ticker,
                "quarter": latest_header,
                "signal": signal or "Missing",
                "rationale": rationale or "",
            }
        )

    trend_coverage = {quarter: sum(counts.values()) for quarter, counts in trend_counts.items()}
    if trend_coverage:
        max_trend_coverage = max(trend_coverage.values())
        trend_floor = max(2, (max_trend_coverage // 2) + 1)
        majority_quarters = sorted(
            (quarter for quarter, count in trend_coverage.items() if count >= trend_floor),
            key=period_sort_key,
        )
        if majority_quarters:
            anchor_quarter = majority_quarters[-1]
        else:
            anchor_quarter = max(trend_coverage.keys(), key=period_sort_key)
        trend_quarters = prior_periods(anchor_quarter, 4)
    else:
        trend_quarters = []
    ordered_trend = []
    for quarter in sorted(trend_quarters, key=period_sort_key):
        ordered_trend.append(
            {
                "quarter": quarter,
                "Green": trend_counts[quarter]["Green"],
                "Yellow": trend_counts[quarter]["Yellow"],
                "Red": trend_counts[quarter]["Red"],
            }
        )

    progress_color = "Yellow"
    if current_signal_counts["Green"] > current_signal_counts["Red"]:
        progress_color = "Yellow-Green" if current_signal_counts["Green"] > 0 else "Yellow"
    elif current_signal_counts["Red"] > current_signal_counts["Green"]:
        progress_color = "Yellow-Red"

    return {
        "trend": ordered_trend,
        "currentSignalCounts": dict(current_signal_counts),
        "progressColor": progress_color,
        "currentSignals": sorted(latest_quarter_notes, key=lambda item: (item["signal"], item["ticker"])),
        "confirming": latest_confirming[:18],
        "disconfirming": latest_disconfirming[:18],
        "thematic": latest_thematic[:18],
        "latestSignals": latest_quarter_notes,
    }


def build_html(bucket: str, kpi_payload: dict[str, object], note_payload: dict[str, object]) -> str:
    title = f"{bucket} Bucket Dashboard"
    payload = json.dumps({"bucket": bucket, "kpis": kpi_payload, "notes": note_payload})
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{
      --bg: #f3efe5;
      --paper: #fffaf0;
      --ink: #18211f;
      --muted: #67736f;
      --line: #d7cdb7;
      --accent: #8c3f2b;
      --accent-soft: #e8c1a4;
      --green: #2f7d4a;
      --yellow: #b98511;
      --red: #9f3025;
      --shadow: 0 18px 50px rgba(24, 33, 31, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(140,63,43,0.18), transparent 30%),
        linear-gradient(180deg, #f8f4ea 0%, var(--bg) 100%);
    }}
    .page {{
      width: min(1200px, calc(100vw - 32px));
      margin: 28px auto 40px;
    }}
    .hero, .panel {{
      background: var(--paper);
      border: 1px solid rgba(140, 63, 43, 0.14);
      border-radius: 24px;
      box-shadow: var(--shadow);
    }}
    .hero {{
      padding: 28px 30px 24px;
      margin-bottom: 22px;
      position: relative;
      overflow: hidden;
    }}
    .hero::after {{
      content: "";
      position: absolute;
      inset: auto -40px -40px auto;
      width: 240px;
      height: 240px;
      border-radius: 999px;
      background: radial-gradient(circle, rgba(140,63,43,0.16), transparent 70%);
    }}
    h1, h2, h3 {{ margin: 0; font-weight: 600; }}
    h1 {{ font-size: clamp(2rem, 4vw, 3.2rem); letter-spacing: -0.03em; }}
    h2 {{ font-size: 1.25rem; margin-bottom: 14px; }}
    h3 {{ font-size: 1rem; margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); }}
    .subhead {{ margin-top: 8px; color: var(--muted); max-width: 760px; line-height: 1.45; }}
    .hero-grid {{
      display: grid;
      grid-template-columns: 1.4fr 1fr;
      gap: 18px;
      margin-top: 22px;
    }}
    .summary-card {{
      background: rgba(255,255,255,0.55);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
    }}
    .progress-pill {{
      display: inline-block;
      padding: 8px 14px;
      border-radius: 999px;
      font-size: 0.9rem;
      border: 1px solid transparent;
      font-weight: 700;
      letter-spacing: 0.04em;
    }}
    .progress-Yellow-Green {{ background: rgba(47,125,74,0.14); border-color: rgba(47,125,74,0.28); color: var(--green); }}
    .progress-Yellow {{ background: rgba(185,133,17,0.15); border-color: rgba(185,133,17,0.3); color: var(--yellow); }}
    .progress-Yellow-Red, .progress-Red {{ background: rgba(159,48,37,0.12); border-color: rgba(159,48,37,0.25); color: var(--red); }}
    .summary-stats {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0,1fr));
      gap: 12px;
      margin-top: 16px;
    }}
    .stat {{
      background: white;
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 12px;
    }}
    .stat.green {{ background: rgba(47,125,74,0.10); border-color: rgba(47,125,74,0.25); }}
    .stat.yellow {{ background: rgba(185,133,17,0.12); border-color: rgba(185,133,17,0.26); }}
    .stat.red {{ background: rgba(159,48,37,0.10); border-color: rgba(159,48,37,0.22); }}
    .stat-value {{ font-size: 1.4rem; font-weight: 700; }}
    .summary-link {{
      display: inline-flex;
      align-items: center;
      margin-top: 16px;
      color: var(--accent);
      text-decoration: underline;
      text-underline-offset: 3px;
      cursor: pointer;
      font-size: 0.95rem;
      background: none;
      border: 0;
      padding: 0;
      font: inherit;
    }}
    .layout {{
      display: grid;
      grid-template-columns: 1.4fr 1fr;
      gap: 22px;
    }}
    .panel {{
      padding: 22px;
      margin-bottom: 22px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.95rem;
    }}
    th, td {{
      text-align: left;
      padding: 12px 10px;
      border-bottom: 1px solid var(--line);
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.07em;
    }}
    .metric-label {{ font-weight: 600; }}
    .controls {{
      display: flex;
      gap: 12px;
      align-items: center;
      margin-bottom: 14px;
      flex-wrap: wrap;
    }}
    select {{
      appearance: none;
      border: 1px solid var(--line);
      background: white;
      border-radius: 12px;
      padding: 10px 14px;
      font: inherit;
      color: var(--ink);
    }}
    .bars {{
      display: grid;
      gap: 12px;
    }}
    .signal-groups {{
      display: grid;
      gap: 14px;
    }}
    .signal-group {{
      border: 1px solid var(--line);
      border-radius: 16px;
      background: white;
      padding: 14px;
    }}
    .signal-group.green {{ border-color: rgba(47,125,74,0.24); background: rgba(47,125,74,0.06); }}
    .signal-group.yellow {{ border-color: rgba(185,133,17,0.26); background: rgba(185,133,17,0.08); }}
    .signal-group.red {{ border-color: rgba(159,48,37,0.24); background: rgba(159,48,37,0.06); }}
    .signal-group.missing {{ border-color: rgba(103,115,111,0.20); background: rgba(103,115,111,0.05); }}
    .signal-group-head {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
      font-size: 0.92rem;
      font-weight: 700;
      letter-spacing: 0.04em;
    }}
    .signal-company-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}
    .signal-company {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 7px 10px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: #fffdf8;
      font-size: 0.9rem;
    }}
    .signal-company small {{
      color: var(--muted);
      font-size: 0.76rem;
    }}
    .bar-row {{
      display: grid;
      grid-template-columns: 180px 1fr 44px;
      align-items: center;
      gap: 12px;
      font-size: 0.93rem;
    }}
    .bar-track {{
      height: 18px;
      border-radius: 999px;
      background: #efe6d2;
      overflow: hidden;
      position: relative;
    }}
    .bar-zero {{
      position: absolute;
      inset: 0 auto 0 0;
      width: 2px;
      background: rgba(24, 33, 31, 0.28);
      transform: translateX(-1px);
    }}
    .bar-fill {{
      position: absolute;
      top: 0;
      bottom: 0;
      border-radius: 999px;
      background: linear-gradient(90deg, var(--accent) 0%, #c46f4d 100%);
    }}
    .bar-fill.negative {{
      background: linear-gradient(90deg, #c98a5b 0%, var(--red) 100%);
    }}
    .signal-trend {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(72px, 1fr));
      gap: 10px;
    }}
    .signal-quarter {{
      background: white;
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 10px;
    }}
    .stack {{
      height: 82px;
      display: flex;
      align-items: flex-end;
      gap: 6px;
      margin-top: 8px;
    }}
    .stack-col {{
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      gap: 4px;
      min-width: 0;
    }}
    .signal-counts {{
      display: grid;
      gap: 5px;
      margin-top: 8px;
      font-size: 0.85rem;
    }}
    .signal-chip {{
      display: flex;
      justify-content: space-between;
      padding: 5px 8px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: #fffaf6;
    }}
    .signal-chip.green {{ color: var(--green); border-color: rgba(47,125,74,0.22); background: rgba(47,125,74,0.08); }}
    .signal-chip.yellow {{ color: var(--yellow); border-color: rgba(185,133,17,0.24); background: rgba(185,133,17,0.10); }}
    .signal-chip.red {{ color: var(--red); border-color: rgba(159,48,37,0.22); background: rgba(159,48,37,0.08); }}
    .seg {{ border-radius: 8px 8px 2px 2px; }}
    .seg.green {{ background: rgba(47,125,74,0.8); }}
    .seg.yellow {{ background: rgba(185,133,17,0.8); }}
    .seg.red {{ background: rgba(159,48,37,0.82); }}
    .bullet-list {{
      display: grid;
      gap: 10px;
      margin: 0;
      padding: 0;
      list-style: none;
    }}
    .bullet-list li {{
      padding: 12px 14px;
      border-radius: 14px;
      border: 1px solid var(--line);
      background: white;
      line-height: 1.4;
    }}
    .details-grid {{
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
    }}
    .details-grid .panel {{
      margin-bottom: 0;
    }}
    .ticker {{
      display: inline-block;
      min-width: 52px;
      font-weight: 700;
      color: var(--accent);
    }}
    details {{
      border: 1px solid var(--line);
      border-radius: 16px;
      background: white;
      padding: 10px 14px;
    }}
    details + details {{ margin-top: 10px; }}
    summary {{
      cursor: pointer;
      font-weight: 600;
      color: var(--ink);
    }}
    .member-lines {{
      margin-top: 12px;
      display: grid;
      gap: 8px;
      font-size: 0.94rem;
    }}
    .member-lines code {{ font-family: "SFMono-Regular", Consolas, monospace; background: #f4ede0; padding: 2px 6px; border-radius: 6px; }}
    .muted {{ color: var(--muted); }}
    @media (max-width: 900px) {{
      .hero-grid, .layout {{ grid-template-columns: 1fr; }}
      .details-grid {{ grid-template-columns: 1fr; }}
      .bar-row {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <section class="hero">
      <h1>{html.escape(title)}</h1>
      <p class="subhead">Connector-safe bucket dashboard built from the KPI CSV export, company notes, and thesis progress signals. This view leads with the bucket KPI trend table, then shows breadth and note evidence.</p>
      <div class="hero-grid">
        <div class="summary-card">
          <h3>Thesis Progress - Current Status</h3>
          <div id="progress-pill" class="progress-pill"></div>
          <div class="summary-stats">
            <div class="stat green"><div class="muted">Green</div><div class="stat-value" id="green-count"></div></div>
            <div class="stat yellow"><div class="muted">Yellow</div><div class="stat-value" id="yellow-count"></div></div>
            <div class="stat red"><div class="muted">Red</div><div class="stat-value" id="red-count"></div></div>
          </div>
          <button type="button" id="thesis-details-toggle" class="summary-link" aria-expanded="false">Thesis Details</button>
        </div>
        <div class="summary-card">
          <h3>Breadth Snapshot</h3>
          <div class="member-lines" id="breadth-snapshot"></div>
        </div>
      </div>
    </section>

    <section id="thesis-details-panel" class="panel" hidden>
      <h2>Thesis Details</h2>
      <div class="details-grid">
        <section class="panel">
          <h2>Thesis Confirming</h2>
          <ul class="bullet-list" id="confirming-list"></ul>
        </section>
        <section class="panel">
          <h2>Thesis Disconfirming</h2>
          <ul class="bullet-list" id="disconfirming-list"></ul>
        </section>
        <section class="panel">
          <h2>Thematic Color</h2>
          <ul class="bullet-list" id="thematic-list"></ul>
        </section>
      </div>
    </section>

    <section class="panel">
      <h2>Thesis Progress Trend</h2>
      <div class="signal-trend" id="signal-trend"></div>
    </section>

    <section class="panel">
      <h2>Bucket KPI Trend</h2>
      <table id="bucket-table"></table>
    </section>

    <section class="panel">
      <h2>Interpretation</h2>
      <div class="member-lines" id="interpretation"></div>
    </section>

    <section class="panel">
      <h2>Forward Estimates</h2>
      <div class="member-lines" id="forecast-summary"></div>
      <div id="forecast-scoreboard"></div>
    </section>

    <section class="panel">
      <div class="controls">
        <div>
          <h2 style="margin-bottom:6px">Company Distribution</h2>
          <div class="muted" id="distribution-subhead">Latest-quarter company distribution for the selected KPI lens.</div>
        </div>
        <select id="distribution-select">
          <option>Thesis Progress</option>
          <option>Revenue YoY Growth</option>
          <option>Revenue YoYΔ</option>
          <option>Gross Margin</option>
          <option>Gross Margin YoYΔ</option>
          <option>Operating Margin</option>
          <option>Operating Margin YoYΔ</option>
        </select>
      </div>
      <div class="bars" id="distribution-bars"></div>
    </section>

    <section class="panel">
      <h2>Member Scoreboard</h2>
      <div id="member-scoreboard"></div>
    </section>
  </div>

  <script>
    const payload = {payload};

    const bucketTable = document.getElementById('bucket-table');
    const tableHead = document.createElement('thead');
    const headRow = document.createElement('tr');
    ['Metric', ...payload.kpis.quarters].forEach(label => {{
      const th = document.createElement('th');
      th.textContent = label;
      headRow.appendChild(th);
    }});
    tableHead.appendChild(headRow);
    bucketTable.appendChild(tableHead);

    const tableBody = document.createElement('tbody');
    payload.kpis.bucketTable.forEach(row => {{
      const tr = document.createElement('tr');
      const metric = document.createElement('td');
      metric.className = 'metric-label';
      metric.textContent = row.metric;
      tr.appendChild(metric);
      row.values.forEach((value, index) => {{
        const td = document.createElement('td');
        const metricName = payload.kpis.bucketTable.find(item => item.metric === row.metric).metric;
        if (metricName === 'Revenue YoY Growth') td.textContent = value === null ? 'na' : `${{(value * 100).toFixed(1)}}%`;
        else if (metricName.includes('YoY')) td.textContent = value === null ? 'na' : `${{value.toFixed(0)}} bps`;
        else td.textContent = value === null ? 'na' : `${{value.toFixed(1)}}%`;
        tr.appendChild(td);
      }});
      tableBody.appendChild(tr);
    }});
    bucketTable.appendChild(tableBody);

    const counts = payload.notes.currentSignalCounts;
    const progressPill = document.getElementById('progress-pill');
    progressPill.textContent = payload.notes.progressColor;
    progressPill.classList.add(`progress-${{payload.notes.progressColor}}`);
    document.getElementById('green-count').textContent = counts.Green || 0;
    document.getElementById('yellow-count').textContent = counts.Yellow || 0;
    document.getElementById('red-count').textContent = counts.Red || 0;

    const thesisDetailsToggle = document.getElementById('thesis-details-toggle');
    const thesisDetailsPanel = document.getElementById('thesis-details-panel');
    thesisDetailsToggle.addEventListener('click', () => {{
      const isHidden = thesisDetailsPanel.hasAttribute('hidden');
      if (isHidden) thesisDetailsPanel.removeAttribute('hidden');
      else thesisDetailsPanel.setAttribute('hidden', '');
      thesisDetailsToggle.setAttribute('aria-expanded', String(isHidden));
      thesisDetailsToggle.textContent = isHidden ? 'Hide Thesis Details' : 'Thesis Details';
    }});

    const breadthSnapshot = document.getElementById('breadth-snapshot');
    [
      `Revenue accel vs decel: ${{payload.kpis.breadth.revenue.accelerating}} / ${{payload.kpis.breadth.revenue.decelerating}}`,
      `GM expand vs shrink: ${{payload.kpis.breadth.grossMargin.expanding}} / ${{payload.kpis.breadth.grossMargin.contracting}}`,
      `OPM expand vs shrink: ${{payload.kpis.breadth.operatingMargin.expanding}} / ${{payload.kpis.breadth.operatingMargin.contracting}}`,
    ].forEach(line => {{
      const item = document.createElement('div');
      item.textContent = line;
      breadthSnapshot.appendChild(item);
    }});

    const interpretation = document.getElementById('interpretation');
    const revMetric = payload.kpis.bucketTable.find(row => row.metric === 'Revenue YoY Growth');
    const gmMetric = payload.kpis.bucketTable.find(row => row.metric === 'Gross Margin YoYΔ');
    const opMetric = payload.kpis.bucketTable.find(row => row.metric === 'Operating Margin YoYΔ');
    [
      `Bucket revenue growth averages have moved from ${{(revMetric.values[0] * 100).toFixed(1)}}% to ${{(revMetric.values[revMetric.values.length - 1] * 100).toFixed(1)}}% across the displayed quarters.`,
      `Gross margin pressure is ${{(gmMetric.values[gmMetric.values.length - 1] || 0) < 0 ? 'net contracting' : 'still net expanding'}} on a simple-average basis, but breadth matters more than the average alone.`,
      `Operating margins remain the cleaner offset, with ${{payload.kpis.breadth.operatingMargin.expanding}} names expanding versus ${{payload.kpis.breadth.operatingMargin.contracting}} shrinking in the latest quarter.`,
    ].forEach(line => {{
      const item = document.createElement('div');
      item.textContent = line;
      interpretation.appendChild(item);
    }});

    const forecastSummary = document.getElementById('forecast-summary');
    const estimateCoverage = payload.kpis.estimateCoverage || [];
    if (estimateCoverage.length) {{
      const coverageLine = document.createElement('div');
      coverageLine.textContent = `Forward revenue estimate coverage: ${{estimateCoverage.map(item => `${{item.quarter}} (${{item.count}})`).join(' · ')}}`;
      forecastSummary.appendChild(coverageLine);
    }} else {{
      const emptyLine = document.createElement('div');
      emptyLine.textContent = 'No forward revenue estimates detected in the KPI export.';
      forecastSummary.appendChild(emptyLine);
    }}

    const forecastScoreboard = document.getElementById('forecast-scoreboard');
    (payload.kpis.forecastRows || []).forEach(row => {{
      const block = document.createElement('details');
      const summary = document.createElement('summary');
      summary.textContent = `${{row.ticker}} · Forward Revenue`;
      const lines = document.createElement('div');
      lines.className = 'member-lines';
      [
        ['Estimate Quarters', row.quarters.join(' → ')],
        ['Revenue YoY', row.revenueYoy.join(' → ')],
      ].forEach(([label, value]) => {{
        const line = document.createElement('div');
        line.innerHTML = `<code>${{label}}</code> ${{value}}`;
        lines.appendChild(line);
      }});
      block.append(summary, lines);
      forecastScoreboard.appendChild(block);
    }});

    const distributions = payload.kpis.distribution;
    const distributionBars = document.getElementById('distribution-bars');
    const distributionSelect = document.getElementById('distribution-select');
    document.getElementById('distribution-subhead').textContent = `Latest-quarter company distribution for the selected KPI lens (${{payload.kpis.latestDistributionQuarter}}).`;
    function renderDistribution(metric) {{
      distributionBars.innerHTML = '';
      if (metric === 'Thesis Progress') {{
        const groups = [
          ['Green', 'green'],
          ['Yellow', 'yellow'],
          ['Red', 'red'],
          ['Missing', 'missing'],
        ];
        const cards = document.createElement('div');
        cards.className = 'signal-groups';
        groups.forEach(([label, cls]) => {{
          const matches = (payload.notes.currentSignals || []).filter(item => item.signal === label);
          if (!matches.length) return;
          const group = document.createElement('div');
          group.className = `signal-group ${{cls}}`;
          const head = document.createElement('div');
          head.className = 'signal-group-head';
          head.innerHTML = `<span>${{label}}</span><span>${{matches.length}}</span>`;
          const list = document.createElement('div');
          list.className = 'signal-company-list';
          matches.forEach(item => {{
            const pill = document.createElement('div');
            pill.className = 'signal-company';
            pill.innerHTML = `<strong>${{item.ticker}}</strong><small>${{item.quarter}}</small>`;
            list.appendChild(pill);
          }});
          group.append(head, list);
          cards.appendChild(group);
        }});
        distributionBars.appendChild(cards);
        return;
      }}
      const values = distributions[metric] || [];
      if (!values.length) return;
      const min = Math.min(...values.map(item => item.value), 0);
      const max = Math.max(...values.map(item => item.value), 0);
      const span = Math.max(max - min, 1);
      const zeroPos = ((0 - min) / span) * 100;
      values.forEach(item => {{
        const row = document.createElement('div');
        row.className = 'bar-row';
        const name = document.createElement('div');
        name.textContent = item.ticker;
        const track = document.createElement('div');
        track.className = 'bar-track';
        const zero = document.createElement('div');
        zero.className = 'bar-zero';
        zero.style.left = `${{zeroPos}}%`;
        const fill = document.createElement('div');
        fill.className = 'bar-fill';
        if (item.value < 0) fill.classList.add('negative');
        const valuePos = ((item.value - min) / span) * 100;
        fill.style.left = `${{Math.min(zeroPos, valuePos)}}%`;
        fill.style.width = `${{Math.max(Math.abs(valuePos - zeroPos), 1.2)}}%`;
        track.append(zero, fill);
        const value = document.createElement('div');
        value.textContent = item.display;
        row.append(name, track, value);
        distributionBars.appendChild(row);
      }});
    }}
    distributionSelect.addEventListener('change', event => renderDistribution(event.target.value));
    renderDistribution(distributionSelect.value);

    const signalTrend = document.getElementById('signal-trend');
    payload.notes.trend.forEach(row => {{
      const total = Math.max(row.Green + row.Yellow + row.Red, 1);
      const card = document.createElement('div');
      card.className = 'signal-quarter';
      const title = document.createElement('div');
      title.innerHTML = `<strong>${{row.quarter}}</strong>`;
      const stack = document.createElement('div');
      stack.className = 'stack';
      const col = document.createElement('div');
      col.className = 'stack-col';
      [['green', row.Green], ['yellow', row.Yellow], ['red', row.Red]].forEach(([cls, count]) => {{
        const seg = document.createElement('div');
        seg.className = `seg ${{cls}}`;
        seg.style.height = `${{(count / total) * 100}}%`;
        seg.title = `${{cls}}: ${{count}}`;
        col.appendChild(seg);
      }});
      stack.appendChild(col);
      const foot = document.createElement('div');
      foot.className = 'signal-counts';
      [['green', row.Green], ['yellow', row.Yellow], ['red', row.Red]].forEach(([cls, count]) => {{
        const chip = document.createElement('div');
        chip.className = `signal-chip ${{cls}}`;
        chip.innerHTML = `<span>${{cls.toUpperCase()}}</span><strong>${{count}}</strong>`;
        foot.appendChild(chip);
      }});
      card.append(title, stack, foot);
      signalTrend.appendChild(card);
    }});

    function renderBulletList(targetId, items) {{
      const target = document.getElementById(targetId);
      items.forEach(item => {{
        const li = document.createElement('li');
        li.innerHTML = `<span class="ticker">${{item.ticker}}</span> ${{item.text}}`;
        target.appendChild(li);
      }});
    }}
    renderBulletList('confirming-list', payload.notes.confirming);
    renderBulletList('disconfirming-list', payload.notes.disconfirming);
    renderBulletList('thematic-list', payload.notes.thematic);

    const memberScoreboard = document.getElementById('member-scoreboard');
    payload.kpis.memberRows.forEach(row => {{
      const block = document.createElement('details');
      const summary = document.createElement('summary');
      summary.textContent = `${{row.ticker}} · LTM ${{row.ltmRevenue}}`;
      const lines = document.createElement('div');
      lines.className = 'member-lines';
      [
        ['Quarters', row.quarters.join(' → ')],
        ['Rev YoY', row.revenueYoy.join(' → ')],
        ['Rev YoYΔ', row.revenueYoyDelta.join(' → ')],
        ['GM', row.grossMargin.join(' → ')],
        ['GM YoYΔ', row.grossMarginYoyDelta.join(' → ')],
        ['OPM', row.operatingMargin.join(' → ')],
        ['OPM YoYΔ', row.operatingMarginYoyDelta.join(' → ')],
      ].forEach(([label, value]) => {{
        const line = document.createElement('div');
        line.innerHTML = `<code>${{label}}</code> ${{value}}`;
        lines.appendChild(line);
      }});
      block.append(summary, lines);
      memberScoreboard.appendChild(block);
    }});
  </script>
</body>
</html>"""


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a standalone HTML dashboard for a Mosaic bucket from local KPI exports and note files."
    )
    parser.add_argument("--bucket", required=True, help="Bucket filesystem id, e.g. AGENTICS")
    parser.add_argument(
        "--output",
        help="Output HTML path. Defaults to buckets/{BUCKET}/{BUCKET}_dashboard.html",
    )
    args = parser.parse_args()

    bucket = args.bucket.lstrip(".")
    note_index_text = read_bucket_note_index(bucket)
    tickers = parse_note_index_tickers(note_index_text)
    rows = read_kpi_csv(bucket)
    kpi_payload = build_kpi_payload(rows)
    note_payload = build_note_payload(bucket, tickers)
    html_text = build_html(bucket, kpi_payload, note_payload)

    output_path = Path(args.output) if args.output else BUCKETS_DIR / bucket / f"{bucket}_dashboard.html"
    output_path.write_text(html_text, encoding="utf-8")
    print(output_path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
