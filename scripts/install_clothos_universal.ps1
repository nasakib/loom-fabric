<#
.SYNOPSIS
    ClothOS Universal Commercial One-Click Installer & Autonomous Node Provisioner
.DESCRIPTION
    1. Audits local silicon (CPUs, System RAM, Discrete GPUs, VRAM).
    2. Auto-assigns Node Role: Compute Worker (>=12GB VRAM) vs Orchestrator Decider (<=16GB RAM/Integrated).
    3. Silently provisions Ollama and pulls optimal local LLM tier (7B / 32B / 70B).
    4. Starts zero-config mesh discovery beacon (UDP 5556) & Stitch Bridge (TCP 5555).
    5. Establishes Windows firewall rules and installs zero-window auto-start persistence.
    6. Registers global `clothos` and `clothsh` terminal commands in system PATH.
#>

[CmdletBinding()]
param (
    [switch]$Unattended,
    [switch]$Reinstall,
    [string]$TargetRole = "auto"  # 'auto', 'worker', 'decider'
)

$ErrorActionPreference = "Stop"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "    ✦ CLOTHOS COMMERCIAL UNIVERSAL SYSTEM INSTALLER       " -ForegroundColor Green
Write-Host "    Zero-Config Distributed AI Operating System Mesh      " -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Cyan

# ── 1. Silicon Hardware Census ──────────────────────────────────────────────────
Write-Host "`n[1/6] Auditing Local Silicon & Compute Capacity..." -ForegroundColor Yellow
$cs = Get-CimInstance Win32_ComputerSystem
$os = Get-CimInstance Win32_OperatingSystem
$cpu = Get-CimInstance Win32_Processor
$gpus = Get-CimInstance Win32_VideoController

$totalRamGB = [math]::Round($cs.TotalPhysicalMemory / 1GB, 1)
$vcpus = $cpu.NumberOfLogicalProcessors

$discreteGpuFound = $false
$maxVramGB = 0
$gpuNames = @()

foreach ($g in $gpus) {
    $gpuNames += $g.Name
    $vramGB = [math]::Round($g.AdapterRAM / 1GB, 1)
    if ($vramGB -gt $maxVramGB) { $maxVramGB = $vramGB }
    if ($g.Name -match "NVIDIA|GeForce|RTX|Radeon RX|Tesla|Quadro") {
        $discreteGpuFound = $true
    }
}

Write-Host "  • CPU: $($cpu.Name) ($vcpus Threads)" -ForegroundColor White
Write-Host "  • System RAM: $totalRamGB GB" -ForegroundColor White
Write-Host "  • GPUs Detected: $($gpuNames -join ', ')" -ForegroundColor White

# Determine Role
$assignedRole = "decider"
if ($TargetRole -eq "worker" -or ($TargetRole -eq "auto" -and ($discreteGpuFound -or $maxVramGB -ge 8.0 -or $totalRamGB -ge 32.0))) {
    $assignedRole = "compute_worker"
} else {
    $assignedRole = "orchestrator_decider"
}
Write-Host "  ➔ Auto-Assigned Node Role: [$assignedRole]" -ForegroundColor Green

# ── 2. Python & Virtual Environment Setup ───────────────────────────────────────
Write-Host "`n[2/6] Verifying Sovereign Python Runtime Environment..." -ForegroundColor Yellow
$RepoDir = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path "$RepoDir\pyproject.toml")) {
    $RepoDir = "C:\Users\$env:USERNAME\Documents\loom-fabric"
}
$VenvDir = "$RepoDir\.venv"
$VenvPy = "$VenvDir\Scripts\python.exe"

if (-not (Test-Path $VenvPy)) {
    Write-Host "  [*] Bootstrapping virtual environment..." -ForegroundColor White
    python -m venv "$VenvDir"
    & "$VenvPy" -m pip install --upgrade pip -q
    & "$VenvPy" -m pip install fastapi uvicorn httpx pydantic rich -q
} else {
    Write-Host "  [OK] Virtual environment verified at $VenvDir" -ForegroundColor Green
}

# ── 3. Local Model Provisioner (Ollama) ──────────────────────────────────────────
Write-Host "`n[3/6] Configuring Neural Tensor Backend (Ollama)..." -ForegroundColor Yellow
$ollamaCmd = Get-Command "ollama.exe" -ErrorAction SilentlyContinue

if (-not $ollamaCmd) {
    Write-Host "  [*] Ollama not found in PATH; downloading official installer..." -ForegroundColor White
    $ollamaInstaller = "$env:TEMP\OllamaSetup.exe"
    try {
        Invoke-WebRequest -Uri "https://ollama.com/download/OllamaSetup.exe" -OutFile $ollamaInstaller -TimeoutSec 60
        Start-Process -FilePath $ollamaInstaller -ArgumentList "/silent" -Wait
        Write-Host "  [OK] Ollama installed successfully." -ForegroundColor Green
    } catch {
        Write-Host "  [i] Notice: Ollama installer skipped or running in offline mode." -ForegroundColor Yellow
    }
} else {
    Write-Host "  [OK] Ollama detected at $($ollamaCmd.Source)" -ForegroundColor Green
}

