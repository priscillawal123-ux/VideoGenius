# ⚡ Quick Start - Phase 1 Complete

**Status**: ✅ Ready to Run Locally  
**Time**: 5-10 minutes to get everything working

---

## 🚀 Get Everything Running (3 Terminal Windows)

### Terminal 1: Start Backend API

```bash
cd /home/walland/Downloads/Video-Genius

# Activate Python environment
source .venv/bin/activate

# Start FastAPI server
uvicorn backend.api.main:app --reload --port 8000

# Expected output:
# INFO:     Uvicorn running on http://127.0.0.1:8000
# INFO:     Application startup complete
```

### Terminal 2: Start Frontend

```bash
cd /home/walland/Downloads/Video-Genius/frontend

# First time: install dependencies
npm install

# Start development server
npm run dev

# Expected output:
# Local: http://localhost:5173/
# press h to show help
```

### Terminal 3: Test the Connection

```bash
# Test API health
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "message": "Server is running",
  "environment": "development",
  "gcp_project": "video-genius-prod-v1",
  "features": {
    "circuit_breaker": true,
    "caching": true,
    "uvloop": true
  }
}
```

---

## 🌐 Open in Browser

### 1. Frontend (Main App)
```
http://localhost:5173
```
You should see:
- ✅ Header: "🎬 Video Genius"
- ✅ Navigation menu
- ✅ Dashboard component
- ✅ Footer with API endpoint

### 2. API Documentation
```
http://localhost:8000/docs
```
Swagger UI with all endpoints

### 3. API Health Check
```
http://localhost:8000/health
```
JSON response with status

---

## 🧪 Test API from Browser Console

Open browser F12 → Console:

### Test 1: Health Check
```javascript
fetch('http://localhost:8000/health')
  .then(r => r.json())
  .then(d => console.log('✅ Health:', d))
  .catch(e => console.error('❌ Error:', e))
```

### Test 2: Dashboard Stats
```javascript
fetch('http://localhost:8000/api/v1/dashboard/stats')
  .then(r => r.json())
  .then(d => console.log('✅ Stats:', d))
  .catch(e => console.error('❌ Error:', e))
```

### Test 3: Get Tasks
```javascript
fetch('http://localhost:8000/api/v1/dashboard/tasks')
  .then(r => r.json())
  .then(d => console.log('✅ Tasks:', d))
  .catch(e => console.error('❌ Error:', e))
```

---

## 📁 Project Structure

```
Video-Genius/
├── backend/
│   ├── api/
│   │   └── main.py              # FastAPI app
│   ├── core/
│   │   └── config.py            # Configuration
│   └── routes/
│       └── dashboard.py         # Dashboard endpoints
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Main app
│   │   ├── App.css              # Styling
│   │   ├── components/
│   │   │   ├── DashboardRoadmap.tsx   # Dashboard
│   │   │   └── DashboardRoadmap.css   # Styles
│   │   └── lib/
│   │       ├── api.ts           # API client
│   │       └── supabase.ts      # Database client
│   ├── .env.local               # Configuration
│   └── package.json             # Dependencies
│
├── migrations/
│   └── 20241018_create_video_tasks.sql  # Database
│
├── requirements.txt             # Python deps
└── Dockerfile                   # Container build
```

---

## 🎯 Available API Endpoints

```bash
# Root
GET http://localhost:8000/

# Health
GET http://localhost:8000/health

# API Documentation
GET http://localhost:8000/docs
GET http://localhost:8000/redoc

# Dashboard Stats
GET http://localhost:8000/api/v1/dashboard/stats

# Dashboard Phases
GET http://localhost:8000/api/v1/dashboard/phases

# Dashboard Tasks
GET http://localhost:8000/api/v1/dashboard/tasks
POST http://localhost:8000/api/v1/dashboard/tasks

# Update Task
PATCH http://localhost:8000/api/v1/dashboard/tasks/{id}

# Delete Task
DELETE http://localhost:8000/api/v1/dashboard/tasks/{id}

# Authentication
POST http://localhost:8000/api/v1/auth/login
POST http://localhost:8000/api/v1/auth/register
GET http://localhost:8000/api/v1/auth/me
```

---

## 📱 Frontend Components

### Current
- ✅ App.tsx - Main application
- ✅ DashboardRoadmap.tsx - Dashboard with 3 views
- ✅ API Client - All endpoints ready
- ✅ Supabase Client - Real-time ready

### What You Can Do
- View project timeline
- Switch between Kanban/Timeline/Burndown views
- See project statistics
- Track progress

---

## 🔧 Troubleshooting

### "Cannot find module" error
```bash
# Frontend missing dependencies
cd frontend
npm install

# Backend missing packages
pip install -r requirements-prod.txt
```

### "Connection refused" error
```bash
# Make sure backend is running
# Terminal 1: Check if listening on 8000
lsof -i :8000

# If nothing: Start backend
source .venv/bin/activate
uvicorn backend.api.main:app --reload --port 8000
```

### CORS errors
```bash
# This is expected if frontend on different port
# API has CORS enabled for localhost
# No changes needed for local dev
```

### Supabase connection failed
```bash
# This is OK for now - backend doesn't need it
# Frontend will fail until database migration runs
# See: INTEGRATION_GUIDE.md Phase 2 for database setup
```

---

## 📊 Next Steps

1. ✅ **Phase 1: Frontend Setup** - DONE
2. ⏳ **Phase 2: Backend Connection** (1 hour)
   - Connect Dashboard to real API data
   - Implement real-time updates
   - Test with live data

3. ⏳ **Phase 3: GitHub Integration** (1 hour)
   - Setup GitHub sync
   - Test bidirectional sync

---

## 🎓 Learn More

- **API Docs**: http://localhost:8000/docs (when running)
- **Frontend Setup**: See PHASE_1_COMPLETE.md
- **Integration Guide**: See INTEGRATION_GUIDE.md
- **Domain Config**: See DOMAIN_CONFIGURATION.md
- **Deployment**: See DEPLOYMENT_SUCCESS.md

---

## ⏱️ Time Breakdown

| Task | Time | Status |
|------|------|--------|
| Backend startup | 2 min | ✅ Quick |
| Frontend install | 3 min | ✅ Quick |
| Frontend startup | 1 min | ✅ Quick |
| First load | 2 min | ✅ Quick |
| API tests | 2 min | ✅ Quick |
| **Total** | **~10 min** | **✅ Done** |

---

## 🎉 You're All Set!

Everything is configured and ready to run locally.

Next: Follow **Phase 2: Backend Connection** in INTEGRATION_GUIDE.md

**Questions?** Check the troubleshooting section or review the documentation files.

Happy coding! 🚀
