# Environment Variables Setup Guide

This project uses `.env` files to manage environment variables for both backend and frontend.

## Backend Environment Variables

### Required Variables

Create a `.env` file in the project root with:

```env
# Google Cloud Configuration (Required for Vertex AI)
GOOGLE_CLOUD_PROJECT=your-project-id
GCP_LOCATION=us-central1

# Vertex AI Model Configuration
LLAMA_MODEL=llama-3.3-70b-instruct
GEMINI_MODEL=gemini-2.0-flash-exp
```

### Optional Variables

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000

# Optional: Gemini API Key (if not using Vertex AI endpoint)
# GEMINI_API_KEY=your-gemini-api-key

# Optional: Rate Limiting
# RATE_LIMIT_PER_MINUTE=10
```

## Frontend Environment Variables

Create a `.env` file in `frontend-react/` directory:

```env
# Backend API URL
REACT_APP_API_URL=http://localhost:5000/api
```

For production, set to your Cloud Run URL:

```env
REACT_APP_API_URL=https://your-cloud-run-url/api
```

## Quick Setup

### Automatic Setup

**Windows:**
```bash
setup_env.bat
```

**Linux/Mac:**
```bash
chmod +x setup_env.sh
./setup_env.sh
```

### Manual Setup

1. **Copy example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit .env file:**
   ```bash
   # Use your preferred editor
   nano .env
   # or
   notepad .env
   ```

3. **Set your project ID:**
   ```env
   GOOGLE_CLOUD_PROJECT=your-actual-project-id
   ```

## Environment Variables Reference

### Backend (.env)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_CLOUD_PROJECT` | Yes | - | Google Cloud project ID |
| `GCP_PROJECT_ID` | Yes* | - | Alternative name for project ID |
| `GCP_LOCATION` | No | `us-central1` | GCP region for Vertex AI |
| `LLAMA_MODEL` | No | `llama-3.3-70b-instruct` | Llama model name |
| `GEMINI_MODEL` | No | `gemini-2.0-flash-exp` | Gemini model name |
| `FLASK_ENV` | No | `development` | Flask environment |
| `FLASK_DEBUG` | No | `True` | Enable Flask debug mode |
| `PORT` | No | `5000` | Server port (Cloud Run uses `PORT` env var) |
| `GEMINI_API_KEY` | No | - | Gemini API key (if not using Vertex AI) |

*Either `GOOGLE_CLOUD_PROJECT` or `GCP_PROJECT_ID` must be set.

### Frontend (frontend-react/.env)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `REACT_APP_API_URL` | No | `http://localhost:5000/api` | Backend API URL |

**Note:** React environment variables must start with `REACT_APP_` to be accessible in the browser.

## Loading Environment Variables

### Backend

The backend automatically loads `.env` file using `python-dotenv`:

- `backend/api.py` - Loads on import
- `backend/vertex_llm_service.py` - Loads on import

No additional code needed - just create the `.env` file!

### Frontend

React automatically loads `.env` files from `frontend-react/` directory:

- Variables must start with `REACT_APP_`
- Restart dev server after changing `.env`
- Rebuild for production after changing `.env`

## Cloud Run Deployment

For Cloud Run, set environment variables in the deployment command:

```bash
gcloud run deploy bias-analysis-api \
  --set-env-vars \
    GOOGLE_CLOUD_PROJECT=$PROJECT_ID,\
    GCP_LOCATION=us-central1,\
    LLAMA_MODEL=llama-3.3-70b-instruct,\
    GEMINI_MODEL=gemini-2.0-flash-exp
```

Or use Secret Manager for sensitive values:

```bash
# Create secret
echo -n "your-project-id" | gcloud secrets create google-cloud-project --data-file=-

# Reference in deployment
gcloud run deploy bias-analysis-api \
  --update-secrets GOOGLE_CLOUD_PROJECT=google-cloud-project:latest
```

## Verification

### Check Backend Environment Variables

```python
# In Python shell
from dotenv import load_dotenv
import os
load_dotenv()
print("Project ID:", os.getenv("GOOGLE_CLOUD_PROJECT"))
print("Location:", os.getenv("GCP_LOCATION"))
```

### Check Frontend Environment Variables

```javascript
// In browser console or React component
console.log("API URL:", process.env.REACT_APP_API_URL);
```

## Troubleshooting

### "GOOGLE_CLOUD_PROJECT not set"

1. Check `.env` file exists in project root
2. Verify variable name is correct (no typos)
3. Restart the server after changing `.env`
4. Check file is not in `.gitignore` (should be ignored, but file should exist)

### "Environment variable not loading"

1. Make sure `python-dotenv` is installed: `pip install python-dotenv`
2. Check `.env` file is in the correct location (project root for backend)
3. Verify no syntax errors in `.env` file
4. Restart the application

### Frontend variables not working

1. Variables must start with `REACT_APP_`
2. Restart dev server: `npm start`
3. Rebuild for production: `npm run build`
4. Check `.env` file is in `frontend-react/` directory

## Security Notes

- **Never commit `.env` files** - They're in `.gitignore`
- **Use `.env.example`** for documentation
- **Use Secret Manager** for production secrets
- **Rotate API keys** regularly
- **Don't share `.env` files** publicly

## Example .env Files

### Development (.env)

```env
GOOGLE_CLOUD_PROJECT=my-dev-project
GCP_LOCATION=us-central1
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
```

### Production (Cloud Run)

Set via `gcloud run deploy --set-env-vars` or Cloud Console.

