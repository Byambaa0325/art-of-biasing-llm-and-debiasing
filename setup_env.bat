@echo off
REM Setup script to create .env file from .env.example

echo ========================================
echo Environment Variables Setup
echo ========================================
echo.

if not exist .env.example (
    echo ERROR: .env.example file not found!
    echo Please create it first.
    pause
    exit /b 1
)

if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo.
    echo ✓ .env file created successfully!
    echo.
    echo ⚠️  IMPORTANT: Edit .env file and set your GOOGLE_CLOUD_PROJECT
    echo.
    echo Opening .env file for editing...
    timeout /t 2 /nobreak >nul
    notepad .env
    echo.
    echo After editing, run: python check_env.py
    echo to verify your configuration.
) else (
    echo .env file already exists.
    echo.
    echo To recreate it, delete .env and run this script again.
    echo.
    echo Current .env file location: %CD%\.env
)

echo.
pause
