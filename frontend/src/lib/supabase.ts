/**
 * Supabase Client Configuration
 * Initializes Supabase connection for real-time updates
 */

import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || ''
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_KEY || ''

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn('Supabase environment variables not configured')
  console.warn('Real-time updates will not work')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

/**
 * Subscribe to real-time changes on video_tasks table
 */
export const subscribeToTasks = (callback: (payload: any) => void) => {
  const channel = supabase
    .channel('public:video_tasks')
    .on(
      'postgres_changes',
      {
        event: '*',
        schema: 'public',
        table: 'video_tasks',
      },
      (payload) => {
        console.log('Real-time update:', payload)
        callback(payload)
      }
    )
    .subscribe()

  return () => {
    channel.unsubscribe()
  }
}

/**
 * Fetch all tasks from database
 */
export const fetchTasks = async () => {
  const { data, error } = await supabase
    .from('video_tasks')
    .select('*')
    .order('created_at', { ascending: false })

  if (error) {
    console.error('Error fetching tasks:', error)
    return []
  }

  return data || []
}

/**
 * Create a new task
 */
export const createTask = async (task: any) => {
  const { data, error } = await supabase
    .from('video_tasks')
    .insert([task])
    .select()

  if (error) {
    console.error('Error creating task:', error)
    return null
  }

  return data?.[0] || null
}

/**
 * Update a task
 */
export const updateTask = async (id: string, updates: any) => {
  const { data, error } = await supabase
    .from('video_tasks')
    .update(updates)
    .eq('id', id)
    .select()

  if (error) {
    console.error('Error updating task:', error)
    return null
  }

  return data?.[0] || null
}

/**
 * Delete a task
 */
export const deleteTask = async (id: string) => {
  const { error } = await supabase
    .from('video_tasks')
    .delete()
    .eq('id', id)

  if (error) {
    console.error('Error deleting task:', error)
    return false
  }

  return true
}

/**
 * Get task statistics
 */
export const getTaskStats = async () => {
  const { data, error } = await supabase
    .from('video_tasks_stats')
    .select('*')

  if (error) {
    console.error('Error fetching stats:', error)
    return null
  }

  return data?.[0] || null
}
