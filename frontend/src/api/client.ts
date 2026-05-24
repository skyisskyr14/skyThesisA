import type { ChatIntent, ChatSendResponse, GenerateFullDocxResponse, ReviewResult, TemplateAnalysisResult, ThesisProject } from '../types'

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
  generateOutline: (payloadOrProjectId: any) => {
    const payload = typeof payloadOrProjectId === 'number' ? { project_id: payloadOrProjectId } : payloadOrProjectId
    return request('/api/thesis/outline/generate-real', { method: 'POST', body: JSON.stringify(payload) })
  },
  generateChapter: (payloadOrProjectId: any, chapterNo = 1) => {
    const payload = typeof payloadOrProjectId === 'number' ? { project_id: payloadOrProjectId, chapter_no: chapterNo } : payloadOrProjectId
    return request('/api/thesis/chapters/generate-real', { method: 'POST', body: JSON.stringify(payload) })
  },
  parseChat: (projectId: number | undefined, message: string) =>
    request<ChatIntent>('/api/chat', { method: 'POST', body: JSON.stringify({ project_id: projectId, message }) }),
  sendChat: (payload: { project_id: number; message: string; current_step: string; current_chapter_id?: number | null; selected_block_id?: string | null }) =>
    request<ChatSendResponse>('/api/thesis/chat/send', { method: 'POST', body: JSON.stringify(payload) }),
  listMemory: () => request('/api/memory'),
  listErrors: () => request('/api/errors'),
  listRules: () => request('/api/rules'),
  runReview: (projectId: number, content: string) =>
    request<ReviewResult>('/api/reviews/run', { method: 'POST', body: JSON.stringify({ project_id: projectId, content }) }),
  generateDocx: (projectId: number) => request('/api/docx/generate?project_id=' + projectId, { method: 'POST' }),
  analyzeDocxTemplate: (payload: { project_id: number; file_id?: number; file_path?: string }) =>
    request<TemplateAnalysisResult>('/api/thesis/templates/analyze-docx', { method: 'POST', body: JSON.stringify(payload) }),
  latestTemplateResult: (projectId: number) => request<TemplateAnalysisResult>(`/api/thesis/templates/${projectId}/latest`),
  applyTemplateRules: (projectId: number, analysisId: number) =>
    request('/api/thesis/templates/apply', { method: 'POST', body: JSON.stringify({ project_id: projectId, analysis_id: analysisId }) }),
  generateFullDocx: (payloadOrProjectId: any, useTemplateRules = true) => {
    const payload = typeof payloadOrProjectId === 'number' ? { project_id: payloadOrProjectId, use_template_rules: useTemplateRules } : payloadOrProjectId
    return request<GenerateFullDocxResponse>('/api/thesis/docx/generate-full', { method: 'POST', body: JSON.stringify(payload) })
  }
}
