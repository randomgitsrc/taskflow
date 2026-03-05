import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// Task types
export interface Task {
  id: number
  title: string
  description: string | null
  status: string
  priority: string
  progress: number
  parent_id: number | null
  project_id: number | null
  owner: string | null
  external_id: string | null
  external_type: string | null
  due_date: string | null
  started_at: string | null
  completed_at: string | null
  created_at: string
  updated_at: string
  // Phase 4: blocking info
  is_blocked: boolean
  parent_title: string | null
  // Phase 2: dependency info
  depends_on: number[] | null
}

export interface TaskCreate {
  title: string
  description?: string
  parent_id?: number | null
  project_id?: number | null
  priority?: string
  owner?: string
  external_id?: string
  external_type?: string
  due_date?: string
  tag_ids?: number[]
  // Phase 2: dependency
  depends_on?: number[]
}

export interface TaskUpdate {
  title?: string
  description?: string
  parent_id?: number | null
  project_id?: number | null
  priority?: string
  owner?: string
  external_id?: string
  external_type?: string
  due_date?: string
  // Phase 2: dependency
  depends_on?: number[]
}

export interface TaskLog {
  id: number
  task_id: number
  message: string
  created_at: string
}

// Tag types
export interface Tag {
  id: number
  name: string
  color: string
}

// Stats types
export interface Stats {
  total: number
  pending: number
  in_progress: number
  completed: number
  completed_rate: number
  overdue: number
  avg_duration_hours: number
}

// Comment types
export interface Comment {
  id: number
  task_id: number
  author: string
  content: string
  created_at: string
}

// API functions
export const taskApi = {
  getTasks: (q?: string, status?: string, priority?: string, tagId?: number) => 
    api.get<Task[]>('/tasks', { params: { q, status_filter: status, priority, tag_id: tagId } }).then(r => r.data),
  
  getTask: (id: number) =>
    api.get<Task>(`/tasks/${id}`).then(r => r.data),
  
  createTask: (data: TaskCreate) =>
    api.post<Task>('/tasks', data).then(r => r.data),
  
  updateTask: (id: number, data: TaskUpdate) =>
    api.put<Task>(`/tasks/${id}`, data).then(r => r.data),
  
  deleteTask: (id: number) =>
    api.delete(`/tasks/${id}`),
  
  updateStatus: (id: number, status: string) =>
    api.patch<Task>(`/tasks/${id}/status`, { status }).then(r => r.data),
  
  getTaskTree: () =>
    api.get<any[]>('/tasks/tree').then(r => r.data),
  
  getLogs: (taskId: number) =>
    api.get<TaskLog[]>(`/tasks/${taskId}/logs`).then(r => r.data),
  
  addLog: (taskId: number, message: string) =>
    api.post<TaskLog>(`/tasks/${taskId}/logs`, { message }).then(r => r.data),
  
  updateProgress: (id: number, progress: number) =>
    api.patch<Task>(`/tasks/${id}/progress`, { progress }).then(r => r.data),
  
  getComments: (taskId: number) =>
    api.get<Comment[]>(`/tasks/${taskId}/comments`).then(r => r.data),
  
  addComment: (taskId: number, author: string, content: string) =>
    api.post<Comment>(`/tasks/${taskId}/comments`, { author, content }).then(r => r.data),
  
  deleteComment: (commentId: number) =>
    api.delete(`/comments/${commentId}`),
}

// Tag API
export const tagApi = {
  getTags: () =>
    api.get<Tag[]>('/tags').then(r => r.data),
  
  createTag: (data: { name: string; color: string }) =>
    api.post<Tag>('/tags', data).then(r => r.data),
  
  updateTag: (id: number, data: { name?: string; color?: string }) =>
    api.put<Tag>(`/tags/${id}`, data).then(r => r.data),
  
  deleteTag: (id: number) =>
    api.delete(`/tags/${id}`),
  
  getTaskTags: (taskId: number) =>
    api.get<Tag[]>(`/tasks/${taskId}/tags`).then(r => r.data),
  
  addTagToTask: (taskId: number, tagId: number) =>
    api.post(`/tasks/${taskId}/tags/${tagId}`),
  
  removeTagFromTask: (taskId: number, tagId: number) =>
    api.delete(`/tasks/${taskId}/tags/${tagId}`),
}

// Stats API
export const statsApi = {
  getStats: () =>
    api.get<Stats>('/stats').then(r => r.data),
}

// Project types
export interface Project {
  id: number
  name: string
  description: string | null
  status: string
  created_at: string
  updated_at: string
}

export interface ProjectCreate {
  name: string
  description?: string
}

export interface ProjectUpdate {
  name?: string
  description?: string
  status?: string
}

// Project API
export const projectApi = {
  getProjects: () =>
    api.get<Project[]>('/projects').then(r => r.data),
  
  getProject: (id: number) =>
    api.get<Project>(`/projects/${id}`).then(r => r.data),
  
  createProject: (data: ProjectCreate) =>
    api.post<Project>('/projects', data).then(r => r.data),
  
  updateProject: (id: number, data: ProjectUpdate) =>
    api.put<Project>(`/projects/${id}`, data).then(r => r.data),
  
  deleteProject: (id: number) =>
    api.delete(`/projects/${id}`),
  
  getProjectTasks: (projectId: number) =>
    api.get<Task[]>(`/projects/${projectId}/tasks`).then(r => r.data),

  // Phase 4: Get available parent tasks
  getAvailableParentTasks: (projectId: number, excludeTaskId?: number) => {
    const params = excludeTaskId ? { exclude_task_id: excludeTaskId } : {}
    return api.get<{id: number; title: string; status: string; priority: string}[]>(
      `/projects/${projectId}/available-parents`,
      { params }
    ).then(r => r.data)
  },
}

export default api
