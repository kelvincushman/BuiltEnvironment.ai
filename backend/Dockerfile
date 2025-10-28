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

# Make startup script executable
RUN chmod +x /app/scripts/startup.sh

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Use startup script (runs migrations then starts app)
CMD ["/app/scripts/startup.sh"]

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

# Make startup script executable
RUN chmod +x /app/scripts/startup.sh

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

# Use startup script (runs migrations then starts app)
CMD ["/app/scripts/startup.sh"]
