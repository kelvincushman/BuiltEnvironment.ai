# BuiltEnvironment.ai - 4-Day MVP Sprint Plan 🚀

**Mission**: Launch a working MVP in 4 days using AI-powered coding assistance

**Goal**: Working SaaS platform with authentication, payment, 1 AI agent, and basic UI

**Team**: You + AI Coding Assistant (Claude Code)

---

## 🎯 MVP Scope

### What We're Building:
✅ User authentication & multi-tenancy
✅ Stripe subscription (Professional plan only for MVP)
✅ Document upload & storage
✅ ONE specialized AI agent (Fire Safety - highest value)
✅ Basic RAG chat
✅ Simple dashboard UI
✅ Audit logging (basic)

### What We're NOT Building (Yet):
❌ All 13 AI agents (just 1 for MVP)
❌ Complex WYSIWYG editor
❌ Advanced audit dashboards
❌ Full compliance reports
❌ Mobile apps
❌ Public API
❌ RevenueCat

---

## 📅 4-Day Breakdown

### **DAY 1: Foundation & Auth** (8 hours)
### **DAY 2: Payments & Documents** (8 hours)
### **DAY 3: AI Agent & RAG** (8 hours)
### **DAY 4: UI Polish & Deploy** (8 hours)

---

## DAY 1: Foundation & Authentication (8 hours)

### Hour 1-2: Project Setup
```bash
# Backend setup
mkdir -p backend/app/{api,core,models,schemas,services}
cd backend

# Create FastAPI app
cat > app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="BuiltEnvironment.ai")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "healthy"}
EOF

# Install dependencies
pip install fastapi uvicorn[standard] sqlalchemy asyncpg python-jose[cryptography] passlib[bcrypt] python-multipart stripe anthropic chromadb python-dotenv pydantic-settings redis

# Frontend setup
npx create-react-app frontend --template typescript
cd frontend
npm install @stripe/stripe-js @stripe/react-stripe-js axios react-router-dom tailwindcss
```

**Files to Create**:
- [x] `backend/app/main.py` - FastAPI app
- [x] `backend/app/core/config.py` - Settings
- [x] `backend/app/core/database.py` - DB connection
- [x] `backend/.env` - Environment variables
- [x] `docker-compose.yml` - PostgreSQL + Redis

**Generate with AI**:
```
Create a FastAPI app with:
- PostgreSQL connection using asyncpg
- Redis connection
- Environment config using pydantic-settings
- Health check endpoint
- CORS middleware
```

### Hour 3-4: Database Models

**Models to Create**:
```python
# backend/app/models/user.py
class User:
    id: UUID
    email: str
    hashed_password: str
    full_name: str
    tenant_id: UUID
    role: UserRole
    is_active: bool
    created_at: datetime

# backend/app/models/tenant.py
class Tenant:
    id: UUID
    name: str
    stripe_customer_id: str
    subscription_status: str
    created_at: datetime
```

**Generate with AI**:
```
Create SQLAlchemy models for User and Tenant with:
- UUID primary keys
- Proper indexes
- Relationships
- Timestamp fields
- Alembic migration
```

### Hour 5-6: Authentication API

**Endpoints to Create**:
- `POST /api/auth/register` - Create account + tenant
- `POST /api/auth/login` - Get JWT token
- `GET /api/auth/me` - Get current user

**Generate with AI**:
```
Create FastAPI authentication endpoints with:
- JWT token generation (7-day expiry)
- Password hashing with bcrypt
- Automatic tenant creation on registration
- Role-based access control
- Dependency for get_current_user
```

**Files**:
- `backend/app/api/auth.py`
- `backend/app/core/security.py`
- `backend/app/schemas/auth.py`

### Hour 7-8: Frontend Auth Pages

**Pages to Create**:
- Login page
- Register page
- Protected route wrapper

**Generate with AI**:
```
Create React TypeScript components:
1. LoginPage with email/password form
2. RegisterPage with company name, email, password
3. AuthContext for JWT token management
4. ProtectedRoute wrapper component
5. axios instance with auth token interceptor
```

**Test**: Can register, login, and access protected routes

---

## DAY 2: Payments & Documents (8 hours)

### Hour 1-3: Stripe Integration

**Setup**:
```bash
# Create Stripe products
python scripts/setup_stripe_products.py

# Set env vars
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

**Endpoints to Create**:
- `POST /api/subscription/checkout` - Create checkout session
- `POST /webhooks/stripe` - Handle webhooks
- `GET /api/subscription/current` - Get subscription status

**Database Models**:
```python
class Subscription:
    id: UUID
    tenant_id: UUID
    stripe_customer_id: str
    stripe_subscription_id: str
    plan_id: str
    status: SubscriptionStatus
    current_period_end: datetime
