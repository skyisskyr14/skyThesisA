<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '../api/client'
const providers = ref<any[]>([])
const form = ref({ provider_name:'DeepSeek', provider_type:'deepseek', base_url:'https://api.deepseek.com/v1', api_key:'', default_model:'deepseek-chat', is_active:true })
async function load(){ providers.value = await (api as any).request?.('/api/thesis/llm/providers') || await fetch('/api/thesis/llm/providers').then(r=>r.json()) }
async function create(){ await fetch('/api/thesis/llm/providers',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(form.value)}); await load() }
onMounted(load)
</script>
<template><section><h2>模型配置中心</h2><el-form><el-input v-model="form.provider_name" placeholder="供应商名称"/><el-input v-model="form.base_url" placeholder="Base URL"/><el-input v-model="form.api_key" placeholder="API Key"/><el-input v-model="form.default_model" placeholder="默认模型"/><el-button @click="create">新增供应商</el-button></el-form><el-table :data="providers"><el-table-column prop="provider_name" label="名称"/><el-table-column prop="provider_type" label="类型"/><el-table-column prop="base_url" label="Base URL"/><el-table-column prop="api_key_masked" label="API Key(脱敏)"/></el-table></section></template>
