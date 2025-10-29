# BuiltEnvironment.ai - Local Development Setup Guide

## 🎯 Quick Start Summary

This guide will help you set up BuiltEnvironment.ai on your local Ubuntu server with Docker.

**Tech Stack:**
- **Backend**: FastAPI (Python 3.11), PostgreSQL 15, Redis, ChromaDB
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS
- **AI**: Anthropic Claude, OpenAI Embeddings, LangChain, LangGraph
- **Infrastructure**: Docker, Docker Compose

**What's Working:**
- ✅ Backend API (57 endpoints, 85% complete)
- ✅ Frontend UI/UX (100% complete, 30% integrated with backend)
- ✅ Authentication & Multi-tenancy
- ✅ Document processing & RAG system
- ✅ Fire Safety AI agent (full compliance checking)
- ✅ Tiptap WYSIWYG editor with collaboration features

**What Needs Work:**
- ⏳ Frontend-Backend API integration (main priority)
- ⏳ 9 remaining AI specialist agents
- ⏳ Email service configuration
- ⏳ Form pages for CRUD operations

---

## 📋 Prerequisites

### Required Software (Ubuntu Server)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
sudo apt install -y docker.io docker-compose
sudo systemctl enable docker
sudo systemctl start docker

# Add your user to docker group (logout/login after)
sudo usermod -aG docker $USER

# Install Git
sudo apt install -y git

# Install Node.js 18+ and npm (for local development)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installations
docker --version          # Should be 20.10+
docker-compose --version  # Should be 1.29+
node --version           # Should be v20+
npm --version            # Should be 9+
git --version
```

### Required API Keys

You'll need to obtain these API keys before starting:

1. **Anthropic Claude API Key** (Required)
   - Sign up at: https://console.anthropic.com/
   - Get API key from: https://console.anthropic.com/settings/keys
   - Used for: AI compliance analysis, chat responses

2. **OpenAI API Key** (Required)
   - Sign up at: https://platform.openai.com/
   - Get API key from: https://platform.openai.com/api-keys
   - Used for: Document embeddings (text-embedding-3-small)

3. **Stripe API Keys** (Optional - for payments)
   - Sign up at: https://stripe.com/
   - Get keys from: https://dashboard.stripe.com/apikeys
   - Get webhook secret: https://dashboard.stripe.com/webhooks
   - Used for: Subscription billing

4. **SMTP Email Service** (Optional - for emails)
   - Recommended: SendGrid, AWS SES, or Mailgun
   - Used for: Password resets, notifications

---

## 🚀 Installation Steps

### Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/kelvincushman/BuiltEnvironment.ai.git
cd BuiltEnvironment.ai

# Checkout the development branch
git checkout claude/setup-docs-structure-011CUXn9hb4dcSA8HJJvxSd2

# Verify you're on the right branch
git branch --show-current
```

### Step 2: Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit the .env file with your API keys
nano .env  # or use vim, code, etc.
```

**Required Configuration in .env:**

```bash
# CRITICAL: Add your API keys here
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-proj-...

# Optional but recommended
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Optional email configuration
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-sendgrid-api-key
SMTP_FROM=noreply@builtenvironment.ai
```

See `.env.example` for all available configuration options.

### Step 3: Build and Start Services

```bash
# Build all Docker images (first time only, ~5-10 minutes)
docker-compose build

# Start all services in detached mode
docker-compose up -d

# Check that all services are running
docker-compose ps

# Expected output: All services should show "Up" status
# - builtenvironment-postgres    (healthy)
# - builtenvironment-redis       (healthy)
# - builtenvironment-chromadb    (healthy)
# - builtenvironment-deepseek-ocr (healthy)
# - builtenvironment-langflow    (healthy)
# - builtenvironment-backend     (healthy)
# - builtenvironment-frontend    (Up)
```

### Step 4: Initialize Database

```bash
# Wait for PostgreSQL to be fully ready (~30 seconds)
docker-compose logs -f postgres | grep "database system is ready to accept connections"
# Press Ctrl+C once you see the message twice

