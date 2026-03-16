# Mosaic Agent Entry Point

Before doing any work in this repository:

1. Read `AGENTS.md`.
2. Read `agents/specs/Mosaic_Architecture_and_Sync_Spec.md`.
3. Follow any repo-local skill trigger rules described in `AGENTS.md`.

Important local skills:

- `agents/skills/bucket-kpi-summary.md`
- `agents/skills/bucket-thesis-progress.md`
- `agents/skills/analyst.md`

Preferred research entry point:

- `00_config/active_manifest.md`
- bucket-level `{BUCKET_FS}_note_index.md` files when listed in the manifest

Notes:

- Do not rely on directory traversal as the primary discovery mechanism when the manifest provides direct paths.
- Prefer bucket note index files for connector-safe company note discovery.
- Prefer the bucket KPI workbook plus any exported text mirrors under `00_config/kpi_exports/` for KPI analysis.
- Preserve the repository's canonical bucket filesystem rules from the architecture spec.
