# Vertex AI Setup Guide

This guide explains how to configure Vertex AI for Llama 3.3 and Gemini 2.5 Flash.

## API Format

### Llama 3.3 REST API

The service uses the Vertex AI REST API endpoint format:

```
POST https://{REGION}-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/{REGION}/endpoints/openapi/chat/completions
```

**Model Name**: `meta/llama-3.3-70b-instruct-maas`

**Request Format**:
```json
{
  "model": "meta/llama-3.3-70b-instruct-maas",
  "stream": false,
  "messages": [
    {"role": "system", "content": "System prompt"},
    {"role": "user", "content": "User prompt"}
  ],
  "temperature": 0.7,
  "max_tokens": 1000
}
```

**Authentication**: Bearer token from `gcloud auth print-access-token` or Application Default Credentials

### Gemini 2.5 Flash

Uses Vertex AI SDK or REST API for evaluation.

## Environment Variables

Set in `.env` file:

```env
GOOGLE_CLOUD_PROJECT=your-project-id
GCP_LOCATION=us-central1
LLAMA_MODEL=meta/llama-3.3-70b-instruct-maas
GEMINI_MODEL=gemini-2.0-flash-exp
```

## Authentication

### Local Development

```bash
# Authenticate with gcloud
gcloud auth login
gcloud auth application-default login

# Set project
gcloud config set project YOUR_PROJECT_ID
```

### Cloud Run (Automatic)

Cloud Run automatically provides Application Default Credentials. No additional setup needed if:
- Service account has `roles/aiplatform.user` permission
- Project has Vertex AI API enabled

## Testing

### Test Llama 3.3 API

```bash
# Set variables
export ENDPOINT=us-central1-aiplatform.googleapis.com
export REGION=us-central1
export PROJECT_ID="your-project-id"

# Test request
curl \
  -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  "https://${ENDPOINT}/v1/projects/${PROJECT_ID}/locations/${REGION}/endpoints/openapi/chat/completions" \
  -d '{
    "model":"meta/llama-3.3-70b-instruct-maas",
    "stream":false,
    "messages":[{"role": "user", "content": "Hello, how are you?"}]
  }'
```

### Test in Python

```python
from backend.vertex_llm_service import get_vertex_llm_service

service = get_vertex_llm_service()
response = service.generate("What is Python?")
print(response)
```

## Troubleshooting

### "Failed to get access token"

**Local:**
```bash
gcloud auth application-default login
```

**Cloud Run:**
- Ensure service account has proper IAM roles
- Check Vertex AI API is enabled

### "Model not found"

- Verify model name: `meta/llama-3.3-70b-instruct-maas`
- Check region availability (us-central1 recommended)
- Ensure billing is enabled

### "Permission denied"

Grant service account permissions:
```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SERVICE_ACCOUNT@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

## Cost

- **Llama 3.3**: ~$0.0005 per 1K input tokens, ~$0.0015 per 1K output tokens
- **Gemini 2.5 Flash**: ~$0.075 per 1M input tokens, ~$0.30 per 1M output tokens

Estimated monthly cost for moderate usage: $15-30

