@echo off
title ClothOS & Loom Unified Master Hub - Port 8087
cd /d "%~dp0"
echo =========================================================================
echo    CLOTHOS + LOOM UNIFIED MASTER HUB - SINGLE PORT 8087
echo    Host: 0.0.0.0 : Port: 8087
echo    Dual-GPU VRAM Mesh: RTX 3060 (CUDA) + RX 580 (OpenCL) + Ray Cluster
echo =========================================================================
echo.
"%~dp0.venv\Scripts\python.exe" -m uvicorn loom.fabric.dashboard_server:app --host 0.0.0.0 --port 8087
pause
