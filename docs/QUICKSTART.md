# Quick Start Guide

Get the Bias Analysis Tool running quickly for development or deployment.

## Prerequisites

- Python 3.11+
- Node.js 18+
- Google Cloud account with billing enabled
- gcloud CLI installed

## 1. Backend Setup (5 minutes)

### Local Development

```bash
# Clone and setup
cd art-of-biasing-LLM
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and set GOOGLE_CLOUD_PROJECT=your-project-id

# Authenticate with Google Cloud
gcloud auth application-default login

# Run server
cd backend
python api.py
```

### Docker (Alternative)

```bash
docker build -t bias-analysis-tool .
docker run -p 8080:8080 \
  -e GOOGLE_CLOUD_PROJECT=your-project-id \
  -e GCP_LOCATION=us-central1 \
  bias-analysis-tool
```

## 2. Frontend Setup (3 minutes)

```bash
cd frontend-react

# Install dependencies
npm install

# Create .env file
echo "REACT_APP_API_URL=http://localhost:5000/api" > .env

# Start development server
npm start
```

Frontend will open at http://localhost:3000

## 3. Google Cloud Setup (10 minutes)

### Enable APIs

```bash
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  aiplatform.googleapis.com
```

### Deploy to Cloud Run

```bash
# Deploy backend
gcloud run deploy bias-analysis-api \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GCP_LOCATION=us-central1 \
  --memory 2Gi \
  --cpu 2

# Get service URL
export API_URL=$(gcloud run services describe bias-analysis-api \
  --region us-central1 \
  --format 'value(status.url)')
```

### Deploy Frontend

```bash
cd frontend-react

# Update API URL
echo "REACT_APP_API_URL=$API_URL/api" > .env.production

# Build
npm run build

# Deploy to Firebase Hosting (easiest)
npm install -g firebase-tools
firebase login
firebase init hosting
# Select build directory, configure
firebase deploy
```

## 4. Test

### Test Backend

```bash
# Health check
curl $API_URL/api/health

# Test graph expansion
curl -X POST $API_URL/api/graph/expand \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What are the best programming languages?"}'
```

### Test Frontend

1. Open the deployed frontend URL
2. Enter a prompt: "What are the best programming languages?"
3. Click "Generate Bias Graph"
4. Explore the graph:
   - Click nodes to expand
   - Use evaluation button (Gemini 2.5 Flash)
   - View source definitions

## Troubleshooting

### "Vertex AI not available"
- Check `GOOGLE_CLOUD_PROJECT` is set
- Verify APIs are enabled
- Check billing is enabled

### "Model not found"
- Verify model names in `vertex_llm_service.py`
- Check region availability (us-central1 recommended)
- Ensure Vertex AI API is enabled

### CORS errors
- Check `REACT_APP_API_URL` matches backend URL
- Verify CORS is configured in Flask

### Frontend build fails
- Check Node.js version (18+)
- Clear node_modules and reinstall
- Check for syntax errors in React code

## Next Steps

- Customize bias detection patterns
- Add more bias types
- Configure rate limiting
- Set up monitoring
- Add authentication (if needed)

See [DEPLOYMENT_GCP.md](DEPLOYMENT_GCP.md) for detailed deployment options.

