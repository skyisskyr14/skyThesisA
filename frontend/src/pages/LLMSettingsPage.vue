<script setup lang="ts">
import { onMounted, ref } from 'vue'
const providers=ref<any[]>([])
const usage=ref<any>(null)
const form=ref<any>({provider_name:'',provider_type:'deepseek',base_url:'https://api.deepseek.com',credential_source:'environment_variable',credential_env_name:'DEEPSEEK_API_KEY',api_key:'',default_model:'deepseek-v4-flash',is_active:true})
async function load(){ providers.value=await fetch('/api/thesis/llm/providers').then(r=>r.json()) }
async function save(){ const method=form.value['id']?'PUT':'POST'; const url=form.value['id']?`/api/thesis/llm/providers/${form.value['id']}`:'/api/thesis/llm/providers'; await fetch(url,{method,headers:{'Content-Type':'application/json'},body:JSON.stringify(form.value)}); form.value.api_key=''; await load() }
async function test(id:number){ alert(JSON.stringify(await fetch(`/api/thesis/llm/providers/${id}/test`,{method:'POST'}).then(r=>r.json()))) }
onMounted(load)
</script>
<template><section><h2>模型配置中心</h2><el-form><el-input v-model="form.provider_name" placeholder="供应商名称"/><el-select v-model="form.credential_source"><el-option label="环境变量" value="environment_variable"/><el-option label="数据库加密" value="encrypted_database"/></el-select><el-input v-model="form.credential_env_name" v-if="form.credential_source==='environment_variable'"/><el-input v-model="form.api_key" v-else placeholder="API Key" show-password/><el-input v-model="form.base_url"/><el-input v-model="form.default_model"/><el-button @click="save">保存</el-button></el-form><el-table :data="providers"><el-table-column prop="provider_name" label="名称"/><el-table-column prop="provider_type" label="类型"/><el-table-column prop="credential_source" label="凭证来源"/><el-table-column prop="credential_status" label="状态"/><el-table-column prop="api_key_masked" label="脱敏Key"/><el-table-column prop="default_model" label="默认模型"/><el-table-column label="操作"><template #default="s"><el-button @click="test(s.row.id)">测试</el-button></template></el-table-column></el-table></section></template>
