#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ ! -d .git ]; then
  git init
  git branch -M main
fi

python tools/export_bucket_kpi_text.py

cat <<'EOF'
Local mirror preparation complete.

Next steps:
1. Review exported text files under 00_config/kpi_exports/
2. git add .
3. git commit -m "Prepare Mosaic GitHub mirror"
4. git remote add origin <github-repo-url>
5. git push -u origin main

Recommended for GitHub-hosted agents:
- Keep AGENTS.md and agents/ checked in.
- Keep .github/copilot-instructions.md checked in.
- Refresh KPI text exports before pushing material workbook changes.
EOF
