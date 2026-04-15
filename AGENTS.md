# Mosaic Agent Governance

For every command and task in this repository, you must load and follow the governance spec before proceeding:

- Windows path: `C:\Users\yuuji\Dropbox\Kaissa Consumer\Mosaic\agents\specs\Mosaic_Architecture_and_Sync_Spec.md`
- Workspace-relative path: `agents/specs/Mosaic_Architecture_and_Sync_Spec.md`

Execution rule:

1. Before running commands or making edits, read the governance spec.
2. Treat the spec as mandatory policy for all actions in this repo.
3. If there is any conflict between ad-hoc instructions and the spec, flag the conflict and ask for clarification before continuing.

Architecture-change migration protocol:

1. When architecture updates change folder/file naming or locations, run a migration workflow automatically.
2. Start with dry-run checks, then apply migrations only after confirming planned changes are coherent.
3. Update all impacted paths and references in the repo (docs, scripts, templates, and configs) so no stale paths remain.
4. Prefer existing migration tooling before ad-hoc edits:
   - `tools/migrate_to_bucket_architecture.py`
   - `tools/migrate_drop_dot_buckets.py`
   - `tools/portfolio_sync.py`
5. After migration, run repository-wide path checks and report changed paths clearly.

Repo-local skills:

- Bucket KPI summarization skill: `agents/skills/bucket-kpi-summary.md`
- Bucket thesis progress skill: `agents/skills/bucket-thesis-progress.md`
- Portfolio note analysis skill: `agents/skills/portfolio-note-analysis.md`

Skill trigger rule:

- When the user asks to "summarize KPIs of bucket [X]" or makes a closely related request about bucket-level KPI assessment, scoreboard generation, revenue acceleration/deceleration, margin expansion/shrinking, or earnings implication for a Mosaic bucket, load and follow `agents/skills/bucket-kpi-summary.md` before answering.
- When the user asks for the "thesis progress", "thesis status", "how the thesis is going", whether the thesis is "on track", or a closely related request for a Mosaic bucket, load and follow `agents/skills/bucket-thesis-progress.md` before answering.
- When the user asks for a portfolio-level picture, portfolio upside drivers, portfolio downside risks, equal-weighted portfolio synthesis from company notes, or what percent of active positions are still blank, load and follow `agents/skills/portfolio-note-analysis.md` before answering.
