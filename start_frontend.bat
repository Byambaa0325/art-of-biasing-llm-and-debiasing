@echo off
REM Start the React frontend development server

echo ========================================
echo Starting React Frontend Server
echo ========================================
echo.

cd frontend-react

REM Check if dependencies are installed
if not exist node_modules (
    echo Installing dependencies...
    call npm install
    echo.
)

echo Starting React development server...
echo.
echo The app will open at: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

call npm start

