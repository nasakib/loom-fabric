@echo off
setlocal
title Loom Fabric - Windows Installer & Setup Wizard

echo =====================================================================
echo           LOOM FABRIC -- MECHANISTIC AI OPERATING SYSTEM
echo                  Windows 1-Click Installer Wizard
echo =====================================================================
echo.

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Locate install_windows.ps1 whether invoked from root or scripts/
set "PS_INSTALLER=%SCRIPT_DIR%scripts\install_windows.ps1"
if not exist "%PS_INSTALLER%" (
    set "PS_INSTALLER=%SCRIPT_DIR%install_windows.ps1"
)

if not exist "%PS_INSTALLER%" (
    echo [!] Could not locate install_windows.ps1 in %SCRIPT_DIR%scripts\
    pause
    exit /b 1
)

echo [*] Running PowerShell installation script: %PS_INSTALLER%
powershell -NoProfile -ExecutionPolicy Bypass -File "%PS_INSTALLER%"

if %errorlevel% neq 0 (
    echo.
    echo [!] Setup encountered an error (Exit Code: %errorlevel%).
    pause
    exit /b 1
)

echo.
echo =====================================================================
echo [OK] Loom Fabric Installation Complete!
echo.
echo Launch Options:
echo   1. Desktop GUI Control Center   : Start-Loom-GUI.bat
echo   2. Web Dashboard ^& Gateway      : http://localhost:8002
echo   3. The Shuttle PWA              : http://localhost:5555
echo   4. Command Line                 : loom probe / loom shard qwen2.5:32b
echo =====================================================================
echo.
pause
