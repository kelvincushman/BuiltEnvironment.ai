# Dokploy Deployment Guide for BuiltEnvironment.ai

This guide explains how to deploy BuiltEnvironment.ai to **Dokploy** hosted on AWS.

## 🌐 What is Dokploy?

Dokploy is an open-source deployment platform (like Heroku/Vercel) that simplifies Docker deployments with:
- Git-based deployments
- Built-in PostgreSQL, Redis, MySQL
- Automatic HTTPS with Let's Encrypt
- Environment variables management
- One-click deployment
- Container health monitoring
- Zero-downtime deployments

**Website**: https://dokploy.com

---

## 📋 Prerequisites

1. **Dokploy Instance**: Running on AWS EC2 (already set up)
2. **Domain Name**: Configured to point to your Dokploy instance
3. **API Keys**: 
   - Anthropic Claude API key
   - OpenAI API key
   - Stripe API keys
4. **Git Repository**: Connected to Dokploy

---

## 🚀 Deployment Steps

### Step 1: Create a New Application in Dokploy

1. Log in to your Dokploy dashboard
2. Click "Create New Application"
3. Choose "Docker Compose" as deployment type
4. Connect your GitHub repository: `https://github.com/kelvincushman/BuiltEnvironment.ai`
5. Set branch: `main` (or your production branch)

### Step 2: Configure Database Services

Dokploy provides built-in databases, but for production we recommend:

#### Option A: Use Dokploy's Built-in Services (Quick)
1. In Dokploy, create:
   - PostgreSQL service (for main database)
   - Redis service (for caching)

2. Dokploy will provide connection strings like:
   ```
   DATABASE_URL=postgresql://user:password@postgres:5432/dbname
   REDIS_URL=redis://redis:6379
   ```

#### Option B: Use External Services (Recommended for Production)
1. **Database**: AWS RDS PostgreSQL or Supabase
2. **Redis**: AWS ElastiCache or Upstash
3. **ChromaDB**: Self-hosted or Chroma Cloud
4. **Langflow**: Deploy separately on Dokploy

### Step 3: Set Environment Variables

In Dokploy UI, go to "Environment Variables" and add:

```bash
# Core Services
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/builtenvironment
REDIS_URL=redis://:password@host:6379/0
CHROMA_HOST=chromadb-host
CHROMA_PORT=8000
LANGFLOW_URL=https://langflow.yourdomain.com

# API Keys
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# Security
SECRET_KEY=<generate-with-openssl-rand-base64-32>
ENVIRONMENT=production
DEBUG=false

# CORS
CORS_ORIGINS=https://app.builtenvironment.ai,https://www.builtenvironment.ai

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=noreply@builtenvironment.ai
```

### Step 4: Configure Docker Build

1. In Dokploy, set:
   - **Dockerfile path**: `backend/Dockerfile`
   - **Build target**: `production`
   - **Port**: `8000`
   - **Health check path**: `/health`

2. Dokploy will automatically:
   - Build the Docker image
   - Deploy the container
   - Run database migrations on startup (via startup.sh)
   - Set up HTTPS with Let's Encrypt
   - Configure health checks

### Step 5: Deploy Supporting Services

#### Deploy Langflow

1. Create a new Dokploy application for Langflow
2. Use Docker image: `langflowai/langflow:latest`
3. Set environment variables:
   ```bash
   LANGFLOW_DATABASE_URL=postgresql://...
   LANGFLOW_SUPERUSER=admin@builtenvironment.ai
   LANGFLOW_SUPERUSER_PASSWORD=<secure-password>
   ```
4. Set custom domain: `langflow.builtenvironment.ai`

#### Deploy ChromaDB (if self-hosting)

1. Create new Dokploy application
2. Use Docker image: `chromadb/chroma:latest`
3. Set persistent volume for `/chroma/chroma`
4. Set custom domain: `chromadb.builtenvironment.ai`

### Step 6: Set Up Custom Domain

1. In Dokploy, go to "Domains"
2. Add your domain: `app.builtenvironment.ai`
3. Dokploy will automatically:
   - Generate SSL certificate
   - Configure Traefik reverse proxy
   - Handle HTTPS redirects

### Step 7: Configure Stripe Webhooks

1. Go to Stripe Dashboard → Webhooks
2. Add endpoint: `https://app.builtenvironment.ai/api/v1/webhooks/stripe`
3. Select events:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
4. Copy webhook secret and add to Dokploy env vars as `STRIPE_WEBHOOK_SECRET`

### Step 8: Database Migrations

After first deployment, run migrations:

```bash
# SSH into Dokploy server or use Dokploy's terminal
docker exec -it builtenvironment-backend alembic upgrade head
```

### Step 9: Verify Deployment

1. Check health endpoint: `https://app.builtenvironment.ai/health`
2. Check API docs: `https://app.builtenvironment.ai/docs`
3. Test authentication endpoints
4. Verify Langflow connection
5. Test file upload
6. Verify database connectivity

