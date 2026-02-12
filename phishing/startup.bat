@echo off
REM PhishGuard AI - Windows Startup Script

echo =========================================
echo PhishGuard AI - Production Startup
echo =========================================

REM Check Python version
python --version

REM Set environment variables
if not defined ENVIRONMENT set ENVIRONMENT=development
if not defined API_WORKERS set API_WORKERS=4

echo Environment: %ENVIRONMENT%
echo API Workers: %API_WORKERS%

REM Create directories
if not exist "backend" mkdir backend
if not exist "logs" mkdir logs
if not exist "ml_model" mkdir ml_model

REM Create and activate virtual environment
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install --upgrade pip
pip install -r backend\requirements.txt

REM Load ML model
echo Loading ML model...
python -c "from ml_model.detector import PhishingDetector; detector = PhishingDetector(); print('Model loaded successfully')"

if errorlevel 1 (
    echo Failed to load ML model
    exit /b 1
)

REM Start server
echo Starting PhishGuard AI server...
echo API available at http://localhost:8000

if "%ENVIRONMENT%"=="production" (
    gunicorn --bind 0.0.0.0:8000 --workers %API_WORKERS% --worker-class uvicorn.workers.UvicornWorker --timeout 60 backend.app:app
) else (
    uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload --log-level info
)
