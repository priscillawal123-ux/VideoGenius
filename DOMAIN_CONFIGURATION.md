# 🌐 Domain Configuration: videogenius.com.br

**Date**: October 18, 2025  
**Status**: ✅ Frontend Phase 1 Complete - Ready for Domain Setup

---

## 📍 Current Status

### Backend (Cloud Run)
- ✅ **Temporary URL**: https://video-genius-api-vch3lr5s3a-uc.a.run.app
- ✅ **Custom Domain Ready**: api.videogenius.com.br (to be configured)
- ✅ Service running and healthy
- ✅ HTTPS/SSL ready

### Frontend (Local Dev - Ready to Deploy)
- ✅ **Local URL**: http://localhost:5173 (development)
- ✅ **Production Ready**: Can be deployed to Firebase, Vercel, or Netlify
- ✅ All components integrated
- ✅ Environment configured

---

## 🔧 Step 1: DNS Configuration for videogenius.com.br

### Where to Configure DNS:
Your domain registrar (GoDaddy, Namecheap, HostGator, Registro.br, etc.)

### Option A: Using CNAME (Recommended for Google Cloud Run)

**Add these DNS records**:

```
Record Type: CNAME
Name: api
Value: ghs.googleusercontent.com

Record Type: CNAME
Name: www
Value: (Your frontend domain)
```

**Result**:
- `api.videogenius.com.br` → Cloud Run API
- `www.videogenius.com.br` → Frontend domain

### Option B: Using A Records (Alternative)

Get your Cloud Run static IP:
```bash
gcloud compute addresses create video-genius-ip \
  --region us-central1 \
  --global

gcloud compute addresses describe video-genius-ip \
  --global \
  --format="value(address)"
```

Then add:
```
Record Type: A
Name: api
Value: <IP_ADDRESS_FROM_ABOVE>
```

---

## ☁️ Step 2: Link Custom Domain to Cloud Run

### Via gcloud Command Line:

```bash
# Map api.videogenius.com.br to Cloud Run
gcloud run domain-mappings create \
  --service=video-genius-api \
  --domain=api.videogenius.com.br \
  --region=us-central1

# Verify the mapping
gcloud run domain-mappings list

# Check status
gcloud run domain-mappings describe api.videogenius.com.br \
  --region=us-central1
```

### Via Google Cloud Console:

1. Go to Cloud Run → video-genius-api service
2. Click "Manage Custom Domains"
3. Click "Add Mapping"
4. Enter: `api.videogenius.com.br`
5. Click "Add"
6. Follow verification steps

---

## ✅ Step 3: Verify DNS Propagation

### Check DNS Resolution:
```bash
# Using dig
dig api.videogenius.com.br

# Using nslookup
nslookup api.videogenius.com.br

# Using host
host api.videogenius.com.br

# DNS lookup propagation checker online:
# https://www.whatsmydns.net/
```

### Expected Result:
```
api.videogenius.com.br has address: 199.36.158.100 (or similar GCP IP)
```

### Check SSL Certificate:
```bash
curl -I https://api.videogenius.com.br/

# Should return:
# HTTP/2 200
# content-type: application/json
```

---

## 🚀 Step 4: Update Frontend Configuration

After domain is live, update environment:

### `.env.local` (Development - Keep as is)
```bash
VITE_API_URL=http://localhost:8000
```

### `.env.production` (For production build)
```bash
# Create this file
VITE_API_URL=https://api.videogenius.com.br
VITE_SUPABASE_URL=https://dfxffpdhxrqzybzjsyxg.supabase.co
VITE_SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 🌍 Step 5: Frontend Deployment Options

### Option A: Firebase Hosting (Recommended)

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Initialize Firebase
firebase init hosting

# Build frontend
cd frontend
npm run build

# Deploy
firebase deploy

# Result: yourproject.web.app
```

### Option B: Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd frontend
vercel

# Automatic HTTPS and custom domain support
```

### Option C: Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
cd frontend
netlify deploy --prod

# Custom domain: Settings → Domain management
```

### Option D: GitHub Pages (Free)

```bash
# Update vite.config.ts
export default {
  base: '/VideoGenius/',
  // ...
}

# Build and deploy
npm run build
git add dist/
git commit -m "build: production build"
git push
```

---

## 📋 Local Development Setup

### Start Backend (Terminal 1)

```bash
cd /home/walland/Downloads/Video-Genius

# Activate environment
source .venv/bin/activate

# Run API server
uvicorn backend.api.main:app --reload --port 8000

# Output:
# ✅ Uvicorn running on http://127.0.0.1:8000
# ✅ Reload enabled
```

