@echo off
title ClothOS Sovereign Commercial Operating System v1.0.0-PROD
color 0B
cls
echo ================================================================================
echo    CLOTHOS SOVEREIGN COMMERCIAL OPERATING SYSTEM -- RELEASE v1.0.0-PROD
echo    Architect: Najmos Sakib ^| Fiduciary Covenant ^| Landauer Bound: ^<= 1000 J
echo ================================================================================
echo.
echo  [1] Launch ClothOS Desktop GUI (Ubuntu / macOS Style with Unix Terminal)
echo  [2] Launch Interactive ClothOS Sovereign Terminal Shell (CLI)
echo  [3] Boot Simulated RISC-V 64-bit + TPU Systolic Matrix Array (RV64GCV)
echo  [4] Boot Simulated x86_64 Multiboot HAL with 4-Level Paging (PML4)
echo  [5] Run Full Diagnostics ^& Operational Auto-Repair Doctor
echo  [6] Inspect Verified Commercial Milestones ^& Quality Gate Audit Report
echo  [7] Exit
echo.
set /p choice="Select target environment [1-7]: "
if "%choice%"=="1" goto launch_desktop
if "%choice%"=="2" goto launch_shell
if "%choice%"=="3" goto launch_riscv
if "%choice%"=="4" goto launch_x86
if "%choice%"=="5" goto launch_diag
if "%choice%"=="6" goto show_audit
if "%choice%"=="7" exit /b 0

:launch_desktop
echo.
echo [*] Launching ClothOS Desktop GUI at http://127.0.0.1:8088/ ...
call "%~dp0Launch-ClothOS-Desktop.bat"
goto menu

:launch_shell
echo.
echo [*] Launching ClothOS Sovereign Shell...
call "%~dp0\.venv\Scripts\python.exe" -m loom.clothos.unified_autonomous_engine --interactive
pause
goto menu

:launch_riscv
echo.
echo [*] Booting ClothOS RISC-V 64-bit + RoCC TPU Systolic Wavefront...
call "%~dp0\.venv\Scripts\python.exe" -m loom.clothos.riscv_tpu_emulator
pause
goto menu

:launch_x86
echo.
echo [*] Booting ClothOS x86_64 Multiboot HAL...
call "%~dp0\.venv\Scripts\python.exe" -m loom.clothos.x86_hal_emulator
pause
goto menu

:launch_diag
echo.
echo [*] Running ClothOS Diagnostics and Self-Repair Doctor...
call "%~dp0\.venv\Scripts\python.exe" -m loom.clothos.diagnostics_and_ops --repair
pause
goto menu

:show_audit
echo.
type "%~dp0deliverables\releases\ClothOS-v1.0.0-PROD\COMMERCIAL_RELEASE_NOTES.md"
pause
goto menu

:menu
call "%~dp0Run-ClothOS-Release.bat"
