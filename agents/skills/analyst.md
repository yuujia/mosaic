# Mosaic Analyst Skill (v1)

mosaic_anchor: ANALYST_SKILL  
skill_name: Mosaic Analyst  
skill_version: 1  

## Purpose
Provide a deterministic, repeatable way to locate Mosaic research files and extract basic structured content for analysis (in chat or via CLI automation).

This skill is designed to work across:
- CLI workflows (Codex + scripts)
- Chat workflows (Dropbox connector limitations: directory traversal may not be available)

## Required Entry Point
All executions MUST start by opening the active manifest:

- manifest_file: 00_config/active_manifest.md
- manifest_anchor: mosaic_anchor: ACTIVE_MANIFEST

Do not attempt directory traversal as a primary discovery mechanism.

## How to Locate Files
1. Open `00_config/active_manifest.md`.
2. Find the target bucket section under `## Buckets` (e.g., `### TESTS`).
3. Use the listed `bucket_note_index_file`, `bucket_thesis_file`, and `company_file` paths for that bucket.
4. Prefer opening the bucket note index first when connector directory traversal is unreliable.
5. Open the listed files directly by path.

Authoritative routing:
- Use paths listed inside:
  - `<!-- BEGIN AUTO:BUCKETS --> ... <!-- END AUTO:BUCKETS -->`
  - `<!-- BEGIN AUTO:GLOBAL_COMPANY_INDEX --> ... <!-- END AUTO:GLOBAL_COMPANY_INDEX -->`
- Ignore any file paths mentioned outside these AUTO blocks.

## Basic Extraction Targets (v1)

### 1) Diligence Questions
Look for a section header exactly:
`## Diligence Questions`

Or:
`### Diligence Questions`

Extract each bullet item under that header until the next `##` header.

Do not infer diligence questions from other note text. Extract only explicit bullet items under these headers.

Output columns:
- bucket_id
- ticker
- question_text
- source_file

### 2) Risks
Look for a section header exactly:
`## Risks`

Extract each bullet item under that header until the next `##` header.

Output columns:
- bucket_id
- ticker
- risk_text
- source_file

### 3) KPI Tables (if present)
If a company file contains a KPI table (markdown table) under any header containing the string `KPI` (case-insensitive), extract the rows.

Output columns (best effort):
- bucket_id
- ticker
- period (if present)
- kpi
- value
- yoy (if present)
- qoq (if present)
- source_file

## Output Format Defaults
Unless the user asks otherwise, return results as markdown tables in chat.

## Minimal Normalization Rules
- Preserve original text and units.
- Do NOT treat blanks as zero.
- Do not infer missing numeric values.
- If a target section is missing in a file, skip it silently.

## KPI Presentation Standard (Default)

When KPIs are requested for a company or bucket, present them using a **latest-quarter snapshot format** rather than a full time series.

Historical values should only be shown if the user explicitly asks for them.

### Canonical KPI Table Layout


KPI | Company | Latest Quarter | YoY | Δ YoY | Δ QoQ | QoQ


### Rules

- Only display the **latest reported quarter value**.
- Do not display prior quarter values unless explicitly requested.
- Companies appear as **rows**.
- Each KPI must be displayed in **its own table**.
- Preserve original units from the KPI source.

### Column Order (Canonical)


KPI
Company
Latest Quarter
YoY
Δ YoY
Δ QoQ
QoQ


This layout applies to:

- company KPI summaries
- bucket KPI comparisons
- analyst tear sheets
- dashboard summaries

### Unit Conventions

| KPI Type | Value Unit | YoY Format | QoQ Format |
|---|---|---|---|
| Dollar KPIs | $mm / $bn | % | % |
| Ratio KPIs | % | bps | bps |

### Examples

| KPI | Value Unit |
|---|---|
| TTM_FFO | $mm |
| capex | $mm |
| rate_base_in_billions | $bn |
| FFO_to_debt | % |

### Rules

- Dollar KPIs → percent changes  
- Ratio KPIs → basis point changes  
- Never convert blanks to zero  
- Preserve negative values exactly as reported

## Notes
This is a v1 skill. Future versions may add:

- explicit “Outstanding vs Closed” logic for diligence questions
- canonical KPI mapping
- thesis confirmation/on-track scoring
- idiosyncratic issue scanning
