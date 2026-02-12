@echo off
REM PhishGuard AI - Quick Start Guide for Windows

cls

echo.
echo ╔════════════════════════════════════════╗
echo ║   Welcome to PhishGuard AI Setup      ║
echo ║   Intelligent Phishing Detection      ║
echo ╚════════════════════════════════════════╝
echo.

REM Check if Docker is installed
where docker >nul 2>nul

if %ERRORLEVEL% == 0 (
    echo ✓ Docker is installed
    echo.
    echo Starting PhishGuard AI with Docker...
    echo.
    docker-compose up --build
) else (
    echo ⚠️  Docker not found. Installing for local development...
    echo.
    
    REM Check Python
    where python >nul 2>nul
    
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Python is required. Please install Python 3.11+
        pause
        exit /b 1
    )
    
    python --version
    echo ✓ Python found
    echo.
    
    REM Create virtual environment
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
    
    REM Install dependencies
    echo Installing dependencies...
    pip install --upgrade pip
    pip install -r backend\requirements.txt
    
    REM Start server
    echo.
    echo ╔════════════════════════════════════════╗
    echo ║    Starting PhishGuard AI Server      ║
    echo ╚════════════════════════════════════════╝
    echo.
    echo 🚀 Server starting on http://localhost:8000
    echo 🌐 Open http://localhost:8000 in your browser
    echo.
    echo Press Ctrl+C to stop the server
    echo.
    
    python backend\app.py
)

pause
