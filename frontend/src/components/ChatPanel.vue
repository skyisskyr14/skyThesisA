<script setup lang="ts">
import { ref } from 'vue'
import { api } from '../api/client'
import type { ChatIntent } from '../types'

const props = defineProps<{ projectId?: number }>()
const emit = defineEmits<{ parsed: [payload: ChatIntent] }>()
const input = ref('刚刚这个图线条交叉了，记住，以后不能再犯。')
const messages = ref<{ role: string; text: string }[]>([
  { role: 'agent', text: '我会把右侧对话解析为局部修改、格式保护、章节重写、图表要求、长期规则或历史错误。' }
])
const loading = ref(false)

async function send() {
  if (!input.value.trim()) return
  const raw = input.value
  messages.value.push({ role: 'user', text: raw })
  input.value = ''
  loading.value = true
  const parsed = await api.parseChat(props.projectId, raw)
  const savedTip = parsed.should_create_rule ? '\n提示：已写入记忆库/错误库，并生成最终审查规则。' : ''
  messages.value.push({
    role: 'agent',
    text: `${parsed.agent_reply}\n意图：${parsed.intent}\n范围：${parsed.scope || '当前步骤'}\n对象：${parsed.target || '未指定'}\n要求：${parsed.requirement}${savedTip}`
  })
  emit('parsed', parsed)
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
