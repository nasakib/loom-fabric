@echo off
REM ============================================================================
REM ClothOS Dual-GPU Heterogeneous Vulkan Model Runner
REM Unifies GPU 0 (NVIDIA RTX 3060 12GB) and GPU 1 (AMD Radeon RX 580 8GB)
REM Total Paired VRAM: 20.0 GB (Zero DDR4 System RAM Spill)
REM ============================================================================

setlocal enabledelayedexpansion

set MODEL_KEY=%1
if "%MODEL_KEY%"=="" set MODEL_KEY=loom-sovereign

set PORT=%2
if "%PORT%"=="" set PORT=8002

echo [ClothOS] Initializing Dual-GPU Paired VRAM Runner for '%MODEL_KEY%' on port %PORT%...
echo [ClothOS] GPU 0: NVIDIA GeForce RTX 3060 (12GB GDDR6 @ 360 GB/s)
echo [ClothOS] GPU 1: AMD Radeon RX 580 (8GB GDDR5 @ 224 GB/s)
echo [ClothOS] Combined VRAM: 20.0 GB (5.9x faster than DDR4 System RAM)

REM Query python helper for exact layer allocation and parameters
python -c "from loom.clothos.dual_gpu_runner import DualGPURunner; res = DualGPURunner.generate_vulkan_launch_command('%MODEL_KEY%', port=%PORT%); print(res['command'])" > "%TEMP%\clothos_vulkan_cmd.txt" 2>nul

if errorlevel 1 (
    echo [ClothOS] Invoking via Python interpreter...
    "C:\Users\natsa\AppData\Local\Programs\FreeCAD 1.1\FreeCAD_1.1.3-Windows-x86_64-py311\bin\python.exe" -c "from loom.clothos.dual_gpu_runner import DualGPURunner; res = DualGPURunner.generate_vulkan_launch_command('%MODEL_KEY%', port=%PORT%); print(res['command'])" > "%TEMP%\clothos_vulkan_cmd.txt"
)

set /p LAUNCH_CMD=<"%TEMP%\clothos_vulkan_cmd.txt"
echo [ClothOS] Generated Vulkan Launch Command:
echo [ClothOS] %LAUNCH_CMD%

where llama-server >nul 2>nul
if %errorlevel% equ 0 (
    echo [ClothOS] Executing native llama-server Vulkan runner...
    %LAUNCH_CMD%
) else (
    echo [ClothOS] NOTICE: 'llama-server' binary not found on global PATH.
    echo [ClothOS] Verifying Vulkan runtime devices...
    python -c "from loom.clothos.dual_gpu_runner import DualGPURunner; print(DualGPURunner.format_cli_summary())" 2>nul
    if errorlevel 1 (
        "C:\Users\natsa\AppData\Local\Programs\FreeCAD 1.1\FreeCAD_1.1.3-Windows-x86_64-py311\bin\python.exe" -c "from loom.clothos.dual_gpu_runner import DualGPURunner; print(DualGPURunner.format_cli_summary())"
    )
)

endlocal
