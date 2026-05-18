<template>
  <el-container class="app-shell">
    <el-header class="topbar">
      <router-link class="brand" to="/">Thesis Agent 论文智能体工作台</router-link>
      <nav>
        <router-link to="/">项目</router-link>
        <router-link to="/memory">记忆库</router-link>
        <router-link to="/errors">错误库</router-link>
      </nav>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
  </el-container>
</template>
