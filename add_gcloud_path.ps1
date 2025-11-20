# Script to add gcloud to PATH on Windows

Write-Host "========================================"
Write-Host "Adding gcloud to PATH"
Write-Host "========================================"
Write-Host ""

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
        Write-Host "Found gcloud at: $path"
        break
    }
}

if ($gcloudPath) {
    Write-Host ""
    Write-Host "Adding to PATH..."
    
    # Add to current session
    if ($env:Path -notlike "*$gcloudPath*") {
        $env:Path += ";$gcloudPath"
        Write-Host "[OK] Added to PATH for this session"
    } else {
        Write-Host "[OK] Already in PATH for this session"
    }
    
    # Add permanently (User PATH)
    $currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($currentPath -notlike "*$gcloudPath*") {
        [Environment]::SetEnvironmentVariable("Path", "$currentPath;$gcloudPath", "User")
        Write-Host "[OK] Added to PATH permanently (User)"
        Write-Host ""
        Write-Host "IMPORTANT: Restart your terminal for permanent changes to take effect"
    } else {
        Write-Host "[OK] Already in permanent PATH"
    }
    
    Write-Host ""
    Write-Host "Verifying installation..."
    Write-Host "----------------------------------------"
    try {
        & gcloud --version
        Write-Host ""
        Write-Host "[OK] gcloud is working!"
    } catch {
        Write-Host "[ERROR] gcloud command failed"
        Write-Host "  Try restarting your terminal"
    }
} else {
    Write-Host ""
    Write-Host "[ERROR] gcloud not found in common installation locations"
    Write-Host ""
    Write-Host "Please install Google Cloud SDK first:"
    Write-Host "1. Visit: https://cloud.google.com/sdk/docs/install"
    Write-Host "2. Download the Windows installer"
    Write-Host "3. Run the installer"
    Write-Host "4. Run this script again"
    Write-Host ""
    Write-Host "Or if gcloud is installed elsewhere, manually add it to PATH:"
    Write-Host "  - Press Win+X -> System -> Advanced system settings"
    Write-Host "  - Click 'Environment Variables'"
    Write-Host "  - Edit 'Path' and add the gcloud bin directory"
}

Write-Host ""
Write-Host "========================================"
