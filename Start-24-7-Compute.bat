@echo off
REM Launch Fabric 24/7 Continuous Sovereign Autonomous Compute Engine (Windowless)
cd /d "%~dp0"
set "PYTHONPATH=%~dp0"
if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\pythonw.exe" -m loom.fabric.continuous_worker
) else (
    start "" pythonw -m loom.fabric.continuous_worker
)
echo [Fabric] 24/7 Sovereign Autonomous Compute Engine started silently in background.
echo Monitor live metrics with: fabric worker status
timeout /t 3 >nul
exit /b 0
