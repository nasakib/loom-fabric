@echo off
title ClothOS Sovereign Desktop GUI (Ubuntu / macOS Hybrid)
color 0A
cls
echo ================================================================================
echo    CLOTHOS SOVEREIGN OPERATING SYSTEM -- DESKTOP GUI LAUNCHER
echo    Ubuntu / macOS Aesthetics ^| POSIX ABI ^| Unix Terminal ^| Systolic TPU Monitor
echo ================================================================================
echo.
echo [*] Starting Unified ClothOS Master Server at http://127.0.0.1:8087/ ...
echo [*] Opening desktop in your default browser...
echo.

start http://127.0.0.1:8087/
call "%~dp0\.venv\Scripts\python.exe" -m uvicorn loom.fabric.dashboard_server:app --host 0.0.0.0 --port 8087
pause
