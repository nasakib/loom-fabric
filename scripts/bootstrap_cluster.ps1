<#
.SYNOPSIS
    Bootstrap and connect the Loom Fabric Ray Cluster across asymmetric nodes.
.DESCRIPTION
    Launches or joins the Ray cluster:
    - Head Node (Ryzen 7 7730U @ 192.168.99.2): GCS on 6379, Dashboard on 8265.
    - Worker Node (SkyTech GPU Desktop @ 192.168.99.1): Dual-GPU custom resources:
      {"GPU_NVIDIA": 1, "VRAM_RTX_3060": 12, "GPU_AMD": 1, "VRAM_RX_580_2048SP": 8, "NODE_WORKER": 1}
.PARAMETER Role
    'head' to launch cluster head, or 'worker' to connect as accelerator worker.
.PARAMETER HeadAddress
    The IP/hostname and port of the Ray Head GCS (default: 192.168.99.2:6379).
#>

param(
    [ValidateSet("head", "worker", "status", "stop")]
    [string]$Role = "worker",

    [string]$HeadAddress = "192.168.99.2:6379",
    [string]$PythonExe = "C:\Users\natsa\Documents\stitch-core\.fabric-env\Scripts\python.exe"
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   LOOM FABRIC DISTRIBUTED RAY CLUSTER BOOTSTRAPPER       " -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

# Ensure Ray CLI exists in target environment
if (-not (Test-Path $PythonExe)) {
    Write-Warning "Configured Python environment not found at $PythonExe. Using system python."
    $PythonExe = "python"
}

switch ($Role) {
    "head" {
        Write-Host "[*] Bootstrapping Ray Cluster HEAD on 192.168.99.2..." -ForegroundColor Green
        Write-Host "    - GCS Redis Port: 6379" -ForegroundColor Gray
        Write-Host "    - Dashboard Port: 8265" -ForegroundColor Gray
        
        $HeadCmd = "& `"$PythonExe`" -m ray start --head --port=6379 --dashboard-host=0.0.0.0 --dashboard-port=8265 --resources='{\`"CPU_HEAD\`": 16, \`"NODE_HEAD\`": 1}' --block"
        Write-Host "Executing: $HeadCmd" -ForegroundColor DarkCyan
        Invoke-Expression $HeadCmd
    }

    "worker" {
        Write-Host "[*] Registering SkyTech Dual-GPU WORKER node with Head at $HeadAddress..." -ForegroundColor Green
        Write-Host "    - Primary Accelerator: NVIDIA RTX 3060 12GB (CUDA)" -ForegroundColor Gray
        Write-Host "    - Secondary Accelerator: AMD Radeon RX 580 8GB (Vulkan)" -ForegroundColor Gray
        Write-Host "    - Host System Memory: 40 GB DDR4" -ForegroundColor Gray

        # Custom JSON resource string with escaped quotes
        $WorkerResources = '{\"GPU_NVIDIA\": 1, \"VRAM_RTX_3060\": 12, \"GPU_AMD\": 1, \"VRAM_RX_580_2048SP\": 8, \"NODE_WORKER\": 1}'
        
        # Stop any existing stale instance first
        Write-Host "[*] Cleaning up any previous Ray worker processes..." -ForegroundColor Yellow
        try {
            & "$PythonExe" -m ray stop | Out-Null
        } catch { }

        Start-Sleep -Seconds 1

        $WorkerCmd = "& `"$PythonExe`" -m ray start --address=$HeadAddress --resources='$WorkerResources'"
        Write-Host "Executing: $WorkerCmd" -ForegroundColor DarkCyan
        Invoke-Expression $WorkerCmd
        Write-Host "[✓] Worker joined Ray cluster successfully!" -ForegroundColor Green
        Write-Host "[i] View dashboard at: http://192.168.99.2:8265" -ForegroundColor Cyan
    }

    "status" {
        Write-Host "[*] Querying Ray Cluster Status..." -ForegroundColor Cyan
        & "$PythonExe" -m ray status
    }

    "stop" {
        Write-Host "[*] Stopping Ray node..." -ForegroundColor Yellow
        & "$PythonExe" -m ray stop
        Write-Host "[✓] Ray stopped." -ForegroundColor Green
    }
}