```

**Generate with AI**:
```
Create Stripe integration with:
1. Subscription model and API
2. Checkout session creation (Professional plan, 14-day trial)
3. Webhook handler for subscription events
4. Usage tracking model
5. React pricing page with Stripe Checkout redirect
```

**Files**:
- `backend/app/models/subscription.py`
- `backend/app/api/subscription.py`
- `backend/app/api/webhooks/stripe.py`
- `frontend/src/pages/Pricing.tsx`

**Test**: Can subscribe and receive webhook events

### Hour 4-5: Document Upload

**Endpoints**:
- `POST /api/documents/upload` - Upload file
- `GET /api/documents` - List documents
- `GET /api/documents/{id}` - Get document

**Storage**: Local filesystem for MVP (S3 later)

**Generate with AI**:
```
Create document management:
1. Document model (id, filename, file_path, tenant_id, size, uploaded_at)
2. Upload endpoint with multipart/form-data
3. File storage to ./uploads/{tenant_id}/
4. List documents endpoint with pagination
5. React upload component with drag-and-drop
```

**Files**:
- `backend/app/models/document.py`
- `backend/app/api/documents.py`
- `backend/app/services/storage_service.py`
- `frontend/src/components/DocumentUpload.tsx`

### Hour 6-8: Basic Text Extraction

**OCR/Extraction**:
```bash
pip install pypdf python-docx
```

**Generate with AI**:
```
Create text extraction service:
1. Extract text from PDF using pypdf
2. Extract text from DOCX using python-docx
3. Store extracted text in document.extracted_text field
4. Run extraction automatically after upload
5. Show extracted text in UI
```

**Files**:
- `backend/app/services/text_extractor.py`

**Test**: Upload PDF, see extracted text

---

## DAY 3: AI Agent & RAG (8 hours)

### Hour 1-2: RAG Setup (ChromaDB)

**Setup**:
```bash
pip install chromadb openai
```

**Generate with AI**:
```
Create RAG service with ChromaDB:
1. Initialize ChromaDB client
2. Create collection per tenant
3. Chunk text (1000 tokens, 200 overlap)
4. Generate embeddings (OpenAI text-embedding-3-small)
5. Index document chunks
6. Query function with hybrid search
```

**Files**:
- `backend/app/services/rag_service.py`
- `backend/app/services/chunking_service.py`

**Indexing Flow**:
```
Document Upload → Text Extraction → Chunking → Embedding → ChromaDB
```

### Hour 3-4: Chat API

**Endpoints**:
- `POST /api/chat/message` - Send message, get response
- `GET /api/chat/conversations` - List conversations

**Generate with AI**:
```
Create chat API with RAG:
1. Conversation model (id, tenant_id, title, messages[])
2. Chat endpoint that:
   - Queries RAG for relevant chunks
   - Sends chunks + question to Claude
   - Returns response with sources
3. Store conversation history
4. React chat component with message list
```

**Files**:
- `backend/app/models/conversation.py`
- `backend/app/api/chat.py`
- `backend/app/services/chat_service.py`
- `frontend/src/components/Chat.tsx`

**Test**: Ask question about uploaded document

### Hour 5-8: Fire Safety AI Agent

**Why Fire Safety First?**
- High value (Part B compliance)
- Clear regulations (BS 9999, BS EN 12845)
- Life safety = compelling demo

**Agent Flow**:
```
Input: Document text
↓
LangGraph Agent:
1. Extract fire safety specs
2. Check Part B requirements
3. Check BS 9999 compliance
4. Assign traffic light status
5. Generate findings
↓
Output: Compliance report
```

**Generate with AI**:
```
Create Fire Safety Agent using LangGraph:
1. Define state (document_text, findings, status)
2. Create nodes:
   - extract_fire_safety_specs
   - check_part_b
   - check_bs9999
   - assign_traffic_light
