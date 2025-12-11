# Dockerfile for Google Cloud Run deployment (Backend + Frontend)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (including Node.js for React build)
# Use --no-install-recommends to reduce package size
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Define build argument for optional HEARTS ML dependencies
# Set to true to enable HEARTS model (adds ~2GB and significant build time)
ARG ENABLE_HEARTS=true

# Copy requirements first for better caching
# Install core dependencies first (faster, better caching)
COPY requirements-core.txt .

# Install core Python dependencies
RUN pip install --no-cache-dir -r requirements-core.txt

# Conditionally install ML dependencies (HEARTS) only if enabled
# This saves significant build time if HEARTS is not needed
COPY requirements-ml.txt .
RUN if [ "$ENABLE_HEARTS" = "true" ]; then \
        pip install --no-cache-dir -r requirements-ml.txt; \
    else \
        echo "Skipping HEARTS ML dependencies (set ENABLE_HEARTS=true to enable)"; \
    fi

# Build React frontend (needs dev dependencies for build)
# Copy package files - npm install will regenerate package-lock.json if needed
COPY frontend-react/package.json ./frontend-react/
WORKDIR /app/frontend-react
# Install only production dependencies first, then dev dependencies for build
# Use npm ci for faster, reliable installs if package-lock.json exists
RUN if [ -f package-lock.json ]; then \
        npm ci --include=dev; \
    else \
        npm install --include=dev; \
    fi && \
    npm cache clean --force
WORKDIR /app

# Copy frontend source and build
COPY frontend-react/ ./frontend-react/
WORKDIR /app/frontend-react
# Build React app for production (outputs to build/ directory)
# Set API URL to relative path since frontend and backend are on same domain
# Use --max_old_space_size to prevent OOM during build
RUN NODE_OPTIONS="--max_old_space_size=2048" REACT_APP_API_URL=/api npm run build || \
    (echo "Warning: React build failed, continuing without frontend" && mkdir -p build)
# Clean up node_modules and npm cache to reduce image size
RUN rm -rf node_modules \
    && npm cache clean --force \
    && rm -rf ~/.npm
WORKDIR /app

# Pre-download HEARTS model during build (only if HEARTS is enabled)
# This prevents downloading on every Cloud Run cold start
# Skip this step if HEARTS is disabled to save build time
RUN if [ "$ENABLE_HEARTS" = "true" ]; then \
        mkdir -p /app/.cache/huggingface && \
        python -c "import os; os.environ['TRANSFORMERS_CACHE'] = '/app/.cache/huggingface'; from transformers import AutoTokenizer, AutoModelForSequenceClassification; tokenizer = AutoTokenizer.from_pretrained('holistic-ai/bias_classifier_albertv2'); model = AutoModelForSequenceClassification.from_pretrained('holistic-ai/bias_classifier_albertv2'); print('✓ HEARTS model downloaded')" || \
        echo "Warning: HEARTS model download failed, will download on first use"; \
    else \
        echo "Skipping HEARTS model download (set ENABLE_HEARTS=true to enable)"; \
        mkdir -p /app/.cache/huggingface; \
    fi

# Copy application code
COPY backend/ ./backend/
COPY data/ ./data/
COPY .env* ./

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV FLASK_APP=backend.api
ENV FLASK_ENV=production
# Use local cached model (pre-downloaded in image)
ENV HEARTS_LOCAL_FILES_ONLY=true
ENV TRANSFORMERS_CACHE=/app/.cache/huggingface

# Expose port (Cloud Run uses PORT env var)
EXPOSE 8080

# Gunicorn is already in requirements-core.txt, no need to install again

# Create non-root user for security and ensure cache and build are accessible
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app/.cache && \
    chmod -R 755 /app/frontend-react/build 2>/dev/null || true
USER appuser

# Run the application
# Cloud Run sets PORT environment variable
# Use 1 worker to reduce memory footprint (HEARTS model is ~500MB per worker)
# Increase threads to handle concurrent requests within single worker
CMD exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 4 --timeout 300 --max-requests 1000 --max-requests-jitter 50 backend.api:app

