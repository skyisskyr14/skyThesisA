<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api/client'
import ChatPanel from '../components/ChatPanel.vue'
import ProcessSidebar from '../components/ProcessSidebar.vue'
import StatusFooter from '../components/StatusFooter.vue'
import { useProjectStore } from '../stores/projectStore'
import type { ChatIntent, GenerateFullDocxResponse, ReviewResult } from '../types'

const route = useRoute()
const router = useRouter()
const store = useProjectStore()
const projectId = Number(route.params.id)
const selectedStep = ref('upload')
const result = ref('请按左侧流程依次执行：模板分析 → 大纲生成 → 生成章节 → 对话补充 → 生成 DOCX → 最终审查。')
const outlineChapters = ref<string[]>([])
const chapterPreview = ref('')
const docxDownloadUrl = ref('')
const reviewResult = ref<ReviewResult | null>(null)
const fullDocxResult = ref<GenerateFullDocxResponse | null>(null)
const useTemplateRules = ref(true)
const operationLogs = ref<string[]>(['v0.2 工作台已就绪，等待创建第一条论文任务闭环。'])

const currentStepTitle = computed(() => {
  const labels: Record<string, string> = {
    upload: '上传资料',
    template: '模板分析',
    outline: '大纲规划',
    writing: '分章写作',
    figures: '图表规划',
    formatting: '格式排版 / DOCX 生成',
    comments: '老师批注返修',
    review: '最终审查',
    export: '导出论文'
  }
  return labels[selectedStep.value] || '论文任务'
})

onMounted(async () => {
  await store.loadProject(projectId)
  selectedStep.value = store.currentProject?.current_step || 'template'
})

async function run(action: 'template' | 'outline' | 'chapter' | 'review' | 'docx') {
  operationLogs.value.unshift(`开始执行：${action}`)
  if (action === 'template') {
    selectedStep.value = 'template'
    const response = await api.analyzeTemplate(projectId)
    result.value = JSON.stringify(response, null, 2)
  }
  if (action === 'outline') {
    selectedStep.value = 'outline'
    const response = await api.generateOutline(projectId) as { result?: { chapters?: string[] } }
    outlineChapters.value = response.result?.chapters || []
    result.value = JSON.stringify(response, null, 2)
  }
  if (action === 'chapter') {
    selectedStep.value = 'writing'
    const response = await api.generateChapter(projectId, 1) as { result?: { blocks?: { text: string }[] } }
    chapterPreview.value = response.result?.blocks?.map((block) => block.text).join('\n') || ''
    result.value = JSON.stringify(response, null, 2)
  }
  if (action === 'docx') {
    selectedStep.value = 'formatting'
    const response = await api.generateDocx(projectId) as { download_url?: string }
    docxDownloadUrl.value = response.download_url || ''
    result.value = JSON.stringify(response, null, 2)
  }
  if (action === 'review') {
    selectedStep.value = 'review'
    const content = `${store.currentProject?.title || ''}\n${chapterPreview.value || '正常论文内容：三线表、流程图包含判断节点，未出现高风险问题。'}`
    const response = await api.runReview(projectId, content)
    reviewResult.value = response
    result.value = JSON.stringify(response, null, 2)
  }
  await store.loadProject(projectId)
  operationLogs.value.unshift(`完成执行：${action}`)
}

async function generateFullDocx() {
  selectedStep.value = 'formatting'
  const response = await api.generateFullDocx(projectId, useTemplateRules.value)
  fullDocxResult.value = response
  docxDownloadUrl.value = response.download_url
  result.value = JSON.stringify(response, null, 2)
  operationLogs.value.unshift(`完整论文 DOCX 已生成，格式审查得分：${response.format_validation.score}`)
}

async function runBlockedReview() {
  selectedStep.value = 'review'
  const response = await api.runReview(projectId, '流程图线条交叉，表格不是三线表，测试章节写成操作流水账。')
  reviewResult.value = response
  result.value = JSON.stringify(response, null, 2)
  operationLogs.value.unshift(response.allow_export ? '最终审查：允许导出' : `最终审查：禁止导出，原因 ${response.blocked_reasons.join('；')}`)
}

function onChatParsed(payload: ChatIntent) {
  operationLogs.value.unshift(`对话解析：${payload.intent} / ${payload.requirement}`)
  if (payload.should_create_rule) {
    operationLogs.value.unshift('已写入记忆库/错误库，并生成 MemoryGuard 规则。')
  }
}
</script>

