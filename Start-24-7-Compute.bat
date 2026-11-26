@echo off
setlocal

:: ============================================================================
:: ClothOS Sovereign 24/7 Continuous Autonomous Compute Fabric
:: ============================================================================
:: Node 1: NVIDIA RTX 3060 12GB (Active Inference) + AMD RX 580 8GB (Evaluator)
:: Node 2: AMD Ryzen 7 7730U 16T (Peer Invariant Verification)
:: ============================================================================

title ClothOS Sovereign 24/7 Autonomous Compute Fabric
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"
set "PYTHONUNBUFFERED=1"

cd /d "%~dp0"
set "LOOM_DIR=%CD%"
set "PYTHONPATH=%LOOM_DIR%;%PYTHONPATH%"

:: Parameter Dispatch
if /i "%~1"=="--help" goto SHOW_HELP
if /i "%~1"=="-h" goto SHOW_HELP
if /i "%~1"=="/?" goto SHOW_HELP
if /i "%~1"=="--status" goto SHOW_STATUS
if /i "%~1"=="-s" goto SHOW_STATUS
if /i "%~1"=="status" goto SHOW_STATUS
if /i "%~1"=="--briefing" goto SHOW_BRIEFING
if /i "%~1"=="-b" goto SHOW_BRIEFING
if /i "%~1"=="briefing" goto SHOW_BRIEFING
if /i "%~1"=="--factory" goto SHOW_FACTORY
if /i "%~1"=="-f" goto SHOW_FACTORY
if /i "%~1"=="factory" goto SHOW_FACTORY
if /i "%~1"=="--all-cylinders" goto IGNITE_ALL
if /i "%~1"=="-all" goto IGNITE_ALL
if /i "%~1"=="--once" goto RUN_ONCE

:: Python Discovery
set "PY_EXE="
if exist "%LOOM_DIR%\.venv\Scripts\python.exe" set "PY_EXE=%LOOM_DIR%\.venv\Scripts\python.exe"
if not defined PY_EXE if exist "C:\Users\natsa\AppData\Local\Programs\FreeCAD 1.1\FreeCAD_1.1.3-Windows-x86_64-py311\bin\python.exe" set "PY_EXE=C:\Users\natsa\AppData\Local\Programs\FreeCAD 1.1\FreeCAD_1.1.3-Windows-x86_64-py311\bin\python.exe"
if not defined PY_EXE set "PY_EXE=python"

:: Check Interpreter Health
"%PY_EXE%" -c "import sys" >nul 2>nul
if errorlevel 1 (
    echo [ClothOS ERROR] Python interpreter not executable: %PY_EXE%
    pause
    exit /b 1
)

:: Banner
cls
echo ============================================================================
echo   CLOTHOS SOVEREIGN 24/7 USEFUL COMPUTE FABRIC (GRID-AWARE ORCHESTRATOR)
echo ============================================================================
echo   [ENGINE]:    ClothOS Continuous 24x7 Orchestrator + UsefulComputeWorkEngine
echo   [WORKLOADS]: 1. Drain .clothos_task_queue.jsonl engineering tasks
echo                2. Rotate real multi-repo pytest suites ^& Python AST audits
echo                3. Live GPU/OpenCL/JIT/Ollama cluster benchmarks ^& telemetry
echo                4. Execution-verified LLM coding distillation (Ollama sandbox)
echo                5. Log rotation, stale lock recovery ^& actionable briefings
echo   [SILICON]:   Node 1: RTX 3060 12GB CUDA + RX 580 8GB OpenCL
echo                Node 2: AMD Ryzen 7 7730U (16T Mesh @ 192.168.99.2)
echo   [BRIEFING]:  deliverables\LATEST_24X7_REPORT.md
echo ============================================================================
echo   Controls: Press [Ctrl+C] to halt the supervisor loop gracefully.
echo ============================================================================
echo.

set CRASH_COUNT=0

:LOOP
echo [%TIME%] [ClothOS Supervisor] Engaging 24/7 Continuous Autonomous Compute Loop...
"%PY_EXE%" -m loom.clothos.continuous_24x7_orchestrator %*
set "EXIT_CODE=%ERRORLEVEL%"

if %EXIT_CODE% equ 0 (
    set CRASH_COUNT=0
    echo [%TIME%] [ClothOS Supervisor] Orchestrator completed cycle cleanly.
    timeout /t 1 >nul
    goto LOOP
)

set /a CRASH_COUNT+=1
echo.
echo ****************************************************************************
echo [ClothOS WARNING] Continuous worker exited with anomaly code %EXIT_CODE%!
echo Consecutive anomaly count: %CRASH_COUNT%
echo ****************************************************************************

if %CRASH_COUNT% geq 5 (
    echo [ClothOS BACKOFF] Repeated crash threshold reached. Pausing 15s...
    timeout /t 15
) else (
    echo [ClothOS] Resuming continuous compute loop in 3 seconds...
    timeout /t 3 >nul
)
goto LOOP

