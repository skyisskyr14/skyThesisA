<script setup lang="ts">
import { ref } from 'vue'
const projectId=ref(1); const fileId=ref(0); const report=ref<any>(null)
async function run(){ report.value=await fetch('/api/thesis/papers/import-docx',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({project_id:projectId.value,file_id:fileId.value})}).then(r=>r.json()) }
</script><template><section><h2>论文导入</h2><el-input v-model="projectId"/><el-input v-model="fileId"/><el-button @click="run">导入为论文结构</el-button><pre>{{report}}</pre></section></template>
