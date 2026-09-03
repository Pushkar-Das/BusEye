@echo off
title BusEye - Backend Server
echo.
echo  ======================================
echo   BusEye - Starting Backend Server
echo  ======================================
echo.

cd /d "%~dp0backend"

:: Create virtual environment if not exists
if not exist "venv" (
    echo  [1/3] Creating Python virtual environment...
    python -m venv venv
    echo  Done!
)

:: Activate venv
call venv\Scripts\activate

:: Install dependencies
echo  [2/3] Installing Python packages (first run takes a few minutes)...
pip install -r requirements.txt -q

:: Start server
echo  [3/3] Starting FastAPI server on http://localhost:8000
echo.
echo  API Docs: http://localhost:8000/docs
echo  Press Ctrl+C to stop
echo.
set PYTHONIOENCODING=utf-8
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause
