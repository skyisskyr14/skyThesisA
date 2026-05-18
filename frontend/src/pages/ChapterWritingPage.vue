<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api/client'

const projectId = Number(useRoute().params.id)
const chapterNo = ref(1)
const result = ref('分章写作结果将在这里展示。')
async function generate() {
  result.value = JSON.stringify(await api.generateChapter(projectId, chapterNo.value), null, 2)
}
</script>

<template>
  <section class="panel-page">
    <h1>分章写作页</h1>
    <p>ChapterWriterAgent MVP 先生成结构化段落，后续接入真实 LLM、引用处理与学术润色。</p>
    <el-input-number v-model="chapterNo" :min="1" :max="6" />
    <el-button type="primary" @click="generate">生成章节</el-button>
    <pre class="result-box">{{ result }}</pre>
  </section>
</template>
