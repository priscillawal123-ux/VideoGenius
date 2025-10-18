/**
 * Dashboard Roadmap - Updated to use Real API
 * Fetches tasks and stats from backend
 */

import React, { useEffect, useState } from 'react'
import TaskService from '@/services/taskService'
import { api, Task, TaskStats } from '@/lib/api'
import './DashboardRoadmap.css'

interface DashboardStats {
  total: number
  completed: number
  inProgress: number
  blocked: number
  todo: number
  progress: number
}

export const DashboardRoadmap: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([])
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedPhase, setSelectedPhase] = useState<string | null>(null)

  // Phases
  const phases = ['phase-1', 'phase-2', 'phase-3', 'phase-4']
  const phaseNames: Record<string, string> = {
    'phase-1': 'MVP Core',
    'phase-2': 'AI Integration',
    'phase-3': 'Production Ready',
    'phase-4': 'Analytics & Scale',
  }

  /**
   * Load tasks and statistics from API
   */
  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Fetch tasks
      const fetchedTasks = await TaskService.fetchTasks()
      setTasks(fetchedTasks)

      // Fetch stats
      const fetchedStats = await api.getTaskStats()
      if (fetchedStats) {
        setStats({
          total: fetchedStats.total,
          completed: fetchedStats.completed,
          inProgress: fetchedStats.in_progress,
          blocked: fetchedStats.blocked,
          todo: fetchedStats.todo,
          progress: fetchedStats.progress_percentage,
        })
      }
    } catch (err) {
      console.error('Failed to load dashboard data:', err)
      setError('Failed to load tasks. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  /**
   * Setup initial data and polling
   */
  useEffect(() => {
    loadData()

    // Refresh data every 30 seconds
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [])

  /**
   * Get tasks for a specific phase
   */
  const getPhaseTasksCount = (phase: string) => {
    return tasks.filter((t) => t.phase === phase).length
  }

  /**
   * Get completed tasks for a specific phase
   */
  const getPhaseCompletedCount = (phase: string) => {
    return tasks.filter((t) => t.phase === phase && t.status === 'completed').length
  }

  /**
   * Calculate phase progress
   */
  const getPhaseProgress = (phase: string): number => {
    const phaseTasksCount = getPhaseTasksCount(phase)
    if (phaseTasksCount === 0) return 0
    const completed = getPhaseCompletedCount(phase)
    return Math.round((completed / phaseTasksCount) * 100)
  }

  /**
   * Get filtered tasks
   */
  const filteredTasks = selectedPhase
    ? tasks.filter((t) => t.phase === selectedPhase)
    : tasks

  return (
    <div className="dashboard-roadmap">
      {/* Header */}
      <div className="dashboard-header">
        <h1>🚀 Video Genius - Project Roadmap</h1>
        <p>Real-time project tracking</p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="error-banner">
          <p>⚠️ {error}</p>
          <button onClick={loadData}>Retry</button>
        </div>
      )}

      {/* Overall Stats */}
      {stats && (
        <div className="stats-grid">
          <div className="stat-card">
            <span className="stat-label">Total Tasks</span>
            <span className="stat-value">{stats.total}</span>
          </div>
          <div className="stat-card completed">
            <span className="stat-label">Completed</span>
            <span className="stat-value">{stats.completed}</span>
          </div>
          <div className="stat-card in-progress">
            <span className="stat-label">In Progress</span>
            <span className="stat-value">{stats.inProgress}</span>
          </div>
          <div className="stat-card blocked">
            <span className="stat-label">Blocked</span>
            <span className="stat-value">{stats.blocked}</span>
          </div>
          <div className="stat-card todo">
            <span className="stat-label">To Do</span>
            <span className="stat-value">{stats.todo}</span>
          </div>
          <div className="stat-card progress">
            <span className="stat-label">Overall Progress</span>
            <span className="stat-value">{Math.round(stats.progress)}%</span>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${stats.progress}%` }}
              />
            </div>
          </div>
        </div>
      )}

      {/* Phases Overview */}
      <div className="phases-section">
        <h2>Project Phases</h2>
        <div className="phases-grid">
          {phases.map((phase) => {
            const phaseProgress = getPhaseProgress(phase)
            const isSelected = selectedPhase === phase

            return (
              <div
                key={phase}
                className={`phase-card ${isSelected ? 'selected' : ''}`}
                onClick={() => setSelectedPhase(isSelected ? null : phase)}
              >
                <h3>{phaseNames[phase]}</h3>
                <div className="phase-stats">
                  <span>{getPhaseTasksCount(phase)} tasks</span>
                  <span className="completed">
                    {getPhaseCompletedCount(phase)} done
                  </span>
                </div>
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${phaseProgress}%` }}
                  />
                </div>
                <span className="progress-text">{phaseProgress}%</span>
              </div>
            )
          })}
        </div>
      </div>

      {/* Tasks List */}
      <div className="tasks-section">
        <h2>
          {selectedPhase ? `${phaseNames[selectedPhase]} Tasks` : 'All Tasks'}
        </h2>

        {loading && !tasks.length && (
          <div className="loading">
            <p>Loading tasks...</p>
          </div>
        )}

        {filteredTasks.length === 0 && !loading && (
          <div className="empty-state">
            <p>No tasks available</p>
          </div>
        )}

        <div className="tasks-list">
          {filteredTasks.map((task) => (
            <div key={task.id} className={`task-item status-${task.status}`}>
              <div className="task-header">
                <h4>{task.title}</h4>
                <span className={`badge priority-${task.priority}`}>
                  {task.priority}
                </span>
              </div>
              <div className="task-meta">
                <span className={`status-badge ${task.status}`}>
                  {task.status.replace('-', ' ')}
                </span>
                {task.assignee && (
                  <span className="assignee">👤 {task.assignee}</span>
                )}
                {task.due_date && (
                  <span className="due-date">📅 {task.due_date}</span>
                )}
              </div>
              {task.description && (
                <p className="task-description">{task.description}</p>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="dashboard-footer">
        <small>
          Last updated: {new Date().toLocaleTimeString()} | Data synced from
          backend API
        </small>
        <button onClick={loadData} disabled={loading}>
          {loading ? 'Refreshing...' : 'Refresh Now'}
        </button>
      </div>
    </div>
  )
}

export default DashboardRoadmap
