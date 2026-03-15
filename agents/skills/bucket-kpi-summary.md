# Mosaic Bucket KPI Summary Skill

skill_name: Bucket KPI Summary
skill_version: 1

## Purpose
Provide a deterministic way to summarize a Mosaic bucket's KPI workbook, including:

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

Then use the canonical KPI workbook:

- `buckets/{BUCKET_FS}/{BUCKET_FS}_kpi.xlsx`

Do not rely on directory traversal as the primary way to find the workbook.

## Trigger Phrases
Use this skill when the user asks for any of the following or something materially similar:

- summarize KPIs of bucket `X`
- assess bucket `X` KPI trends
- is bucket `X` seeing revenue acceleration or deceleration
- are margins expanding or shrinking in bucket `X`
- does bucket `X` imply earnings acceleration or deceleration
- create a KPI scoreboard for bucket `X`

## Data Source Rules
- Prefer the bucket workbook over company markdown files for KPI analysis.
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
Use LTM revenue as the default weighting basis.

### LTM Revenue
- LTM revenue for a company = sum of the latest 4 available quarterly `revenue` values in the workbook
- Order companies descending by LTM revenue

### Bucket Summary Calculations
- Revenue YoY:
  - weighted average of company revenue YoY values using LTM revenue weights
- Revenue acceleration/deceleration breadth:
  - count names with latest-quarter revenue YoY above vs below prior-quarter revenue YoY
  - when useful, also report revenue-weighted breadth
- Gross margin and operating margin levels:
  - weighted average of company margin levels using LTM revenue weights
- Gross margin and operating margin YoY deltas:
  - weighted average of the reported company margin YoY delta values using LTM revenue weights

Important:
- Keep the original method above for bucket margin deltas.
- Do not recompute bucket margin deltas from weighted margin levels unless the user explicitly asks for that alternate method.

## Default Output Structure
Unless the user asks for something else, produce:

1. Short summary
2. Bucket overall scoreboard
3. Member scoreboard ordered by LTM revenue
4. Brief caveats if data coverage is incomplete

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

## Presentation Rules
- Keep bucket summary concise and interpretation-first.
- Use markdown for readability.
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
- large weights can dominate bucket conclusions

## Minimal Workflow
1. Open the governance spec.
2. Open `00_config/active_manifest.md` and confirm the bucket path.
3. Open the bucket KPI workbook.
4. Extract normalized KPI rows if available; otherwise read worksheet matrices carefully.
5. Compute LTM revenue weights.
6. Build the bucket summary.
7. Build the company scoreboard ordered by LTM revenue.
8. State the main conclusion in plain English before or above the scoreboard.
