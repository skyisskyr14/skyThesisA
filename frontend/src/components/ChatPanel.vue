<script setup lang="ts">
import { ref } from 'vue'
import { api } from '../api/client'

const props = defineProps<{ projectId?: number; currentStep?: string }>()
const emit = defineEmits<{ parsed: [payload: any] }>()
const input = ref('第3章写得太多了，只改第3章，不要动格式。')
const messages = ref<{ role: string; text: string }[]>([{ role: 'agent', text: '已切换为真实大模型对话。' }])
const loading = ref(false)

async function send() {
  if (!input.value.trim() || !props.projectId) return
  const raw = input.value
  messages.value.push({ role: 'user', text: raw })
  input.value = ''
  loading.value = true
  try {
    const resp = await api.sendChat({ project_id: props.projectId, message: raw, current_step: props.currentStep || 'chapter_writing' })
    messages.value.push({ role: 'agent', text: `${resp.assistant_message}\n动作:${JSON.stringify(resp.parsed_intent)}` })
    emit('parsed', resp)
  } catch (e: any) {
    messages.value.push({ role: 'agent', text: `调用失败：${e.message}` })
  }
  loading.value = false
}
</script>
<template><aside class="chat-panel"><h3>右侧实时对话</h3><div class="chat-list"><div v-for="(msg, i) in messages" :key="i" class="chat-message" :class="msg.role"><b>{{ msg.role === 'user' ? '用户' : 'Agent' }}</b><p>{{ msg.text }}</p></div></div><el-input v-model="input" type="textarea" :rows="4" /><el-button type="primary" :loading="loading" @click="send">发送</el-button></aside></template>
