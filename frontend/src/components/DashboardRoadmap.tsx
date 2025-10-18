/**
 * Dashboard Completa com Roadmap e Progress do Video Genius
 * Monitora progresso em tempo real com Supabase
 */

import React, { useEffect, useState } from 'react'
import { supabase } from '@/lib/supabase'
import './DashboardRoadmap.css'

// ============================================================================
// TIPOS
// ============================================================================

interface Phase {
  id: string
  name: string
  startDate: string
  endDate: string
  progress: number
  status: 'planning' | 'in-progress' | 'completed'
  color: string
}

interface Task {
  id: string
  title: string
  phase: string
  status: 'todo' | 'in-progress' | 'completed' | 'blocked'
  priority: 'low' | 'medium' | 'high' | 'critical'
  assignee?: string
  dueDate?: string
  completedDate?: string
  subtasks?: Task[]
}

interface ProjectStats {
  totalTasks: number
  completedTasks: number
  inProgressTasks: number
  blockedTasks: number
  overallProgress: number
  velocityPerDay: number
  estimatedCompletion: string
}

interface RealtimeUpdate {
  type: 'task_created' | 'task_updated' | 'task_completed'
  data: Task
  timestamp: string
}

// ============================================================================
// PHASES DATA
// ============================================================================

const PHASES: Phase[] = [
  {
    id: 'phase-1',
    name: 'MVP Core',
    startDate: '2024-10-18',
    endDate: '2024-11-15',
    progress: 85,
    status: 'in-progress',
    color: '#0366d6'
  },
  {
    id: 'phase-2',
    name: 'AI Integration',
    startDate: '2024-11-16',
    endDate: '2024-12-15',
    progress: 45,
    status: 'in-progress',
    color: '#1f6feb'
  },
  {
    id: 'phase-3',
    name: 'Production Ready',
    startDate: '2024-12-16',
    endDate: '2025-01-15',
    progress: 0,
    status: 'planning',
    color: '#28a745'
  },
  {
    id: 'phase-4',
    name: 'Analytics & Scale',
    startDate: '2025-01-16',
    endDate: '2025-02-15',
    progress: 0,
    status: 'planning',
    color: '#6f42c1'
  }
]

const INITIAL_TASKS: Task[] = [
  // Phase 1: MVP Core
  {
    id: 'task-1',
    title: 'Supabase Setup & Database',
    phase: 'phase-1',
    status: 'completed',
    priority: 'critical',
    assignee: 'walland',
    completedDate: '2024-10-20'
  },
  {
    id: 'task-2',
    title: 'FastAPI Backend with Realtime',
    phase: 'phase-1',
    status: 'completed',
    priority: 'critical',
    assignee: 'walland',
    completedDate: '2024-10-22'
  },
  {
    id: 'task-3',
    title: 'React Frontend Setup',
    phase: 'phase-1',
    status: 'completed',
    priority: 'critical',
    assignee: 'walland',
    completedDate: '2024-10-23'
  },
  {
    id: 'task-4',
    title: 'Video Upload & Processing',
    phase: 'phase-1',
    status: 'in-progress',
    priority: 'high',
    assignee: 'walland',
    dueDate: '2024-10-28'
  },
  {
    id: 'task-5',
    title: 'User Authentication & RLS',
    phase: 'phase-1',
    status: 'completed',
    priority: 'critical',
    assignee: 'walland',
    completedDate: '2024-10-24'
  },
  {
    id: 'task-6',
    title: 'Realtime Dashboard',
    phase: 'phase-1',
    status: 'in-progress',
    priority: 'high',
    assignee: 'walland',
    dueDate: '2024-10-30'
  },
  // Phase 2: AI Integration
  {
    id: 'task-7',
    title: 'Vertex AI Integration',
    phase: 'phase-2',
    status: 'in-progress',
    priority: 'critical',
    assignee: 'walland',
    dueDate: '2024-11-25'
  },
  {
    id: 'task-8',
    title: 'Script Generation with AI',
    phase: 'phase-2',
    status: 'todo',
    priority: 'high',
    dueDate: '2024-11-30'
  },
  {
    id: 'task-9',
    title: 'Video Thumbnail Generation',
    phase: 'phase-2',
    status: 'blocked',
    priority: 'medium',
    dueDate: '2024-12-05'
  },
  // Phase 3: Production
  {
    id: 'task-10',
    title: 'Cloud Run Deployment',
    phase: 'phase-3',
    status: 'todo',
    priority: 'critical',
    dueDate: '2024-12-25'
  },
  {
    id: 'task-11',
    title: 'Load Testing & Optimization',
    phase: 'phase-3',
    status: 'todo',
    priority: 'high',
    dueDate: '2024-12-30'
  }
]

// ============================================================================
// DASHBOARD COMPONENT
// ============================================================================

