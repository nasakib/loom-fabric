@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"

title ClothOS Living Neuro-Screensaver and Visualizer
echo ======================================================================
echo    CLOTHOS // 60 FPS COUPLED NEURO-SCREENSAVER & VISUALIZER
echo    (Upgraded from legacy screensaver to Antigravity 60fps Kuramoto Visualizer)
echo ======================================================================

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

call "%PROJECT_ROOT%Launch-Antigravity-GUIs.bat" --screensaver
exit /b %ERRORLEVEL%
