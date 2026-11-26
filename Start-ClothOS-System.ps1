<#
.SYNOPSIS
    ClothOS Sovereign System Starter (Single-Port :8087 Unified Launcher)
.DESCRIPTION
    Idempotently starts Ollama (:11434) and the ClothOS Unified Command Center (:8087)
    without duplicate-port conflicts, waits for /api/health, and opens the Web UI.
#>

$ErrorActionPreference = "SilentlyContinue"
$RepoRoot = "c:\Users\natsa\Documents\loom-fabric"
$PythonExe = Join-Path $RepoRoot ".venv\Scripts\python.exe"
$LogFile = Join-Path $RepoRoot "clothos_system.log"
$OllamaExe = Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe"

# Sanitize cross-environment Python variables
Remove-Item Env:PYTHONHOME -ErrorAction SilentlyContinue
Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
Remove-Item Env:VIRTUAL_ENV -ErrorAction SilentlyContinue

function Test-PortListening {
    param([string]$HostAddr = "127.0.0.1", [int]$Port)
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $iar = $client.BeginConnect($HostAddr, $Port, $null, $null)
        $wait = $iar.AsyncWaitHandle.WaitOne(400, $false)
        if ($wait -and $client.Connected) {
            $client.Close()
            return $true
        }
        $client.Close()
    } catch {}
    return $false
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  CLOTHOS SOVEREIGN SYSTEM STARTER  (Unified Port :8087)" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

# 1. Ensure Ollama (:11434) is running
if (-not (Test-PortListening -Port 11434)) {
    if (Test-Path $OllamaExe) {
        Write-Host "[*] Starting Ollama inference engine (:11434)..." -ForegroundColor Yellow
        Start-Process -FilePath $OllamaExe -ArgumentList "serve" -WindowStyle Hidden
        Start-Sleep -Milliseconds 800
    } else {
        Write-Host "[!] Ollama executable not found at $OllamaExe (skipping)" -ForegroundColor DarkYellow
    }
} else {
    Write-Host "[OK] Ollama (:11434) already active." -ForegroundColor Green
}

# 2. Ensure ClothOS Unified Server (:8087) is running
if (-not (Test-PortListening -Port 8087)) {
    Write-Host "[*] Starting ClothOS Unified Server (:8087)..." -ForegroundColor Yellow
    Start-Process -FilePath $PythonExe `
        -ArgumentList "-m", "uvicorn", "loom.fabric.dashboard_server:app", "--host", "0.0.0.0", "--port", "8087" `
        -WorkingDirectory $RepoRoot `
        -RedirectStandardOutput $LogFile `
        -RedirectStandardError (Join-Path $RepoRoot "clothos_system.err.log") `
        -WindowStyle Hidden

    $ready = $false
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Milliseconds 500
        try {
            $resp = Invoke-RestMethod -Uri "http://127.0.0.1:8087/api/health" -TimeoutSec 2
            if ($resp.status -eq "ONLINE") {
                $ready = $true
                break
            }
        } catch {}
    }
    if ($ready) {
        Write-Host "[OK] ClothOS Unified Server (:8087) is ONLINE." -ForegroundColor Green
    } else {
        Write-Host "[!] Server is still initializing; check $LogFile if it does not load." -ForegroundColor Yellow
    }
} else {
    Write-Host "[OK] ClothOS Unified Server (:8087) already active." -ForegroundColor Green
}

# 3. Open the Unified Command Center in the default browser
Write-Host "[*] Opening http://127.0.0.1:8087/ ..." -ForegroundColor Cyan
Start-Process "http://127.0.0.1:8087/"
Start-Sleep -Seconds 2
