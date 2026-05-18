<script setup lang="ts">
import { ref } from 'vue'
import { api } from '../api/client'

const props = defineProps<{ projectId?: number }>()
const input = ref('只改第5章，其他不要动，并保持原格式。')
const messages = ref<{ role: string; text: string }[]>([
  { role: 'agent', text: '我会把右侧对话解析为局部修改、格式保护、记录错误或长期规则等任务意图。' }
])
const loading = ref(false)

async function send() {
  if (!input.value.trim()) return
  const raw = input.value
  messages.value.push({ role: 'user', text: raw })
  input.value = ''
  loading.value = true
  const parsed = await api.parseChat(props.projectId, raw)
  messages.value.push({ role: 'agent', text: `${parsed.agent_reply}\n意图：${parsed.intent}；范围：${parsed.scope || '当前步骤'}；保护格式：${parsed.protect_format}` })
  loading.value = false
}
</script>

<template>
  <aside class="chat-panel">
    <h3>和论文 Agent 聊</h3>
    <div class="chat-list">
      <div v-for="(msg, index) in messages" :key="index" class="chat-message" :class="msg.role">
        <b>{{ msg.role === 'user' ? '用户' : 'Agent' }}</b>
        <p>{{ msg.text }}</p>
      </div>
    </div>
    <el-input v-model="input" type="textarea" :rows="4" placeholder="输入对论文任务的补充要求" />
    <el-button type="primary" :loading="loading" @click="send">解析并记录任务</el-button>
  </aside>
</template>
