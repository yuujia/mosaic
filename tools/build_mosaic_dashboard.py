#!/usr/bin/env python3
"""Build a Mosaic decision dashboard for a bucket."""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[1]
BUCKETS_DIR = ROOT / "buckets"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a Mosaic dashboard for one bucket.")
    parser.add_argument("bucket", help="Filesystem bucket name, e.g. CANCER")
    return parser.parse_args()


def parse_note_sections(text: str) -> list[tuple[str, str]]:
    parts = re.split(r"(^##\s+.+$)", text, flags=re.M)
    sections: list[tuple[str, str]] = []
    for idx in range(1, len(parts), 2):
        header = parts[idx].strip()[3:].strip()
        body = parts[idx + 1]
        sections.append((header, body))
    return sections


def parse_field(body: str, field_name: str) -> str:
    match = re.search(rf"^{re.escape(field_name)}:\s*(.+?)\s*$", body, flags=re.M)
    return match.group(1).strip() if match else ""


def extract_bullets(body: str, heading: str) -> list[str]:
    match = re.search(rf"^### {re.escape(heading)}\s*\n(.*?)(?=^### |\Z)", body, flags=re.S | re.M)
    if not match:
        return []
    bullets: list[str] = []
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            text = stripped[2:].strip()
            if text:
                bullets.append(text)
    return bullets


def instrument_to_ticker(instrument: str) -> str:
    return instrument.split()[0]


def quarter_key(label: str) -> tuple[int, int]:
    match = re.search(r"(\d{4})\s+Q([1-4])", label)
    if not match:
        return (0, 0)
    return int(match.group(1)), int(match.group(2))


def extract_top_section(text: str, heading: str) -> list[str]:
    match = re.search(rf"^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)", text, flags=re.S | re.M)
    if not match:
        return []
    bullets = []
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(stripped[2:].strip())
    return [bullet for bullet in bullets if bullet]


def latest_quarter_section(text: str) -> tuple[str, str]:
    sections = [
        (header, body)
        for header, body in parse_note_sections(text)
        if re.fullmatch(r"\d{4}\s+Q[1-4]", header.strip())
    ]
    if not sections:
        return ("", "")
    return max(sections, key=lambda item: quarter_key(item[0]))


def classify_risk_bullets(bullets: list[str]) -> dict[str, list[str]]:
    grouped = {"Macro": [], "Execution": [], "Structural": [], "Other": []}
    for bullet in bullets:
        match = re.match(r"^(Macro|Execution|Structural):\s*(.+)$", bullet, flags=re.I)
        if not match:
            grouped["Other"].append(bullet)
            continue
        key = match.group(1).capitalize()
        grouped[key].append(match.group(2).strip())
    return grouped


def split_tagged_bullet(text: str) -> tuple[str, str]:
    if ":" not in text:
        return ("", text.strip())
    tag, remainder = text.split(":", 1)
    return (tag.strip(), remainder.strip())


def compact_bullets(bullets: list[str]) -> str:
    compact = []
    for bullet in bullets:
        tag, detail = split_tagged_bullet(bullet)
        compact.append(f"{tag}: {detail}" if tag else detail)
    return " | ".join(item for item in compact if item)


def first_compact_bullet(bullets: list[str]) -> str:
    if not bullets:
        return ""
    tag, detail = split_tagged_bullet(bullets[0])
    return f"{tag}: {detail}" if tag else detail


def bucket_implication_groups(bullets: list[str]) -> dict[str, list[str]]:
    groups = {
        "Confirms secular thesis": [],
        "Drivers and risk factors": [],
        "Other": [],
    }
    for bullet in bullets:
        tag, detail = split_tagged_bullet(bullet)
        normalized = tag.lower()
        if normalized == "confirms secular thesis":
            groups["Confirms secular thesis"].append(detail)
        elif normalized == "drivers and risk factors":
            groups["Drivers and risk factors"].append(detail)
        else:
            groups["Other"].append(detail if detail else bullet)
    return groups


