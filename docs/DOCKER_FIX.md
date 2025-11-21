# Docker/Gunicorn Import Fix

## Problem

When running with gunicorn in Docker/Cloud Run, the imports failed with:
```
ModuleNotFoundError: No module named 'bias_detection'
```

## Root Cause

Gunicorn runs the app as `backend.api:app`, which means:
- The working directory is `/app`
- Python imports `backend.api` as a module
- Within `backend/api.py`, imports need to be relative to the `backend` package

## Solution

### 1. Updated Imports in `backend/api.py`

Changed from absolute imports to relative imports with fallback:

```python
# Try relative imports first (works when backend is a package)
try:
    from .bias_detection import BiasDetector
    from .bias_injection import BiasInjector
    from .debiasing import PromptDebiaser
except ImportError:
    # Fallback to absolute imports (works in local development)
    from bias_detection import BiasDetector
    from bias_injection import BiasInjector
    from debiasing import PromptDebiaser
```

### 2. Updated Dockerfile

Added `PYTHONPATH=/app` to ensure Python can find modules:

```dockerfile
ENV PYTHONPATH=/app
```

### 3. Created `backend/__init__.py`

Ensures `backend` is recognized as a Python package.

## Testing

### Local Development
```bash
cd backend
python api.py
```
Uses absolute imports (fallback).

### Docker/Gunicorn
```bash
docker build -t bias-analysis-tool .
docker run -p 8080:8080 bias-analysis-tool
```
Uses relative imports (primary).

## Verification

The imports now work in both scenarios:
- ✅ Local development (absolute imports)
- ✅ Docker/Gunicorn (relative imports)
- ✅ Cloud Run deployment


