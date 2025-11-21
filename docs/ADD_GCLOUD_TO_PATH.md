# Adding gcloud to PATH on Windows

## Step 1: Find gcloud Installation

gcloud is typically installed in one of these locations:
- `%LOCALAPPDATA%\Google\Cloud SDK\google-cloud-sdk\bin`
- `%ProgramFiles%\Google\Cloud SDK\google-cloud-sdk\bin`
- `%ProgramFiles(x86)%\Google\Cloud SDK\google-cloud-sdk\bin`

## Step 2: Add to PATH (Method 1 - PowerShell - Current Session)

Run this in PowerShell (temporary, only for current session):

```powershell
$gcloudPath = "$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin"
if (Test-Path $gcloudPath) {
    $env:Path += ";$gcloudPath"
    Write-Host "Added to PATH for this session: $gcloudPath"
} else {
    Write-Host "gcloud not found at: $gcloudPath"
    Write-Host "Please install gcloud first or update the path above"
}
```

## Step 3: Add to PATH Permanently (Method 2 - System Settings)

### Option A: Using GUI

1. Press `Win + X` and select "System"
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "User variables" or "System variables", find "Path" and click "Edit"
5. Click "New" and add:
   ```
   %LOCALAPPDATA%\Google\Cloud SDK\google-cloud-sdk\bin
   ```
6. Click "OK" on all dialogs
7. **Restart your terminal/PowerShell** for changes to take effect

### Option B: Using PowerShell (Permanent)

Run PowerShell **as Administrator**:

```powershell
# For current user
$gcloudPath = "$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin"
if (Test-Path $gcloudPath) {
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($currentPath -notlike "*$gcloudPath*") {
        [Environment]::SetEnvironmentVariable("Path", "$currentPath;$gcloudPath", "User")
        Write-Host "Added to PATH permanently: $gcloudPath"
        Write-Host "Please restart your terminal for changes to take effect"
    } else {
        Write-Host "Already in PATH"
    }
} else {
    Write-Host "gcloud not found. Please install it first."
}
```

## Step 4: Verify Installation

After adding to PATH, restart your terminal and run:

```powershell
gcloud --version
```

You should see the gcloud version information.

## If gcloud is Not Installed

1. **Download Google Cloud SDK:**
   - Visit: https://cloud.google.com/sdk/docs/install
   - Download the Windows installer

2. **Install:**
   - Run the installer
   - Follow the installation wizard
   - The installer will offer to add gcloud to PATH automatically

3. **Or use package manager:**
   ```powershell
   # Using Chocolatey
   choco install gcloudsdk
   
   # Using Scoop
   scoop install gcloud
   ```

## Quick Script

Save this as `add_gcloud_path.ps1` and run it:

```powershell
# Find gcloud
$possiblePaths = @(
    "$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin",
    "$env:ProgramFiles\Google\Cloud SDK\google-cloud-sdk\bin",
    "$env:ProgramFiles(x86)\Google\Cloud SDK\google-cloud-sdk\bin"
)

$gcloudPath = $null
foreach ($path in $possiblePaths) {
    if (Test-Path "$path\gcloud.cmd") {
        $gcloudPath = $path
        break
    }
}

if ($gcloudPath) {
    Write-Host "Found gcloud at: $gcloudPath"
    
    # Add to current session
    $env:Path += ";$gcloudPath"
    Write-Host "Added to PATH for this session"
    
    # Add permanently (requires admin for system PATH)
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($currentPath -notlike "*$gcloudPath*") {
        [Environment]::SetEnvironmentVariable("Path", "$currentPath;$gcloudPath", "User")
        Write-Host "Added to PATH permanently (User)"
        Write-Host "Please restart your terminal for permanent changes"
    } else {
        Write-Host "Already in permanent PATH"
    }
    
    # Verify
    Write-Host "`nVerifying installation..."
    gcloud --version
} else {
    Write-Host "gcloud not found. Please install Google Cloud SDK first."
    Write-Host "Download from: https://cloud.google.com/sdk/docs/install"
}
```

