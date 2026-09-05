# ReturnShield AI — PowerShell Launcher
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   Starting ReturnShield AI (Backend + Frontend)" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Start Backend in separate window
Write-Host "[1/2] Starting FastAPI Backend on http://127.0.0.1:8000..." -ForegroundColor Yellow
Start-Process cmd.exe -ArgumentList "/k cd /d `"$Root\backend`" && `"$Root\.venv\Scripts\python.exe`" -m uvicorn main:app --host 127.0.0.1 --port 8000"

# 2. Start Frontend in separate window
Write-Host "[2/2] Starting React Dashboard on http://localhost:3000..." -ForegroundColor Yellow
Start-Process cmd.exe -ArgumentList "/k cd /d `"$Root\frontend`" && npm run dev"

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host "  Services launched successfully!" -ForegroundColor Green
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  Backend:  http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  API Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Green
