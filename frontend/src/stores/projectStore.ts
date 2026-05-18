import { defineStore } from 'pinia'
import { api } from '../api/client'
import type { ThesisProject } from '../types'

export const useProjectStore = defineStore('project', {
  state: () => ({
    projects: [] as ThesisProject[],
    currentProject: undefined as ThesisProject | undefined
  }),
  actions: {
    async loadProjects() {
      this.projects = await api.listProjects()
    },
    async loadProject(id: number) {
      this.currentProject = await api.getProject(id)
    }
  }
})
