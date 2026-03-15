@echo off
setlocal

cd /d "%~dp0"

if "%~1"=="" (
  set /p COMMIT_MSG=Commit message: 
) else (
  set "COMMIT_MSG=%~1"
)

if "%COMMIT_MSG%"=="" (
  echo Commit message is required.
  exit /b 1
)

git add .
if errorlevel 1 exit /b 1

git commit -m "%COMMIT_MSG%"
if errorlevel 1 exit /b 1

git push
if errorlevel 1 exit /b 1

echo.
echo Push complete.
