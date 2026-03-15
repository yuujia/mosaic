# Mosaic Bucket KPI Summary Skill

skill_name: Bucket KPI Summary
skill_version: 1

## Purpose
Provide a deterministic way to summarize a Mosaic bucket's KPIs, including:

- bucket-level KPI summary
- company scoreboard ordered by LTM revenue
- assessment of revenue acceleration/deceleration
- assessment of gross margin and operating margin expansion/shrinking
- earnings implication from the combination of revenue and margin trends

This skill is intended for any agent with repository access, including Codex, ChatGPT, or other agents that read `AGENTS.md`.

## Required Entry Points
Always start with:

1. `agents/specs/Mosaic_Architecture_and_Sync_Spec.md`
2. `00_config/active_manifest.md`

Use the manifest to confirm:

- `bucket_id`
- `bucket_path`
- `bucket_thesis_file`
- companies currently listed in the bucket

Then use the canonical KPI sources in this order:

1. `00_config/kpi_exports/{BUCKET_FS}_kpi.csv`
2. `buckets/{BUCKET_FS}/{BUCKET_FS}_kpi.xlsx`

If the CSV export exists, treat it as the KPI source of truth for agent workflows because it is text-friendly and more reliable for GitHub-based agents.

The canonical KPI workbook remains:

- `buckets/{BUCKET_FS}/{BUCKET_FS}_kpi.xlsx`

Do not rely on directory traversal as the primary way to find KPI sources.

## Trigger Phrases
Use this skill when the user asks for any of the following or something materially similar:

- summarize KPIs of bucket `X`
- assess bucket `X` KPI trends
- is bucket `X` seeing revenue acceleration or deceleration
- are margins expanding or shrinking in bucket `X`
- does bucket `X` imply earnings acceleration or deceleration
- create a KPI scoreboard for bucket `X`
- provide a summary of KPI trends for bucket `X`

## Data Source Rules
- Prefer `00_config/kpi_exports/{BUCKET_FS}_kpi.csv` when it exists.
- Otherwise use the bucket workbook.
- Do not use company markdown files as the primary KPI source if the CSV export or workbook is available.
- Treat each worksheet as one company unless the workbook clearly uses a different convention.
- If a manifest company is missing from the workbook, note it briefly and exclude it from calculations.
- Preserve reported values exactly; do not infer missing values.
- Ignore blank cells and malformed placeholder rows.

## Canonical KPI Set
Default to these KPIs unless the user asks otherwise:

- `revenue`
- `gross_margin_gaap`
- `operating_margin_gaap`

If requested, infer earnings implication from revenue trend plus operating margin trend.

## Company-Level Interpretation Rules
For each company:

- Revenue acceleration/deceleration:
  - compare latest quarter `revenue` YoY growth to the prior quarter `revenue` YoY growth
- Gross margin expansion/shrinking:
  - use `gross_margin_gaap` YoY delta as reported
- Operating margin expansion/shrinking:
  - use `operating_margin_gaap` YoY delta as reported
- Earnings implication:
  - `accelerating` if revenue YoY is accelerating and operating margin YoY delta is positive
  - `decelerating` if revenue YoY is decelerating and operating margin YoY delta is negative
  - otherwise `mixed`

## Bucket-Level Aggregation Rules
Use equal-weight simple averages plus breadth as the default bucket methodology.

### LTM Revenue
- LTM revenue for a company = sum of the latest 4 available quarterly `revenue` values in the workbook
- Use LTM revenue to order companies descending in the member scoreboard
- Do not use LTM revenue as the default bucket weighting basis unless the user explicitly asks for weighted analysis

### Bucket Summary Calculations
- Revenue YoY:
  - simple average of company revenue YoY values across the bucket
- Revenue acceleration/deceleration breadth:
  - count names with latest-quarter revenue YoY above vs below prior-quarter revenue YoY
  - this breadth read is a primary output, not a secondary one
- Gross margin and operating margin levels:
  - simple average of company margin levels across the bucket
- Gross margin and operating margin YoY deltas:
  - simple average of the reported company margin YoY delta values across the bucket

### Breadth Expectations
Always assess and, when useful, report:

- revenue decelerating vs accelerating count
- gross margin shrinking vs expanding count
- operating margin shrinking vs expanding count
- earnings implication breadth (`accelerating`, `decelerating`, `mixed`)

Important:
- Keep the original method above for bucket margin deltas.
- Do not switch to weighted averages unless the user explicitly asks for weighted analysis.
- If weighted analysis is requested, present it as a secondary lens, not the default.

## Default Output Structure
Unless the user explicitly asks for a shorter or different format, produce all of the following:

1. Short summary
2. Bucket overall scoreboard
3. Member scoreboard ordered by LTM revenue
4. Bucket breadth summary
5. Brief caveats if data coverage is incomplete

Important:
- A request to "summarize KPI trends" still requires the bucket overall scoreboard and the member scoreboard.
- Do not replace the scoreboard with a prose-only summary unless the user explicitly asks for prose only.

## Default Scoreboard Format
Use quarter-by-quarter trend strings when consecutive quarters are available.

### Bucket Overall
Show:

- quarter range
- `Rev YoY`
- `GM`
- `GM YoYΔ`
- `OPM`
- `OPM YoYΔ`

Also include a concise breadth read when the user asks for trend assessment:

- revenue accel vs decel count
- GM expand vs shrink count
- OPM expand vs shrink count

### Members
For each company, show:

- ticker
- LTM revenue
- quarter range
- `Rev YoY`
- `GM`
- `GM YoYΔ`
- `OPM`
- `OPM YoYΔ`

Do not include delta-of-delta columns unless the user explicitly asks for them.

When the user asks for "summary of KPI trends", the default response should still follow this scoreboard format after a short introductory summary.

## Presentation Rules
- Keep bucket summary concise and interpretation-first.
- Use markdown for readability.
- Prefer monospace labels and compact trend strings over narrative tables unless the user explicitly asks for tables.
- Prefer breadth-first interpretation over outlier-driven interpretation.
- Preserve units exactly:
  - revenue YoY as percent
  - margin levels as percent
  - margin YoY deltas as basis points
- Distinguish clearly between:
  - margin level
  - margin YoY delta
  - revenue growth rate
  - revenue acceleration/deceleration

## Caveats to Mention When Relevant
- bucket workbook may have fewer names than the manifest
- some companies may have fewer than 4 populated quarters
- mixed fiscal quarter endpoints can make bucket rows slightly heterogeneous
- large outliers can distort simple averages; note them separately when relevant

## Minimal Workflow
1. Open the governance spec.
2. Open `00_config/active_manifest.md` and confirm the bucket path.
3. Open `00_config/kpi_exports/{BUCKET_FS}_kpi.csv` if it exists; otherwise open the bucket KPI workbook.
4. Extract normalized KPI rows if available; otherwise read worksheet matrices carefully.
5. Compute LTM revenue only for company ordering.
6. Build the bucket summary using equal-weight simple averages.
7. Build the bucket breadth summary.
8. Build the company scoreboard ordered by LTM revenue.
9. State the main conclusion in plain English before or above the scoreboard.
