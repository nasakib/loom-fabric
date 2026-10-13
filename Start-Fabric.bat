@echo off
REM Launch Fabric (ClothOS Agentic OS // Loom · Stitch · Torque) with zero console windows
cd /d "%~dp0"
if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\pythonw.exe" -m loom.gui
) else (
    start "" pythonw -m loom.gui
)
exit /b 0
