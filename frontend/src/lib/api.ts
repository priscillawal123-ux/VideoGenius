/**
 * API Client for Video Genius Backend
 * Handles all communication with the FastAPI backend
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_TIMEOUT = parseInt(import.meta.env.VITE_API_TIMEOUT || '30000')

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

  // Dashboard Stats
  async getStats() {
    return apiRequest('/api/v1/dashboard/stats')
  },

  async getPhases() {
    return apiRequest('/api/v1/dashboard/phases')
  },

  // Tasks
  async getTasks() {
    return apiRequest('/api/v1/dashboard/tasks')
  },

  async createTask(task: any) {
    return apiRequest('/api/v1/dashboard/tasks', {
      method: 'POST',
      body: JSON.stringify(task),
    })
  },

  async updateTask(id: string, updates: any) {
    return apiRequest(`/api/v1/dashboard/tasks/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(updates),
    })
  },

  async deleteTask(id: string) {
    return apiRequest(`/api/v1/dashboard/tasks/${id}`, {
      method: 'DELETE',
    })
  },

  // GitHub Sync
  async syncGitHub() {
    return apiRequest('/api/v1/dashboard/sync-github', {
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
}

export { API_URL, API_TIMEOUT, ApiError }
