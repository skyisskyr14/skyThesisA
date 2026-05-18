import type { ChatIntent, ReviewResult, ThesisProject } from '../types'

const baseUrl = import.meta.env.VITE_API_BASE_URL || ''

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${url}`, {
    headers: { 'Content-Type': 'application/json', ...(options?.headers || {}) },
    ...options
  })
  if (!response.ok) {
    throw new Error(await response.text())
  }
  return response.json() as Promise<T>
}

export const api = {
  listProjects: () => request<ThesisProject[]>('/api/projects'),
  createProject: (payload: { title: string; author: string; major: string; school: string }) =>
    request<ThesisProject>('/api/projects', { method: 'POST', body: JSON.stringify(payload) }),
  getProject: (id: number) => request<ThesisProject>(`/api/projects/${id}`),
  analyzeTemplate: (projectId: number) => request('/api/templates/analyze?project_id=' + projectId, { method: 'POST' }),
  generateOutline: (projectId: number) => request('/api/outlines/generate?project_id=' + projectId, { method: 'POST' }),
  generateChapter: (projectId: number, chapterNo = 1) =>
    request(`/api/chapters/generate?project_id=${projectId}&chapter_no=${chapterNo}`, { method: 'POST' }),
  parseChat: (projectId: number | undefined, message: string) =>
    request<ChatIntent>('/api/chat', { method: 'POST', body: JSON.stringify({ project_id: projectId, message }) }),
  listMemory: () => request('/api/memory'),
  listErrors: () => request('/api/errors'),
  listRules: () => request('/api/rules'),
  runReview: (projectId: number, content: string) =>
    request<ReviewResult>('/api/reviews/run', { method: 'POST', body: JSON.stringify({ project_id: projectId, content }) }),
  generateDocx: (projectId: number) => request('/api/docx/generate?project_id=' + projectId, { method: 'POST' })
}
