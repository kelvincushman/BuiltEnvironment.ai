#!/bin/bash
# Startup script for BuiltEnvironment.ai backend
# Runs database migrations and starts the application

set -e  # Exit on error

echo "🚀 Starting BuiltEnvironment.ai Backend..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
max_retries=30
retry_count=0

while [ $retry_count -lt $max_retries ]; do
    if pg_isready -h ${POSTGRES_HOST:-postgres} -p ${POSTGRES_PORT:-5432} -U ${POSTGRES_USER:-postgres} > /dev/null 2>&1; then
        echo "✅ PostgreSQL is ready!"
        break
    fi

    retry_count=$((retry_count + 1))
    echo "   Waiting for PostgreSQL... (${retry_count}/${max_retries})"
    sleep 2
done

if [ $retry_count -eq $max_retries ]; then
    echo "❌ Failed to connect to PostgreSQL after ${max_retries} attempts"
    exit 1
fi

# Run database migrations
echo "🔄 Running database migrations..."
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Database migrations completed successfully"
else
    echo "❌ Database migrations failed"
    exit 1
fi

# Start the application
echo "🚀 Starting application..."

# Check if we're in development or production mode
if [ "${ENVIRONMENT}" = "production" ]; then
    echo "📦 Starting production server with Gunicorn..."
    exec gunicorn app.main:app \
        --workers 4 \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:8000 \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        --timeout 120 \
        --graceful-timeout 30 \
        --keep-alive 5
else
    echo "🔧 Starting development server with Uvicorn..."
    exec uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload
fi
