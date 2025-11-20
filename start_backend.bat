@echo off
REM Start the backend server

echo ========================================
echo Starting Bias Analysis Backend Server
echo ========================================
echo.

REM Add gcloud to PATH for this session
set PATH=%PATH%;C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import flask" 2>nul
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo Starting server on http://localhost:5000
echo.
echo API Endpoints:
echo   POST /api/graph/expand - Expand graph from starter prompt
echo   POST /api/graph/evaluate - Evaluate bias using Gemini 2.5 Flash
echo   POST /api/graph/expand-node - Expand specific node
echo   GET  /api/health - Health check
echo.
echo Press Ctrl+C to stop the server
echo.

cd backend
python api.py