def derive_performance_read(
    relative_return_vs_benchmark: float,
    relative_return_vs_bucket: float | None,
    kpi_assessment: str,
    forward_trajectory: str,
) -> str:
    assessment = (kpi_assessment or "").lower()
    trajectory = (forward_trajectory or "").lower()
    improving = any(token in assessment for token in ("accelerat", "expanding", "continued accelerating"))
    decelerating = "decelerat" in assessment or "decelerat" in trajectory
    if relative_return_vs_bucket is not None and relative_return_vs_bucket < 0 and improving:
        return "Lagging bucket despite solid current fundamentals; market appears focused on durability."
    if relative_return_vs_bucket is not None and relative_return_vs_bucket > 0 and decelerating:
        return "Leading bucket even as trajectory softens; market may see the slowdown as better contained."
    if relative_return_vs_benchmark < 0 and decelerating:
        return "Underperforming as the market discounts slower forward growth."
    if relative_return_vs_benchmark > 0 and improving:
        return "Outperforming as recent evidence is translating into market recognition."
    return "Mixed translation between current results and forward expectations."


def parse_company_notes(bucket: str) -> list[dict[str, str]]:
    bucket_dir = BUCKETS_DIR / bucket
    rows: list[dict[str, str]] = []
    for company_dir in sorted(path for path in bucket_dir.iterdir() if path.is_dir() and not path.name.startswith("_")):
        note_path = company_dir / f"{company_dir.name}.md"
        if not note_path.exists():
            continue
        text = note_path.read_text(encoding="utf-8", errors="ignore")
        header, body = latest_quarter_section(text)
        if not body:
            continue
        forward_bullets = extract_bullets(body, "Forward Trajectory")
        bucket_implication_bullets = extract_bullets(body, "Bucket Implications")
        implication_groups = bucket_implication_groups(bucket_implication_bullets)
        risk_bullets = extract_bullets(body, "Risk Factors (Macro, Execution, Structural)")
        risk_groups = classify_risk_bullets(risk_bullets)
        rows.append(
            {
                "ticker": company_dir.name,
                "calendar_quarter": parse_field(body, "calendar_quarter") or header,
                "event_date": parse_field(body, "event_date"),
                "thematic_color": " | ".join(extract_top_section(text, "Thematic Color")),
                "diligence_questions": " | ".join(extract_top_section(text, "Diligence Questions")),
                "major_changes": " | ".join(extract_bullets(body, "Major Announcements and Changes")),
                "kpi_assessment": " | ".join(extract_bullets(body, "Quarterly KPI Assessment")),
                "key_kpi_drivers": " | ".join(extract_bullets(body, "Key KPI Drivers")),
                "forward_trajectory": " | ".join(forward_bullets),
                "forward_trajectory_first": first_compact_bullet(forward_bullets),
                "forward_trajectory_compact": compact_bullets(forward_bullets),
                "upside_drivers": " | ".join(extract_bullets(body, "Upside Drivers")),
                "risk_factors": " | ".join(risk_bullets),
                "macro_risks": " | ".join(risk_groups["Macro"]),
                "execution_risks": " | ".join(risk_groups["Execution"]),
                "structural_risks": " | ".join(risk_groups["Structural"] + risk_groups["Other"]),
                "bucket_implications": " | ".join(bucket_implication_bullets),
                "bucket_implications_compact": compact_bullets(bucket_implication_bullets),
                "bucket_implication_groups": implication_groups,
                "path": str(note_path.relative_to(ROOT)),
            }
        )
    return rows


def read_event_rows(bucket: str) -> list[dict[str, str]]:
    path = BUCKETS_DIR / bucket / f"{bucket}_event_returns.csv"
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def latest_quarter(rows: list[dict[str, str]]) -> str:
    quarters = sorted({row["calendar_quarter"] for row in rows if row.get("calendar_quarter")})
    return quarters[-1] if quarters else ""
