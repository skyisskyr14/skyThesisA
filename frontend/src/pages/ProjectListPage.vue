<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectStore } from '../stores/projectStore'

const store = useProjectStore()
const router = useRouter()
onMounted(() => store.loadProjects())
</script>

<template>
  <section>
    <div class="page-header">
      <h1>论文项目列表</h1>
      <el-button type="primary" @click="router.push('/projects/new')">新建论文任务</el-button>
    </div>
    <el-empty v-if="!store.projects.length" description="暂无项目，请先新建论文任务" />
    <el-row :gutter="16">
      <el-col v-for="project in store.projects" :key="project.id" :span="8">
        <el-card class="project-card">
          <h3>{{ project.title }}</h3>
          <p>{{ project.school }} / {{ project.major }} / {{ project.author }}</p>
          <el-tag>{{ project.status }}</el-tag>
          <el-button text type="primary" @click="router.push(`/workspace/${project.id}`)">进入工作台</el-button>
        </el-card>
      </el-col>
    </el-row>
  </section>
</template>