export function DashboardRoadmap() {
  const [phases, setPhases] = useState<Phase[]>(PHASES)
  const [tasks, setTasks] = useState<Task[]>(INITIAL_TASKS)
  const [stats, setStats] = useState<ProjectStats | null>(null)
  const [selectedPhase, setSelectedPhase] = useState<string>('phase-1')
  const [realtimeUpdates, setRealtimeUpdates] = useState<RealtimeUpdate[]>([])
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [viewMode, setViewMode] = useState<'timeline' | 'kanban' | 'burndown'>('timeline')

  // =========================================================================
  // LOAD TASKS FROM API
  // =========================================================================

  useEffect(() => {
    const loadTasksFromAPI = async () => {
      try {
        // Try to fetch from API
        const response = await fetch('/api/v1/tasks')
        if (response.ok) {
          const apiTasks = await response.json()
          // Map API response to Task format
          const mappedTasks = apiTasks.map((t: any) => ({
            id: t.id,
            title: t.title,
            phase: t.phase || 'phase-1',
            status: t.status || 'todo',
            priority: t.priority || 'medium',
            assignee: t.assignee,
            dueDate: t.due_date,
            completedDate: t.completed_date,
          }))
          setTasks(mappedTasks)
          console.log(`✅ Loaded ${mappedTasks.length} tasks from API`)
        }
      } catch (error) {
        console.warn('ℹ️  Could not load tasks from API, using sample data:', error)
        // Fallback to INITIAL_TASKS already set
      }
    }

    loadTasksFromAPI()
  }, [])

  // =========================================================================
  // CALCULAR ESTATÍSTICAS
  // =========================================================================

  useEffect(() => {
    const calculateStats = () => {
      const completed = tasks.filter(t => t.status === 'completed').length
      const inProgress = tasks.filter(t => t.status === 'in-progress').length
      const blocked = tasks.filter(t => t.status === 'blocked').length
      const total = tasks.length

      const overallProgress = Math.round((completed / total) * 100)
      const velocityPerDay = completed / getDaysSinceStart()
      const remainingTasks = total - completed
      const estimatedDaysLeft = Math.ceil(remainingTasks / Math.max(velocityPerDay, 0.1))
      const estimatedCompletion = new Date(Date.now() + estimatedDaysLeft * 24 * 60 * 60 * 1000)
        .toLocaleDateString('pt-BR')

      setStats({
        totalTasks: total,
        completedTasks: completed,
        inProgressTasks: inProgress,
        blockedTasks: blocked,
        overallProgress,
        velocityPerDay: Math.round(velocityPerDay * 100) / 100,
        estimatedCompletion
      })

      // Atualizar progresso das fases
      setPhases(phases => phases.map(phase => {
        const phaseTasks = tasks.filter(t => t.phase === phase.id)
        const phaseCompleted = phaseTasks.filter(t => t.status === 'completed').length
        const progress = phaseTasks.length > 0 
          ? Math.round((phaseCompleted / phaseTasks.length) * 100)
          : 0

        return { ...phase, progress }
      }))
    }

    calculateStats()
  }, [tasks])

  // =========================================================================
  // REALTIME SUBSCRIPTION
  // =========================================================================

  useEffect(() => {
    // Subscribe to task changes via Supabase Realtime
    const subscription = supabase
      .channel('tasks_channel')
      .on(
        'postgres_changes',
        {
          event: '*',
          schema: 'public',
          table: 'video_tasks'
        },
        (payload) => {
          const update: RealtimeUpdate = {
            type: payload.eventType as any,
            data: payload.new as Task,
            timestamp: new Date().toISOString()
          }

          setRealtimeUpdates(prev => [update, ...prev.slice(0, 9)])
          
          // Atualizar tasks locais
          if (payload.eventType === 'INSERT') {
            setTasks(prev => [...prev, payload.new as Task])
          } else if (payload.eventType === 'UPDATE') {
            setTasks(prev => prev.map(t => t.id === payload.new.id ? (payload.new as Task) : t))
          } else if (payload.eventType === 'DELETE') {
            setTasks(prev => prev.filter(t => t.id !== payload.old.id))
          }
        }
      )
      .subscribe()

    return () => {
      subscription.unsubscribe()
    }
  }, [])

  // =========================================================================
  // FUNÇÕES UTILITÁRIAS
  // =========================================================================

  const getDaysSinceStart = (): number => {
    const startDate = new Date('2024-10-18')
    const today = new Date()
    return Math.ceil((today.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24))
  }

  const getPhaseTasksFiltered = (phaseId: string): Task[] => {
    return tasks
      .filter(t => t.phase === phaseId)
      .filter(t => filterStatus === 'all' || t.status === filterStatus)
  }

  const getStatusColor = (status: string): string => {
    const colors: Record<string, string> = {
      'completed': '#28a745',
      'in-progress': '#ffc107',
      'todo': '#6c757d',
      'blocked': '#dc3545'
    }
    return colors[status] || '#6c757d'
  }

  const getPriorityIcon = (priority: string): string => {
    const icons: Record<string, string> = {
      'critical': '🔴',
      'high': '🟠',
      'medium': '🟡',
      'low': '🟢'
    }
    return icons[priority] || '⚪'
  }

  // =========================================================================
  // RENDER
  // =========================================================================

  return (
    <div className="dashboard-roadmap">
      {/* ===== HEADER ===== */}
      <header className="dashboard-header">
        <div className="header-content">
          <h1>🎬 Video Genius - Roadmap & Progress</h1>
          <p className="subtitle">Acompanhe o progresso do projeto em tempo real</p>
        </div>

        <div className="view-mode-selector">
          <button
            className={`view-btn ${viewMode === 'timeline' ? 'active' : ''}`}
            onClick={() => setViewMode('timeline')}
          >
            📅 Timeline
          </button>
          <button
            className={`view-btn ${viewMode === 'kanban' ? 'active' : ''}`}
            onClick={() => setViewMode('kanban')}
          >
            📊 Kanban
          </button>
          <button
            className={`view-btn ${viewMode === 'burndown' ? 'active' : ''}`}
            onClick={() => setViewMode('burndown')}
          >
            📈 Burndown
          </button>
        </div>
      </header>

      {/* ===== STATS CARDS ===== */}
      {stats && (
        <section className="stats-grid">
          <StatCard
            icon="✅"
            label="Tarefas Completas"
            value={`${stats.completedTasks}/${stats.totalTasks}`}
            color="#28a745"
          />
          <StatCard
            icon="⚙️"
            label="Em Progresso"
            value={stats.inProgressTasks}
            color="#ffc107"
          />
          <StatCard
            icon="🚫"
            label="Bloqueadas"
            value={stats.blockedTasks}
            color="#dc3545"
          />
          <StatCard
            icon="🎯"
            label="Progresso Geral"
            value={`${stats.overallProgress}%`}
            color="#0366d6"
          />
          <StatCard
            icon="⚡"
            label="Velocidade"
            value={`${stats.velocityPerDay} tarefas/dia`}
            color="#6f42c1"
          />
          <StatCard
            icon="📅"
            label="Conclusão Estimada"
            value={stats.estimatedCompletion}
            color="#28a745"
          />
        </section>
      )}

      {/* ===== MAIN CONTENT ===== */}
      <main className="dashboard-main">
        {/* ===== TIMELINE VIEW ===== */}
        {viewMode === 'timeline' && (
          <section className="timeline-section">
            <h2>📅 Timeline do Projeto</h2>
            <div className="phases-container">
              {phases.map(phase => (
                <PhaseCard
                  key={phase.id}
                  phase={phase}
                  tasks={getPhaseTasksFiltered(phase.id)}
                  isSelected={selectedPhase === phase.id}
                  onSelect={() => setSelectedPhase(phase.id)}
                />
              ))}
            </div>
          </section>
        )}

        {/* ===== KANBAN VIEW ===== */}
        {viewMode === 'kanban' && (
          <section className="kanban-section">
            <h2>📊 Quadro Kanban</h2>
            <div className="kanban-board">
              {['todo', 'in-progress', 'blocked', 'completed'].map(status => (
                <KanbanColumn
                  key={status}
                  status={status}
                  tasks={tasks.filter(t => t.status === status)}
                  statusColor={getStatusColor(status)}
                />
              ))}
            </div>
          </section>
        )}

        {/* ===== BURNDOWN VIEW ===== */}
        {viewMode === 'burndown' && (
          <section className="burndown-section">
            <h2>📈 Gráfico de Burndown</h2>
            <BurndownChart tasks={tasks} phases={phases} />
          </section>
        )}

        {/* ===== PHASE DETAILS ===== */}
        <section className="phase-details">
          <h2>📋 Detalhes da Fase</h2>
          <div className="filter-controls">
            <label>Filtrar por Status:</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
            >
              <option value="all">Todos</option>
              <option value="todo">À Fazer</option>
              <option value="in-progress">Em Progresso</option>
              <option value="blocked">Bloqueados</option>
              <option value="completed">Completos</option>
            </select>
          </div>

          <div className="tasks-list">
            {getPhaseTasksFiltered(selectedPhase).map(task => (
              <TaskCard key={task.id} task={task} priorityIcon={getPriorityIcon(task.priority)} />
            ))}
          </div>
        </section>
      </main>

      {/* ===== REALTIME FEED ===== */}
      <aside className="realtime-feed">
        <h3>🔔 Atualizações em Tempo Real</h3>
        <div className="updates-list">
          {realtimeUpdates.length > 0 ? (
            realtimeUpdates.map((update, idx) => (
              <div key={idx} className="update-item">
                <span className="update-type">{update.type}</span>
                <span className="update-task">{update.data.title}</span>
                <span className="update-time">
                  {new Date(update.timestamp).toLocaleTimeString('pt-BR')}
                </span>
              </div>
            ))
          ) : (
            <p className="no-updates">Nenhuma atualização recente</p>
          )}
        </div>
      </aside>
    </div>
  )
}