def read_bucket_thesis(bucket: str) -> dict[str, list[str] | str]:
    path = BUCKETS_DIR / bucket / f"{bucket}_bucket_thesis.md"
    text = path.read_text(encoding="utf-8", errors="ignore")
    sections = {}
    for title in ("Core Thesis", "Structural Drivers (Required Conditions)", "Structural Failure Modes"):
        match = re.search(rf"## {re.escape(title)}\s*\n(.*?)(?=\n## |\Z)", text, flags=re.S)
        body = match.group(1).strip() if match else ""
        if title == "Core Thesis":
            sections["core_thesis"] = " ".join(line.strip() for line in body.splitlines() if line.strip() and line.strip() != "---")
        elif body:
            bullets = [line.strip()[2:].strip() for line in body.splitlines() if line.strip().startswith("- ")]
            sections[title] = [bullet for bullet in bullets if bullet]
        else:
            sections[title] = []
    return sections


def build_payload(bucket: str) -> dict[str, object]:
    note_rows = parse_company_notes(bucket)
    event_rows = read_event_rows(bucket)
    latest_event_quarter = latest_quarter(event_rows)
    latest_note_quarter = max((row["calendar_quarter"] for row in note_rows), default="", key=quarter_key)

    latest_event_rows = [
        row for row in event_rows
        if row.get("calendar_quarter") == latest_event_quarter
        and row.get("instrument") == row.get("event_ticker")
    ]
    average_rel = mean(float(row["relative_return_vs_benchmark"]) for row in latest_event_rows) if latest_event_rows else None
    average_bucket_raw = mean(float(row["raw_return"]) for row in latest_event_rows) if latest_event_rows else None
    exact_or_near = sum(1 for row in latest_event_rows if row.get("match_quality") in {"exact_date", "near_date"})

    company_by_ticker = {row["ticker"]: row for row in note_rows}
    event_cards = []
    for row in sorted(latest_event_rows, key=lambda item: item["event_ticker"]):
        ticker = instrument_to_ticker(row["event_ticker"])
        note = company_by_ticker.get(ticker, {})
        raw_return = float(row["raw_return"])
        event_cards.append(
            {
                "ticker": ticker,
                "report_date": row["report_date"],
                "calendar_quarter": row["calendar_quarter"],
                "relative_return_vs_benchmark": float(row["relative_return_vs_benchmark"]),
                "relative_return_vs_bucket": (
                    None if average_bucket_raw is None else raw_return - average_bucket_raw
                ),
                "raw_return": raw_return,
                "kpi_assessment": note.get("kpi_assessment", ""),
                "key_kpi_drivers": note.get("key_kpi_drivers", ""),
                "forward_trajectory": note.get("forward_trajectory", ""),
                "execution_risks": note.get("execution_risks", ""),
                "structural_risks": note.get("structural_risks", ""),
                "bucket_implications": note.get("bucket_implications", ""),
                "performance_read": derive_performance_read(
                    float(row["relative_return_vs_benchmark"]),
                    None if average_bucket_raw is None else raw_return - average_bucket_raw,
                    note.get("kpi_assessment", ""),
                    note.get("forward_trajectory", ""),
                ),
            }
        )

    thesis = read_bucket_thesis(bucket)
    latest_note_rows = [row for row in note_rows if row["calendar_quarter"] == latest_note_quarter]
    mosaic_focus = {
        "secular_confirmation": [
            {
                "ticker": row["ticker"],
                "groups": row["bucket_implication_groups"],
            }
            for row in latest_note_rows
            if row["bucket_implications_compact"] or row["bucket_implications"] or row["kpi_assessment"]
        ],
        "durability": [
            {
                "ticker": row["ticker"],
                "text": row["forward_trajectory_first"] or row["forward_trajectory_compact"] or row["forward_trajectory"] or row["execution_risks"],
                "detail": row["forward_trajectory_compact"] or row["forward_trajectory"] or row["execution_risks"],
            }
            for row in latest_note_rows
            if row["forward_trajectory_first"] or row["forward_trajectory_compact"] or row["forward_trajectory"] or row["execution_risks"]
        ],
    }
    return {
        "bucket": bucket,
        "thesis": thesis,
        "coverage": {
            "company_notes": len(note_rows),
            "latest_note_quarter": latest_note_quarter,
            "latest_event_quarter": latest_event_quarter,
            "latest_events": len(latest_event_rows),
            "matched_events": exact_or_near,
        },
        "mosaic_focus": mosaic_focus,
        "market_translation": {
            "average_relative_return": average_rel,
            "average_bucket_raw_return": average_bucket_raw,
            "event_cards": event_cards,
        },
        "company_notes": note_rows,
    }


