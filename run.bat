@echo off
title ReturnShield AI Launcher
echo ========================================================
echo    Starting ReturnShield AI (Backend + Frontend)
echo ========================================================
echo.

REM 1. Start Backend in a dedicated window
echo [1/2] Launching FastAPI Backend on http://127.0.0.1:8000 ...
start "ReturnShield AI Backend (FastAPI)" cmd /k "cd /d %~dp0backend && ..\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000"

REM 2. Start Frontend in a dedicated window
echo [2/2] Launching React Dashboard on http://localhost:3000 ...
start "ReturnShield AI Frontend (Vite)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================================
echo   Services are running!
echo   - Frontend: http://localhost:3000
echo   - Backend:  http://127.0.0.1:8000
echo   - API Docs: http://127.0.0.1:8000/docs
echo ========================================================
echo You can keep this window open or close it.
pause
