@echo off
REM ==============================================================================
REM SafeStack AI - 1-Click Launch Script (Windows)
REM ==============================================================================

echo ==================================================================
echo   SafeStack AI: Real-Time Damage-Free Warehouse Intelligence
echo ==================================================================
echo.

set PYTHONPATH=.

REM Start Backend
start "SafeStack Backend" cmd /k "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"

REM Start Frontend if node is installed
if exist "frontend\node_modules" (
    cd frontend
    start "SafeStack Frontend" cmd /k "npm run dev"
    cd ..
    echo Frontend started on http://localhost:5173
) else (
    echo Frontend pre-built dist served via backend on http://localhost:8000
)

echo Backend API docs available on http://localhost:8000/docs
echo System is running.
pause