def render_dashboard(payload: dict[str, object]) -> str:
    data_json = json.dumps(payload)
    bucket = html.escape(str(payload["bucket"]))
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{bucket} Mosaic Dashboard</title>
  <style>
    :root {{
      --bg: #f4f0e8;
      --ink: #1f2520;
      --muted: #667166;
      --card: rgba(255,255,255,0.78);
      --line: rgba(31,37,32,0.12);
      --accent: #215f43;
      --warn: #9a6700;
      --risk: #a33a2b;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(33,95,67,0.15), transparent 30%),
        radial-gradient(circle at top right, rgba(163,58,43,0.12), transparent 28%),
        linear-gradient(180deg, #f7f3ec, var(--bg));
    }}
    main {{ max-width: 1200px; margin: 0 auto; padding: 32px 20px 48px; }}
    h1, h2 {{ margin: 0 0 12px; font-weight: 600; }}
    h3 {{ margin: 0 0 8px; font-size: 1rem; }}
    p {{ margin: 0; line-height: 1.5; }}
    .lede {{ color: var(--muted); max-width: 860px; margin-bottom: 28px; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 16px;
      margin-bottom: 28px;
    }}
    .card {{
      background: var(--card);
      backdrop-filter: blur(8px);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
      box-shadow: 0 10px 30px rgba(31,37,32,0.06);
    }}
    .metric {{
      font-size: 2rem;
      margin-top: 10px;
    }}
    .metric-card-spotlight {{
      background: linear-gradient(135deg, rgba(33,95,67,0.16), rgba(255,255,255,0.9));
      border-color: rgba(33,95,67,0.28);
      box-shadow: 0 14px 34px rgba(33,95,67,0.12);
    }}
    .metric-card-negative {{
      background: linear-gradient(135deg, rgba(163,58,43,0.16), rgba(255,255,255,0.9));
      border-color: rgba(163,58,43,0.28);
      box-shadow: 0 14px 34px rgba(163,58,43,0.12);
    }}
    .metric-card-spotlight .metric {{
      color: var(--accent);
      font-size: 2.25rem;
    }}
    .metric-card-negative .metric {{
      color: var(--risk);
      font-size: 2.25rem;
    }}
    .label {{ color: var(--muted); font-size: 0.88rem; text-transform: uppercase; letter-spacing: 0.08em; }}
    .list {{ padding-left: 18px; margin: 8px 0 0; }}
    .section {{ margin-top: 28px; }}
    .stack {{ display: grid; gap: 12px; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 18px;
      overflow: hidden;
    }}
    th, td {{
      padding: 12px 10px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
      font-size: 0.95rem;
    }}
    th {{ font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); }}
    tr:last-child td {{ border-bottom: none; }}
    .pill {{
      display: inline-block;
      border-radius: 999px;
      padding: 4px 10px;
      font-size: 0.8rem;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.75);
    }}
    .green {{ color: var(--accent); }}
    .yellow {{ color: var(--warn); }}
    .red {{ color: var(--risk); }}
    .negative {{ color: var(--risk); }}
    .positive {{ color: var(--accent); }}
    .focus-card {{
      min-height: 180px;
    }}
    .focus-item {{
      margin-top: 10px;
      padding-top: 10px;
      border-top: 1px solid var(--line);
    }}
    .focus-lines {{
      display: grid;
      gap: 6px;
      margin-top: 6px;
    }}
    .focus-line {{
      padding-left: 12px;
      position: relative;
      line-height: 1.45;
    }}
    .focus-line::before {{
      content: '';
      width: 5px;
      height: 5px;
      border-radius: 999px;
      background: var(--accent);
      position: absolute;
      left: 0;
      top: 0.58rem;
    }}
    .detail-toggle {{
      margin-top: 8px;
      border: 1px solid var(--line);
      background: rgba(255,255,255,0.72);
      border-radius: 999px;
      padding: 6px 10px;
      font: inherit;
      color: var(--ink);
      cursor: pointer;
    }}
    dialog {{
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 18px;
      max-width: 560px;
      width: calc(100vw - 32px);
      background: #fffdf9;
      color: var(--ink);
      box-shadow: 0 20px 60px rgba(31,37,32,0.18);
    }}
    dialog::backdrop {{
      background: rgba(31,37,32,0.28);
    }}
    .dialog-close {{
      margin-top: 14px;
      border: 1px solid var(--line);
      background: white;
      border-radius: 999px;
      padding: 6px 10px;
      font: inherit;
      cursor: pointer;
    }}
    .focus-item strong {{
      display: inline-block;
      min-width: 52px;
      font-size: 0.82rem;
      color: var(--muted);
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }}
    .focus-group-title {{
      margin-top: 8px;
      font-size: 0.82rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    @media (max-width: 720px) {{
      table, thead, tbody, th, td, tr {{ display: block; }}
      thead {{ display: none; }}
      td {{ padding: 10px 12px; }}
      td::before {{
        content: attr(data-label);
        display: block;
        font-size: 0.78rem;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 4px;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <h1>{bucket} Mosaic Dashboard</h1>
    <p class="lede">This view centers Mosaic's core questions: is the bucket thesis intact, what is the market translating from recent evidence, and where do company updates point to timing, execution, or structural risk.</p>

    <section class="section">
      <h2>Bucket Thesis</h2>
      <div class="grid">
        <div class="card">
          <div class="label">Core Thesis</div>
          <p id="core-thesis"></p>
        </div>
        <div class="card">
          <div class="label">Structural Drivers</div>
          <ul class="list" id="structural-drivers"></ul>
        </div>
        <div class="card">
          <div class="label">Failure Modes</div>
          <ul class="list" id="failure-modes"></ul>
        </div>
      </div>
    </section>

    <div class="grid" id="summary-grid"></div>

    <section class="section">
      <h2>Bucket Level Snapshot</h2>
      <div class="grid">
        <div class="card focus-card">
          <div class="label">Secular confirmation vs disruptive risk factors</div>
          <div class="stack" id="focus-secular"></div>
        </div>
        <div class="card focus-card">
          <div class="label">Durability</div>
          <div class="stack" id="focus-timing"></div>
        </div>
      </div>
    </section>

    <section class="section">
      <h2>Latest Market Translation</h2>
      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Quarter</th>
            <th>Report Date</th>
            <th>Rel Perf vs Benchmark</th>
            <th>Rel Perf vs Bucket</th>
            <th>Performance Read</th>
            <th>KPI Assessment</th>
            <th>Key KPI Drivers</th>
            <th>Forward Trajectory</th>
            <th>Bucket Implications</th>
          </tr>
        </thead>
        <tbody id="event-rows"></tbody>
      </table>
    </section>

    <section class="section">
      <h2>Latest Company Notes</h2>
      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Quarter</th>
            <th>Event Date</th>
            <th>Key KPI Drivers</th>
            <th>Forward Trajectory</th>
            <th>Risk Factors</th>
            <th>Diligence Questions</th>
          </tr>
        </thead>
        <tbody id="company-rows"></tbody>
      </table>
    </section>
  </main>
  <dialog id="detail-dialog">
    <h3 id="detail-title"></h3>
    <div id="detail-body" class="focus-lines"></div>
    <button class="dialog-close" id="detail-close" type="button">Close</button>
  </dialog>
  <script>
    const payload = {data_json};

    const fmtPct = value => {{
      if (value === null || value === undefined || Number.isNaN(value)) return 'na';
      return `${{(value * 100).toFixed(1)}}%`;
    }};

    const summaryGrid = document.getElementById('summary-grid');
    const relPerfClass = (payload.market_translation.average_relative_return ?? 0) < 0
      ? 'metric-card-negative'
      : 'metric-card-spotlight';
    const summaryCards = [
      ['Latest event quarter', payload.coverage.latest_event_quarter || 'Missing', ''],
      ['Updated for latest quarter', `${{payload.coverage.matched_events}} / ${{payload.coverage.latest_events}}`, ''],
      ['Average bucket return', fmtPct(payload.market_translation.average_bucket_raw_return), ''],
      ['Average rel perf', fmtPct(payload.market_translation.average_relative_return), relPerfClass],
    ];
    summaryCards.forEach(([label, value, className]) => {{
      const card = document.createElement('div');
      card.className = `card ${{className || ''}}`.trim();
      card.innerHTML = `<div class="label">${{label}}</div><div class="metric">${{value}}</div>`;
      summaryGrid.appendChild(card);
    }});

    document.getElementById('core-thesis').textContent = payload.thesis.core_thesis || 'Missing';
    const fillList = (id, items) => {{
      const target = document.getElementById(id);
      (items || []).forEach(item => {{
        const li = document.createElement('li');
        li.textContent = item;
        target.appendChild(li);
      }});
    }};
    fillList('structural-drivers', payload.thesis['Structural Drivers (Required Conditions)']);
    fillList('failure-modes', payload.thesis['Structural Failure Modes']);

    const renderFocus = (id, items, mode = 'lines') => {{
      const root = document.getElementById(id);
      if (!items.length) {{
        const p = document.createElement('p');
        p.textContent = 'Missing';
        root.appendChild(p);
        return;
      }}
      const splitText = text => text.split(' | ').map(part => part.trim()).filter(Boolean);
      if (mode === 'grouped') {{
        const grouped = [
          ['Confirms Secular Thesis', []],
          ['Drivers and Risk Factors', []],
          ['Other', []],
        ];
        items.forEach(item => {{
          (item.groups?.['Confirms secular thesis'] || []).forEach(entry => grouped[0][1].push([item.ticker, entry]));
          (item.groups?.['Drivers and risk factors'] || []).forEach(entry => grouped[1][1].push([item.ticker, entry]));
          (item.groups?.Other || []).forEach(entry => grouped[2][1].push([item.ticker, entry]));
        }});
        grouped.forEach(([title, entries]) => {{
          if (!entries.length) return;
          const section = document.createElement('div');
          section.className = 'focus-item';
          const groupTitle = document.createElement('div');
          groupTitle.className = 'focus-group-title';
          groupTitle.textContent = `${{title}}:`;
          section.appendChild(groupTitle);
          const body = document.createElement('div');
          body.className = 'focus-lines';
          entries.forEach(([ticker, entry]) => {{
            const line = document.createElement('div');
            line.className = 'focus-line';
            line.innerHTML = `<strong>${{ticker}}</strong><span>${{entry}}</span>`;
            body.appendChild(line);
          }});
          section.appendChild(body);
          root.appendChild(section);
        }});
        return;
      }}
      items.forEach(item => {{
        const div = document.createElement('div');
        div.className = 'focus-item';
        const body = document.createElement('div');
        body.className = 'focus-lines';
        if (mode === 'single') {{
          const line = document.createElement('div');
          line.className = 'focus-line';
          line.textContent = item.text || 'Missing';
          body.appendChild(line);
        }} else {{
          const lines = splitText(item.text || '');
          lines.forEach(entry => {{
            const line = document.createElement('div');
            line.className = 'focus-line';
            line.textContent = entry;
            body.appendChild(line);
          }});
        }}
        div.innerHTML = `<strong>${{item.ticker}}</strong>`;
        div.appendChild(body);
        if (item.detail && item.detail !== item.text) {{
          const button = document.createElement('button');
          button.type = 'button';
          button.className = 'detail-toggle';
          button.textContent = 'More';
          button.addEventListener('click', () => openDetail(item.ticker, item.detail));
          div.appendChild(button);
        }}
        root.appendChild(div);
      }});
    }};
    const dialog = document.getElementById('detail-dialog');
    const detailTitle = document.getElementById('detail-title');
    const detailBody = document.getElementById('detail-body');
    const openDetail = (ticker, text) => {{
      detailTitle.textContent = `${{ticker}} durability detail`;
      detailBody.innerHTML = '';
      text.split(' | ').map(part => part.trim()).filter(Boolean).forEach(entry => {{
        const line = document.createElement('div');
        line.className = 'focus-line';
        line.textContent = entry;
        detailBody.appendChild(line);
      }});
      dialog.showModal();
    }};
    document.getElementById('detail-close').addEventListener('click', () => dialog.close());
    renderFocus('focus-secular', payload.mosaic_focus.secular_confirmation, 'grouped');
    renderFocus('focus-timing', payload.mosaic_focus.durability, 'single');

    const eventRows = document.getElementById('event-rows');
    payload.market_translation.event_cards.forEach(row => {{
      const tr = document.createElement('tr');
      const relBenchClass = row.relative_return_vs_benchmark < 0 ? 'negative' : 'positive';
      const relBucketClass = row.relative_return_vs_bucket < 0 ? 'negative' : 'positive';
      tr.innerHTML = `
        <td data-label="Ticker">${{row.ticker}}</td>
        <td data-label="Quarter">${{row.calendar_quarter || 'Missing'}}</td>
        <td data-label="Report Date">${{row.report_date}}</td>
        <td data-label="Rel Perf vs Benchmark" class="${{relBenchClass}}">${{fmtPct(row.relative_return_vs_benchmark)}}</td>
        <td data-label="Rel Perf vs Bucket" class="${{relBucketClass}}">${{fmtPct(row.relative_return_vs_bucket)}}</td>
        <td data-label="Performance Read">${{row.performance_read || 'Missing'}}</td>
        <td data-label="KPI Assessment">${{row.kpi_assessment || 'Missing'}}</td>
        <td data-label="Key KPI Drivers">${{row.key_kpi_drivers || 'Missing'}}</td>
        <td data-label="Forward Trajectory">${{row.forward_trajectory || 'Missing'}}</td>
        <td data-label="Bucket Implications">${{row.bucket_implications || 'Missing'}}</td>
      `;
      eventRows.appendChild(tr);
    }});

    const companyRows = document.getElementById('company-rows');
    payload.company_notes.forEach(row => {{
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td data-label="Ticker">${{row.ticker}}</td>
        <td data-label="Quarter">${{row.calendar_quarter}}</td>
        <td data-label="Event Date">${{row.event_date || 'Missing'}}</td>
        <td data-label="Key KPI Drivers">${{row.key_kpi_drivers || 'Missing'}}</td>
        <td data-label="Forward Trajectory">${{row.forward_trajectory || 'Missing'}}</td>
        <td data-label="Risk Factors">${{row.risk_factors || 'Missing'}}</td>
        <td data-label="Diligence Questions">${{row.diligence_questions || 'Missing'}}</td>
      `;
      companyRows.appendChild(tr);
    }});
  </script>
</body>
</html>
"""


def main() -> None:
    args = parse_args()
    payload = build_payload(args.bucket)
    output_path = BUCKETS_DIR / args.bucket / f"{args.bucket}_mosaic_dashboard.html"
    output_path.write_text(render_dashboard(payload), encoding="utf-8")
    print(f"Wrote dashboard to {output_path}")


if __name__ == "__main__":
    main()
