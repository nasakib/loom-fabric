<#
.SYNOPSIS
    Loom Fabric -- ClothOS x86 / x86_64 Multiboot Builder & Simulator Launcher
#>
$ErrorActionPreference = "Continue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $ScriptDir

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  LOOM FABRIC -- CLOTHOS x86_64 & x86_32 MULTIBOOT SPECIAL EDITION" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Cyan

if (Get-Command "cargo.exe" -ErrorAction SilentlyContinue) {
    & cargo build --release
} else {
    Write-Host "[i] Launching ClothOS x86 HAL via Loom Python runtime..." -ForegroundColor Yellow
    $RepoDir = Split-Path -Parent (Split-Path -Parent $ScriptDir)
    & "$RepoDir\.venv\Scripts\python.exe" -m loom.clothos.x86_hal_emulator
}
Pop-Location
