"""Export bucket KPI workbooks into text-friendly CSV mirrors for GitHub-based agents."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parents[1]
BUCKETS_DIR = ROOT / "buckets"
EXPORT_DIR = ROOT / "00_config" / "kpi_exports"


def export_workbook(workbook_path: Path, export_dir: Path) -> Path | None:
    wb = load_workbook(workbook_path, data_only=True)
    rows = []

    for ws in wb.worksheets:
        for row in ws.iter_rows(min_row=2, values_only=True):
            company, quarter, record_type, kpi, value, yoy, yoy_vs_last_q, yoy_vs_last_y, qoq = row[16:25]
            if not (company and quarter and kpi and value not in (None, "")):
                continue

            quarter_text = quarter.date().isoformat() if hasattr(quarter, "date") else str(quarter)
            rows.append(
                {
                    "sheet": ws.title,
                    "company": str(company),
                    "calendar_quarter": quarter_text,
                    "type": "" if record_type is None else str(record_type),
                    "kpi": str(kpi),
                    "value": value,
                    "yoy": yoy,
                    "yoy_vs_last_q": yoy_vs_last_q,
                    "yoy_vs_last_y": yoy_vs_last_y,
                    "qoq": qoq,
                }
            )

    if not rows:
        return None

    export_dir.mkdir(parents=True, exist_ok=True)
    output_path = export_dir / f"{workbook_path.stem}.csv"
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "sheet",
                "company",
                "calendar_quarter",
                "type",
                "kpi",
                "value",
                "yoy",
                "yoy_vs_last_q",
                "yoy_vs_last_y",
                "qoq",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def iter_bucket_workbooks(bucket: str | None) -> list[Path]:
    if bucket:
        bucket_fs = bucket.lstrip(".")
        candidate = BUCKETS_DIR / bucket_fs / f"{bucket_fs}_kpi.xlsx"
        return [candidate] if candidate.exists() else []

    return sorted(
        workbook
        for workbook in BUCKETS_DIR.glob("*/*_kpi.xlsx")
        if workbook.is_file() and not workbook.name.startswith(".")
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export Mosaic bucket KPI workbooks into text-friendly CSV mirrors."
    )
    parser.add_argument(
        "--bucket",
        help="Bucket ID or dotted bucket symbol to export. Defaults to all bucket KPI workbooks.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(EXPORT_DIR),
        help="Directory for CSV exports. Default: 00_config/kpi_exports",
    )
    args = parser.parse_args()

    export_dir = Path(args.output_dir)
    workbooks = iter_bucket_workbooks(args.bucket)
    if not workbooks:
        raise SystemExit("No matching bucket KPI workbooks found.")

    written = 0
    for workbook_path in workbooks:
        output_path = export_workbook(workbook_path, export_dir)
        if output_path is not None:
            written += 1
            print(output_path.relative_to(ROOT))

    if written == 0:
        raise SystemExit("No normalized KPI rows found to export.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