### Start Frontend (Terminal 2)

```bash
cd /home/walland/Downloads/Video-Genius/frontend

# Install dependencies (first time only)
npm install

# Start dev server
npm run dev

# Output:
# ✅ Local: http://localhost:5173
# ✅ use --host to expose
```

### Test Both (Terminal 3)

```bash
# Check API health
curl http://localhost:8000/health

# Check frontend loads
curl http://localhost:5173

# Check API is accessible from frontend
# Open browser: http://localhost:5173
# Open console: F12 → Console
# Run: fetch('http://localhost:8000/health').then(r => r.json()).then(d => console.log(d))
```

---

## 🔒 HTTPS/SSL Certificate

### Automatic (Cloud Run + Custom Domain)
- ✅ Cloud Run automatically provides SSL via Google
- ✅ Certificate auto-renews every 90 days
- ✅ No additional setup required

### Verify Certificate:
```bash
# Check certificate
openssl s_client -connect api.videogenius.com.br:443 -servername api.videogenius.com.br

# Should show:
# subject=CN = api.videogenius.com.br
# issuer=C = US, O = Google Trust Services LLC, ...
```

---

## 📊 Domain Summary

### Current Architecture
```
┌─────────────────────────────────────────────────┐
│          videogenius.com.br (Your Domain)        │
├──────────────────────┬──────────────────────────┤
│   api subdomain      │   www/root subdomain      │
│ api.videogenius      │ videogenius.com.br        │
│ .com.br              │ or www.videogenius        │
│                      │ .com.br                   │
├──────────────────────┼──────────────────────────┤
│ Cloud Run API        │ Frontend (Firebase/       │
│ (Python FastAPI)     │ Vercel/Netlify)          │
│ Port: 8080 (internal)│ Port: 443 (HTTPS)        │
│ HTTPS: Yes           │ HTTPS: Yes               │
│ Health: ✅           │ Status: Ready             │
└──────────────────────┴──────────────────────────┘
```

### DNS Records Needed
```
api.videogenius.com.br    CNAME    ghs.googleusercontent.com
www.videogenius.com.br    CNAME    <frontend-domain>
videogenius.com.br        A        <frontend-ip>
```

---

## 🎯 Quick Checklist

### Pre-Deployment
- [ ] Domain `videogenius.com.br` purchased
- [ ] Access to domain registrar account
- [ ] Backend running on Cloud Run
- [ ] Frontend built and ready to deploy

### DNS Configuration
- [ ] CNAME record for `api.videogenius.com.br` added
- [ ] CNAME record for `www.videogenius.com.br` added
- [ ] DNS propagated (24-48 hours)
- [ ] SSL certificate issued

### Testing
- [ ] API accessible at `https://api.videogenius.com.br`
- [ ] Frontend deployed and accessible
- [ ] API → Frontend communication working
- [ ] Real-time Supabase subscriptions working
- [ ] HTTPS working for both domains

### Post-Deployment
- [ ] Monitor Cloud Run logs
- [ ] Set up alerting
- [ ] Configure monitoring dashboard
- [ ] Document support contacts

---

## 🚨 Troubleshooting

### Domain not resolving
```bash
# Clear DNS cache (macOS)
sudo dscacheutil -flushcache

# Clear DNS cache (Linux)
sudo systemctl restart systemd-resolved

# Wait 24-48 hours for propagation
```

### SSL Certificate not working
```bash
# Check certificate status
curl -vI https://api.videogenius.com.br

# Should show Certificate Details
# If failed: Wait 30 minutes for Cloud Run to provision cert
```

### Frontend can't reach API
```bash
# Check environment variables
cat frontend/.env.local

# Should have:
# VITE_API_URL=https://api.videogenius.com.br

# Check CORS:
# API logs should show request headers
```

### 404 Not Found on API domain
```bash
# Verify service is mapped
gcloud run domain-mappings list

# Check service is running
gcloud run services describe video-genius-api --region us-central1
```

---

## 📞 Support Links

- **Cloud Run Console**: https://console.cloud.google.com/run?project=video-genius-prod-v1
- **DNS Checker**: https://www.whatsmydns.net/
- **SSL Checker**: https://www.sslshopper.com/ssl-checker.html
- **API Health**: https://api.videogenius.com.br/health
- **Swagger Docs**: https://api.videogenius.com.br/docs

---

**Next Phase**: Phase 2 - Backend Connection (1 hour)  
**Overall Progress**: 75% (Phases 1-2 done, Phase 3 remaining)
