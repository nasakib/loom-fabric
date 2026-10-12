@echo off
setlocal
title Loom Fabric - Windows Installer & Setup Wizard

echo =====================================================================
echo           LOOM FABRIC -- SOVEREIGN AI OPERATING SYSTEM
echo                  Windows 1-Click Installer Wizard
echo =====================================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "REPO_DIR=%SCRIPT_DIR%.."

:: Check for Administrative Privileges
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [i] Requesting standard user setup (No Admin Required).
)

echo [*] Checking Python installation...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python not found in system PATH.
    echo Please install Python 3.10+ from https://python.org and re-run this setup.
    pause
    exit /b 1
)

echo [*] Initializing sovereign Python environment in %%USERPROFILE%%\.loom\env...
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%install_windows.ps1"

if %errorlevel% neq 0 (
    echo [!] Setup encountered an error.
    pause
    exit /b 1
)

echo.
echo =====================================================================
echo [OK] Loom Fabric Installation Complete!
echo.
echo Launch Options:
echo   1. Desktop GUI Control Center   : Start-Loom-GUI.bat
echo   2. Web Dashboard & Gateway      : http://localhost:8002
echo   3. Command Line                 : loom probe / loom shard qwen2.5:32b
echo =====================================================================
echo.
pause
