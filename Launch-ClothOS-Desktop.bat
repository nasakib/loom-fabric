@echo off
title ClothOS Sovereign Desktop GUI (Ubuntu / macOS Hybrid)
color 0A
cls
echo ================================================================================
echo    CLOTHOS SOVEREIGN OPERATING SYSTEM -- DESKTOP GUI LAUNCHER
echo    Ubuntu / macOS Aesthetics ^| POSIX ABI ^| Unix Terminal ^| Systolic TPU Monitor
echo ================================================================================
echo.
echo [*] Starting ClothOS Web Desktop Server at http://127.0.0.1:8088/ ...
echo [*] Opening desktop in your default browser...
echo.

call "%~dp0\.venv\Scripts\python.exe" -m loom.clothos.desktop_server --port 8088
pause
