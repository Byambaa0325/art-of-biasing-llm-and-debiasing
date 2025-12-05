# Docker Build Optimization

## Quick Start

### Default Build (No HEARTS - Fastest)
```bash
docker build -t bias-analysis-tool .
```

### With HEARTS ML Model (Slower, ~2GB larger)
```bash
docker build --build-arg ENABLE_HEARTS=true -t bias-analysis-tool .
```

## Optimizations Applied

### 1. Split Requirements
- **requirements-core.txt**: Essential packages only (~50MB)
- **requirements-ml.txt**: HEARTS ML dependencies (~2GB with PyTorch)
- ML dependencies only installed if `ENABLE_HEARTS=true`

### 2. Conditional HEARTS Model Download
- Model download skipped by default (saves ~30 minutes)
- Only downloads if `ENABLE_HEARTS=true`
- Model will download on first use if not in image

### 3. Optimized System Packages
- Uses `--no-install-recommends` to reduce size
- Cleans apt cache and temp files
- Removes unnecessary packages

### 4. Node.js Build Optimization
- Uses `npm ci` when package-lock.json exists (faster)
- Sets Node memory limit to prevent OOM
- Cleans npm cache after build
- Removes node_modules after build

### 5. Docker Layer Caching
- Requirements copied first for better caching
- Frontend build separated from dependencies
- Application code copied last

### 6. .dockerignore
- Excludes unnecessary files from build context
- Reduces build context size significantly

## Build Time Comparison

| Configuration | Estimated Build Time | Image Size |
|--------------|---------------------|------------|
| Without HEARTS | ~5-10 minutes | ~500MB |
| With HEARTS | ~30-45 minutes | ~2.5GB |

## Cloud Build Configuration

For Google Cloud Build, set the build arg:

```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '--build-arg'
      - 'ENABLE_HEARTS=false'
      - '-t'
      - 'gcr.io/$PROJECT_ID/bias-analysis-tool'
      - '.'
```

## Notes

- HEARTS model is optional - the app works without it
- If HEARTS is needed, it will download on first use (adds cold start time)
- For production with HEARTS, consider pre-baking the model with `ENABLE_HEARTS=true`


