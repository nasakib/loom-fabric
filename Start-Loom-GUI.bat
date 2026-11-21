@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"

title Start ClothOS GUI
echo ======================================================================
echo    CLOTHOS // ANTIGRAVITY UNIVERSAL DESKTOP SUITE
echo    (Upgraded from legacy GUI to Antigravity Suite)
echo ======================================================================

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

call "%PROJECT_ROOT%Launch-Antigravity-GUIs.bat"
exit /b %ERRORLEVEL%
