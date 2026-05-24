<script setup lang="ts">
import { ref } from 'vue'
const projectId=ref(1); const rows=ref<any[]>([])
async function load(){ rows.value=await fetch(`/api/thesis/versions/${projectId.value}`).then(r=>r.json()) }
</script><template><section><h2>版本管理</h2><el-input v-model="projectId"/><el-button @click="load">加载版本</el-button><pre>{{rows}}</pre></section></template>
