@echo off
REM Script to add gcloud to PATH in current CMD session

echo Adding gcloud to PATH for this session...
set PATH=%PATH%;C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin

echo.
echo Verifying installation...
gcloud --version

echo.
echo gcloud is now available in this terminal session.
echo.
echo To make it permanent, the PATH was already added to User environment variables.
echo Restart your terminal for permanent changes to take effect.

