@echo off
setlocal
title Loom Fabric & ClothOS - Windows Installer Wizard

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

call "%PROJECT_ROOT%Install-ClothOS.bat"
exit /b %ERRORLEVEL%