<template>
  <section v-if="store.currentProject" class="workspace-grid">
    <ProcessSidebar
      :current-step="store.currentProject.current_step"
      :selected-step="selectedStep"
      :statuses="store.currentProject.step_statuses"
      @select="selectedStep = $event"
    />
    <main class="workspace-center">
      <div class="workspace-title">
        <div>
          <h1>{{ store.currentProject.title }}</h1>
          <p>当前状态：{{ store.currentProject.status }} / 当前版本：v0.2 / 当前工作区：{{ currentStepTitle }}</p>
        </div>
        <el-button type="success" @click="generateFullDocx">生成完整论文 DOCX</el-button>
      </div>

      <el-alert title="v0.2 完整闭环" description="依次完成模板分析、大纲生成、章节生成、对话记忆、DOCX 生成、MemoryGuard 审查和导出闸门判断。" type="info" show-icon />

      <div class="action-row">
        <el-button @click="router.push(`/templates/${projectId}`)">模板分析页</el-button>
        <el-button @click="router.push(`/outline/${projectId}`)">大纲规划页</el-button>
        <el-button @click="router.push(`/chapters/${projectId}`)">分章写作页</el-button>
        <el-button @click="router.push(`/reviews/${projectId}`)">审查报告页</el-button>
      </div>
      <div class="action-row">
        <el-button type="primary" @click="run('template')">模板分析</el-button>
        <el-button type="primary" @click="run('outline')">大纲生成</el-button>
        <el-button type="primary" @click="run('chapter')">生成第1章</el-button>
        <el-button type="success" @click="run('docx')">生成 DOCX</el-button>
        <el-button type="success" @click="generateFullDocx">生成完整论文 DOCX</el-button>
        <el-switch v-model="useTemplateRules" active-text="使用模板规则" inactive-text="默认格式" />
        <el-button type="warning" @click="run('review')">最终审查</el-button>
        <el-button type="danger" @click="runBlockedReview">模拟禁止导出</el-button>
      </div>

      <section class="step-work-area">
        <h2>{{ currentStepTitle }}</h2>
        <template v-if="selectedStep === 'outline'">
          <el-timeline>
            <el-timeline-item v-for="chapter in outlineChapters" :key="chapter">{{ chapter }}</el-timeline-item>
          </el-timeline>
        </template>
        <template v-else-if="selectedStep === 'writing'">
          <el-card><pre>{{ chapterPreview || '点击“生成第1章”后展示章节示例内容。' }}</pre></el-card>
        </template>
        <template v-else-if="selectedStep === 'formatting'">
          <p>DOCX 下载路径：<code>{{ docxDownloadUrl || '尚未生成' }}</code></p>
          <el-card v-if="fullDocxResult" class="docx-report">
            <h3>格式审查报告</h3>
            <p>是否使用模板规则：{{ fullDocxResult.used_template_rules ? '是' : '否' }}</p>
            <p>格式审查评分：{{ fullDocxResult.format_validation.score }}</p>
            <p>审查结果：{{ fullDocxResult.format_validation.passed ? '通过' : '存在警告' }}</p>
            <h4>已应用规则</h4>
            <el-tag v-for="item in fullDocxResult.applied_rules_summary" :key="item" class="tag-item">{{ item }}</el-tag>
            <h4>缺失规则（已使用默认值）</h4>
            <el-tag v-for="item in fullDocxResult.missing_rules" :key="item" type="warning" class="tag-item">{{ item }}</el-tag>
            <h4>warnings</h4>
            <el-alert v-for="warning in fullDocxResult.format_validation.warnings" :key="warning" type="warning" :title="warning" show-icon />
          </el-card>
        </template>
        <template v-else-if="selectedStep === 'review'">
          <el-result
            v-if="reviewResult"
            :icon="reviewResult.allow_export ? 'success' : 'error'"
            :title="reviewResult.allow_export ? '允许导出' : '禁止导出'"
            :sub-title="reviewResult.blocked_reasons.join('；') || `审查得分：${reviewResult.score}`"
          />
        </template>
        <pre class="result-box">{{ result }}</pre>
      </section>

      <StatusFooter version="v0.2" :status="store.currentProject.status" :step="store.currentProject.current_step" />
      <footer class="operation-log">
        <strong>最近一次操作日志：</strong>{{ operationLogs[0] }}
      </footer>
    </main>
    <ChatPanel :project-id="projectId" @parsed="onChatParsed" />
  </section>
</template>