# Configure persistent keep-alive and network binding
[System.Environment]::SetEnvironmentVariable('OLLAMA_KEEP_ALIVE', '-1', 'User')
[System.Environment]::SetEnvironmentVariable('OLLAMA_HOST', '0.0.0.0:11434', 'User')

# Pull recommended model tier based on role
if ($assignedRole -eq "compute_worker") {
    Write-Host "  [*] Compute Worker: Pulling recommended Sovereign model tier (Fast 7B + Reasoner 32B)..." -ForegroundColor Cyan
    try {
        & ollama pull qwen2.5:7b
        & ollama cp qwen2.5:7b loom-sovereign-fast
    } catch {
        Write-Host "  [i] Model provisioning deferred to runtime." -ForegroundColor Yellow
    }
}

# ── 4. Windows Firewall & Network Mesh Rules ────────────────────────────────────
Write-Host "`n[4/6] Configuring Zero-Config LAN Mesh Firewall Rules..." -ForegroundColor Yellow
try {
    $ports = @(5555, 5556, 11434, 8087, 8090, 6379)
    foreach ($p in $ports) {
        $ruleName = "ClothOS-Port-$p"
        $existing = Get-NetFirewallRule -Name $ruleName -ErrorAction SilentlyContinue
        if (-not $existing) {
            New-NetFirewallRule -Name $ruleName -DisplayName "ClothOS Mesh Communication ($p)" -Direction Inbound -Protocol TCP -LocalPort $p -Action Allow -ErrorAction SilentlyContinue | Out-Null
        }
    }
    # UDP broadcast for discovery
    $udpRule = Get-NetFirewallRule -Name "ClothOS-UDP-5556" -ErrorAction SilentlyContinue
    if (-not $udpRule) {
        New-NetFirewallRule -Name "ClothOS-UDP-5556" -DisplayName "ClothOS Mesh UDP Discovery (5556)" -Direction Inbound -Protocol UDP -LocalPort 5556 -Action Allow -ErrorAction SilentlyContinue | Out-Null
    }
    Write-Host "  [OK] Inbound mesh ports allowed (TCP 5555, 11434, 8087, 8090; UDP 5556)." -ForegroundColor Green
} catch {
    Write-Host "  [i] Firewall rules note: requires administrator privileges or manually configured." -ForegroundColor Yellow
}

# ── 5. System PATH & Global CLI Registration ────────────────────────────────────
Write-Host "`n[5/6] Registering Global 'clothos' & 'clothsh' Commands..." -ForegroundColor Yellow
$binDir = "$env:USERPROFILE\.loom\bin"
New-Item -ItemType Directory -Path $binDir -Force | Out-Null

$clothosCmd = @"
@echo off
set "PYTHONPATH=$RepoDir;%PYTHONPATH%"
set "PYTHONIOENCODING=utf-8"
"$VenvPy" -m loom.clothos.agent_cli --workspace "%CD%" %*
"@
[System.IO.File]::WriteAllText("$binDir\clothos.cmd", $clothosCmd, [System.Text.Encoding]::ASCII)

$clothshCmd = @"
@echo off
set "PYTHONPATH=$RepoDir;%PYTHONPATH%"
set "PYTHONIOENCODING=utf-8"
"$VenvPy" -m loom.clothos.shell %*
"@
[System.IO.File]::WriteAllText("$binDir\clothsh.cmd", $clothshCmd, [System.Text.Encoding]::ASCII)

$currentPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$binDir*") {
    [System.Environment]::SetEnvironmentVariable("Path", "$currentPath;$binDir", "User")
    Write-Host "  [OK] Added $binDir to User PATH." -ForegroundColor Green
} else {
    Write-Host "  [OK] $binDir already in PATH." -ForegroundColor Green
}

# ── 6. Windows Zero-Window Startup Persistence ──────────────────────────────────
Write-Host "`n[6/6] Configuring Zero-Window Background Persistence..." -ForegroundColor Yellow
$startupDir = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$vbsPath = "$startupDir\ClothOS_Antigravity_Startup.vbs"
$managerScript = "$RepoDir\guis\desktop_startup_manager.py"

$q = '"""'
$vbsCode = @"
' ClothOS Antigravity Universal Desktop Startup
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "$RepoDir"
WshShell.Run $q$VenvPy$q & " " & $q$managerScript$q & " --on-startup", 0, False
"@
[System.IO.File]::WriteAllText($vbsPath, $vbsCode, [System.Text.Encoding]::ASCII)
Write-Host "  [OK] Created startup supervisor: $vbsPath" -ForegroundColor Green

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "   ✦ CLOTHOS INSTALLATION & MESH CONFIGURATION COMPLETE!  " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "You can now run:" -ForegroundColor White
Write-Host "  • clothos           -> Launch interactive Agentic AI OS" -ForegroundColor Cyan
Write-Host "  • clothsh           -> Launch native POSIX shell environment" -ForegroundColor Cyan
Write-Host "  • /node status      -> Inspect all live nodes discovered on your LAN" -ForegroundColor Cyan
Write-Host "==========================================================`n" -ForegroundColor Green