<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api/client'
import ChatPanel from '../components/ChatPanel.vue'
import ProcessSidebar from '../components/ProcessSidebar.vue'
import StatusFooter from '../components/StatusFooter.vue'
import { useProjectStore } from '../stores/projectStore'

const route = useRoute()
const router = useRouter()
const store = useProjectStore()
const result = ref('请选择中间工作区的动作，MVP 会调用真实后端接口并返回模拟 Agent 结果。')
const projectId = Number(route.params.id)

onMounted(() => store.loadProject(projectId))

async function run(action: 'template' | 'outline' | 'chapter' | 'review' | 'docx') {
  const map = {
    template: () => api.analyzeTemplate(projectId),
    outline: () => api.generateOutline(projectId),
    chapter: () => api.generateChapter(projectId, 1),
    review: () => api.runReview(projectId, '最终导出前不做审查 线条交叉'),
    docx: () => api.generateDocx(projectId)
  }
  const response = await map[action]()
  result.value = JSON.stringify(response, null, 2)
  await store.loadProject(projectId)
}
</script>

<template>
  <section v-if="store.currentProject" class="workspace-grid">
    <ProcessSidebar :current-step="store.currentProject.current_step" :statuses="store.currentProject.step_statuses" />
    <main class="workspace-center">
      <div class="workspace-title">
        <div>
          <h1>{{ store.currentProject.title }}</h1>
          <p>顶部：论文项目名称 / 当前版本 / 导出按钮</p>
        </div>
        <el-button type="success" @click="run('docx')">生成 DOCX</el-button>
      </div>
      <el-alert title="MVP 工作台" description="左侧流程导航，中间显示当前步骤内容，右侧对话区绑定当前论文任务。" type="info" show-icon />
      <div class="action-row">
        <el-button @click="router.push(`/templates/${projectId}`)">模板分析页</el-button>
        <el-button @click="router.push(`/outline/${projectId}`)">大纲规划页</el-button>
        <el-button @click="router.push(`/chapters/${projectId}`)">分章写作页</el-button>
        <el-button @click="router.push(`/reviews/${projectId}`)">审查报告页</el-button>
      </div>
      <div class="action-row">
        <el-button type="primary" @click="run('template')">调用模板分析接口</el-button>
        <el-button type="primary" @click="run('outline')">调用大纲生成接口</el-button>
        <el-button type="primary" @click="run('chapter')">调用章节生成接口</el-button>
        <el-button type="warning" @click="run('review')">触发 MemoryGuard 审查</el-button>
      </div>
      <pre class="result-box">{{ result }}</pre>
      <StatusFooter version="v0.1" :status="store.currentProject.status" :step="store.currentProject.current_step" />
    </main>
    <ChatPanel :project-id="projectId" />
  </section>
</template>
