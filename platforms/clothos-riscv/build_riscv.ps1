<#
.SYNOPSIS
    Loom Fabric -- ClothOS RISC-V (RV64GC + RVV 1.0) Builder & Simulator Launcher
#>
$ErrorActionPreference = "Continue"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $ScriptDir

Write-Host "==================================================================" -ForegroundColor Magenta
Write-Host "  LOOM FABRIC -- CLOTHOS RISC-V (RV64GC + RVV 1.0) SPECIAL EDITION" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Magenta

if (Get-Command "rustup.exe" -ErrorAction SilentlyContinue) {
    & rustup target add riscv64gc-unknown-none-elf riscv64gc-unknown-linux-gnu 2>$null
}

if (Get-Command "cargo.exe" -ErrorAction SilentlyContinue) {
    & cargo build --release
} else {
    Write-Host "[i] Launching ClothOS RISC-V (RV64GC + RVV 1.0 + PMP Enclave) via Loom CLI..." -ForegroundColor Cyan
    $RepoDir = Split-Path -Parent (Split-Path -Parent $ScriptDir)
    & "$RepoDir\.venv\Scripts\python.exe" -m loom.cli.main clothos
}
Pop-Location
