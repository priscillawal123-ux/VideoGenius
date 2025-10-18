# 🗄️ Database Migration Instructions

## Phase 2: Database Setup

The `video_tasks` table needs to be created in your Supabase database to enable the Task API and Dashboard functionality.

### ✅ Option 1: Automatic Migration (Recommended)

```bash
# 1. Ensure you have the migration file
ls -la migrations/20241018_create_video_tasks.sql

# 2. Copy the SQL content to Supabase SQL Editor (see Option 2 below)
```

### 🔧 Option 2: Manual Migration (Via Supabase Dashboard)

**Step 1: Open Supabase SQL Editor**
```
1. Go to https://app.supabase.com
2. Select project: video-genius-prod-v1
3. Navigate to: SQL Editor
4. Click "+ New Query"
```

**Step 2: Copy Migration SQL**
```bash
# Copy all content from the migration file
cat migrations/20241018_create_video_tasks.sql
```

**Step 3: Paste & Execute**
```
1. Paste the entire SQL content into the SQL editor
2. Click "Run" (or Cmd+Enter)
3. Wait for completion (should take ~5 seconds)
```

**Expected Output:**
```
✅ ENUM type task_status_enum created
✅ ENUM type task_priority_enum created
✅ ENUM type task_phase_enum created
✅ Table video_tasks created
✅ Indexes created
✅ Row-Level Security (RLS) policies created
✅ Sample data inserted (11 tasks)
```

### 📋 What Gets Created

#### ENUM Types (for type safety)
- `task_status_enum` - Values: todo, in-progress, blocked, completed
- `task_priority_enum` - Values: low, medium, high, critical
- `task_phase_enum` - Values: phase-1, phase-2, phase-3, phase-4

#### video_tasks Table
```sql
id              UUID PRIMARY KEY (auto-generated)
title           VARCHAR(255) - Task title
description     TEXT - Full description
status          task_status_enum - Current status
priority        task_priority_enum - Task priority
phase           task_phase_enum - Project phase
assignee        VARCHAR(255) - Assigned person
due_date        TIMESTAMP - When it's due
completed_date  TIMESTAMP - When completed
github_issue_id INTEGER - GitHub issue sync
github_issue_url VARCHAR(512) - GitHub link
github_issue_synced_at TIMESTAMP - Last sync time
created_at      TIMESTAMP - Created date
updated_at      TIMESTAMP - Updated date
```

#### Indexes (for performance)
- Index on `status` - Fast filtering by status
- Index on `phase` - Fast filtering by phase
- Index on `assignee` - Fast filtering by assignee
- Index on `github_issue_id` - Fast GitHub lookups

#### Row-Level Security (RLS)
- **Enable RLS**: ALL users can read and write video_tasks
- **Note**: In production, restrict this to authenticated users only

#### Sample Data
- 11 pre-loaded tasks across all phases
- Mix of statuses and priorities
- Ready for testing

### ✅ Verification

After running the migration, verify it worked:

**In Supabase Dashboard:**
```
1. Go to Tables → video_tasks
2. You should see 11 rows of sample data
3. Check Columns tab for the fields listed above
```

**Via API:**
```bash
# Test the API endpoint
curl http://localhost:8000/api/v1/tasks

# Expected response (11 tasks as JSON)
```

**Via Frontend:**
```
1. Start backend: uvicorn backend.api.main:app --reload
2. Start frontend: cd frontend && npm run dev
3. Open http://localhost:5173
4. Dashboard should show tasks from database
```

### 🚨 Troubleshooting

**Problem: ENUM types already exist**
```sql
-- Skip ENUM creation and run only the table creation
DROP TABLE IF EXISTS video_tasks CASCADE;
CREATE TABLE video_tasks (...);
```

**Problem: Table already exists**
```sql
-- Drop and recreate
DROP TABLE IF EXISTS video_tasks CASCADE;
DROP TYPE IF EXISTS task_status_enum CASCADE;
DROP TYPE IF EXISTS task_priority_enum CASCADE;
DROP TYPE IF EXISTS task_phase_enum CASCADE;

-- Then run full migration
```

**Problem: RLS errors**
```sql
-- If RLS policies fail, they're not critical
-- The table will still work without them
-- Add policies later for production security
```

### 🔐 Production Security

For production deployment, update RLS policies:

```sql
-- Only allow authenticated users
ALTER TABLE video_tasks ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can read their own tasks"
ON video_tasks FOR SELECT
USING (auth.uid()::text = assignee OR assignee IS NULL);

CREATE POLICY "Users can update their own tasks"
ON video_tasks FOR UPDATE
USING (auth.uid()::text = assignee);
```

### 📚 Files Reference

- **SQL Migration**: `migrations/20241018_create_video_tasks.sql` (269 lines)
- **Backend API**: `backend/api/routes/tasks.py` (250+ lines)
- **Frontend Component**: `frontend/src/components/DashboardRoadmap.tsx` (691 lines)
- **Documentation**: `PHASE_2_INTEGRATION.md` (251 lines)

### ✅ Next Steps

**After Migration:**
1. ✅ Database table created
2. ✅ Backend API ready to use
3. ✅ Frontend will fetch from database
4. ⏳ Real-time sync active
5. ⏳ Ready for Phase 3 (GitHub Integration)

---

## 🎯 Command Reference

```bash
# View migration SQL
cat migrations/20241018_create_video_tasks.sql

# Test API after migration
curl -X GET http://localhost:8000/api/v1/tasks

# Test API with filters
curl "http://localhost:8000/api/v1/tasks?phase=phase-1&status=todo"

# Create new task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New task",
    "description": "Task description",
    "phase": "phase-2",
    "status": "in-progress",
    "priority": "high"
  }'
```

---

**Status**: Ready for migration execution ✅
**Last Updated**: 18 de outubro de 2025
