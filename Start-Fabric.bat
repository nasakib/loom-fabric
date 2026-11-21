@echo off
REM Launch Fabric (ClothOS Agentic OS // Loom · Stitch · Torque)
title ClothOS Sovereign Command Center
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    start "" ".venv\Scripts\python.exe" "apps\loom-desktop\launch_desktop.py"
) else (
    start "" python "apps\loom-desktop\launch_desktop.py"
)
exit /b 0
