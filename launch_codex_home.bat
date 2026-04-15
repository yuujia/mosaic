@echo off
setlocal

title Codex Home

set "REPO_WIN_PATH=%~dp0"
if "%REPO_WIN_PATH:~-1%"=="\" set "REPO_WIN_PATH=%REPO_WIN_PATH:~0,-1%"

for /f "delims=" %%I in ('wsl.exe wslpath -a "%REPO_WIN_PATH%" 2^>nul') do set "WSL_REPO_PATH=%%I"

if not defined WSL_REPO_PATH (
    echo Failed to resolve WSL path for "%REPO_WIN_PATH%".
    pause
    exit /b 1
)

wsl.exe bash -ilc "cd \"$WSL_REPO_PATH\" && exec codex"
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo.
    echo Codex failed to launch. Exit code: %EXIT_CODE%
    echo Repo path: %REPO_WIN_PATH%
    echo WSL path: %WSL_REPO_PATH%
    pause
)

exit /b %EXIT_CODE%
