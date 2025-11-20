# Dockerfile for Google Cloud Run deployment
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY .env* ./

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=backend.api
ENV FLASK_ENV=production

# Expose port (Cloud Run uses PORT env var)
EXPOSE 8080

# Use gunicorn for production
RUN pip install gunicorn

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Run the application
# Cloud Run sets PORT environment variable
CMD exec gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 2 --threads 2 --timeout 300 backend.api:app

