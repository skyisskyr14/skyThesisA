<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api/client'
import type { TemplateAnalysisResult } from '../types'

const projectId = Number(useRoute().params.id)
const fixturePath = ref('tests/fixtures/sample_template.docx')
const result = ref<TemplateAnalysisResult | null>(null)
const rawVisible = ref(false)
const loading = ref(false)

const typeLabel = computed(() => {
  const map: Record<string, string> = {
    instruction_only: '纯说明型',
    sample_paper: '成品论文型',
    mixed: '混合型',
    unknown: '未知'
  }
  return result.value ? map[result.value.template_type] : '未分析'
})

onMounted(async () => {
  try {
    result.value = await api.latestTemplateResult(projectId)
  } catch {
    // 首次进入允许无历史结果。
  }
})

async function analyzeRealDocx() {
  loading.value = true
  result.value = await api.analyzeDocxTemplate({ project_id: projectId, file_path: fixturePath.value })
  loading.value = false
}

async function applyRules() {
  if (!result.value) return
  await api.applyTemplateRules(projectId, result.value.id)
  result.value = await api.latestTemplateResult(projectId)
}

async function rerun() {
  await analyzeRealDocx()
}

async function runMockAnalysis() {
  const response = await api.analyzeTemplate(projectId)
  result.value = {
    id: 0,
    project_id: projectId,
    template_type: 'mixed',
    confidence: 0.5,
    rules_json: response as Record<string, any>,
    conflicts_json: [],
    warnings_json: ['当前为 v0.2 兼容模拟分析结果，不是 template_rules 标准结构。'],
    source_evidence_json: [],
    applied: false,
    created_at: new Date().toISOString()
  }
}
</script>

<template>
  <section class="panel-page">
    <h1>模板分析页 v0.3</h1>
    <p>真实读取 DOCX 模板，输出统一 template_rules JSON，为后续 DOCX 精排引擎提供依据。</p>
    <el-form label-width="140px">
      <el-form-item label="DOCX 模板路径">
        <el-input v-model="fixturePath" placeholder="tests/fixtures/sample_template.docx 或上传文件路径" />
      </el-form-item>
    </el-form>
    <div class="action-row">
      <el-button type="primary" :loading="loading" @click="analyzeRealDocx">真实解析 DOCX 模板</el-button>
      <el-button type="success" :disabled="!result" @click="applyRules">应用模板规则</el-button>
      <el-button :disabled="!result" @click="rerun">重新分析</el-button>
      <el-button :disabled="!result" @click="rawVisible = !rawVisible">查看 JSON</el-button>
      <el-button @click="runMockAnalysis">兼容 v0.2 模拟分析</el-button>
    </div>

    <el-empty v-if="!result" description="尚未解析模板，请点击真实解析 DOCX 模板" />
    <template v-else>
      <el-descriptions title="模板概览" border :column="4">
        <el-descriptions-item label="模板类型">{{ typeLabel }}</el-descriptions-item>
        <el-descriptions-item label="置信度">{{ result.confidence }}</el-descriptions-item>
        <el-descriptions-item label="分析 ID">{{ result.id }}</el-descriptions-item>
        <el-descriptions-item label="是否应用">{{ result.applied ? '已应用' : '未应用' }}</el-descriptions-item>
      </el-descriptions>

      <el-tabs class="template-tabs">
        <el-tab-pane label="页面设置"><pre>{{ JSON.stringify(result.rules_json.page, null, 2) }}</pre></el-tab-pane>
        <el-tab-pane label="正文规则"><pre>{{ JSON.stringify(result.rules_json.body, null, 2) }}</pre></el-tab-pane>
        <el-tab-pane label="标题规则"><pre>{{ JSON.stringify(result.rules_json.headings, null, 2) }}</pre></el-tab-pane>
        <el-tab-pane label="图题规则"><pre>{{ JSON.stringify(result.rules_json.figures, null, 2) }}</pre></el-tab-pane>
        <el-tab-pane label="表题/表格规则"><pre>{{ JSON.stringify(result.rules_json.tables, null, 2) }}</pre></el-tab-pane>
        <el-tab-pane label="页眉页脚"><pre>{{ JSON.stringify(result.rules_json.header_footer, null, 2) }}</pre></el-tab-pane>
        <el-tab-pane label="参考文献"><pre>{{ JSON.stringify(result.rules_json.references, null, 2) }}</pre></el-tab-pane>
      </el-tabs>

      <h3>冲突列表</h3>
      <el-table :data="result.conflicts_json" border empty-text="暂无冲突">
        <el-table-column prop="field" label="字段" />
        <el-table-column prop="instruction_value" label="说明值" />
        <el-table-column prop="sample_value" label="样例值" />
        <el-table-column prop="suggested_value" label="建议值" />
        <el-table-column prop="reason" label="原因" />
      </el-table>

      <h3>warnings</h3>
      <el-alert v-for="warning in result.warnings_json" :key="warning" type="warning" :title="String(warning)" show-icon />

      <h3>source_evidence</h3>
      <el-table :data="result.source_evidence_json" border empty-text="暂无证据">
        <el-table-column prop="field" label="字段" width="180" />
        <el-table-column prop="source" label="来源" width="180" />
        <el-table-column prop="text" label="证据文本" />
      </el-table>

      <pre v-if="rawVisible" class="result-box">{{ JSON.stringify(result.rules_json, null, 2) }}</pre>
    </template>
  </section>
</template>
