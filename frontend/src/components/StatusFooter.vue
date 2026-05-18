<script setup lang="ts">
defineProps<{ version: string; status: string; step: string }>()
</script>

<template>
  <footer class="status-footer">
    <span>当前版本：{{ version }}</span>
    <span>项目状态：{{ status }}</span>
    <span>当前步骤：{{ step }}</span>
  </footer>
</template>
