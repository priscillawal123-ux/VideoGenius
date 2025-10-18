-- 🔧 CLEAN DATABASE MIGRATION - Fixes "ENUM already exists" error
DROP TABLE IF EXISTS video_tasks CASCADE;
DROP VIEW IF EXISTS video_tasks_stats CASCADE;
DROP VIEW IF EXISTS video_tasks_phase_progress CASCADE;
DROP TRIGGER IF EXISTS video_tasks_updated_at_trigger ON video_tasks CASCADE;
DROP FUNCTION IF EXISTS update_video_tasks_updated_at() CASCADE;
DROP TYPE IF EXISTS task_status_enum CASCADE;
DROP TYPE IF EXISTS task_priority_enum CASCADE;
DROP TYPE IF EXISTS task_phase_enum CASCADE;

CREATE TYPE task_status_enum AS ENUM ('todo', 'in-progress', 'blocked', 'completed');
CREATE TYPE task_priority_enum AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE task_phase_enum AS ENUM ('phase-1', 'phase-2', 'phase-3', 'phase-4');

CREATE TABLE video_tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255) NOT NULL,
  description TEXT,
  status task_status_enum NOT NULL DEFAULT 'todo',
  priority task_priority_enum NOT NULL DEFAULT 'medium',
  phase task_phase_enum NOT NULL DEFAULT 'phase-1',
  assignee VARCHAR(255),
  due_date TIMESTAMP,
  completed_date TIMESTAMP,
  github_issue_id INTEGER UNIQUE,
  github_issue_url VARCHAR(512),
  github_issue_synced_at TIMESTAMP,
  github_issue_number INTEGER,
  github_pr_id INTEGER,
  github_pr_url VARCHAR(512),
  github_pr_synced_at TIMESTAMP,
  github_pr_number INTEGER,
  github_labels TEXT[],
  github_assignees TEXT[],
  github_milestone VARCHAR(255),
  tags TEXT[],
  dependencies UUID[],
  created_by VARCHAR(255),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_video_tasks_status ON video_tasks(status);
CREATE INDEX idx_video_tasks_priority ON video_tasks(priority);
CREATE INDEX idx_video_tasks_phase ON video_tasks(phase);
CREATE INDEX idx_video_tasks_assignee ON video_tasks(assignee);
CREATE INDEX idx_video_tasks_github_issue_id ON video_tasks(github_issue_id);
CREATE INDEX idx_video_tasks_created_at ON video_tasks(created_at);
CREATE INDEX idx_video_tasks_phase_status ON video_tasks(phase, status);

CREATE OR REPLACE FUNCTION update_video_tasks_updated_at() RETURNS TRIGGER AS $$ BEGIN NEW.updated_at = CURRENT_TIMESTAMP; RETURN NEW; END; $$ LANGUAGE plpgsql;
CREATE TRIGGER video_tasks_updated_at_trigger BEFORE UPDATE ON video_tasks FOR EACH ROW EXECUTE FUNCTION update_video_tasks_updated_at();

ALTER TABLE video_tasks ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow read" ON video_tasks FOR SELECT USING (true);
CREATE POLICY "Allow insert" ON video_tasks FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow update" ON video_tasks FOR UPDATE USING (true) WITH CHECK (true);
CREATE POLICY "Allow delete" ON video_tasks FOR DELETE USING (true);

INSERT INTO video_tasks (title, description, status, priority, phase, assignee, created_by) VALUES
('Frontend Setup', 'Initialize React with TypeScript and Vite', 'completed', 'high', 'phase-1', 'frontend-team', 'system'),
('Backend API Structure', 'Create FastAPI project structure', 'completed', 'high', 'phase-1', 'backend-team', 'system'),
('Database Schema Design', 'Design initial database schema', 'completed', 'high', 'phase-1', 'database-team', 'system'),
('API CRUD Endpoints', 'Implement CRUD endpoints', 'completed', 'high', 'phase-2', 'backend-team', 'system'),
('Dashboard Integration', 'Connect frontend to backend API', 'completed', 'high', 'phase-2', 'frontend-team', 'system'),
('Database Migration Setup', 'Create Supabase tables and migrations', 'in-progress', 'high', 'phase-2', 'database-team', 'system'),
('GitHub Integration', 'Setup GitHub Sync Service and webhooks', 'in-progress', 'high', 'phase-3', 'devops-team', 'system'),
('GitHub Label Mapping', 'Create priority and status label mapping', 'todo', 'medium', 'phase-3', 'devops-team', 'system'),
('DNS Configuration', 'Setup Google Cloud DNS and domain', 'completed', 'critical', 'phase-4', 'devops-team', 'system'),
('Systemd Services', 'Create systemd services for backend and frontend', 'in-progress', 'high', 'phase-4', 'devops-team', 'system'),
('Production Deployment', 'Deploy to Google Cloud Run with SSL', 'todo', 'critical', 'phase-4', 'devops-team', 'system');