:RUN_ONCE
set "PY_EXE="
if exist "%LOOM_DIR%\.venv\Scripts\python.exe" set "PY_EXE=%LOOM_DIR%\.venv\Scripts\python.exe"
if not defined PY_EXE if exist "C:\Users\natsa\AppData\Local\Programs\FreeCAD 1.1\FreeCAD_1.1.3-Windows-x86_64-py311\bin\python.exe" set "PY_EXE=C:\Users\natsa\AppData\Local\Programs\FreeCAD 1.1\FreeCAD_1.1.3-Windows-x86_64-py311\bin\python.exe"
if not defined PY_EXE set "PY_EXE=python"
echo [ClothOS] Executing single supervised compute cycle with research ingestion...
"%PY_EXE%" -m loom.clothos.continuous_24x7_orchestrator --once
exit /b %ERRORLEVEL%

:IGNITE_ALL
set "PY_EXE="
if exist "%LOOM_DIR%\.venv\Scripts\python.exe" set "PY_EXE=%LOOM_DIR%\.venv\Scripts\python.exe"
if not defined PY_EXE if exist "C:\Users\natsa\AppData\Local\Programs\FreeCAD 1.1\FreeCAD_1.1.3-Windows-x86_64-py311\bin\python.exe" set "PY_EXE=C:\Users\natsa\AppData\Local\Programs\FreeCAD 1.1\FreeCAD_1.1.3-Windows-x86_64-py311\bin\python.exe"
if not defined PY_EXE set "PY_EXE=python"
echo [ClothOS] Igniting all 8 operational cylinders across the sovereign mesh...
"%PY_EXE%" "%LOOM_DIR%\scripts\ignite_all_cylinders.py"
echo [ClothOS] Transitioning into 24/7 Continuous Supervisor Loop...
goto LOOP

:SHOW_FACTORY
set "PY_EXE="
if exist "%LOOM_DIR%\.venv\Scripts\python.exe" set "PY_EXE=%LOOM_DIR%\.venv\Scripts\python.exe"
if not defined PY_EXE if exist "C:\Users\natsa\AppData\Local\Programs\FreeCAD 1.1\FreeCAD_1.1.3-Windows-x86_64-py311\bin\python.exe" set "PY_EXE=C:\Users\natsa\AppData\Local\Programs\FreeCAD 1.1\FreeCAD_1.1.3-Windows-x86_64-py311\bin\python.exe"
if not defined PY_EXE set "PY_EXE=python"
"%PY_EXE%" -m loom.clothos.factory_visualizer
exit /b 0

:SHOW_STATUS
set "PY_EXE="
if exist "%LOOM_DIR%\.venv\Scripts\python.exe" set "PY_EXE=%LOOM_DIR%\.venv\Scripts\python.exe"
if not defined PY_EXE if exist "C:\Users\natsa\AppData\Local\Programs\FreeCAD 1.1\FreeCAD_1.1.3-Windows-x86_64-py311\bin\python.exe" set "PY_EXE=C:\Users\natsa\AppData\Local\Programs\FreeCAD 1.1\FreeCAD_1.1.3-Windows-x86_64-py311\bin\python.exe"
if not defined PY_EXE set "PY_EXE=python"
echo [ClothOS] Querying 24/7 Compute Worker Telemetry...
"%PY_EXE%" -c "import json, pathlib; p = pathlib.Path.home() / '.loom' / 'continuous_worker_state.json'; print(json.dumps(json.loads(p.read_text(encoding='utf-8')), indent=2)) if p.exists() else print('No worker state found.'); u = pathlib.Path.home() / '.loom' / '24x7_useful_state.json'; print('\n--- Useful Work Summary ---\n' + json.dumps({k: v for k, v in json.loads(u.read_text(encoding='utf-8')).items() if k in ('workload_mode','real_tests_passed','real_tests_failed','real_test_pass_rate_pct','tasks_drained_total','recent_actions')}, indent=2)) if u.exists() else None"
exit /b 0

:SHOW_BRIEFING
set "PY_EXE="
if exist "%LOOM_DIR%\.venv\Scripts\python.exe" set "PY_EXE=%LOOM_DIR%\.venv\Scripts\python.exe"
if not defined PY_EXE set "PY_EXE=python"
"%PY_EXE%" -m loom.clothos.continuous_24x7_orchestrator --briefing
exit /b 0

:SHOW_HELP
echo ============================================================================
echo   ClothOS Sovereign 24/7 Autonomous Compute Engine -- Command Options
echo ============================================================================
echo Usage:
echo   Start-24-7-Compute.bat [OPTIONS]
echo.
echo Options:
echo   --status, -s        Display current 24/7 telemetry and useful work metrics
echo   --briefing, -b      Print the latest 24/7 executive briefing markdown
echo   --factory, -f       Launch animated ASCII cognitive factory floor in terminal
echo   --all-cylinders     Ignite all 8 ClothOS cylinders before continuous loop
echo   --once              Execute a single supervised cycle and exit
echo   --mode ^<m^>          Workload mode: auto, night, day, maintenance
echo   --help, -h, /?      Display this help dialog
echo.
echo Telemetry Files:
echo   ~/.loom/continuous_worker_state.json
echo   ~/.loom/24x7_useful_state.json
echo   deliverables/LATEST_24X7_REPORT.md
echo ============================================================================
exit /b 0
