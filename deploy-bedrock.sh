#!/bin/bash
# Deployment script for Bedrock Integration Branch
# This script deploys the bedrock-api-integration branch to a separate Cloud Run service

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Deploying Bedrock Integration Branch to Cloud Run${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: No GCP project set. Run: gcloud config set project YOUR_PROJECT_ID${NC}"
    exit 1
fi

echo -e "${YELLOW}Project ID: ${PROJECT_ID}${NC}"

# Check if user wants to use Secret Manager for Bedrock credentials
read -p "Do you want to use Secret Manager for Bedrock credentials? (y/n) " -n 1 -r
echo
USE_SECRETS=0
if [[ $REPLY =~ ^[Yy]$ ]]; then
    USE_SECRETS=1
    echo -e "${YELLOW}Using Secret Manager for Bedrock credentials${NC}"
    
    # Check if secrets exist
    if ! gcloud secrets describe bedrock-team-id --project=$PROJECT_ID &>/dev/null; then
        echo -e "${YELLOW}Creating bedrock-team-id secret...${NC}"
        read -sp "Enter BEDROCK_TEAM_ID: " TEAM_ID
        echo
        echo -n "$TEAM_ID" | gcloud secrets create bedrock-team-id --data-file=- --project=$PROJECT_ID
    fi
    
    if ! gcloud secrets describe bedrock-api-token --project=$PROJECT_ID &>/dev/null; then
        echo -e "${YELLOW}Creating bedrock-api-token secret...${NC}"
        read -sp "Enter BEDROCK_API_TOKEN: " API_TOKEN
        echo
        echo -n "$API_TOKEN" | gcloud secrets create bedrock-api-token --data-file=- --project=$PROJECT_ID
    fi
else
    echo -e "${YELLOW}Using environment variables for Bedrock credentials${NC}"
    read -sp "Enter BEDROCK_TEAM_ID: " BEDROCK_TEAM_ID
    echo
    read -sp "Enter BEDROCK_API_TOKEN: " BEDROCK_API_TOKEN
    echo
fi

# Build and deploy using Cloud Build
echo -e "${GREEN}Starting Cloud Build...${NC}"

if [ $USE_SECRETS -eq 1 ]; then
    # Deploy with secrets
    gcloud builds submit \
        --config=cloudbuild.bedrock.yaml \
        --project=$PROJECT_ID \
        --substitutions=_SERVICE_NAME=bias-analysis-tool-bedrock,_IMAGE_NAME=bias-analysis-tool-bedrock,_REGION=us-central1
else
    # Deploy with environment variables
    gcloud builds submit \
        --config=cloudbuild.bedrock.yaml \
        --project=$PROJECT_ID \
        --substitutions=_SERVICE_NAME=bias-analysis-tool-bedrock,_IMAGE_NAME=bias-analysis-tool-bedrock,_REGION=us-central1
fi

# After deployment, set environment variables if not using secrets
if [ $USE_SECRETS -eq 0 ]; then
    echo -e "${YELLOW}Setting Bedrock environment variables...${NC}"
    gcloud run services update bias-analysis-tool-bedrock \
        --region=us-central1 \
        --project=$PROJECT_ID \
        --set-env-vars="BEDROCK_TEAM_ID=${BEDROCK_TEAM_ID},BEDROCK_API_TOKEN=${BEDROCK_API_TOKEN},BEDROCK_API_ENDPOINT=https://ctwa92wg1b.execute-api.us-east-1.amazonaws.com/prod/invoke"
fi

# Get the service URL
SERVICE_URL=$(gcloud run services describe bias-analysis-tool-bedrock \
    --region=us-central1 \
    --project=$PROJECT_ID \
    --format='value(status.url)')

echo -e "${GREEN}✓ Deployment complete!${NC}"
echo -e "${GREEN}Service URL: ${SERVICE_URL}${NC}"
echo -e "${YELLOW}Note: Make sure to set Bedrock credentials via Secret Manager or environment variables${NC}"


