# Quick Deployment Guide - Apply Fixes to Cloud Run

## Your Current Setup

- **Region:** `europe-west1` (from your URL)
- **Service Name:** `art-of-biasing-llm-and-debiasing-bedrock` (from your URL)
- **Project:** `lazy-jeopardy` (from your logs)

## Deploy the Fixes

### Option 1: Quick Deploy (Recommended)

Run this command from your project root:

```bash
gcloud builds submit \
  --config=cloudbuild.bedrock.yaml \
  --project=lazy-jeopardy \
  --region=europe-west1
```

If you need to deploy to a different service name, use:

```bash
gcloud builds submit --config=cloudbuild.bedrock.yaml
```

Then manually update the service:

```bash
gcloud run services update art-of-biasing-llm-and-debiasing-bedrock \
  --region=europe-west1 \
  --project=lazy-jeopardy \
  --image=gcr.io/lazy-jeopardy/bias-analysis-tool-bedrock:latest
```

### Option 2: Manual Docker Build and Deploy

If you prefer more control:

```bash
# 1. Build the Docker image
docker build -t gcr.io/lazy-jeopardy/bias-analysis-tool-bedrock:latest .

# 2. Push to Google Container Registry
docker push gcr.io/lazy-jeopardy/bias-analysis-tool-bedrock:latest

# 3. Deploy to Cloud Run
gcloud run deploy art-of-biasing-llm-and-debiasing-bedrock \
  --image gcr.io/lazy-jeopardy/bias-analysis-tool-bedrock:latest \
  --region europe-west1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --project lazy-jeopardy
```

### Option 3: PowerShell Script (Windows)

Since you're on Windows, here's a PowerShell one-liner:

```powershell
gcloud builds submit --config=cloudbuild.bedrock.yaml --project=lazy-jeopardy
```

## What Will Be Deployed

✅ **Dockerfile** - Now includes `data/` directory  
✅ **Backend** - Ollama models removed, only Bedrock models  
✅ **Frontend** - Badge readability fixed, new placeholder text, Llama 3.1 70B as default

## Expected Build Time

- **With HEARTS model:** ~20-30 minutes (default)
- **Without HEARTS:** ~10-15 minutes

The build is set to include HEARTS by default (`_ENABLE_HEARTS: 'true'` in cloudbuild.bedrock.yaml).

## After Deployment

### 1. Verify Endpoints Work

Open these URLs in your browser:

```
https://art-of-biasing-llm-and-debiasing-bedrock-1067269232886.europe-west1.run.app/api/models/available

https://art-of-biasing-llm-and-debiasing-bedrock-1067269232886.europe-west1.run.app/api/dataset/stats

https://art-of-biasing-llm-and-debiasing-bedrock-1067269232886.europe-west1.run.app/api/dataset/entries?limit=5
```

**Expected Response:**
- ✅ HTTP 200 OK (not 500)
- ✅ JSON data returned
- ✅ Only Bedrock models listed (no Ollama)

### 2. Test Frontend

Visit your frontend:
```
https://art-of-biasing-llm-and-debiasing-bedrock-1067269232886.europe-west1.run.app/
```

Check:
- ✅ Placeholder text shows incomplete sentence examples
- ✅ Model dropdown only shows Bedrock models
- ✅ Default model is "Llama 3.1 70B"
- ✅ "Explore Dataset" tab works
- ✅ Badges are readable (dark text on light background)

## Troubleshooting

### Build Fails

If the build fails, check:

```bash
# View recent build logs
gcloud builds list --project=lazy-jeopardy --limit=5

# View specific build
gcloud builds log <BUILD_ID> --project=lazy-jeopardy
```

### Deployment Succeeds but Endpoints Still Return 500

This might mean:
1. Old container is still cached - wait 1-2 minutes and try again
2. Data files are missing - check build logs for "COPY data/ ./data/" step
3. Import errors - check Cloud Run logs:
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=art-of-biasing-llm-and-debiasing-bedrock" --project=lazy-jeopardy --limit=50
   ```

### Need to Roll Back

If something goes wrong:

```bash
# List revisions
gcloud run revisions list --service=art-of-biasing-llm-and-debiasing-bedrock --region=europe-west1 --project=lazy-jeopardy

# Roll back to previous revision
gcloud run services update-traffic art-of-biasing-llm-and-debiasing-bedrock \
  --region=europe-west1 \
  --project=lazy-jeopardy \
  --to-revisions=<PREVIOUS_REVISION>=100
```

## Quick Commands Reference

```bash
# Start deployment
gcloud builds submit --config=cloudbuild.bedrock.yaml --project=lazy-jeopardy

# Check build status
gcloud builds list --project=lazy-jeopardy --limit=5

# View service details
gcloud run services describe art-of-biasing-llm-and-debiasing-bedrock --region=europe-west1 --project=lazy-jeopardy

# View logs
gcloud logging read "resource.type=cloud_run_revision" --project=lazy-jeopardy --limit=20

# Test endpoint
curl "https://art-of-biasing-llm-and-debiasing-bedrock-1067269232886.europe-west1.run.app/api/models/available"
```

---

## Ready to Deploy?

**Run this command now:**

```bash
gcloud builds submit --config=cloudbuild.bedrock.yaml --project=lazy-jeopardy
```

This will:
1. Build new Docker image with data files included
2. Deploy to Cloud Run
3. All fixes will be live in ~20-30 minutes

---

**Created:** December 11, 2025  
**Status:** Ready to deploy ✅