3. Implement tools for regulation checking
4. Return structured findings with traffic lights
5. API endpoint to run agent
```

**Files**:
- `backend/app/agents/fire_safety_agent.py`
- `backend/app/api/compliance.py`
- `backend/app/data/regulations/part_b.json`

**Regulations Data**:
```json
{
  "part_b": {
    "b1_means_of_warning": {
      "requirement": "Fire alarm system must cover all areas",
      "reference": "Part B1, BS 5839-1"
    },
    "b2_internal_fire_spread": {
      "requirement": "Fire resistance ratings for walls/floors",
      "reference": "Part B2, Table A1"
    }
  }
}
```

**Test**: Upload MEP spec, run fire safety check, see traffic lights

---

## DAY 4: UI Polish & Deploy (8 hours)

### Hour 1-3: Dashboard UI

**Pages to Create**:
- Dashboard home (project list, recent activity)
- Documents page (list, upload, view)
- Compliance page (run checks, view results)
- Settings (account, billing)

**Generate with AI**:
```
Create React dashboard with Tailwind CSS:
1. DashboardLayout with sidebar navigation
2. Home page with stats cards
3. Documents page with upload area and list
4. Compliance page showing traffic light results
5. Settings page with subscription info
6. Responsive design for mobile
```

**Components**:
- `frontend/src/layouts/DashboardLayout.tsx`
- `frontend/src/pages/Dashboard.tsx`
- `frontend/src/pages/Documents.tsx`
- `frontend/src/pages/Compliance.tsx`
- `frontend/src/pages/Settings.tsx`

### Hour 4-5: Basic Audit Logging

**Simple Audit**:
```python
# Just log to database for MVP
class AuditEvent:
    id: UUID
    tenant_id: UUID
    user_id: UUID
    event_type: str
    details: dict
    timestamp: datetime

# Log on key actions
await log_audit(
    event_type="document.uploaded",
    details={"filename": "spec.pdf"}
)
```

**Generate with AI**:
```
Create simple audit logging:
1. AuditEvent model
2. log_audit() helper function
3. Log on: login, upload, compliance_check
4. Basic audit log view in Settings
```

### Hour 6-7: Deployment Setup

**Docker Compose**:
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: builtenvironment
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD}@postgres/builtenvironment
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      REACT_APP_API_URL: http://localhost:8000
```

**Generate with AI**:
```
Create deployment configuration:
1. Backend Dockerfile (Python, uvicorn)
2. Frontend Dockerfile (Node, nginx)
3. docker-compose.yml for all services
4. .env.example with all required variables
5. Deploy script (./deploy.sh)
```

### Hour 8: Testing & Fixes

**Full User Flow Test**:
1. ✅ Register account → Create tenant
2. ✅ Subscribe → Stripe checkout → Webhook activates subscription
3. ✅ Upload document → Text extracted
4. ✅ Run fire safety check → Get traffic light results
5. ✅ Chat with document → RAG retrieves context
6. ✅ View audit log → See all actions

**Fix Issues**:
- Error handling
- Loading states
- Empty states
- Mobile responsiveness
- Environment variables

---

## 🚀 Deployment (End of Day 4)

### Quick Deploy Options:

**Option 1: Render.com** (Fastest)
```bash
# Push to GitHub
git push origin main

# Deploy on Render:
# 1. Connect GitHub repo
# 2. Add web service (FastAPI backend)
# 3. Add PostgreSQL database
# 4. Add Redis
# 5. Add static site (React frontend)
# All done in 10 minutes!
```

**Option 2: Railway.app** (Easy)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

**Option 3: DigitalOcean App Platform** (Medium)
- Connect GitHub repo
- Auto-detect Docker Compose
- Deploy in one click

---

## 📝 Day-by-Day AI Prompts

### Day 1 Prompts:

**Project Setup**:
```
Create a FastAPI backend with PostgreSQL and Redis integration. Include:
- Main app with CORS middleware
- Database connection with asyncpg
- Config management with pydantic-settings
- Health check endpoint
- Docker compose with PostgreSQL and Redis
```

**Auth System**:
```
Create a complete JWT authentication system with:
- User and Tenant SQLAlchemy models
- Registration endpoint (creates user + tenant)
- Login endpoint (returns JWT)
- Password hashing with bcrypt
- get_current_user dependency
- Role-based access control
```

**Frontend Auth**:
```
Create React TypeScript authentication:
- LoginPage component with form
- RegisterPage component
- AuthContext with JWT storage
- axios instance with auth interceptor
- ProtectedRoute wrapper
- Tailwind CSS styling
```

### Day 2 Prompts:

**Stripe Integration**:
```
Create Stripe subscription integration:
- Subscription model with SQLAlchemy
- Checkout session creation endpoint
- Webhook handler for subscription events
- Subscription status checking
- React pricing page with Stripe redirect
- Use pricing.json for Professional plan
```

**Document Management**:
```
Create document upload and management:
- Document model with metadata
- Upload endpoint with multipart/form-data
- File storage to local filesystem
- List and retrieve endpoints
- React upload component with drag-and-drop
- Text extraction from PDF and DOCX
```

### Day 3 Prompts:

