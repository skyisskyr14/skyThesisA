<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '../api/client'

const rows = ref<unknown[]>([])
onMounted(async () => {
  rows.value = (await api.listMemory()) as unknown[]
})
</script>

<template>
  <section class="panel-page">
    <h1>记忆库页面</h1>
    <p>展示用户偏好、项目记忆、老师意见、审查结果等记忆，后续接入 MemoryGuard 检索。</p>
    <pre class="result-box">{{ JSON.stringify(rows, null, 2) }}</pre>
  </section>
</template>
