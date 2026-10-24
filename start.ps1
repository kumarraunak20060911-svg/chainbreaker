# ChainBreaker Instant Production / Demo Launcher for Windows PowerShell
$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " CHAINBREAKER · Smart City Incident Reconstruction SOC" -ForegroundColor Green
Write-Host " Hackathon ChronoForge · Cybersecurity Track · Team PVR" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Cyan

# Find Python binary
$PyBin = "python"
if (Get-Command "py" -ErrorAction SilentlyContinue) {
    $PyBin = "py -3"
}

$env:PYTHONPATH = "src;$env:PYTHONPATH"

# Ensure runtime directories exist
New-Item -ItemType Directory -Force -Path "runtime\databases" | Out-Null
New-Item -ItemType Directory -Force -Path "runtime\uploads" | Out-Null
New-Item -ItemType Directory -Force -Path "runtime\reports" | Out-Null

Write-Host "[+] Launching ChainBreaker console on http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "    - Workbench:        http://127.0.0.1:8000/" -ForegroundColor Yellow
Write-Host "    - Attack Recreator: http://127.0.0.1:8000/recreate" -ForegroundColor Yellow
Write-Host "    - Scenarios:        http://127.0.0.1:8000/scenarios" -ForegroundColor Yellow
Write-Host "    - Database Hub:     http://127.0.0.1:8000/database" -ForegroundColor Yellow
Write-Host "    - Evasion Lab:      http://127.0.0.1:8000/evasion" -ForegroundColor Yellow
Write-Host "    - Benchmarks:       http://127.0.0.1:8000/metrics" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

Invoke-Expression "$PyBin -m uvicorn chainbreaker.api.app:app --host 127.0.0.1 --port 8000 --reload"
