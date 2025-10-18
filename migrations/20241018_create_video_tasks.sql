-- ============================================================================
-- Create Video Tasks Table for Dashboard
-- ============================================================================
-- This migration creates the video_tasks table that stores dashboard tasks
-- which can be synchronized with GitHub issues.

-- Create ENUM types
CREATE TYPE task_status_enum AS ENUM (
    'todo',
    'in-progress',
    'blocked',
    'completed'
);

CREATE TYPE task_priority_enum AS ENUM (
    'low',
    'medium',
    'high',
    'critical'
);

CREATE TYPE task_phase_enum AS ENUM (
    'phase-1',
    'phase-2',
    'phase-3',
    'phase-4'
);

-- Create video_tasks table
CREATE TABLE IF NOT EXISTS video_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Task Content
    title VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',
    
    -- Task Status & Priority
    status task_status_enum NOT NULL DEFAULT 'todo',
    priority task_priority_enum NOT NULL DEFAULT 'medium',
    phase task_phase_enum NOT NULL DEFAULT 'phase-1',
    
    -- Assignments & Dates
    assignee VARCHAR(255),
    due_date TIMESTAMP WITH TIME ZONE,
    
    -- GitHub Integration
    github_issue_id INTEGER,
    github_issue_url VARCHAR(512),
    github_issue_synced_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    
    -- Constraints
    CONSTRAINT task_title_not_empty CHECK (title <> ''),
    CONSTRAINT unique_github_issue UNIQUE (github_issue_id)
);

-- Create indexes for common queries
CREATE INDEX idx_video_tasks_status ON video_tasks(status);
CREATE INDEX idx_video_tasks_priority ON video_tasks(priority);
CREATE INDEX idx_video_tasks_phase ON video_tasks(phase);
CREATE INDEX idx_video_tasks_assignee ON video_tasks(assignee);
CREATE INDEX idx_video_tasks_due_date ON video_tasks(due_date);
CREATE INDEX idx_video_tasks_github_issue_id ON video_tasks(github_issue_id);
CREATE INDEX idx_video_tasks_created_at ON video_tasks(created_at DESC);
CREATE INDEX idx_video_tasks_updated_at ON video_tasks(updated_at DESC);

-- Create compound indexes for common filters
CREATE INDEX idx_video_tasks_phase_status ON video_tasks(phase, status);
CREATE INDEX idx_video_tasks_phase_priority ON video_tasks(phase, priority);

-- Enable Row Level Security
ALTER TABLE video_tasks ENABLE ROW LEVEL SECURITY;

-- Create RLS policy: Allow authenticated users to read all tasks
CREATE POLICY "Allow authenticated users to read tasks"
    ON video_tasks FOR SELECT
    USING (auth.role() = 'authenticated_user');

-- Create RLS policy: Allow authenticated users to create tasks
CREATE POLICY "Allow authenticated users to create tasks"
    ON video_tasks FOR INSERT
    WITH CHECK (auth.role() = 'authenticated_user');

-- Create RLS policy: Allow authenticated users to update tasks
CREATE POLICY "Allow authenticated users to update tasks"
    ON video_tasks FOR UPDATE
    USING (auth.role() = 'authenticated_user')
    WITH CHECK (auth.role() = 'authenticated_user');

-- Create RLS policy: Allow authenticated users to delete tasks
CREATE POLICY "Allow authenticated users to delete tasks"
    ON video_tasks FOR DELETE
    USING (auth.role() = 'authenticated_user');

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_video_tasks_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update updated_at on changes
CREATE TRIGGER video_tasks_updated_at_trigger
    BEFORE UPDATE ON video_tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_video_tasks_updated_at();

-- Create view for task statistics
CREATE OR REPLACE VIEW video_tasks_stats AS
SELECT
    phase,
    status,
    priority,
    COUNT(*) as count,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_count,
    COUNT(CASE WHEN status = 'blocked' THEN 1 END) as blocked_count
FROM video_tasks
GROUP BY phase, status, priority;

