@echo off
echo Starting Bias Analysis API Server...
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
cd backend
python api.py
pause

