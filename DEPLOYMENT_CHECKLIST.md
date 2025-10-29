# 🚀 BuiltEnvironment.ai - Deployment Checklist

Use this checklist when setting up BuiltEnvironment.ai on your Ubuntu server.

---

## ☑️ Pre-Deployment Checklist

### 1. Server Requirements
- [ ] Ubuntu 20.04+ or similar Linux distribution
- [ ] Minimum 8GB RAM (16GB recommended)
- [ ] Minimum 50GB storage
- [ ] Docker 20.10+ installed
- [ ] Docker Compose 1.29+ installed
- [ ] Git installed
- [ ] Ports available: 3000, 5432, 6379, 7860, 8000, 8001, 8002

### 2. API Keys Obtained
- [ ] Anthropic Claude API key (https://console.anthropic.com/)
- [ ] OpenAI API key (https://platform.openai.com/)
- [ ] Stripe API keys (optional - https://dashboard.stripe.com/)
- [ ] SMTP credentials (optional - SendGrid/AWS SES)

### 3. Domain & DNS (Production Only)
- [ ] Domain name purchased
- [ ] DNS A record pointing to server IP
- [ ] SSL certificate ready (Let's Encrypt or commercial)

---

## 📥 Installation Steps

### Step 1: Clone Repository ✅
```bash
git clone https://github.com/kelvincushman/BuiltEnvironment.ai.git
cd BuiltEnvironment.ai
git checkout claude/setup-docs-structure-011CUXn9hb4dcSA8HJJvxSd2
git branch --show-current  # Verify correct branch
```
- [ ] Repository cloned successfully
- [ ] On correct branch

### Step 2: Configure Environment ✅
```bash
cp .env.example .env
nano .env  # Edit with your values
```

**Required in .env:**
- [ ] ANTHROPIC_API_KEY set
- [ ] OPENAI_API_KEY set
- [ ] SECRET_KEY changed (use: `openssl rand -hex 32`)
- [ ] POSTGRES_PASSWORD changed
- [ ] REDIS_PASSWORD changed
- [ ] LANGFLOW_SUPERUSER_PASSWORD changed
- [ ] STRIPE keys set (if using payments)
- [ ] SMTP configured (if using emails)
- [ ] CORS_ORIGINS updated for your domain

### Step 3: Build Docker Images ✅
```bash
docker-compose build
```
- [ ] Build completed without errors (~5-10 minutes)
- [ ] All services built successfully

### Step 4: Start Services ✅
```bash
docker-compose up -d
```
- [ ] All containers started
- [ ] Run `docker-compose ps` - all show "Up" status

### Step 5: Wait for Services ✅
```bash
# Wait 30-60 seconds for all services to initialize
sleep 30
docker-compose ps
```
- [ ] PostgreSQL shows "healthy"
- [ ] Redis shows "healthy"
- [ ] ChromaDB shows "healthy"
- [ ] DeepSeek-OCR shows "healthy"
- [ ] Langflow shows "healthy"
- [ ] Backend shows "healthy"
- [ ] Frontend shows "Up"

### Step 6: Run Database Migrations ✅
```bash
docker-compose exec backend alembic upgrade head
```
- [ ] Migrations completed successfully
- [ ] No error messages
- [ ] Run `docker-compose exec backend alembic current` to verify

---

## 🧪 Post-Deployment Testing

### Test 1: Service Health Checks ✅
```bash
# Backend health
curl http://localhost:8001/health
# Expected: {"status":"ok"}

# ChromaDB health
curl http://localhost:8000/api/v1/heartbeat
# Expected: {"nanosecond heartbeat": timestamp}

# Frontend accessibility
curl http://localhost:3000
# Expected: HTML response
```
- [ ] Backend health check passes
- [ ] ChromaDB health check passes
- [ ] Frontend loads

### Test 2: Service Logs ✅
```bash
# Check for errors
docker-compose logs --tail=100 backend | grep -i error
docker-compose logs --tail=100 frontend | grep -i error
docker-compose logs --tail=100 postgres | grep -i error
```
- [ ] No critical errors in backend logs
- [ ] No errors in frontend logs
- [ ] No errors in PostgreSQL logs

### Test 3: API Documentation ✅
```bash
# Open in browser
http://localhost:8001/docs
```
- [ ] Swagger UI loads
- [ ] Can see all API endpoints
- [ ] Can expand and view endpoint details

### Test 4: User Registration ✅
```bash
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@test.com",
    "password": "TestPass123!",
    "first_name": "Test",
    "last_name": "User",
    "organization_name": "Test Org"
  }'
```
- [ ] Registration successful
- [ ] Received access_token and refresh_token
- [ ] User and tenant created in database

### Test 5: Frontend Login ✅
1. Open http://localhost:3000
2. Click "Register"
3. Fill in form and submit
4. Should redirect to dashboard

- [ ] Registration form works
- [ ] Can create account
- [ ] Redirects to dashboard after registration
- [ ] Can see user name in header

### Test 6: Document Upload (Backend) ✅
```bash
# Test with a sample PDF
curl -X POST http://localhost:8001/api/v1/documents/upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@sample.pdf" \
  -F "project_id=test-project" \
  -F "document_type=compliance"
```
- [ ] Upload successful
- [ ] Document processing started (check logs)
- [ ] Text extraction working
- [ ] ChromaDB indexing working

### Test 7: AI Chat ✅
```bash
curl -X POST http://localhost:8001/api/v1/chat/chat \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "test-conversation-id",
    "message": "What are fire safety requirements?",
    "specialist_agent": "fire_safety"
  }'
```
- [ ] Chat response received
- [ ] AI response contains relevant information
- [ ] No API key errors

---

## 🔒 Security Checklist (Production Only)

### Before Going Live
- [ ] All default passwords changed to strong passwords (32+ characters)
- [ ] SECRET_KEY is unique and random (32+ characters)
- [ ] .env file NOT committed to git (check .gitignore)
- [ ] HTTPS/SSL configured (not HTTP)
- [ ] Firewall rules configured:
  - [ ] Allow 80 (HTTP) and 443 (HTTPS) from internet
  - [ ] Deny direct access to 5432, 6379, 8000, 8001 from internet
  - [ ] Only allow backend to access database/redis
- [ ] CORS_ORIGINS set to production domain only
- [ ] DEBUG=false in .env
- [ ] ENVIRONMENT=production in .env
- [ ] Database backups configured (daily minimum)
- [ ] Error monitoring setup (Sentry recommended)
- [ ] Log aggregation configured
- [ ] Rate limiting enabled and tested
- [ ] API keys stored securely (secrets manager)
- [ ] Regular security updates scheduled

---

## 📊 Monitoring Checklist

### Setup Monitoring (Recommended)
- [ ] Docker container monitoring (Portainer, Watchtower)
- [ ] Application logs aggregation (ELK stack, Loki, or Papertrail)
- [ ] Error tracking (Sentry)
- [ ] Uptime monitoring (UptimeRobot, Pingdom)
- [ ] Database backup verification
- [ ] Disk space monitoring
- [ ] Memory usage monitoring
- [ ] API response time monitoring

---

## 🔄 Maintenance Checklist

### Weekly
- [ ] Check docker-compose logs for errors
- [ ] Verify database backups are running
- [ ] Check disk space usage
- [ ] Review error reports

### Monthly
- [ ] Update Docker images (docker-compose pull)
- [ ] Update dependencies (npm/pip)
- [ ] Review and rotate API keys if needed
- [ ] Test backup restoration
- [ ] Review security logs

---

## 🆘 Troubleshooting Common Issues

### Issue: Services won't start
**Solution:**
```bash
# Check Docker daemon
sudo systemctl status docker

# Check logs for errors
docker-compose logs

# Rebuild images
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Issue: Port conflicts
**Solution:**
```bash
# Find what's using the port
sudo lsof -i :8001

# Kill the process or change port in docker-compose.yml
# Then restart: docker-compose restart
```

### Issue: Database connection errors
**Solution:**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Try manual connection
docker-compose exec postgres psql -U postgres -d builtenvironment

# If needed, recreate database
docker-compose down -v
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

### Issue: AI not responding
**Solution:**
```bash
# Verify API keys are set
docker-compose exec backend env | grep ANTHROPIC_API_KEY
docker-compose exec backend env | grep OPENAI_API_KEY

# Check for API errors in logs
docker-compose logs backend | grep -i "anthropic\|openai"

# Test API key manually
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "content-type: application/json" \
  -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":100,"messages":[{"role":"user","content":"Hi"}]}'
```

---

## ✅ Final Verification

Before considering deployment complete:

- [ ] All services running and healthy
- [ ] Database migrations applied
- [ ] Can register new user
- [ ] Can login successfully
- [ ] Can upload document
- [ ] Document processing works
- [ ] AI chat responds
- [ ] All logs show no critical errors
- [ ] Frontend loads correctly
- [ ] API documentation accessible
- [ ] .env file secured (not in git)
- [ ] Passwords changed from defaults
- [ ] Backups configured (production)
- [ ] Monitoring setup (production)

---

## 📝 Deployment Notes

**Record these for future reference:**

- Deployment Date: _______________
- Server IP: _______________
- Domain: _______________
- Docker Version: _______________
- Database Version: _______________
- Last Migration Applied: _______________
- Deployed By: _______________

**API Keys Used:**
- Anthropic: ____________ (last 4 chars)
- OpenAI: ____________ (last 4 chars)
- Stripe: ____________ (last 4 chars)

**Backup Configuration:**
- Backup Location: _______________
- Backup Frequency: _______________
- Retention Period: _______________

---

## 🎯 Next Steps After Deployment

Once deployed successfully:

1. **Open Claude Code** on the server
2. **Copy prompt from CLAUDE_PROMPT.md**
3. **Paste into Claude Code**
4. **Start development work:**
   - Frontend-Backend API integration
   - Complete remaining AI agents
   - Add email service
   - Build form pages

**Estimated time to MVP: 4 weeks of active development**

---

## 📞 Support Resources

- Documentation: See SETUP.md
- API Docs: http://localhost:8001/docs
- Docker Logs: `docker-compose logs -f`
- GitHub Issues: https://github.com/kelvincushman/BuiltEnvironment.ai/issues

---

**Deployment completed successfully? Congratulations! 🎉**

You're ready to continue development with Claude Code!
