# Mosaic Architecture & Sync Governance Spec
Version: 2.4
Last Updated: 2026-03-15

---

# 1. Purpose

This document defines the canonical architecture, filesystem schema, sync behavior, and migration policy for the Mosaic research operating system.

All structural changes to Mosaic must comply with this specification.

---

# 2. Canonical Identity Rules

## 2.1 Bucket Identity

- bucket_symbol: `.TESTS` (Bloomberg canonical identifier)
- bucket_fs: `TESTS` (filesystem-safe identifier)

Rule:
bucket_fs = bucket_symbol.lstrip(".")

The leading dot remains in active_portfolio for Bloomberg compatibility.
The leading dot must NEVER appear in filesystem folder names.

---

## 2.2 Company Identity

- ticker: `DGX`
- Company folder name: `DGX`
- Company file name: `DGX.md`

Company folders and filenames must never begin with `.`.

---

# 3. Filesystem Schema (v2.2)

Canonical structure:

Mosaic/
  buckets/
    TESTS/
      TESTS_bucket_thesis.md
      TESTS_note_index.md
      DGX/
        source/
        DGX.md

Rules:

- No leading dots in folder names.
- No intermediate `companies/` wrapper folders.
- Bucket thesis file name is always `{BUCKET_FS}_bucket_thesis.md` (example: `TESTS_bucket_thesis.md`).
- Bucket note index file name is always `{BUCKET_FS}_note_index.md` (example: `TESTS_note_index.md`).
- Bucket symbol must not be embedded in filenames.
- Folder name determines bucket identity on disk.
- bucket_symbol remains inside file content only.

---

# 4. Sync Responsibilities (portfolio_sync.py)

The sync system must:

1. Read active_portfolio (bucket_symbol remains dotted).
2. Derive bucket_fs from bucket_symbol.
3. Ensure bucket folder exists using bucket_fs.
4. Ensure company folders exist directly under each bucket.
5. Generate and maintain:
   - `{BUCKET_FS}_bucket_thesis.md`
   - `{BUCKET_FS}_note_index.md`
   - `{BUCKET_FS}_kpi.xlsx` (seeded from `tools/templates/BUCKET_kpi_template.xlsx` when missing)
   - Company markdown files
   - company `source/` folders
   - note-index references in active manifests
6. Perform safe in-sync migration if dot-prefixed folders exist.
7. Never overwrite user-authored content.
8. Only modify managed sections.
9. Support opt-in stale bucket archival:
   - Identify top-level `buckets/{BUCKET_FS}` folders not present in `active_portfolio`.
   - Move stale folders to `buckets/_archive/buckets/` (never hard-delete).
   - Run dry-run by default and report conflicts explicitly.

---

# 5. Managed vs User-Owned Sections

Markdown files may contain managed blocks:

<!-- MOSAIC:BEGIN:SECTION_NAME -->
...
<!-- MOSAIC:END:SECTION_NAME -->

Sync may modify managed blocks only.

Managed generated files may also be fully sync-owned when they are explicit architectural artifacts, such as:

- `{BUCKET_FS}_note_index.md`

User-owned sections include:
- Quarterly Updates
- Diligence Questions
- Freeform Notes
- Commentary

Sync must never modify these sections.

---

# 6. Migration Policy (Mandatory for Structural Changes)

All structural changes must include:

- A one-time migration script
- Dry-run by default
- Safe merge logic
- No destructive deletes
- No silent overwrites
- Conflict reporting
- Idempotency

Migrations live in:

mosaic/tools/migrations/

Migration logs live in:

Mosaic/00_config/migrations/

---

# 7. Schema Versioning

Schema version is tracked via:

Mosaic/00_config/schema_version.txt

When filesystem schema changes:

1. Increment schema version.
2. Include migration script.
3. Update this spec.
4. Maintain backward compatibility in sync when reasonable.

---

# 8. Architectural Change Protocol

Every architectural change must:

1. Update this spec.
2. Update sync logic.
3. Include migration script.
4. Bump schema version.
5. Preserve backward compatibility where feasible.
6. Avoid breaking mobile/iOS visibility.

No change is complete without migration consideration.

---

# 9. Non-Negotiable Rules

- No dot-prefixed bucket folders.
- No destructive migrations.
- No destructive stale-bucket cleanup; stale buckets must be archived, not deleted.
- No template assumptions tied to filenames.
- No dashboard logic dependent on folder names with dots.
- All filesystem logic must derive from canonical rules.

---

# 10. Guiding Principle

Mosaic is an investment research operating system.

It must remain:

- Deterministic
- Cross-platform compatible
- iOS-visible
- Sync-safe
- Backward compatible
- Auditable
