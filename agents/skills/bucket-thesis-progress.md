# Mosaic Bucket Thesis Progress Skill

skill_name: Bucket Thesis Progress
skill_version: 1

## Purpose
Provide a deterministic way to assess whether a Mosaic bucket thesis is becoming more or less on track.

This skill is broader than KPI summary. It combines:

- bucket thesis definitions
- latest and prior quarter company notes
- supporting KPI trend context when useful

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

Then open:

- `buckets/{BUCKET_FS}/{BUCKET_FS}_bucket_thesis.md`
- relevant company files under `buckets/{BUCKET_FS}/{TICKER}/{TICKER}.md`

Use the KPI workbook only as supporting evidence, not the primary source, unless the user explicitly asks for KPI-only analysis.

## Trigger Phrases
Use this skill when the user asks for any of the following or something materially similar:

- thesis progress for bucket `X`
- thesis status for bucket `X`
- how the thesis is going for bucket `X`
- is the thesis more or less on track
- is the thesis improving or deteriorating
- summarize thesis progress of bucket `X`

## Core Question
Assess whether the bucket thesis is:

- more on track than the prior quarter
- less on track than the prior quarter
- unchanged / mixed

Base the answer on the bucket thesis definitions plus the latest company evidence.

## Primary Evidence Hierarchy
1. Bucket thesis file:
   - `Core Thesis`
   - `On Track Definition`
   - `Off Track Definition`
2. Latest company quarter notes
3. Prior company quarter notes for comparison
4. KPI workbook only as corroboration

## What To Look For In Company Notes
Prefer narrative evidence directly tied to the thesis, including:

- weak or below-Street guidance
- decelerating bookings, billings, customers, NRR/DBNR, ARR, or revenue
- churn, weaker seat trends, pricing pressure, or usage pressure
- explicit comments that AI, copilots, agents, or new products are not offsetting slowdown
- competitive pressure from AI-native tools or larger platform vendors
- gross margin dilution from inference or pricing
- operating margin pressure from defensive spend
- signs that a company's own agentic strategy is gaining traction
- signs that partnerships, launches, or bundling may disconfirm the thesis

## Synthesis Rules
Build three sections in this order:

1. `Thesis Progress Summary`
2. `Thesis Confirmation`
3. `Thesis Disconfirmation`

Then provide:

- `Progress Color`
- rationale paragraph
- concise conclusion on whether the thesis is more or less on track than last quarter

If the user later asks for counts of `Green`, `Yellow-Green`, `Yellow`, `Yellow-Red`, or `Red`, do one of the following:

- if the company notes contain an explicit, consistently populated per-company signal field, use it and say so
- otherwise derive the count from the latest company note evidence using the color framework in this skill, and say that the counts are agent-derived rather than note-authored

Do not imply that a canonical per-company `signal:` field exists unless it is actually present and populated.

## Progress Color Framework
Use a simple color-style label:

- `Green`: clearly more on track
- `Yellow-Green`: modestly more on track
- `Yellow`: mixed / little net change
- `Yellow-Red`: modestly less on track
- `Red`: clearly less on track

Choose the color from the balance of confirming vs disconfirming evidence.

## Color Guidance
- Use `Green` when confirming evidence is broad, recent, and material, with limited important offsets.
- Use `Yellow-Green` when confirming evidence is stronger than disconfirming evidence, but important offsets remain.
- Use `Yellow` when evidence is mixed, contradictory, or inconclusive.
- Use `Yellow-Red` when disconfirming evidence has improved modestly versus prior quarter.
- Use `Red` when disconfirming evidence is broad and material.

## Output Format
Unless the user asks otherwise, use this structure:

`Thesis Progress Summary`

`Thesis Confirmation`
- short bullets

`Thesis Disconfirmation`
- short bullets

`Progress Color: <color>`

Short rationale paragraph.

Short concluding paragraph answering whether the thesis is more or less on track than last quarter.

## Writing Rules
- Lead with the thesis-progress structure above.
- Be explicit about the comparison point: versus last quarter.
- Prefer plain-English synthesis over exhaustive inventories.
- Mention representative company examples when useful, not every company by default.
- If KPI evidence supports the narrative, mention it briefly, but keep narrative evidence primary.
- If the evidence is mixed, say so directly.
- Judge thesis progress breadth-first across the bucket.
- Treat large or economically important exceptions as important caveats, not automatic overrides of broad bucket evidence.
- Do not default to weighted-average reasoning unless the user explicitly asks for a weighted view.
- When the breadth evidence is mostly confirming but meaningful offsets remain, prefer `Yellow-Green` over `Yellow-Red`.
- Reserve `Yellow-Red` for cases where disconfirming evidence is actually broader than confirming evidence.

## Caveats To Mention When Relevant
- company notes may not be equally current across all names
- some names may only have one quarter of notes
- larger companies can matter more economically even if note count is balanced
- thesis evidence may be stronger in demand indicators than in reported margins

## Minimal Workflow
1. Open the governance spec.
2. Open `00_config/active_manifest.md` and confirm the bucket path.
3. Open the bucket thesis file and read `On Track Definition` and `Off Track Definition`.
4. Open the latest company notes, then prior quarter notes where available.
5. Sort evidence into confirming vs disconfirming.
6. Compare the net balance versus the prior quarter.
7. Assign a progress color.
8. Write the structured summary with confirmation, disconfirmation, color, and rationale.
