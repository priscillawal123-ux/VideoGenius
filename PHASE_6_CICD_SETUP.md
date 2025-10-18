# Phase 6: CI/CD & Cloud Deployment - Video Genius

## 📋 Overview

Phase 6 establishes automated testing, linting, and deployment pipelines using GitHub Actions and Google Cloud Run.

---

## ✅ What Was Implemented

### 1. GitHub Actions CI/CD Pipeline (`.github/workflows/ci.yml`)

**Backend Testing Matrix:**
- Python 3.11 & 3.12 compatibility testing
- Ruff linting (import ordering, style checks)
- Black formatting validation
- MyPy type checking
- Pytest with coverage reports
- Coverage upload to CodeCov

**Frontend Testing:**
- ESLint linting checks
- TypeScript compilation
- Production build verification
- Playwright E2E tests (5-minute timeout)
- Artifact storage (Playwright reports)

**Docker Build & Push:**
- Multi-stage builds for efficiency
- GHCR (GitHub Container Registry) push
- Layer caching optimization
- Automatic tagging (branch, semver, SHA)

**Security Scanning:**
- Trivy vulnerability scanning
- SARIF format integration
- GitHub Security tab uploads

**Production Deployment:**
- Auto-deploy on main branch push
- Cloud Run deployment (backend + frontend)
- Environment variables from secrets
- Health checks pre-deployment

### 2. Docker Images

**Backend (`Dockerfile`):**
- Python 3.12-slim base
- Multi-stage build
- Non-root user (appuser)
- Uvicorn with 4 workers
- Health check endpoint
- Image size: ~200MB

**Frontend (`frontend/Dockerfile`):**
- Node 18-alpine builder stage
- Nginx-alpine runtime
- Built assets (dist/)
- Security headers in nginx
- Image size: ~50MB

### 3. Nginx Configuration (`frontend/nginx.conf`)

```nginx
- SPA routing (try_files)
- API proxy to backend
- Cache control (versioned assets)
- Gzip compression
- Security headers
```

### 4. Cloud Run Deployment

**Backend Service:**
- Container: video-genius-backend
- Memory: 512MB
- CPU: 1 vCPU
- Max instances: 100
- Min instances: 1
- Timeout: 60 seconds

**Frontend Service:**
- Container: video-genius-frontend
- Memory: 256MB
- CPU: 0.5 vCPU
- Max instances: 50
- Min instances: 1
- Timeout: 60 seconds

---

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `.github/workflows/ci.yml` | GitHub Actions pipeline |
| `Dockerfile` | Backend Docker image |
| `frontend/Dockerfile` | Frontend Docker image |
| `frontend/nginx.conf` | Frontend Nginx config |
| `deploy-cloud-run.sh` | Manual deployment script |
| `cloudbuild.yaml` | Google Cloud Build config |

---

## 🚀 Deployment Methods

### Method 1: GitHub Actions (Automated)

**Trigger:** Push to `main` branch

```bash
git commit -m "feature: add new endpoint"
git push origin main

# Workflow automatically runs:
# 1. Tests backend (Python 3.11, 3.12)
# 2. Tests frontend (ESLint, TypeScript, E2E)
# 3. Builds Docker images
# 4. Scans for vulnerabilities
# 5. Deploys to Cloud Run
```

### Method 2: Manual Cloud Run Deploy

```bash
chmod +x deploy-cloud-run.sh

# Deploy backend only
./deploy-cloud-run.sh backend

# Deploy frontend only
./deploy-cloud-run.sh frontend

# Deploy both
./deploy-cloud-run.sh both
```

### Method 3: Google Cloud Build (gcloud)

```bash
gcloud builds submit \
  --config cloudbuild.yaml \
  --substitutions=SHORT_SHA=$(git rev-parse --short HEAD)
```

---

## 📊 Pipeline Status

### GitHub Actions Jobs

1. **backend-test** (Matrix: Python 3.11, 3.12)
   - ✅ Ruff lint
   - ✅ Black format check
   - ✅ MyPy type check
   - ✅ Pytest + coverage

