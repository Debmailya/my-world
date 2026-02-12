REM PhishGuard AI - Quick Reference Guide (Windows)
REM All commands and common operations

@echo off
cls

echo PhishGuard AI - Quick Reference
echo ================================
echo.
echo 1. LOCAL DEVELOPMENT
echo    quickstart.bat               :: Windows quick start
echo    python backend\app.py        :: Run backend only
echo.
echo 2. DOCKER
echo    docker-compose up --build    :: Start all services
echo    docker-compose down          :: Stop services  
echo    docker-compose logs -f       :: View logs
echo    docker-compose restart       :: Restart services
echo.
echo 3. PYTHON SETUP
echo    python -m venv venv          :: Create virtual environment
echo    venv\Scripts\activate.bat    :: Activate environment
echo    pip install -r backend\requirements.txt :: Install deps
echo.
echo 4. TESTING
echo    pytest tests\ -v             :: Run all tests
echo    pytest tests\ -v --cov=backend :: With coverage
echo.
echo 5. DEVELOPMENT
echo    python backend\app.py        :: Dev server with auto-reload
echo.
echo 6. PRODUCTION
echo    gunicorn --bind 0.0.0.0:8000 --workers 4 backend.app:app
echo.
echo 7. DEPLOYMENT
echo    REM Heroku
echo    heroku login
echo    heroku create phishguard-ai
echo    git push heroku main
echo.
echo 8. ENVIRONMENT VARIABLES
echo    set ENVIRONMENT=production
echo    set API_WORKERS=4
echo    set LOG_LEVEL=INFO
echo.
echo 9. USEFUL URLS (local)
echo    http://localhost:8000              :: Main app
echo    http://localhost:8000/docs         :: API docs
echo    http://localhost:8000/health       :: Health check
echo.
echo 10. API CALL EXAMPLE
echo     curl -X POST http://localhost:8000/api/analyze ^
echo       -H "Content-Type: application/json" ^
echo       -d "{\"url\": \"https://example.com\"}"
echo.
echo 11. KEY FILES
echo     backend\app.py              :: Main API
echo     frontend\index.html         :: Web UI
echo     ml_model\detector.py        :: ML model
echo     backend\config.py           :: Configuration
echo.
echo 12. DOCUMENTATION
echo     README.md                   :: Getting started
echo     ARCHITECTURE.md             :: System design
echo     DEPLOYMENT_GUIDE.md         :: Deployment
echo     API_DOCUMENTATION.md        :: API reference
echo.
echo 13. TROUBLESHOOTING
echo     REM Check port usage
echo     netstat -ano | findstr :8000
echo.
echo     REM Clear Docker
echo     docker-compose down -v
echo     docker system prune
echo.
echo     REM Update dependencies
echo     pip install --upgrade -r backend\requirements.txt
echo.
echo 14. MONITORING
echo     docker stats                :: Container stats
echo     tasklist | findstr python   :: Find Python processes
echo.
echo Done!
pause
