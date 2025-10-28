# Multi-stage Dockerfile for BuiltEnvironment.ai Backend
# Optimized for both local development and Dokploy production deployment

# ============================================================================
# Base Stage - Common dependencies
# ============================================================================
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies (including OCR tools)
RUN apt-get update && apt-get install -y \
    curl \
    git \
    gcc \
    build-essential \
    libpq-dev \
    postgresql-client \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first (for layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ============================================================================
# Development Stage
# ============================================================================
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    pytest-cov \
    black \
    flake8 \
    mypy \
    ipython \
    watchfiles

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p /app/uploads /app/data/chroma && chmod 777 /app/uploads

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ============================================================================
# Production Stage (for Dokploy deployment)
# ============================================================================
FROM base as production

# Set production environment
ENV ENVIRONMENT=production \
    DEBUG=false

# Install Gunicorn for production
RUN pip install --no-cache-dir gunicorn

# Copy application code only (no dev tools)
COPY . .

# Create data directories with restricted permissions
RUN mkdir -p /app/uploads /app/data/chroma && chmod 755 /app/uploads

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production command with Gunicorn + Uvicorn workers
CMD ["gunicorn", "app.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "info", \
     "--timeout", "120", \
     "--graceful-timeout", "30", \
     "--keep-alive", "5"]
