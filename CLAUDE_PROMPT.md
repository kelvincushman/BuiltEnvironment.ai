# 🤖 Claude Code Continuation Prompt

**Copy and paste this prompt to your local Claude Code instance to continue development.**

---

## Initial Context Prompt

```
You are continuing development on BuiltEnvironment.ai, a SaaS platform for AI-powered building compliance checking.

PROJECT OVERVIEW:
- Tech Stack: FastAPI backend, React/TypeScript frontend, PostgreSQL, Redis, ChromaDB vector DB
- Purpose: Help engineers analyze building documents for compliance with UK building regulations
- Current Status: ~50-55% complete MVP
- Git Branch: claude/setup-docs-structure-011CUXn9hb4dcSA8HJJvxSd2

WHAT'S COMPLETE:
✅ Backend API: 57 endpoints, 9 database models, multi-tenant architecture (85% complete)
✅ Frontend UI/UX: Complete component library, all pages designed with dark mode (100% complete)
✅ Authentication: JWT-based auth with registration, login, token refresh
✅ Document Processing: Upload → Text extraction (multi-OCR) → Chunking → Embeddings → ChromaDB indexing
✅ RAG System: 14 specialist agent collections in ChromaDB for context retrieval
✅ Fire Safety AI Agent: Full LangGraph workflow for Part B compliance analysis
✅ WYSIWYG Editor: Tiptap editor with export (PDF/DOCX/Markdown), comments, track changes, version history
✅ Infrastructure: Docker Compose with 7 services, all configured and ready

WHAT NEEDS WORK (PRIORITY ORDER):
1. 🎯 Frontend-Backend API Integration (HIGHEST PRIORITY - 2 weeks)
   - Create API service clients: projects.ts, documents.ts, chat.ts, findings.ts
   - Replace ALL mock data in Dashboard, Projects, Documents, Chat, Findings pages
   - Implement real file upload with progress indicators
   - Connect chat to real RAG backend
   - Add form pages for Create/Edit Project, Document metadata

2. 🤖 Complete AI Specialist Agents (1 week)
   - 9 of 13 agents need implementation (only Fire Safety is complete)
   - Building Envelope, Mechanical, Electrical, Environmental, Health & Safety, Quality, Legal, Specialist Systems, External Works
   - Each needs: system prompts, regulation knowledge, compliance checking logic

3. 📧 Email Service Configuration (3 days)
   - Configure SMTP (SendGrid/AWS SES recommended)
   - Implement password reset emails
   - Implement notification emails

4. ✨ Polish & Forms (1 week)
   - Create/Edit Project form with validation
   - Document metadata edit form
   - User profile/settings page
   - Error handling and loading states
   - Form validation throughout

KNOWN ISSUES:
- ~93 TypeScript warnings remaining (mostly unused imports - non-critical)
- Form component generic types need fixing
- Select component doesn't support leftIcon prop (used in several places)
- DocumentEditor has mock event listeners on non-DOM objects

RECENT WORK COMPLETED:
- Fixed Card component compound pattern (Card.Header, Card.Content, etc.)
- Fixed Tiptap TextStyle import error
- Added Vite environment type definitions
- Fixed ~100+ TypeScript compilation errors
- Created comprehensive SETUP.md guide

PROJECT STRUCTURE:
- backend/app/ - FastAPI application (api/v1/endpoints/, models/, services/, core/)
- frontend/src/ - React application (pages/, components/, services/, contexts/)
- docker-compose.yml - 7 services: postgres, redis, chromadb, deepseek-ocr, langflow, backend, frontend

IMPORTANT FILES:
- SETUP.md - Complete setup guide (just created)
- .env.example - Environment configuration template
- docker-compose.yml - All service definitions
- backend/app/main.py - FastAPI app entry point
- frontend/src/App.tsx - React app with routing
- frontend/src/services/api.ts - Axios instance with auth interceptors

DEVELOPMENT WORKFLOW:
1. Services run in Docker containers with volume mounts for hot reload
2. Backend: uvicorn with --reload flag (changes reflect immediately)
3. Frontend: Vite dev server (hot module replacement)
4. Database migrations: alembic (12 migrations already applied)

YOUR FIRST TASKS:
1. Verify all Docker services are running: docker-compose ps
2. Check logs for any errors: docker-compose logs --tail=50
3. Test the application at http://localhost:3000
4. Review the codebase structure
5. Ask me what you should work on next (recommend starting with frontend API integration)

Please confirm you understand the project state and are ready to continue development. What would you like to work on first?
```

---

## Quick Start Commands

**After cloning the repository on your Ubuntu server**, run these commands:

