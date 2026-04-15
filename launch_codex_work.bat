@echo off
setlocal

set "WSL_REPO_PATH=/mnt/c/Users/YuujiAnderson/Dropbox/Kaissa Consumer/Mosaic"

wsl.exe bash -lc "cd \"%WSL_REPO_PATH%\" && exec codex"