2. **frontend-test**
   - ✅ ESLint
   - ✅ TypeScript compile
   - ✅ npm build
   - ✅ Playwright E2E

3. **build-and-push** (On main branch only)
   - ✅ Build backend image
   - ✅ Build frontend image
   - ✅ Push to GHCR

4. **security-scan**
   - ✅ Trivy vulnerability scan
   - ✅ Upload to GitHub Security

5. **deploy-production** (Main branch only)
   - ✅ Deploy backend to Cloud Run
   - ✅ Deploy frontend to Cloud Run
   - ✅ Create deployment summary

---

## 🔐 Required Secrets (GitHub)

Configure in Settings → Secrets and variables → Actions:

```
SUPABASE_URL              # https://khkiebkjaqncqpjsknup.supabase.co
SUPABASE_ANON_KEY         # Public API key
SUPABASE_SERVICE_ROLE_KEY # Service role key
GCP_SA_KEY                # Google Cloud Service Account JSON
```

---

## 📈 Performance Metrics

| Component | Size | Build Time | Deploy Time |
|-----------|------|-----------|------------|
| Backend | ~200MB | 2-3 min | 3-5 min |
| Frontend | ~50MB | 1-2 min | 2-3 min |
| **Total** | ~250MB | **3-5 min** | **5-8 min** |

---

## 🔄 Workflow Triggers

```yaml
on:
  push:
    branches: [main, develop]    # Run on push
  pull_request:
    branches: [main, develop]    # Run on PR
```

**Jobs by trigger:**
- PR: Tests only (no deploy)
- Push to develop: Tests only
- Push to main: Tests → Build → Deploy

---

## ✅ Health Checks

### Backend Health
```bash
curl https://video-genius-backend.run.app/health
# Returns: {"status": "healthy"}
```

### Frontend Health
```bash
curl https://video-genius-frontend.run.app
# Returns: 200 OK with HTML
```

### API Endpoint
```bash
curl https://video-genius-backend.run.app/api/v1/tasks | jq 'length'
# Returns: 13 (number of tasks)
```

---

## 📝 Logs & Monitoring

### Cloud Run Logs
```bash
# Backend
gcloud run logs read video-genius-backend --limit 50

# Frontend
gcloud run logs read video-genius-frontend --limit 50
```

### GitHub Actions Logs
```
Repository → Actions tab → Select workflow → View logs
```

### Local Testing
```bash
# Backend tests
pytest tests/ -v --cov=backend

# Frontend tests
cd frontend && npm run test:e2e

# Docker build locally
docker build -t video-genius-backend .
docker run -p 8000:8000 video-genius-backend
```

---

## 🚨 Troubleshooting

### Issue: Tests failing in CI but passing locally

**Solutions:**
- Verify Python 3.11, 3.12 compatibility
- Check environment variables in GitHub secrets
- Run tests locally: `pytest tests/ -v`

### Issue: Docker image build fails

**Solutions:**
- Check Dockerfile syntax: `docker build .`
- Verify requirements files exist
- Check for large files in .dockerignore

### Issue: Cloud Run deployment fails

**Solutions:**
- Verify GCP service account has permissions
- Check secrets are set: `gcloud secrets list`
- Test locally: `docker run video-genius-backend`

### Issue: Frontend shows 404

**Solutions:**
- Verify nginx.conf try_files rule
- Check Vite build output: `npm run build`
- Verify API proxy URL is correct

---

## 📋 Next Steps (Phase 7)

1. [ ] Configure monitoring & alerts (Cloud Logging)
2. [ ] Setup error reporting (Cloud Error Reporting)
3. [ ] Configure autoscaling policies
4. [ ] Setup database backups
5. [ ] Implement rate limiting & DDoS protection

---

## 📚 Documentation

- [GitHub Actions](https://docs.github.com/en/actions)
- [Google Cloud Run](https://cloud.google.com/run/docs)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/concepts/)

---

**Status**: ✅ CI/CD Pipeline Ready for Production
