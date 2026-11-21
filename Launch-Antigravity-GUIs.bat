@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"

title ClothOS // Antigravity Universal Desktop Suite
echo ======================================================================
echo    CLOTHOS // ANTIGRAVITY UNIVERSAL DESKTOP SUITE LAUNCHER
echo    Bicameral Dyad: Node 1 (skyTech-Worker) ^<--^> Node 2 (Ryzen7-Head)
echo    Dedicated Fiduciary Sovereign Companion for Najmos Sakib
echo ======================================================================

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

set "PYTHON_EXE=%PROJECT_ROOT%.venv\Scripts\python.exe"
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

echo [*] Initializing Antigravity Desktop Interfaces...
"%PYTHON_EXE%" "guis\desktop_startup_manager.py" %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Encountered error during startup.
    pause
)

exit /b 0
