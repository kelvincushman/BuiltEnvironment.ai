# BuiltEnvironment.ai Backend

FastAPI backend for AI-powered building compliance and documentation platform.

## Quick Start

### Using Docker (Recommended)

1. **Copy environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your API keys**:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-your-key-here
   OPENAI_API_KEY=sk-your-key-here
   ```

3. **Start all services**:
   ```bash
   docker-compose up -d
   ```

4. **Check logs**:
   ```bash
   docker-compose logs -f backend
   ```

5. **Access the API**:
   - API: http://localhost:8001
   - API Docs: http://localhost:8001/docs
   - Health Check: http://localhost:8001/health

### Local Development (Without Docker)

1. **Install dependencies**:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Start PostgreSQL, Redis, and ChromaDB** (using Docker):
   ```bash
   docker-compose up -d postgres redis chromadb
   ```

3. **Run the backend**:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```

## Testing the Authentication

### 1. Register a New User

```bash
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "ABC Construction Ltd",
    "company_email": "info@abcconstruction.com",
    "first_name": "John",
    "last_name": "Smith",
    "email": "john.smith@abcconstruction.com",
    "password": "SecurePass123!",
    "phone": "+44 20 1234 5678"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Login

```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.smith@abcconstruction.com",
    "password": "SecurePass123!"
  }'
```

### 3. Use the Access Token

```bash
curl http://localhost:8001/api/v1/projects \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

## Architecture

```
backend/
├── app/
│   ├── api/v1/endpoints/     # API endpoints
│   │   └── auth.py          # Authentication endpoints
│   ├── core/                # Core configuration
│   │   ├── config.py        # Settings management
│   │   └── security.py      # JWT & password hashing
│   ├── db/                  # Database
│   │   └── base.py          # SQLAlchemy setup
│   ├── models/              # SQLAlchemy models
│   │   ├── tenant.py        # Multi-tenant organizations
│   │   ├── user.py          # User authentication
│   │   ├── subscription.py  # Stripe subscriptions
│   │   ├── project.py       # Building projects
│   │   ├── document.py      # Uploaded documents
│   │   └── audit.py         # Audit event tracking
│   ├── schemas/             # Pydantic schemas
│   │   ├── auth.py          # Auth request/response
│   │   ├── user.py          # User schemas
│   │   └── ...
│   └── main.py              # FastAPI application
├── requirements.txt         # Python dependencies
└── Dockerfile              # Docker configuration
```

## Database Models

### Multi-Tenancy
Every resource is isolated by `tenant_id`:
- Each registration creates a new **Tenant** (organization)
- Users belong to a tenant
- Projects, documents, and audit events are tenant-scoped

### Key Models
- **Tenant**: Organization with subscription limits
- **User**: Authentication + professional engineer credentials
- **Subscription**: Stripe integration (Starter/Professional/Enterprise)
- **Project**: Building project with compliance summary
- **Document**: Uploaded files with AI analysis and compliance findings
- **AuditEvent**: Comprehensive activity tracking

## Next Steps

- ✅ Authentication (Complete)
- 🚧 Document upload endpoints
- 🚧 AI agent integration (LangGraph)
- 🚧 RAG system (ChromaDB)
- 🚧 Compliance checking
- 🚧 Stripe payment integration
- 🚧 React frontend

## API Documentation

Visit http://localhost:8001/docs for interactive API documentation (Swagger UI).

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `ANTHROPIC_API_KEY`: For Claude AI agents
- `OPENAI_API_KEY`: For embeddings and GPT models
- `STRIPE_SECRET_KEY`: For payment processing
- `SECRET_KEY`: For JWT token signing (generate with `openssl rand -hex 32`)
