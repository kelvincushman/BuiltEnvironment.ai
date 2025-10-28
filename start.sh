#!/bin/bash

# BuiltEnvironment.ai Quick Start Script
# This script sets up and launches your entire development environment

set -e  # Exit on error

echo "🏗️  BuiltEnvironment.ai - Quick Start"
echo "===================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "   Please start Docker Desktop and try again"
    exit 1
fi

echo "✅ Docker is running"

# Check if .env exists
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your API keys:"
    echo "   - ANTHROPIC_API_KEY=sk-ant-xxxxx"
    echo "   - OPENAI_API_KEY=sk-xxxxx"
    echo ""
    echo "Press Enter after you've added your API keys..."
    read -r
fi

# Start Docker Compose
echo "🚀 Starting all services..."
echo "   - PostgreSQL (with TimescaleDB)"
echo "   - Redis"
echo "   - ChromaDB"
echo "   - Langflow"
echo "   - Backend API"
echo ""

docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy (this may take 60-90 seconds)..."
sleep 5

# Wait for services with timeout
TIMEOUT=120
ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
    HEALTHY=$(docker-compose ps | grep -c "healthy" || true)
    TOTAL=$(docker-compose ps | grep -c "Up" || true)
    
    if [ $HEALTHY -ge 4 ]; then
        echo "✅ All services are healthy!"
        break
    fi
    
    echo "   Waiting... ($HEALTHY/$TOTAL services healthy)"
    sleep 10
    ELAPSED=$((ELAPSED + 10))
done

echo ""
echo "✅ BuiltEnvironment.ai is running!"
echo "===================================="
echo ""
echo "📍 Access your services:"
echo "   🌐 Backend API:    http://localhost:8001"
echo "   📚 API Docs:       http://localhost:8001/docs"
echo "   🤖 Langflow UI:    http://localhost:7860"
echo "   🗄️  ChromaDB:       http://localhost:8000"
echo "   🔍 PostgreSQL:     localhost:5432"
echo "   ⚡ Redis:          localhost:6379"
echo ""
echo "🔑 Langflow Login:"
echo "   Email:    admin@builtenvironment.ai"
echo "   Password: changeme123"
echo ""
echo "📖 Useful commands:"
echo "   View logs:     docker-compose logs -f backend"
echo "   Stop all:      docker-compose down"
echo "   Restart:       docker-compose restart backend"
echo "   Clean restart: docker-compose down -v && ./start.sh"
echo ""
echo "🎯 Next steps:"
echo "   1. Open http://localhost:8001/docs to explore the API"
echo "   2. Open http://localhost:7860 to build AI workflows in Langflow"
echo "   3. Check the logs: docker-compose logs -f"
echo ""
echo "Happy building! 🚀"
