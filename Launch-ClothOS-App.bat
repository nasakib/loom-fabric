@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"

title ClothOS Sovereign Universal Desktop Application
echo ======================================================================
echo    CLOTHOS // ANTIGRAVITY COMMAND CENTER & DESKTOP SUITE
echo    (Upgraded from legacy dashboard to Antigravity Universal Suite)
echo ======================================================================

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

call "%PROJECT_ROOT%Launch-Antigravity-GUIs.bat" --web
exit /b %ERRORLEVEL%
