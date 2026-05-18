import type { ChatIntent, GenerateFullDocxResponse, ReviewResult, TemplateAnalysisResult, ThesisProject } from '../types'

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
  generateDocx: (projectId: number) => request('/api/docx/generate?project_id=' + projectId, { method: 'POST' }),
  analyzeDocxTemplate: (payload: { project_id: number; file_id?: number; file_path?: string }) =>
    request<TemplateAnalysisResult>('/api/thesis/templates/analyze-docx', { method: 'POST', body: JSON.stringify(payload) }),
  latestTemplateResult: (projectId: number) => request<TemplateAnalysisResult>(`/api/thesis/templates/${projectId}/latest`),
  applyTemplateRules: (projectId: number, analysisId: number) =>
    request('/api/thesis/templates/apply', { method: 'POST', body: JSON.stringify({ project_id: projectId, analysis_id: analysisId }) }),
  generateFullDocx: (projectId: number, useTemplateRules: boolean) =>
    request<GenerateFullDocxResponse>('/api/thesis/docx/generate-full', {
      method: 'POST',
      body: JSON.stringify({ project_id: projectId, use_template_rules: useTemplateRules, use_mock_content: true })
    })
}