# Run database migrations
docker-compose exec backend alembic upgrade head

# Verify migrations completed
docker-compose exec backend alembic current
```

### Step 5: Verify Services

```bash
# Check all service logs for errors
docker-compose logs --tail=50

# Check individual service logs
docker-compose logs -f backend    # Backend API logs
docker-compose logs -f frontend   # Frontend dev server logs
docker-compose logs -f postgres   # Database logs
docker-compose logs -f chromadb   # Vector DB logs

# Test backend health endpoint
curl http://localhost:8001/health
# Expected: {"status":"ok"}

# Test ChromaDB
curl http://localhost:8000/api/v1/heartbeat
# Expected: heartbeat timestamp
```

### Step 6: Access the Application

Open your browser and navigate to:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs (Swagger UI)
- **Langflow**: http://localhost:7860 (AI workflow builder)

**First Time Login:**
- Click "Register" to create a new account
- This will create your tenant organization and admin user
- You'll be automatically logged in

---

## 🧪 Testing the Setup

### Test 1: User Registration & Login

```bash
# Test registration endpoint
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "TestPass123!",
    "first_name": "Test",
    "last_name": "Admin",
    "organization_name": "Test Organization"
  }'

# Should return: access_token, refresh_token, and user data
```

### Test 2: Document Upload & Processing

1. Login to http://localhost:3000
2. Go to "Documents" page
3. Click "Upload Document"
4. Upload a PDF file
5. Check backend logs: `docker-compose logs -f backend`
6. Should see: Text extraction → Chunking → Embedding → ChromaDB indexing

### Test 3: AI Chat (RAG)

1. Go to "Chat" page
2. Select "Fire Safety Agent"
3. Ask: "What are the Part B fire safety requirements?"
4. Should receive AI response with context from uploaded documents

---

## 🛠️ Development Workflow

### Making Changes

```bash
# Frontend changes (hot reload automatically)
cd frontend
npm run dev
# Edit files in frontend/src/

# Backend changes (auto-reload with --reload flag)
# Edit files in backend/app/
# Changes are reflected immediately via volume mount

# Database schema changes
cd backend
# 1. Edit models in app/models/
# 2. Create migration
alembic revision --autogenerate -m "Description of changes"
# 3. Review the migration in alembic/versions/
# 4. Apply migration
docker-compose exec backend alembic upgrade head
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# Last N lines
docker-compose logs --tail=100 backend

# Follow logs from specific timestamp
docker-compose logs --since 2024-01-01T00:00:00 backend
```

### Restarting Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart frontend

# Stop all services
docker-compose down

# Stop and remove volumes (CAUTION: deletes all data)
docker-compose down -v

# Start services again
docker-compose up -d
```

---

## 🐛 Troubleshooting

### Issue: Services fail to start

```bash
# Check Docker daemon status
sudo systemctl status docker

# Check disk space (need at least 10GB free)
df -h

# Check logs for specific error
docker-compose logs backend | grep -i error
docker-compose logs postgres | grep -i error
```

### Issue: Port already in use

```bash
# Find process using port
sudo lsof -i :8001  # Backend
sudo lsof -i :3000  # Frontend
sudo lsof -i :5432  # PostgreSQL

# Kill process or change port in docker-compose.yml
```

### Issue: Database connection errors

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Try connecting manually
docker-compose exec postgres psql -U postgres -d builtenvironment

# Check DATABASE_URL in .env matches docker-compose.yml
```

### Issue: Frontend can't connect to backend

```bash
# Check backend is running
curl http://localhost:8001/health

# Check CORS configuration in backend
# Should allow http://localhost:3000

# Check frontend .env
# VITE_API_URL should be http://localhost:8001

# Rebuild frontend
docker-compose build frontend
docker-compose restart frontend
```

### Issue: AI responses failing

```bash
# Verify API keys are set
docker-compose exec backend env | grep ANTHROPIC_API_KEY
docker-compose exec backend env | grep OPENAI_API_KEY

# Check ChromaDB is running
curl http://localhost:8000/api/v1/heartbeat

