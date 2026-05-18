<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api/client'

const projectId = Number(useRoute().params.id)
const content = ref('这里输入待审查论文内容。包含“线条交叉”会触发图表规则。')
const result = ref('终审报告将在这里展示。')
async function runReview() {
  result.value = JSON.stringify(await api.runReview(projectId, content.value), null, 2)
}
</script>

<template>
  <section class="panel-page">
    <h1>终审报告页</h1>
    <p>FinalReviewAgent + MemoryGuard 会检查格式、内容、引用、图表、老师批注和历史错误。</p>
    <el-input v-model="content" type="textarea" :rows="5" />
    <el-button type="warning" @click="runReview">运行最终审查</el-button>
    <pre class="result-box">{{ result }}</pre>
  </section>
</template>
