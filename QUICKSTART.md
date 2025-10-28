# Quick Start Guide - BuiltEnvironment.ai

Get your entire development environment running in **2 minutes**! 🚀

## Prerequisites

- **Docker Desktop** installed and running
- **Git** installed
- **API Keys** (get these first):
  - [Anthropic Claude API Key](https://console.anthropic.com/)
  - [OpenAI API Key](https://platform.openai.com/)

---

## 🚀 Quick Start (2 minutes)

### Option 1: Automated Script (Recommended)

```bash
# Clone the repository
git clone https://github.com/kelvincushman/BuiltEnvironment.ai.git
cd BuiltEnvironment.ai

# Run the quick start script
./start.sh
```

The script will:
1. Check Docker is running
2. Create `.env` file from template
3. Prompt you to add your API keys
4. Start all services
5. Wait for health checks
6. Show you access URLs

### Option 2: Manual Setup

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env and add your API keys
nano .env  # or use your favorite editor

# Required: Add these keys
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx

# 3. Start all services
docker-compose up -d

# 4. Check logs
docker-compose logs -f backend
```

---

## 📍 Access Your Services

Once running, access:

| Service | URL | Description |
|---------|-----|-------------|
| **Backend API** | http://localhost:8001 | FastAPI application |
| **API Docs** | http://localhost:8001/docs | Interactive API documentation |
| **Langflow** | http://localhost:7860 | Visual AI workflow builder |
| **ChromaDB** | http://localhost:8000 | Vector database |
| **PostgreSQL** | localhost:5432 | Main database |
| **Redis** | localhost:6379 | Cache |

### Langflow Login Credentials

```
Email:    admin@builtenvironment.ai
Password: changeme123
```

---

## 🎯 What's Running?

Your full stack includes:

1. **PostgreSQL 15** with TimescaleDB - Main database + Langflow database
2. **Redis** - Caching and session storage
3. **ChromaDB** - Vector database for RAG
4. **Langflow** - Visual AI workflow orchestration (your 13 specialist agents)
5. **FastAPI Backend** - Your API application

---

## 📖 Common Commands

```bash
# View all container logs
docker-compose logs -f

# View backend logs only
docker-compose logs -f backend

# View Langflow logs
docker-compose logs -f langflow

# Stop all services
docker-compose down

# Stop and remove all data (clean slate)
docker-compose down -v

# Restart backend only
docker-compose restart backend

# Rebuild backend after code changes
docker-compose up -d --build backend
```

---

## 🔧 Troubleshooting

### Services won't start
```bash
# Check Docker is running
docker info

# Check container status
docker-compose ps

# View error logs
docker-compose logs
```

### Port already in use
```bash
# Check what's using the port
lsof -i :8001  # Backend
lsof -i :7860  # Langflow
lsof -i :5432  # PostgreSQL

# Kill the process or change ports in docker-compose.yml
```

### Database connection errors
```bash
# Check PostgreSQL is running
docker exec builtenvironment-postgres pg_isready

# Restart PostgreSQL
docker-compose restart postgres

# Check environment variables
docker exec builtenvironment-backend env | grep DATABASE
```

### Reset everything
```bash
# Nuclear option - remove all containers and volumes
docker-compose down -v
docker system prune -a
./start.sh
```

---

## 🎨 Building Your First AI Agent in Langflow

1. Open http://localhost:7860
2. Login with credentials above
3. Click "New Flow"
4. Your custom components are available in the sidebar:
   - Base Compliance Agent
   - Document Classifier
   - Traffic Light Scorer
   - Evidence Extractor
   - Regulation Checker
   - Confidence Calculator
5. Drag and drop to build your workflow
6. Connect nodes visually
7. Test with sample documents
8. Export and save to `langflow/flows/`

---

## 📚 Next Steps

1. **Explore the API**: http://localhost:8001/docs
2. **Build an AI agent**: http://localhost:7860
3. **Read the docs**: See `DOKPLOY_DEPLOYMENT.md` for production deployment
4. **Check PROJECT_IMPLEMENTATION_TODO.md**: See what to build next

---

## 🚢 Deploy to Production (Dokploy)

See `DOKPLOY_DEPLOYMENT.md` for complete Dokploy deployment guide.

Quick version:
1. Connect Git repo to Dokploy
2. Set environment variables in Dokploy UI
3. Deploy! Dokploy handles the rest (HTTPS, health checks, auto-restart)

---

## 🆘 Getting Help

- **Documentation**: See `/docs` folder
- **Issues**: https://github.com/kelvincushman/BuiltEnvironment.ai/issues
- **Logs**: Always check `docker-compose logs -f` first

---

**Ready to build the future of building compliance! 🏗️**
