# Google Cloud Run Deployment Guide

This guide covers deploying the Bias Analysis Tool to Google Cloud Run using Vertex AI (Llama 3.3) and Gemini 2.5 Flash.

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed and configured
3. **Docker** installed (for local testing)
4. **Node.js** and npm (for React frontend)

## Setup

### 1. Enable Required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  aiplatform.googleapis.com \
  artifactregistry.googleapis.com
```

### 2. Set Project ID

```bash
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID
```

### 3. Authenticate

```bash
gcloud auth login
gcloud auth application-default login
```

## Backend Deployment

### 1. Build and Deploy to Cloud Run

```bash
# Build and deploy
gcloud run deploy bias-analysis-api \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GCP_LOCATION=us-central1 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10
```

### 2. Or Use Cloud Build

```bash
# Submit build
gcloud builds submit --config cloudbuild.yaml

# The build will automatically deploy to Cloud Run
```

### 3. Get Service URL

```bash
gcloud run services describe bias-analysis-api --region us-central1 --format 'value(status.url)'
```

## Frontend Deployment

### 1. Build React App

```bash
cd frontend-react
npm install
REACT_APP_API_URL=https://your-cloud-run-url/api npm run build
```

### 2. Deploy to Cloud Storage + Cloud CDN

```bash
# Create bucket
gsutil mb gs://your-project-bias-analysis-frontend

# Upload build
gsutil -m cp -r build/* gs://your-project-bias-analysis-frontend/

# Make public
gsutil iam ch allUsers:objectViewer gs://your-project-bias-analysis-frontend

# Set up Cloud CDN (optional but recommended)
```

### 3. Or Deploy to Firebase Hosting

```bash
npm install -g firebase-tools
firebase login
firebase init hosting
# Select your project and set public directory to 'build'
firebase deploy
```

## Environment Variables

Set in Cloud Run:

```bash
gcloud run services update bias-analysis-api \
  --region us-central1 \
  --update-env-vars \
    GOOGLE_CLOUD_PROJECT=$PROJECT_ID,\
    GCP_LOCATION=us-central1
```

## Vertex AI Configuration

### 1. Enable Vertex AI API

```bash
gcloud services enable aiplatform.googleapis.com
```

### 2. Set Up Service Account

```bash
# Create service account
gcloud iam service-accounts create bias-analysis-sa \
  --display-name="Bias Analysis Service Account"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:bias-analysis-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

### 3. Models Available

- **Llama 3.3**: `llama-3.3-70b-instruct` (for generation)
- **Gemini 2.5 Flash**: `gemini-2.0-flash-exp` (for evaluation)

## Cost Estimation

### Vertex AI Pricing (as of 2024)

- **Llama 3.3**: ~$0.0005 per 1K input tokens, ~$0.0015 per 1K output tokens
- **Gemini 2.5 Flash**: ~$0.075 per 1M input tokens, ~$0.30 per 1M output tokens

### Cloud Run Pricing

- **CPU**: $0.00002400 per vCPU-second
- **Memory**: $0.00000250 per GiB-second
- **Requests**: $0.40 per million requests

### Estimated Monthly Cost

For moderate usage (1000 users/month):
- Vertex AI: ~$10-20
- Cloud Run: ~$5-10
- **Total: ~$15-30/month**

## Testing

### Local Testing with Docker

```bash
# Build image
docker build -t bias-analysis-tool .

# Run locally
docker run -p 8080:8080 \
  -e GOOGLE_CLOUD_PROJECT=$PROJECT_ID \
  -e GCP_LOCATION=us-central1 \
  bias-analysis-tool
```

### Test API

```bash
# Health check
curl https://your-cloud-run-url/api/health

# Test graph expansion
curl -X POST https://your-cloud-run-url/api/graph/expand \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What are the best programming languages?"}'
```

## Monitoring

### 1. Cloud Run Logs

```bash
gcloud run services logs read bias-analysis-api --region us-central1
```

### 2. Set Up Alerts

```bash
# Create alert policy for errors
gcloud alpha monitoring policies create \
  --notification-channels=YOUR_CHANNEL_ID \
  --display-name="Bias Analysis API Errors" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05
```

## Troubleshooting

### Common Issues

1. **"Vertex AI not available"**
   - Check API is enabled
   - Verify service account permissions
   - Check project ID is set correctly

2. **"Model not found"**
   - Verify model names are correct
   - Check region availability
   - Ensure billing is enabled

3. **CORS errors**
   - Verify CORS is configured in Flask
   - Check frontend API URL is correct

4. **Timeout errors**
   - Increase Cloud Run timeout (max 300s)
   - Optimize model calls
   - Use async processing for long operations

## Scaling

### Auto-scaling Configuration

Cloud Run automatically scales based on:
- Request rate
- CPU utilization
- Memory usage

Configure limits:

```bash
gcloud run services update bias-analysis-api \
  --region us-central1 \
  --min-instances 0 \
  --max-instances 10 \
  --concurrency 80 \
  --cpu-throttling
```

## Security

1. **API Keys**: Never commit API keys
2. **CORS**: Configure for specific domains in production
3. **Authentication**: Consider adding authentication for production
4. **Rate Limiting**: Implement rate limiting to prevent abuse

## Next Steps

1. Set up custom domain
2. Configure Cloud CDN for frontend
3. Set up monitoring and alerts
4. Implement rate limiting
5. Add authentication if needed

