@echo off
REM Install all Python dependencies including Google Cloud libraries

echo ========================================
echo Installing Python Dependencies
echo ========================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

echo Installing from requirements.txt...
pip install -r requirements.txt

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo To verify, run:
echo   python -c "import google.cloud.aiplatform; print('OK')"
echo.
pause

