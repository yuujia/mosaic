@echo off
setlocal
cd /d "%~dp0"

python tools/export_bucket_kpi_text.py
if errorlevel 1 goto :fail

for /f "usebackq delims=" %%B in (`powershell -NoProfile -Command "$rows = Import-Csv '00_config/active_manifest.csv'; $prop = if ($rows -and $rows[0].PSObject.Properties.Name -contains 'bucket_fs') { 'bucket_fs' } else { 'bucket_id' }; $rows | Select-Object -ExpandProperty $prop -Unique | Sort-Object"`) do (
  echo Refreshing %%B...
  python tools/build_bucket_dashboard.py --bucket %%B
  if errorlevel 1 goto :fail
)

echo Refreshed all active bucket dashboards.
pause
exit /b 0

:fail
echo Dashboard refresh failed.
pause
exit /b 1