# Check backend logs for AI errors
docker-compose logs backend | grep -i "anthropic\|openai"
```

---

## 📁 Project Structure

```
BuiltEnvironment.ai/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/v1/         # API endpoints (57 endpoints)
│   │   ├── models/         # SQLAlchemy models (9 models)
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic (11 services)
│   │   ├── core/           # Config, security, dependencies
│   │   └── main.py         # FastAPI app
│   ├── alembic/            # Database migrations
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
├── frontend/               # React frontend
│   ├── src/
│   │   ├── pages/         # 11 pages (Dashboard, Projects, etc.)
│   │   ├── components/    # 30+ UI components
│   │   ├── services/      # API clients (2 services)
│   │   ├── contexts/      # React contexts (Auth, Theme)
│   │   └── App.tsx        # Main app with routing
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml      # All services configuration
├── .env                    # Environment variables (create from .env.example)
├── .env.example           # Environment template
├── SETUP.md               # This file
├── DEPLOYMENT.md          # Deployment guide
└── README.md              # Project overview
```

---

## 🎯 Next Steps After Setup

Once your local environment is running, the **highest priority** tasks are:

### 1. Frontend-Backend API Integration (2 weeks)

**Goal**: Replace all mock data with real API calls

- [ ] Create `frontend/src/services/projects.ts` API client
- [ ] Create `frontend/src/services/documents.ts` API client
- [ ] Create `frontend/src/services/chat.ts` API client
- [ ] Create `frontend/src/services/findings.ts` API client
- [ ] Update Dashboard to fetch real data
- [ ] Update Projects page with real CRUD operations
- [ ] Update Documents page with real file upload
- [ ] Update Chat page with real RAG responses
- [ ] Update Findings page with real data

### 2. Complete AI Specialist Agents (1 week)

**Goal**: Implement 9 remaining specialist agents

- [ ] Building Envelope Agent
- [ ] Mechanical Services Agent
- [ ] Electrical Services Agent
- [ ] Environmental & Sustainability Agent
- [ ] Health & Safety Agent
- [ ] Quality Assurance Agent
- [ ] Legal & Contracts Agent
- [ ] Specialist Systems Agent
- [ ] External Works Agent

### 3. Polish & Testing (1 week)

- [ ] Configure email service (SMTP)
- [ ] Add form pages (Create/Edit Project, Document metadata)
- [ ] Error handling and validation
- [ ] Write unit tests for critical services
- [ ] Manual testing of all workflows

**Total Estimated Time to MVP: 4 weeks**

---

## 📞 Getting Help

If you encounter issues:

1. Check this SETUP.md guide
2. Check DEPLOYMENT.md for advanced deployment topics
3. Review docker-compose logs for errors
4. Check the GitHub Issues: https://github.com/kelvincushman/BuiltEnvironment.ai/issues

---

## 🔐 Security Notes

**For Development:**
- Default passwords in `.env.example` are for LOCAL development only
- Change all passwords and secret keys for production
- Never commit `.env` file to git (it's in .gitignore)

**For Production:**
- Use strong passwords (32+ characters)
- Use proper SSL/TLS certificates
- Set up proper firewall rules
- Use secrets management (AWS Secrets Manager, HashiCorp Vault, etc.)
- Enable database backups
- Set up monitoring and alerting

---

## ✅ Setup Checklist

Use this checklist to verify your setup:

- [ ] Docker and Docker Compose installed
- [ ] Git repository cloned
- [ ] .env file created with API keys
- [ ] `docker-compose build` completed successfully
- [ ] `docker-compose up -d` started all services
- [ ] All services show "healthy" status in `docker-compose ps`
- [ ] Database migrations completed successfully
- [ ] Frontend accessible at http://localhost:3000
- [ ] Backend API accessible at http://localhost:8001
- [ ] API docs accessible at http://localhost:8001/docs
- [ ] User registration works
- [ ] User login works
- [ ] Can upload a document
- [ ] Document processing works (check logs)
- [ ] Can chat with AI agent
- [ ] AI responses working (requires API keys)

Once all items are checked, you're ready to develop! 🚀
