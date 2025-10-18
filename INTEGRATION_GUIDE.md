# 🎯 Integration Guide - Video Genius Dashboard

Now that the **Video Genius API** is deployed and running on Google Cloud Run, here's how to integrate it with the frontend dashboard.

## 📍 API Endpoint
```
https://video-genius-api-752423186317.us-central1.run.app
```

## ✅ What's Ready

### Backend API
- ✅ Service deployed on Cloud Run
- ✅ Health checks passing
- ✅ Authentication endpoints available
- ✅ Dashboard endpoints defined and ready for implementation
- ✅ Real-time dashboard component created (React/TypeScript)

### Database Schema
- ✅ SQL migration created with sample data
- ✅ 11 sample tasks ready for import
- ✅ Supabase RLS policies defined
- ✅ Real-time subscriptions configured

### Frontend Components
- ✅ DashboardRoadmap component (2600 lines TypeScript)
- ✅ 3 visualization modes (Timeline, Kanban, Burndown)
- ✅ CSS styling with responsive design
- ✅ Real-time update handler

## 🚀 Next Steps (In Order)

### Phase 1: Frontend Setup (30 minutes)

#### Step 1: Add Environment Configuration
Create `.env.local` in your React app:
```env
# API Configuration
REACT_APP_API_URL=https://video-genius-api-752423186317.us-central1.run.app

# Supabase Configuration (when ready)
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_ANON_KEY=your-anon-key

# GitHub Integration (optional)
REACT_APP_GITHUB_TOKEN=your-github-token
```

#### Step 2: Import Dashboard Component
Update your `App.tsx`:
```typescript
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import DashboardRoadmap from './components/DashboardRoadmap';

function App() {
  return (
    <Router>
      <Routes>
        {/* Other routes... */}
        <Route path="/dashboard" element={<DashboardRoadmap />} />
      </Routes>
    </Router>
  );
}
```

#### Step 3: Add Navigation Link
Add to your nav component:
```typescript
<Link to="/dashboard">📊 Dashboard</Link>
```

#### Step 4: Test Component
```bash
npm start
# Navigate to http://localhost:3000/dashboard
```

### Phase 2: Backend Integration (1 hour)

#### Step 1: Database Setup
Execute migration on Supabase:
```sql
-- Copy contents of migrations/20241018_create_video_tasks.sql
-- Execute in Supabase SQL Editor
```

#### Step 2: Enable Realtime
In Supabase:
1. Go to Realtime > Publications
2. Enable `video_tasks` table for realtime
3. Save changes

#### Step 3: Set Up Authentication
```typescript
// In your Supabase client:
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.REACT_APP_SUPABASE_URL!,
  process.env.REACT_APP_SUPABASE_ANON_KEY!
)
```

#### Step 4: Connect Dashboard to Backend
Update DashboardRoadmap to use real data:
```typescript
const [tasks, setTasks] = useState<Task[]>([])
const [loading, setLoading] = useState(true)

useEffect(() => {
  // Fetch from API
  const fetchTasks = async () => {
    const response = await fetch(
      `${process.env.REACT_APP_API_URL}/api/v1/dashboard/tasks`
    )
    const data = await response.json()
    setTasks(data)
    setLoading(false)
  }

  fetchTasks()

  // Subscribe to real-time updates
  const channel = supabase
    .channel('public:video_tasks')
    .on(
      'postgres_changes',
      { event: '*', schema: 'public', table: 'video_tasks' },
      (payload) => {
        // Handle updates
      }
    )
    .subscribe()

  return () => channel.unsubscribe()
}, [])
```

### Phase 3: GitHub Integration (1 hour)

#### Step 1: Configure GitHub Token
1. Generate personal access token on GitHub
2. Add to environment: `REACT_APP_GITHUB_TOKEN`

#### Step 2: Implement Sync Service
The sync service is ready at: `backend/services/github_sync_service.py`

