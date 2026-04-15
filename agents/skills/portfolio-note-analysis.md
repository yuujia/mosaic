# Mosaic Portfolio Note Analysis Skill

skill_name: Portfolio Note Analysis
skill_version: 1

## Purpose
Provide a deterministic way to summarize Mosaic at the portfolio level from company update notes.

This skill is for requests such as:

- portfolio-level upside drivers
- portfolio-level downside risks
- equal-weighted portfolio picture from written company updates
- what percent of active positions are still blank
- coverage-aware portfolio synthesis from active company notes

## Required Entry Points
Always start with:

1. `agents/specs/Mosaic_Architecture_and_Sync_Spec.md`
2. `00_config/active_manifest.md`

Use the manifest as the active-position source of truth.

Do not discover active names by filesystem traversal as the primary method.

## Canonical Workflow
1. Open the governance spec.
2. Open `00_config/active_manifest.md`.
3. Run `python tools/portfolio_note_analysis.py --exclude-cash`.
4. If the user wants the blank names listed, rerun with `--include-blank-names`.
5. Use the latest authored quarter in each active company file only.
6. Treat a note as blank when the latest quarter block is missing or all key fields are placeholders / `-`.
7. Use side-level equal weighting by default unless the user explicitly asks for another weighting scheme.

## Portfolio Weighting Rule
Unless the user specifies otherwise, treat positions as roughly equally sized within each side:

- Long book: all active longs share 100% long gross exposure.
- Short book: all active shorts share 100% short gross exposure.
- Bucket and factor exposure should be calculated as percent of long-side gross for longs and percent of short-side gross for shorts.
- Do not treat one long and one short as equal portfolio gross exposure when the active book has different counts on each side.
- Position counts remain useful for coverage and breadth, but exposure interpretation should use side-gross weighting.

## Interpretation Rules
- Use `Thesis On Track` bullets as portfolio upside drivers.
- Use `Thesis Off Track` bullets as portfolio downside risks.
- Treat coverage as a first-class caveat, not a footnote.
- Be explicit that the portfolio read is based only on active names with authored latest-note content.
- If coverage is concentrated in only a few buckets, say so directly.
- Use position counts for note coverage and evidence breadth.
- Use side-gross weighting when discussing net long or net short portfolio exposure to a bucket, factor, or theme.

## Default Output Structure
Unless the user asks otherwise, answer in this order:

1. `Portfolio Picture`
2. `Upside Drivers`
3. `Downside Risks`
4. `Coverage / Blank Positions`
5. short caveat on what is and is not represented by the current notes

## Writing Rules
- Lead with the portfolio-level conclusion, not file mechanics.
- Distinguish between:
  - actual recurring themes in authored notes
  - missing coverage
- When a theme only appears in one or two names, present it as a representative example, not a broad portfolio driver.
- If a bucket dominates coverage, name the bucket explicitly.
- Keep the answer synthesis-first; do not dump raw tool output unless the user asks for it.

## Tooling
Primary tool:

- `tools/portfolio_note_analysis.py`

Useful flags:

- `--exclude-cash`
- `--include-blank-names`
- `--format json`
- `--top <N>`
