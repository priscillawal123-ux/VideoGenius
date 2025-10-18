/**
 * Task Service Layer
 * Business logic for task management
 */

import { api, Task, TaskStats } from '../lib/api'

export class TaskService {
  /**
   * Fetch all tasks with optional filtering
   */
  static async fetchTasks(filters?: {
    phase?: string
    status?: string
    priority?: string
  }): Promise<Task[]> {
    try {
      const tasks = await api.getTasks(filters)
      return Array.isArray(tasks) ? tasks : []
    } catch (error) {
      console.error('Failed to fetch tasks:', error)
      return []
    }
  }

  /**
   * Fetch a single task by ID
   */
  static async fetchTask(taskId: string): Promise<Task | null> {
    try {
      return await api.getTask(taskId)
    } catch (error) {
      console.error(`Failed to fetch task ${taskId}:`, error)
      return null
    }
  }

  /**
   * Create a new task
   */
  static async createTask(task: {
    title: string
    phase: string
    status?: string
    priority?: string
    assignee?: string
    due_date?: string
    description?: string
  }): Promise<Task | null> {
    try {
      return await api.createTask(task)
    } catch (error) {
      console.error('Failed to create task:', error)
      throw error
    }
  }

  /**
   * Update an existing task
   */
  static async updateTask(
    taskId: string,
    updates: Partial<Task>
  ): Promise<Task | null> {
    try {
      return await api.updateTask(taskId, updates)
    } catch (error) {
      console.error(`Failed to update task ${taskId}:`, error)
      throw error
    }
  }

  /**
   * Delete a task
   */
  static async deleteTask(taskId: string): Promise<boolean> {
    try {
      await api.deleteTask(taskId)
      return true
    } catch (error) {
      console.error(`Failed to delete task ${taskId}:`, error)
      return false
    }
  }

  /**
   * Get task statistics
   */
  static async fetchTaskStats(): Promise<TaskStats | null> {
    try {
      return await api.getTaskStats()
    } catch (error) {
      console.error('Failed to fetch task stats:', error)
      return null
    }
  }

  /**
   * Group tasks by phase
   */
  static groupByPhase(tasks: Task[]): Record<string, Task[]> {
    return tasks.reduce(
      (acc, task) => {
        if (!acc[task.phase]) {
          acc[task.phase] = []
        }
        acc[task.phase].push(task)
        return acc
      },
      {} as Record<string, Task[]>
    )
  }

  /**
   * Group tasks by status
   */
  static groupByStatus(tasks: Task[]): Record<string, Task[]> {
    return tasks.reduce(
      (acc, task) => {
        if (!acc[task.status]) {
          acc[task.status] = []
        }
        acc[task.status].push(task)
        return acc
      },
      {} as Record<string, Task[]>
    )
  }

  /**
   * Filter tasks by phase
   */
  static filterByPhase(tasks: Task[], phase: string): Task[] {
    return tasks.filter((t) => t.phase === phase)
  }

  /**
   * Filter tasks by status
   */
  static filterByStatus(tasks: Task[], status: Task['status']): Task[] {
    return tasks.filter((t) => t.status === status)
  }

  /**
   * Sort tasks by creation date (newest first)
   */
  static sortByDate(tasks: Task[]): Task[] {
    return [...tasks].sort(
      (a, b) =>
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    )
  }

  /**
   * Sort tasks by priority
   */
  static sortByPriority(tasks: Task[]): Task[] {
    const priorityOrder: Record<string, number> = {
      critical: 0,
      high: 1,
      medium: 2,
      low: 3,
    }

    return [...tasks].sort(
      (a, b) =>
        (priorityOrder[a.priority] ?? 999) - (priorityOrder[b.priority] ?? 999)
    )
  }

  /**
   * Calculate progress percentage
   */
  static calculateProgress(tasks: Task[]): number {
    if (tasks.length === 0) return 0
    const completed = tasks.filter((t) => t.status === 'completed').length
    return Math.round((completed / tasks.length) * 100)
  }

  /**
   * Get tasks by specific status count
   */
  static getStatusCounts(tasks: Task[]): Record<Task['status'], number> {
    return {
      'todo': tasks.filter((t) => t.status === 'todo').length,
      'in-progress': tasks.filter((t) => t.status === 'in-progress').length,
      'completed': tasks.filter((t) => t.status === 'completed').length,
      'blocked': tasks.filter((t) => t.status === 'blocked').length,
    }
  }

  /**
   * Get overdue tasks
   */
  static getOverdueTasks(tasks: Task[]): Task[] {
    const now = new Date()
    return tasks.filter((t) => {
      if (!t.due_date || t.status === 'completed') return false
      return new Date(t.due_date) < now
    })
  }

  /**
   * Get tasks due soon (within 7 days)
   */
  static getTasksDueSoon(tasks: Task[]): Task[] {
    const now = new Date()
    const sevenDaysLater = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000)

    return tasks.filter((t) => {
      if (!t.due_date || t.status === 'completed') return false
      const dueDate = new Date(t.due_date)
      return dueDate >= now && dueDate <= sevenDaysLater
    })
  }
}

export default TaskService
