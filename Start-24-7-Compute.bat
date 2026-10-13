@echo off
REM Fabric 24/7 Continuous Sovereign Autonomous Compute Engine (Windowless Loop)
cd /d "%~dp0"
set "PYTHONPATH=%~dp0"
:LOOP
.venv\Scripts\python.exe -m loom.fabric.continuous_worker
timeout /t 1 >nul
goto LOOP
