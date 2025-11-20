@echo off
REM Script to set up gcloud PATH and authentication for CMD

echo ========================================
echo Setting up gcloud for CMD
echo ========================================
echo.

REM Add gcloud to PATH for this session
set PATH=%PATH%;C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin

echo [OK] Added gcloud to PATH for this session
echo.

REM Check if gcloud is available
gcloud --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] gcloud not found. Please restart your terminal.
    pause
    exit /b 1
)

echo [OK] gcloud is available
echo.

REM Check if already authenticated
gcloud auth application-default print-access-token >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Already authenticated
) else (
    echo Authenticating with Google Cloud...
    gcloud auth application-default login
)

echo.
echo Setting quota project...
gcloud auth application-default set-quota-project lazy-jeopardy

echo.
echo Setting default project...
gcloud config set project lazy-jeopardy

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo You can now run the backend server:
echo   cd backend
echo   python api.py
echo.

