<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api/client'

const projectId = Number(useRoute().params.id)
const result = ref('大纲规划结果将在这里展示。')
async function generate() {
  result.value = JSON.stringify(await api.generateOutline(projectId), null, 2)
}
</script>

<template>
  <section class="panel-page">
    <h1>大纲规划页</h1>
    <p>PaperStructureAgent 将生成论文目录，并把结果进入结构化 JSON。</p>
    <el-button type="primary" @click="generate">生成模拟大纲</el-button>
    <pre class="result-box">{{ result }}</pre>
  </section>
</template>
