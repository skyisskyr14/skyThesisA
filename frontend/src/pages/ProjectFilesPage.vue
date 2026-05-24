<script setup lang="ts">
import { ref } from 'vue'
const projectId=ref(1); const role=ref('unknown'); const files=ref<any[]>([]); const f=ref<File|null>(null)
async function load(){ files.value = await fetch(`/api/thesis/files/${projectId.value}`).then(r=>r.json()) }
async function upload(){ if(!f.value) return; const fd=new FormData(); fd.append('project_id',String(projectId.value)); fd.append('file_role',role.value); fd.append('file',f.value); await fetch('/api/thesis/files/upload',{method:'POST',body:fd}); await load() }
</script><template><section><h2>项目资料</h2><el-input v-model="projectId"/><input type="file" @change="e=>f=(e.target as any).files[0]"/><el-input v-model="role"/><el-button @click="upload">上传</el-button><el-button @click="load">刷新</el-button><pre>{{files}}</pre></section></template>
