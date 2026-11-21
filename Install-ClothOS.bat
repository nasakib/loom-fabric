@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"

title ClothOS Commercial Zero-Config Installer ^& Mesh Deployer
echo =====================================================================
echo    ? CLOTHOS // SOVEREIGN AGENTIC DISTRIBUTED OPERATING SYSTEM
echo    Commercial 1-Click Universal Installer ^& Mesh Deployer
echo    Architect: Najmos Sakib
echo =====================================================================
echo.

set "SCRIPT_DIR=%~dp0"
set "PS_SCRIPT=%SCRIPT_DIR%scripts\install_clothos_universal.ps1"

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%" %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Installation encountered an error (Code: %ERRORLEVEL%).
    pause
    exit /b %ERRORLEVEL%
)

echo.
pause
exit /b 0