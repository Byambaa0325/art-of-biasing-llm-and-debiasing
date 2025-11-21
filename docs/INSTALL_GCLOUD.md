# Installing and Adding gcloud to PATH

## Option 1: Install Google Cloud SDK (Recommended)

### Step 1: Download and Install

1. **Visit the official download page:**
   - https://cloud.google.com/sdk/docs/install

2. **Download the Windows installer:**
   - Click "Download Google Cloud SDK for Windows"
   - Run the installer (`GoogleCloudSDKInstaller.exe`)

3. **During installation:**
   - The installer will ask if you want to add gcloud to PATH
   - **Check "Add to PATH"** option
   - Complete the installation

4. **After installation:**
   - Restart your terminal/PowerShell
   - Run: `gcloud --version` to verify

### Step 2: Initialize gcloud

```powershell
gcloud init
```

This will:
- Authenticate with your Google account
- Set your default project
- Configure default region

## Option 2: Manual PATH Addition (If Already Installed)

If gcloud is already installed but not in PATH:

### Method A: Using PowerShell Script

Run the provided script:

```powershell
powershell -ExecutionPolicy Bypass -File add_gcloud_path.ps1
```

### Method B: Manual GUI Method

1. **Find gcloud installation:**
   - Usually at: `%LOCALAPPDATA%\Google\Cloud SDK\google-cloud-sdk\bin`
   - Or: `%ProgramFiles%\Google\Cloud SDK\google-cloud-sdk\bin`

2. **Add to PATH:**
   - Press `Win + X` → Select "System"
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "User variables", find "Path" and click "Edit"
   - Click "New" and add:
     ```
     %LOCALAPPDATA%\Google\Cloud SDK\google-cloud-sdk\bin
     ```
   - Click "OK" on all dialogs

3. **Restart terminal** for changes to take effect

### Method C: Using PowerShell (Permanent)

Run PowerShell and execute:

```powershell
# Replace with your actual gcloud path if different
$gcloudPath = "$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin"

# Add to User PATH permanently
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$gcloudPath*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$gcloudPath", "User")
    Write-Host "Added to PATH. Please restart your terminal."
} else {
    Write-Host "Already in PATH"
}
```

## Option 3: Using Package Managers

### Chocolatey

```powershell
choco install gcloudsdk
```

### Scoop

```powershell
scoop install gcloud
```

## Verify Installation

After installation and adding to PATH, restart your terminal and run:

```powershell
gcloud --version
```

You should see output like:
```
Google Cloud SDK 450.0.0
...
```

## Authenticate

After installation, authenticate:

```powershell
gcloud auth login
gcloud auth application-default login
```

## Quick Setup for This Project

Once gcloud is installed and in PATH:

```powershell
# 1. Authenticate
gcloud auth application-default login

# 2. Set your project (if not already set)
gcloud config set project lazy-jeopardy

# 3. Verify
gcloud config list
```

## Troubleshooting

### "gcloud: command not found"

- **Solution 1:** Restart your terminal after adding to PATH
- **Solution 2:** Verify PATH was added correctly:
  ```powershell
  $env:Path -split ';' | Select-String "gcloud"
  ```
- **Solution 3:** Manually add to PATH using GUI method

### "gcloud is not recognized"

- Make sure you restarted the terminal
- Check if gcloud is actually installed:
  ```powershell
  Test-Path "$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd"
  ```

### Installation Issues

- Make sure you have administrator privileges
- Check Windows Defender isn't blocking the installer
- Try running installer as administrator

## Next Steps

After gcloud is installed and in PATH:

1. **Authenticate:**
   ```powershell
   gcloud auth application-default login
   ```

2. **Run the project:**
   - See `RUN_PROJECT.md` for instructions
   - Or use: `start_server.bat` to start backend

