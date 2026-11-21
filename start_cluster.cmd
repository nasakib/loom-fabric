@echo off
setlocal
title ClothOS Sovereign Compute Console
cd /d "%~dp0"
set "PYTHONIOENCODING=utf-8"
set "PYTHONPATH=%~dp0;%PYTHONPATH%"

python start_cluster.py %*
if errorlevel 1 (
    echo.
    echo ClothOS execution exited with error code %errorlevel%.
    pause
)