-- Create view for phase progress
CREATE OR REPLACE VIEW video_tasks_phase_progress AS
SELECT
    phase,
    COUNT(*) as total_tasks,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_tasks,
    ROUND(
        100.0 * COUNT(CASE WHEN status = 'completed' THEN 1 END) / COUNT(*),
        2
    ) as completion_percentage,
    COUNT(CASE WHEN status = 'in-progress' THEN 1 END) as in_progress_tasks,
    COUNT(CASE WHEN status = 'blocked' THEN 1 END) as blocked_tasks,
    COUNT(CASE WHEN status = 'todo' THEN 1 END) as todo_tasks
FROM video_tasks
GROUP BY phase;

-- Insert sample data
INSERT INTO video_tasks (
    id, title, description, status, priority, phase,
    assignee, due_date, created_by
) VALUES
    (
        'a0000000-0000-0000-0000-000000000001'::uuid,
        'MVP Dashboard Setup',
        'Create initial dashboard infrastructure and UI components',
        'completed',
        'high',
        'phase-1',
        'priscilla',
        '2024-10-25 00:00:00+00',
        'system'
    ),
    (
        'a0000000-0000-0000-0000-000000000002'::uuid,
        'API Integration',
        'Implement FastAPI routes for dashboard data',
        'in-progress',
        'high',
        'phase-1',
        'team',
        '2024-10-30 00:00:00+00',
        'system'
    ),
    (
        'a0000000-0000-0000-0000-000000000003'::uuid,
        'Real-time Subscriptions',
        'Setup Supabase Realtime for live task updates',
        'in-progress',
        'critical',
        'phase-1',
        'priscilla',
        '2024-11-02 00:00:00+00',
        'system'
    ),
    (
        'a0000000-0000-0000-0000-000000000004'::uuid,
        'GitHub Sync Service',
        'Create bidirectional sync between GitHub and dashboard',
        'todo',
        'high',
        'phase-1',
        'team',
        '2024-11-05 00:00:00+00',
        'system'
    ),
    (
        'a0000000-0000-0000-0000-000000000005'::uuid,
        'Testing Suite',
        'Write comprehensive tests for dashboard API',
        'todo',
        'medium',
        'phase-1',
        NULL,
        '2024-11-10 00:00:00+00',
        'system'
    ),
    (
        'a0000000-0000-0000-0000-000000000006'::uuid,
        'AI Integration Layer',
        'Integrate Vertex AI with task processing',
        'blocked',
        'critical',
        'phase-2',
        'priscilla',
        '2024-12-01 00:00:00+00',
        'system'
    ),
    (
        'a0000000-0000-0000-0000-000000000007'::uuid,
        'Advanced Analytics',
        'Implement task velocity and burndown analytics',
        'todo',
        'high',
        'phase-3',
        NULL,
        '2025-01-15 00:00:00+00',
        'system'
    ),
    (
        'a0000000-0000-0000-0000-000000000008'::uuid,
        'Performance Optimization',
        'Optimize dashboard queries and caching',
        'todo',
        'medium',
        'phase-3',
        NULL,
        '2025-01-20 00:00:00+00',
        'system'
    ),
    (
        'a0000000-0000-0000-0000-000000000009'::uuid,
        'Production Deployment',
        'Deploy dashboard to production environment',
        'todo',
        'critical',
        'phase-3',
        'team',
        '2025-02-01 00:00:00+00',
        'system'
    ),
    (
        'a0000000-0000-0000-0000-000000000010'::uuid,
        'Monitoring & Alerts',
        'Setup monitoring and alerting for dashboard',
        'todo',
        'high',
        'phase-3',
        NULL,
        '2025-02-05 00:00:00+00',
        'system'
    ),
    (
        'a0000000-0000-0000-0000-000000000011'::uuid,
        'Documentation',
        'Create comprehensive dashboard documentation',
        'in-progress',
        'medium',
        'phase-4',
        'priscilla',
        '2025-02-15 00:00:00+00',
        'system'
    )
ON CONFLICT DO NOTHING;