#### Step 3: Add Sync Endpoint to API
```python
# In backend/api/routes/dashboard.py
@router.post("/sync-github")
async def sync_github():
    """Sync GitHub issues to dashboard tasks."""
    service = GitHubSyncService()
    result = await service.sync_github_to_dashboard()
    return result
```

#### Step 4: Test Sync
```bash
curl -X POST https://your-api/api/v1/dashboard/sync-github
```

## 📋 Testing Checklist

### API Testing
- [ ] Root endpoint returns API info
- [ ] Health check responds
- [ ] Swagger UI accessible at `/docs`
- [ ] Auth endpoints available
- [ ] Dashboard endpoints callable

### Frontend Testing
- [ ] Component renders without errors
- [ ] Can switch between views (Timeline/Kanban/Burndown)
- [ ] Sample data displays correctly
- [ ] Responsive design works on mobile

### Backend Testing
- [ ] Database migration executed
- [ ] Sample tasks inserted
- [ ] Real-time subscriptions working
- [ ] GitHub sync functional

### Full Integration Testing
- [ ] Frontend receives live task updates
- [ ] Changing a task updates in real-time
- [ ] Multiple users see same updates
- [ ] Performance acceptable with sample data

## 🐛 Troubleshooting

### API Not Responding
```bash
# Check if service is running
curl https://video-genius-api-752423186317.us-central1.run.app/health

# View recent logs
gcloud logging read "resource.labels.service_name=video-genius-api" \
  --project=video-genius-prod-v1 \
  --limit=50 \
  --format=json
```

### CORS Issues
The API has CORS enabled for:
- `http://localhost:3000` (dev)
- `http://localhost:5173` (Vite)
- Production domains (configure in `.env`)

### Supabase Connection Issues
1. Verify credentials in `.env`
2. Check network connectivity
3. Confirm table exists: `SELECT * FROM video_tasks LIMIT 1`
4. Check RLS policies are not too restrictive

### Real-time Updates Not Working
1. Verify Realtime is enabled on table
2. Check Supabase subscription channel name
3. Ensure JWT token has correct permissions
4. Check browser console for errors

## 📚 Documentation

- **API Specification**: See `DASHBOARD_README.md`
- **Implementation Details**: See `DASHBOARD_IMPLEMENTATION_SUMMARY.md`
- **Design System**: See `DASHBOARD_DESIGN_SYSTEM.md`
- **Deployment Info**: See `DEPLOYMENT_SUCCESS.md`
- **Quick Start**: See `QUICK_START.md`

## 🔗 Useful Links

- **API URL**: https://video-genius-api-752423186317.us-central1.run.app
- **Swagger UI**: https://video-genius-api-752423186317.us-central1.run.app/docs
- **Cloud Run Console**: https://console.cloud.google.com/run/detail/us-central1/video-genius-api
- **GitHub Repository**: https://github.com/priscillawal123-ux/VideoGenius
- **Cloud Logging**: https://console.cloud.google.com/logs?project=video-genius-prod-v1

## ⏱️ Estimated Timeline

| Phase | Task | Time | Status |
|-------|------|------|--------|
| 0 | Backend API Deployment | ✅ Complete | 🟢 DONE |
| 1 | Frontend Setup | 30 min | 🟡 Ready to Start |
| 2 | Backend Integration | 1 hour | 🟡 Ready to Start |
| 3 | GitHub Integration | 1 hour | 🟡 Ready to Start |
| 4 | Testing & QA | 1-2 hours | 🟡 Ready to Start |
| 5 | Production Deployment | 30 min | 🟡 Ready to Start |

**Total Estimated Time**: 4-5 hours to full integration

## ✨ Once You're Done

After integration, the dashboard will support:
- ✅ Real-time project tracking
- ✅ GitHub issues bidirectional sync
- ✅ Multiple visualization modes
- ✅ Team collaboration
- ✅ Analytics and metrics
- ✅ Mobile-responsive interface

---

**Questions?** Check the documentation files or review the sample code in the components directory.

**Ready to start?** Begin with Phase 1: Frontend Setup! 🚀