**RAG System**:
```
Create RAG system with ChromaDB:
- Initialize ChromaDB client
- Tenant-isolated collections
- Document chunking (1000 tokens, 200 overlap)
- OpenAI embeddings (text-embedding-3-small)
- Hybrid search (vector + keyword)
- Query with context retrieval
```

**Chat Interface**:
```
Create chat system with RAG:
- Conversation model
- Chat endpoint that queries RAG and calls Claude
- Response with source citations
- React chat component
- Message history
- Streaming responses (optional)
```

**Fire Safety Agent**:
```
Create Fire Safety compliance agent with LangGraph:
- State: document_text, findings, compliance_status
- Nodes: extract_specs, check_part_b, check_bs9999, assign_traffic_light
- Tools: regulation_checker, standards_validator
- API endpoint to run agent
- Return structured findings with traffic lights
- Load Part B regulations from JSON
```

### Day 4 Prompts:

**Dashboard UI**:
```
Create complete dashboard UI with Tailwind:
- DashboardLayout with sidebar
- Home page with stats
- Documents page with list and upload
- Compliance page with results
- Settings page with subscription
- Fully responsive design
```

**Deployment**:
```
Create production deployment configuration:
- Backend Dockerfile (multi-stage, Python 3.11)
- Frontend Dockerfile (multi-stage, nginx)
- docker-compose.yml for all services
- Environment variable configuration
- Database migrations (alembic)
- Deploy script
```

---

## 🎯 Success Metrics (After 4 Days)

### Must Have (MVP):
- ✅ User can register and login
- ✅ User can subscribe (test mode)
- ✅ User can upload PDF/DOCX
- ✅ Fire safety agent analyzes document
- ✅ Traffic light results display
- ✅ Chat with uploaded documents
- ✅ Basic audit logging
- ✅ Deployed and accessible

### Nice to Have (If time):
- ⭐ Email notifications
- ⭐ PDF report generation
- ⭐ Usage dashboard
- ⭐ Admin panel

---

## 💡 AI Coding Assistant Tips

### Maximize Efficiency:

1. **Generate Full Files**: Ask for complete files, not snippets
2. **Use Templates**: Reference existing patterns
3. **Batch Requests**: Generate multiple related files at once
4. **Test-Driven**: Ask for tests alongside code
5. **Fix Iteratively**: Run code, report errors, get fixes

### Example Prompt Pattern:
```
Create the complete file backend/app/api/auth.py with:
- All necessary imports
- Login endpoint (POST /api/auth/login)
- Register endpoint (POST /api/auth/register)
- Get current user endpoint (GET /api/auth/me)
- Proper error handling
- Pydantic schemas for request/response
- JWT token generation
- Include docstrings
```

### Time Savers:
- Use AI for boilerplate (models, schemas, CRUD)
- Use AI for repetitive UI components
- Use AI for test generation
- Use AI for Docker configs
- Use AI for database migrations

---

## 📦 Deliverables After 4 Days

### Working MVP:
```
✅ Authentication system
✅ Multi-tenant database
✅ Stripe subscriptions (test mode)
✅ Document upload & storage
✅ Text extraction (PDF/DOCX)
✅ RAG with ChromaDB
✅ Chat interface
✅ Fire Safety AI agent with traffic lights
✅ Basic dashboard UI
✅ Audit logging
✅ Deployed to production
```

### Code Stats:
- ~50 files
- ~3,000-5,000 lines of code
- 10 API endpoints
- 10 React components
- 1 specialized AI agent
- 1 working SaaS platform! 🎉

---

## 🚀 Next Steps (After MVP)

### Week 2:
- Add remaining 12 AI agents
- Improve UI/UX
- Add more regulations
- Better reports

### Week 3:
- Advanced audit dashboards
- Usage analytics
- Email notifications
- More standards

### Week 4:
- Performance optimization
- Security hardening
- Beta customer onboarding
- Marketing site

---

## ⚡ Quick Start Commands

```bash
# Day 1: Setup
git clone <repo>
cd BuiltEnvironment.ai
./init/setup.sh
docker-compose up -d

# Day 2: Dev
cd backend && uvicorn app.main:app --reload
cd frontend && npm start

# Day 3: Test
pytest backend/tests
npm test

# Day 4: Deploy
docker-compose -f docker-compose.prod.yml up -d
# OR: git push origin main (auto-deploy on Render/Railway)
```

---

**With AI assistance, you can build in 4 days what would take a team 12 months!**

**Ready to code? Let's go! 🚀**

---

**Document Version**: 1.0.0
**Last Updated**: 2025-10-27
**Sprint Duration**: 4 days
**Team**: You + AI Coding Assistant
