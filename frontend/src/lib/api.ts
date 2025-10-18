/**
 * API Client for Video Genius Backend
 * Handles all communication with the FastAPI backend
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '30000')

export interface Task {
  id: string
  title: string
  phase: string
  status: 'todo' | 'in-progress' | 'completed' | 'blocked'
  priority: 'low' | 'medium' | 'high' | 'critical'
  assignee?: string
  due_date?: string
  completed_date?: string
  description?: string
  created_at: string
  updated_at: string
}

export interface TaskStats {
  total: number
  completed: number
  in_progress: number
  blocked: number
  todo: number
  progress_percentage: number
}

interface ApiError {
  status: number
  message: string
  detail?: any
}

/**
 * Make an API request with timeout and error handling
 */
async function apiRequest(
  endpoint: string,
  options: RequestInit = {}
): Promise<any> {
  const controller = new AbortController()
  const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT)

  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      signal: controller.signal,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })

    clearTimeout(timeoutId)

    if (!response.ok) {
      const error: ApiError = {
        status: response.status,
        message: `HTTP ${response.status}`,
      }

      try {
        const data = await response.json()
        error.detail = data
      } catch (e) {
        // Response was not JSON
      }

      throw error
    }

    return await response.json()
  } catch (error) {
    clearTimeout(timeoutId)

    if (error instanceof TypeError && error.message === 'Failed to fetch') {
      throw {
        status: 0,
        message: 'Connection refused. Is the API server running?',
      }
    }

    throw error
  }
}

/**
 * API Methods
 */
export const api = {
  // Health & Status
  async health() {
    return apiRequest('/health')
  },

  async status() {
    return apiRequest('/')
  },

  // Tasks - Real API endpoints
  async getTasks(filters?: { phase?: string; status?: string; priority?: string }) {
    const params = new URLSearchParams()
    if (filters?.phase) params.append('phase', filters.phase)
    if (filters?.status) params.append('status', filters.status)
    if (filters?.priority) params.append('priority', filters.priority)
    
    const query = params.toString() ? `?${params.toString()}` : ''
    return apiRequest(`/api/v1/tasks${query}`)
  },

  async getTask(id: string) {
    return apiRequest(`/api/v1/tasks/${id}`)
  },

  async createTask(task: any) {
    return apiRequest('/api/v1/tasks', {
      method: 'POST',
      body: JSON.stringify(task),
    })
  },

  async updateTask(id: string, updates: any) {
    return apiRequest(`/api/v1/tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    })
  },

  async deleteTask(id: string) {
    return apiRequest(`/api/v1/tasks/${id}`, {
      method: 'DELETE',
    })
  },

  // Task Statistics
  async getTaskStats() {
    return apiRequest('/api/v1/tasks/stats/summary')
  },

  // GitHub Sync
  async syncGitHub() {
    return apiRequest('/api/v1/github/sync', {
      method: 'POST',
    })
  },

  // Auth
  async login(email: string, password: string) {
    return apiRequest('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
  },

  async register(email: string, password: string, name: string) {
    return apiRequest('/api/v1/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, name }),
    })
  },

  async getCurrentUser() {
    return apiRequest('/api/v1/auth/me')
  },

  async logout() {
    return apiRequest('/api/v1/auth/logout', {
      method: 'POST',
    })
  },

  // GCP
  async createSecret(name: string, value: string) {
    return apiRequest('/gcp/secret', {
      method: 'POST',
      body: JSON.stringify({ secret_id: name, secret_value: value }),
    })
  },

  async getSecret(id: string) {
    return apiRequest(`/gcp/secret/${id}`)
  },

  async getBuckets() {
    return apiRequest('/gcp/buckets')
  },
}

export { API_URL, API_TIMEOUT }
export type { ApiError }