// ============================================================================
// SUB-COMPONENTS
// ============================================================================

interface StatCardProps {
  icon: string
  label: string
  value: string | number
  color: string
}

function StatCard({ icon, label, value, color }: StatCardProps) {
  return (
    <div className="stat-card" style={{ borderLeftColor: color }}>
      <div className="stat-icon">{icon}</div>
      <div className="stat-content">
        <p className="stat-label">{label}</p>
        <p className="stat-value">{value}</p>
      </div>
    </div>
  )
}

interface PhaseCardProps {
  phase: Phase
  tasks: Task[]
  isSelected: boolean
  onSelect: () => void
}

function PhaseCard({ phase, tasks, isSelected, onSelect }: PhaseCardProps) {
  const statusEmoji: Record<string, string> = {
    'planning': '📋',
    'in-progress': '⚙️',
    'completed': '✅'
  }

  return (
    <div
      className={`phase-card ${isSelected ? 'selected' : ''}`}
      onClick={onSelect}
      style={{ borderTopColor: phase.color }}
    >
      <h3>
        {statusEmoji[phase.status]} {phase.name}
      </h3>
      <p className="phase-dates">
        {new Date(phase.startDate).toLocaleDateString('pt-BR')} - {new Date(phase.endDate).toLocaleDateString('pt-BR')}
      </p>
      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{ width: `${phase.progress}%`, backgroundColor: phase.color }}
        />
      </div>
      <p className="progress-text">{phase.progress}% Completo</p>
      <p className="task-count">{tasks.length} tarefas</p>
    </div>
  )
}