```bash
# Navigate to project
cd BuiltEnvironment.ai

# Checkout the correct branch
git checkout claude/setup-docs-structure-011CUXn9hb4dcSA8HJJvxSd2

# Create .env file (then edit with your API keys)
cp .env.example .env
nano .env  # Add your ANTHROPIC_API_KEY and OPENAI_API_KEY

# Build and start all services
docker-compose build
docker-compose up -d

# Wait 30 seconds for services to initialize
sleep 30

# Check all services are running
docker-compose ps

# Run database migrations
docker-compose exec backend alembic upgrade head

# View logs
docker-compose logs -f
```

Then open Claude Code and paste the prompt above!

---

## Helpful Commands for Claude Code

Share these with Claude Code if needed:

```bash
# Service management
docker-compose ps                    # Check service status
docker-compose logs -f backend       # View backend logs
docker-compose logs -f frontend      # View frontend logs
docker-compose restart backend       # Restart service
docker-compose down                  # Stop all services
docker-compose up -d                 # Start all services

# Database
docker-compose exec backend alembic upgrade head    # Run migrations
docker-compose exec backend alembic current         # Check current version
docker-compose exec postgres psql -U postgres -d builtenvironment  # Connect to DB

# Testing
curl http://localhost:8001/health                   # Test backend
curl http://localhost:3000                          # Test frontend
curl http://localhost:8001/docs                     # API documentation

# Development
docker-compose exec backend bash                    # Shell into backend
docker-compose exec frontend sh                     # Shell into frontend
docker-compose logs --tail=100 backend              # Last 100 log lines

# Git
git status                                          # Check changes
git log --oneline -10                               # Recent commits
git diff                                            # View changes
```

---

## Environment Variables Claude Code Needs to Know

**Configured in .env file:**

```bash
# CRITICAL - Must be set for AI features to work
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-proj-...

# Optional but recommended
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# SMTP for emails (optional)
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your-api-key
```

---

## API Endpoints Claude Code Should Know

**Backend API Base: http://localhost:8001/api/v1**

**Authentication:**
- POST /auth/register - Create account + tenant
- POST /auth/login - Get JWT tokens
- POST /auth/refresh - Refresh access token
- POST /auth/forgot-password - Request password reset
- POST /auth/reset-password - Complete password reset

**Projects:**
- GET /projects - List all projects (tenant-scoped)
- POST /projects - Create new project
- GET /projects/{id} - Get project details
- PATCH /projects/{id} - Update project
- DELETE /projects/{id} - Delete project

**Documents:**
- POST /documents/upload - Upload document (multipart/form-data)
- GET /documents - List documents with filters
- GET /documents/{id} - Get document details
- GET /documents/{id}/download - Download file
- PATCH /documents/{id} - Update metadata
- DELETE /documents/{id} - Delete document

**Chat:**
- GET /chat/agents - List specialist AI agents
- POST /chat/conversations - Create conversation
- GET /chat/conversations - List conversations
- GET /chat/conversations/{id} - Get conversation
- POST /chat/chat - Send message (get AI response)

**Findings:**
- GET /findings - List compliance findings
- GET /findings/{id} - Get finding details
- PATCH /findings/{id} - Update finding status

**AI:**
- POST /ai/analyze - Trigger document analysis
- GET /ai/agents - List available AI agents

**Users:**
- GET /users/me - Current user profile
- PATCH /users/me - Update profile
- POST /users/me/change-password - Change password

**Subscriptions:**
- POST /subscriptions/checkout - Create Stripe checkout
- GET /subscriptions/usage - Get usage stats

**Full API Documentation:** http://localhost:8001/docs

---

## Common Development Scenarios

### Scenario 1: "I want to connect the Projects page to the backend API"

**Tell Claude Code:**
```
I want to connect the Projects page to the real backend API. Currently it uses mock data.

Tasks:
1. Create frontend/src/services/projects.ts with API client functions
2. Update frontend/src/pages/Projects.tsx to use real API calls
3. Replace mock data with useState/useEffect to fetch from API
4. Add loading states and error handling
5. Implement Create Project form/modal
6. Test CRUD operations work end-to-end

The backend endpoints are:
- GET /api/v1/projects (list all)
- POST /api/v1/projects (create)
- GET /api/v1/projects/{id} (get one)
- PATCH /api/v1/projects/{id} (update)
- DELETE /api/v1/projects/{id} (delete)

Follow the pattern in frontend/src/services/auth.ts for the API client structure.
```

### Scenario 2: "I want to implement a new AI specialist agent"

**Tell Claude Code:**
```
I want to implement the Building Envelope specialist agent. Currently only the Fire Safety agent is complete.

Tasks:
1. Study backend/app/services/agents/fire_safety_agent.py as reference
2. Create backend/app/services/agents/building_envelope_agent.py
3. Define system prompts for Building Envelope compliance (thermal, moisture, airtightness)
4. Implement compliance checking logic for Part L (Conservation of fuel and power)
5. Create LangGraph workflow similar to Fire Safety agent
6. Add UK Building Regulations Part L knowledge
7. Test with sample building envelope documents
8. Register agent in backend/app/services/chat_service.py

Reference materials:
- Fire Safety Agent implementation (complete example)
- UK Building Regulations Part L
- ChromaDB collection: 'building_envelope_agent'
```

