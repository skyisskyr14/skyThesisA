<script setup lang="ts">
import type { StepStatus } from '../types'

const props = defineProps<{ currentStep: string; statuses: Record<string, StepStatus> }>()

const steps = [
  ['upload', '上传资料'],
  ['template', '解析模板'],
  ['outline', '生成大纲'],
  ['writing', '分章写作'],
  ['figures', '图表规划'],
  ['formatting', '格式排版'],
  ['comments', '批注返修'],
  ['review', '最终审查'],
  ['export', '导出论文']
]
</script>

<template>
  <aside class="process-sidebar">
    <h3>论文流程</h3>
    <div
      v-for="([key, label], index) in steps"
      :key="key"
      class="step-card"
      :class="{ active: key === props.currentStep }"
    >
      <span class="step-index">{{ index + 1 }}</span>
      <div>
        <strong>{{ label }}</strong>
        <small>{{ props.statuses[key] || 'pending' }}</small>
      </div>
    </div>
  </aside>
</template>
