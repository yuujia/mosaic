# Mosaic

Operational workspace for Mosaic portfolio, bucket, and migration tooling.

## AI Agent Entry

Agents should start with:

- `AGENTS.md`
- `agents/specs/Mosaic_Architecture_and_Sync_Spec.md`
- `00_config/active_manifest.md`

For connector-safe bucket research, use the managed bucket note indexes:

- `buckets/{BUCKET_FS}/{BUCKET_FS}_note_index.md`

Repo-local skills live under `agents/skills/`.

For GitHub-hosted agents and ChatGPT-style access, prefer the text KPI mirrors under:

- `00_config/kpi_exports/`

Refresh them with:

```bash
python tools/export_bucket_kpi_text.py
```

Prepare the repository for a GitHub mirror with:

```bash
bash tools/prepare_github_mirror.sh
```

## Tools Inventory

Generate the live Python tools inventory:

```bash
python tools/update_tools_inventory.py
```

Output is written to:

`00_config/TOOLS_INVENTORY.md`
