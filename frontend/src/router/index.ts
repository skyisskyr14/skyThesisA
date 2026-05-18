import { createRouter, createWebHistory } from 'vue-router'
import ProjectListPage from '../pages/ProjectListPage.vue'
import NewProjectPage from '../pages/NewProjectPage.vue'
import WorkspacePage from '../pages/WorkspacePage.vue'
import TemplateAnalysisPage from '../pages/TemplateAnalysisPage.vue'
import OutlinePage from '../pages/OutlinePage.vue'
import ChapterWritingPage from '../pages/ChapterWritingPage.vue'
import MemoryPage from '../pages/MemoryPage.vue'
import ErrorPage from '../pages/ErrorPage.vue'
import ReviewReportPage from '../pages/ReviewReportPage.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: ProjectListPage },
    { path: '/projects/new', component: NewProjectPage },
    { path: '/workspace/:id', component: WorkspacePage },
    { path: '/templates/:id', component: TemplateAnalysisPage },
    { path: '/outline/:id', component: OutlinePage },
    { path: '/chapters/:id', component: ChapterWritingPage },
    { path: '/memory', component: MemoryPage },
    { path: '/errors', component: ErrorPage },
    { path: '/reviews/:id', component: ReviewReportPage }
  ]
})