interface TaskCardProps {
  task: Task
  priorityIcon: string
}

function TaskCard({ task, priorityIcon }: TaskCardProps) {
  const statusEmoji: Record<string, string> = {
    'completed': '✅',
    'in-progress': '⚙️',
    'todo': '⭕',
    'blocked': '🚫'
  }

  return (
    <div className="task-card">
      <div className="task-header">
        <span className="task-status">{statusEmoji[task.status]}</span>
        <h4>{task.title}</h4>
        <span className="task-priority">{priorityIcon}</span>
      </div>
      {task.assignee && <p className="task-assignee">👤 {task.assignee}</p>}
      {task.dueDate && (
        <p className="task-due">📅 Vence em: {new Date(task.dueDate).toLocaleDateString('pt-BR')}</p>
      )}
    </div>
  )
}

interface KanbanColumnProps {
  status: string
  tasks: Task[]
  statusColor: string
}

function KanbanColumn({ status, tasks, statusColor }: KanbanColumnProps) {
  const statusLabels: Record<string, string> = {
    'todo': 'À Fazer',
    'in-progress': 'Em Progresso',
    'blocked': 'Bloqueados',
    'completed': 'Completos'
  }

  return (
    <div className="kanban-column">
      <h3 style={{ borderBottomColor: statusColor }}>
        {statusLabels[status]} ({tasks.length})
      </h3>
      <div className="tasks">
        {tasks.map(task => (
          <div key={task.id} className="kanban-card">
            <p className="card-title">{task.title}</p>
            <p className="card-meta">{task.priority}</p>
          </div>
        ))}
      </div>
    </div>
  )
}

interface BurndownChartProps {
  tasks: Task[]
  phases: Phase[]
}

function BurndownChart({ tasks, phases }: BurndownChartProps) {
  const completedTasks = tasks.filter(t => t.status === 'completed').length
  const totalTasks = tasks.length

  return (
    <div className="burndown-chart">
      <div className="chart-placeholder">
        <p>📊 Gráfico de Burndown</p>
        <p className="chart-stat">Tarefas Completas: {completedTasks} / {totalTasks}</p>
        <svg viewBox="0 0 400 300" className="simple-chart">
          <line x1="40" y1="250" x2="380" y2="250" stroke="#ccc" strokeWidth="2" />
          <line x1="40" y1="250" x2="40" y2="20" stroke="#ccc" strokeWidth="2" />
          <polyline
            points="40,250 100,230 160,200 220,170 280,140 340,120"
            fill="none"
            stroke="#0366d6"
            strokeWidth="2"
          />
          <circle cx="340" cy="120" r="4" fill="#0366d6" />
        </svg>
      </div>
    </div>
  )
}

export default DashboardRoadmap
