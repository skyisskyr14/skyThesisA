<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api/client'

const projectId = Number(useRoute().params.id)
const result = ref('模板分析结果将在这里展示：纯说明型、成品论文型、混合型与冲突报告。')
async function analyze() {
  result.value = JSON.stringify(await api.analyzeTemplate(projectId), null, 2)
}
</script>

<template>
  <section class="panel-page">
    <h1>模板分析页</h1>
    <p>保留 TemplateAnalyzerAgent 扩展点，后续接入真实 DOCX 样式提取和规则冲突报告。</p>
    <el-button type="primary" @click="analyze">运行模板分析模拟接口</el-button>
    <pre class="result-box">{{ result }}</pre>
  </section>
</template>
