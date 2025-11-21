# Dockerfile for Google Cloud Run deployment (Backend + Frontend)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (including Node.js for React build)
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Build React frontend (needs dev dependencies for build)
# Copy package files - npm install will regenerate package-lock.json if needed
COPY frontend-react/package.json ./frontend-react/
WORKDIR /app/frontend-react
# Install all dependencies (including dev dependencies needed for build)
# Delete package-lock.json if exists and do fresh install to avoid conflicts
RUN rm -f package-lock.json && \
    npm install && \
    npm cache clean --force
WORKDIR /app

# Copy frontend source and build
COPY frontend-react/ ./frontend-react/
WORKDIR /app/frontend-react
# Build React app for production (outputs to build/ directory)
# Set API URL to relative path since frontend and backend are on same domain
RUN REACT_APP_API_URL=/api npm run build || (echo "Warning: React build failed, continuing without frontend" && mkdir -p build)
# Clean up node_modules to reduce image size (build artifacts remain in build/)
RUN rm -rf node_modules
WORKDIR /app

# Pre-download HEARTS model during build (bakes into image)
# This prevents downloading on every Cloud Run cold start
RUN mkdir -p /app/.cache/huggingface && \
    python -c "import os; os.environ['TRANSFORMERS_CACHE'] = '/app/.cache/huggingface'; from transformers import AutoTokenizer, AutoModelForSequenceClassification; tokenizer = AutoTokenizer.from_pretrained('holistic-ai/bias_classifier_albertv2'); model = AutoModelForSequenceClassification.from_pretrained('holistic-ai/bias_classifier_albertv2'); print('✓ HEARTS model downloaded')" || \
    echo "Warning: HEARTS model download failed, will download on first use"

# Copy application code
COPY backend/ ./backend/
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

# Use gunicorn for production
RUN pip install gunicorn

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