### Scenario 3: "I want to add real document upload"

**Tell Claude Code:**
```
I want to replace the mock document upload with real file upload to the backend.

Tasks:
1. Create frontend/src/services/documents.ts API client
2. Implement uploadDocument function using FormData and apiMultipart
3. Update frontend/src/pages/Documents.tsx upload modal
4. Add file validation (size, type)
5. Add upload progress indicator
6. Handle upload errors gracefully
7. Refresh document list after successful upload
8. Test with various file types (PDF, DOCX, images)

The backend endpoint is:
- POST /api/v1/documents/upload
- Accepts multipart/form-data
- Fields: file, project_id, document_type
- Returns: document metadata + processing status
```

---

## Testing Checklist for Claude Code

After making changes, Claude Code should verify:

```bash
# 1. TypeScript compilation (frontend)
cd frontend && npx tsc --noEmit --skipLibCheck

# 2. Backend syntax (Python)
docker-compose exec backend python -m py_compile app/main.py

# 3. Services are running
docker-compose ps | grep -c "Up"  # Should be 7

# 4. Backend health check
curl -f http://localhost:8001/health

# 5. Frontend is accessible
curl -f http://localhost:3000

# 6. Database migrations are current
docker-compose exec backend alembic current

# 7. No critical errors in logs
docker-compose logs --tail=100 backend | grep -i "error" | grep -v "404"

# 8. Git status is clean (or changes are intentional)
git status
```

---

## Project Goals Reminder for Claude Code

**Mission:** Build an AI-powered SaaS platform that helps engineers ensure building compliance with UK regulations.

**Target Users:**
- Fire Safety Engineers
- Structural Engineers
- Building Control Officers
- Architects
- Project Managers

**Core Value Proposition:**
- Upload building documents (plans, calculations, assessments)
- AI analyzes against UK Building Regulations (Parts A-P)
- Generates compliance findings with regulation references
- Chat with specialist AI agents for guidance
- Collaborative document review and editing
- Export compliance reports

**Business Model:**
- Freemium SaaS (Starter / Pro / Enterprise tiers)
- Stripe subscription billing
- Usage limits per tier
- Multi-tenant architecture

**Unique Features:**
- 13 specialist AI agents (Fire Safety, Structural, MEP, etc.)
- RAG-powered responses with document context
- Multi-OCR document processing (handles technical drawings)
- WYSIWYG collaborative document editing
- Real-time compliance checking
- SOC2-compliant architecture

---

## Success Metrics

Claude Code should help achieve:

**Week 1-2: Frontend Integration**
- [ ] All pages connected to real APIs
- [ ] Mock data completely removed
- [ ] Forms working for CRUD operations
- [ ] File upload functional
- [ ] Error handling throughout

**Week 3: AI Agents**
- [ ] 9 remaining specialist agents implemented
- [ ] All agents can analyze documents
- [ ] Compliance findings generated correctly

**Week 4: Polish**
- [ ] Email service working
- [ ] All forms validated
- [ ] Error messages user-friendly
- [ ] Testing completed
- [ ] Ready for staging deployment

**MVP Launch Target: 4 weeks from start**

---

## Important Notes for Claude Code

1. **Always check docker-compose logs** before assuming something is broken
2. **Hot reload works** - no need to restart containers for code changes
3. **Database migrations** - create new migrations with `alembic revision --autogenerate`
4. **TypeScript errors** - ~93 warnings are known and non-critical (unused imports)
5. **Mock data** - every page currently uses mock data, needs to be replaced
6. **API authentication** - already handled by axios interceptors in services/api.ts
7. **Multi-tenant** - all API calls are automatically scoped to the authenticated tenant
8. **Git workflow** - work on claude/setup-docs-structure-011CUXn9hb4dcSA8HJJvxSd2 branch

---

## Getting Help

If Claude Code encounters issues:

1. Check SETUP.md for troubleshooting steps
2. Review docker-compose logs for errors
3. Verify .env file has required API keys
4. Check all services are healthy: `docker-compose ps`
5. Restart services if needed: `docker-compose restart`
6. Check GitHub issues for similar problems

---

## Next Steps for Claude Code

**Recommended Starting Point:**

```
Start with Task 1: Frontend-Backend API Integration

Step 1: Create API service clients
- Create frontend/src/services/projects.ts
- Create frontend/src/services/documents.ts
- Create frontend/src/services/chat.ts
- Create frontend/src/services/findings.ts

Follow the pattern in frontend/src/services/auth.ts and use the api instance from frontend/src/services/api.ts (already configured with auth interceptors).

Let me know when you're ready to start!
```

---

**END OF CONTINUATION PROMPT**

✅ Copy everything from "Initial Context Prompt" section above and paste it into your local Claude Code instance!