---

## 🔧 Continuous Deployment

Dokploy supports automatic deployments:

1. In Dokploy, enable "Auto Deploy"
2. Push to `main` branch
3. Dokploy automatically:
   - Pulls latest code
   - Builds Docker image
   - Deploys with zero downtime
   - Runs health checks
   - Rolls back if deployment fails

---

## 📊 Monitoring

### Dokploy Built-in Monitoring

Dokploy provides:
- Container logs (real-time)
- Resource usage (CPU, Memory, Disk)
- Deployment history
- Health check status

### External Monitoring (Optional)

For production, consider adding:
- **Sentry**: Error tracking (`pip install sentry-sdk`)
- **Datadog**: APM monitoring
- **UptimeRobot**: Uptime monitoring

---

## 🔐 Security Best Practices

### 1. Environment Variables
- Store all secrets in Dokploy's environment variables (encrypted at rest)
- Never commit `.env` files to Git
- Rotate credentials regularly

### 2. Database Security
- Use AWS RDS with encryption at rest
- Enable SSL/TLS for database connections
- Restrict database access to Dokploy's IP range
- Enable automated backups

### 3. API Keys
- Use production API keys (not test keys)
- Restrict API key permissions (Stripe: restricted keys)
- Enable 2FA on all service accounts

### 4. HTTPS
- Dokploy automatically handles HTTPS
- Force HTTPS redirects (Dokploy does this)
- Use HSTS headers

### 5. Rate Limiting
- Add rate limiting middleware in FastAPI
- Use Redis for distributed rate limiting
- Configure Traefik rate limits in Dokploy

---

## 🗄️ Backup Strategy

### Database Backups

**Option 1: AWS RDS Automated Backups**
- Enable automated backups (retention: 30 days)
- Enable point-in-time recovery
- Test restore procedure monthly

**Option 2: Manual Backups**
```bash
# Backup
docker exec postgres pg_dump -U postgres builtenvironment > backup.sql

# Restore
docker exec -i postgres psql -U postgres builtenvironment < backup.sql
```

### File Storage Backups

If using local file storage:
- Use AWS S3 for persistent storage
- Enable versioning on S3 bucket
- Configure lifecycle policies

---

## 📈 Scaling

### Vertical Scaling (Increase Resources)
1. In Dokploy, increase container resources:
   - CPU: 2 cores → 4 cores
   - Memory: 4GB → 8GB

### Horizontal Scaling (Multiple Instances)
1. In Dokploy, increase replicas:
   - Set replicas: 3
   - Dokploy will load balance automatically

### Database Scaling
1. AWS RDS:
   - Enable read replicas
   - Use connection pooling (PgBouncer)
2. Redis:
   - Use AWS ElastiCache with clustering

---

## 🐛 Troubleshooting

### Application Won't Start

**Check logs**:
```bash
# In Dokploy UI
Logs → Backend → Last 1000 lines
```

**Common issues**:
- Missing environment variables → Check Dokploy env vars
- Database connection failed → Verify DATABASE_URL
- Port already in use → Check port mappings

### Database Connection Errors

```bash
# Test connection
docker exec backend python -c "from app.core.database import engine; print(engine.url)"

# Check PostgreSQL is running
docker exec postgres pg_isready
```

### Langflow Connection Failed

```bash
# Verify Langflow is accessible
curl https://langflow.builtenvironment.ai/health

# Check environment variable
echo $LANGFLOW_URL
```

### SSL Certificate Issues

- Dokploy automatically renews Let's Encrypt certificates
- If issues persist, check DNS configuration
- Verify domain points to Dokploy server IP

---

## 📞 Support

- **Dokploy Docs**: https://docs.dokploy.com
- **Dokploy GitHub**: https://github.com/Dokploy/dokploy
- **BuiltEnvironment.ai Issues**: https://github.com/kelvincushman/BuiltEnvironment.ai/issues

---

## ✅ Deployment Checklist

Before going live:

- [ ] All environment variables set in Dokploy
- [ ] Database migrations run successfully
- [ ] Stripe webhooks configured and tested
- [ ] Custom domain configured with SSL
- [ ] Health checks passing
- [ ] API keys are production keys (not test)
- [ ] CORS origins include production domain
- [ ] Database backups enabled
- [ ] Monitoring configured (Sentry, Datadog)
- [ ] Load testing completed
- [ ] Security audit completed
- [ ] Terms of Service and Privacy Policy deployed
- [ ] Email service configured and tested

---

## 🎉 You're Live!

Your BuiltEnvironment.ai platform is now deployed and running on Dokploy!

Access your application at: **https://app.builtenvironment.ai**

---

**Last Updated**: 2025-10-28
**Version**: 1.0
**Maintained by**: BuiltEnvironment.ai Team
