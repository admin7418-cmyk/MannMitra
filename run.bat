@echo off
title MannMitra AI Platform Launcher
echo ========================================================
echo        Starting MannMitra AI Platform
echo ========================================================

:: 1. Check and Start Ollama if not running
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo [1/3] Starting Local Ollama AI Engine with GPU...
    start "" "%LOCALAPPDATA%\Programs\Ollama\ollama.exe" serve
    timeout /t 3 /nobreak >nul
) else (
    echo [1/3] Local Ollama AI Engine is already running.
)

:: 2. Open browser after brief delay
echo [2/3] Opening browser at http://127.0.0.1:5000...
start "" timeout /t 2 ^>nul ^& start http://127.0.0.1:5000

:: 3. Run Flask App
echo [3/3] Starting Flask Web Server...
echo Press Ctrl+C in this window anytime to stop the server.
echo.
python app.py
pause
