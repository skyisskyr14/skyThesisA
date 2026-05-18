<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '../api/client'

const errors = ref<unknown[]>([])
const rules = ref<unknown[]>([])
onMounted(async () => {
  errors.value = (await api.listErrors()) as unknown[]
  rules.value = (await api.listRules()) as unknown[]
})
</script>

<template>
  <section class="panel-page">
    <h1>错误库 / 规则库页面</h1>
    <p>错误会转化为规则，并在最终导出闸门中拦截同类问题。</p>
    <h3>历史错误</h3>
    <pre class="result-box">{{ JSON.stringify(errors, null, 2) }}</pre>
    <h3>内置与用户规则</h3>
    <pre class="result-box">{{ JSON.stringify(rules, null, 2) }}</pre>
  </section>
</template>
