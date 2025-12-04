# PowerShell deployment script for Bedrock Integration Branch
# This script deploys the bedrock-api-integration branch to a separate Cloud Run service

$ErrorActionPreference = "Stop"

Write-Host "Deploying Bedrock Integration Branch to Cloud Run" -ForegroundColor Green

# Check if gcloud is installed
try {
    $null = Get-Command gcloud -ErrorAction Stop
} catch {
    Write-Host "Error: gcloud CLI is not installed. Please install it first." -ForegroundColor Red
    exit 1
}

# Get project ID
$PROJECT_ID = gcloud config get-value project 2>$null
if (-not $PROJECT_ID) {
    Write-Host "Error: No GCP project set. Run: gcloud config set project YOUR_PROJECT_ID" -ForegroundColor Red
    exit 1
}

Write-Host "Project ID: $PROJECT_ID" -ForegroundColor Yellow

# Check if user wants to use Secret Manager for Bedrock credentials
$useSecrets = Read-Host "Do you want to use Secret Manager for Bedrock credentials? (y/n)"
$USE_SECRETS = $useSecrets -eq "y" -or $useSecrets -eq "Y"

if ($USE_SECRETS) {
    Write-Host "Using Secret Manager for Bedrock credentials" -ForegroundColor Yellow
    
    # Check if secrets exist
    $teamIdExists = gcloud secrets describe bedrock-team-id --project=$PROJECT_ID 2>$null
    if (-not $teamIdExists) {
        Write-Host "Creating bedrock-team-id secret..." -ForegroundColor Yellow
        $TEAM_ID = Read-Host "Enter BEDROCK_TEAM_ID" -AsSecureString
        $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($TEAM_ID)
        $TEAM_ID_PLAIN = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
        $TEAM_ID_PLAIN | gcloud secrets create bedrock-team-id --data-file=- --project=$PROJECT_ID
    }
    
    $tokenExists = gcloud secrets describe bedrock-api-token --project=$PROJECT_ID 2>$null
    if (-not $tokenExists) {
        Write-Host "Creating bedrock-api-token secret..." -ForegroundColor Yellow
        $API_TOKEN = Read-Host "Enter BEDROCK_API_TOKEN" -AsSecureString
        $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($API_TOKEN)
        $API_TOKEN_PLAIN = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
        $API_TOKEN_PLAIN | gcloud secrets create bedrock-api-token --data-file=- --project=$PROJECT_ID
    }
} else {
    Write-Host "Using environment variables for Bedrock credentials" -ForegroundColor Yellow
    $BEDROCK_TEAM_ID = Read-Host "Enter BEDROCK_TEAM_ID"
    $BEDROCK_API_TOKEN = Read-Host "Enter BEDROCK_API_TOKEN" -AsSecureString
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($BEDROCK_API_TOKEN)
    $BEDROCK_API_TOKEN_PLAIN = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
}

# Build and deploy using Cloud Build
Write-Host "Starting Cloud Build..." -ForegroundColor Green

gcloud builds submit `
    --config=cloudbuild.bedrock.yaml `
    --project=$PROJECT_ID `
    --substitutions=_SERVICE_NAME=bias-analysis-tool-bedrock,_IMAGE_NAME=bias-analysis-tool-bedrock,_REGION=us-central1

# After deployment, set environment variables if not using secrets
if (-not $USE_SECRETS) {
    Write-Host "Setting Bedrock environment variables..." -ForegroundColor Yellow
    gcloud run services update bias-analysis-tool-bedrock `
        --region=us-central1 `
        --project=$PROJECT_ID `
        --set-env-vars="BEDROCK_TEAM_ID=$BEDROCK_TEAM_ID,BEDROCK_API_TOKEN=$BEDROCK_API_TOKEN_PLAIN,BEDROCK_API_ENDPOINT=https://ctwa92wg1b.execute-api.us-east-1.amazonaws.com/prod/invoke"
}

# Get the service URL
$SERVICE_URL = gcloud run services describe bias-analysis-tool-bedrock `
    --region=us-central1 `
    --project=$PROJECT_ID `
    --format='value(status.url)'

Write-Host "✓ Deployment complete!" -ForegroundColor Green
Write-Host "Service URL: $SERVICE_URL" -ForegroundColor Green
Write-Host "Note: Make sure to set Bedrock credentials via Secret Manager or environment variables" -ForegroundColor Yellow

