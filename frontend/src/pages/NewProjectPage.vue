<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/client'

const router = useRouter()
const form = reactive({ title: '基于 Spring Boot 和 Vue 的论文智能体工作台', author: '学生姓名', major: '软件工程', school: '学校名称' })

async function submit() {
  const project = await api.createProject(form)
  router.push(`/workspace/${project.id}`)
}
</script>

<template>
  <section class="form-page">
    <h1>新建论文任务</h1>
    <el-form label-width="100px">
      <el-form-item label="论文题目"><el-input v-model="form.title" /></el-form-item>
      <el-form-item label="作者"><el-input v-model="form.author" /></el-form-item>
      <el-form-item label="专业"><el-input v-model="form.major" /></el-form-item>
      <el-form-item label="学校"><el-input v-model="form.school" /></el-form-item>
      <el-button type="primary" @click="submit">创建并进入工作台</el-button>
    </el-form>
  </section>
</template>
