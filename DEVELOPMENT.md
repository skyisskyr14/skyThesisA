# Thesis Agent MVP 开发说明

## 1. 项目结构

```text
backend/                  FastAPI 后端服务
  app/main.py             应用入口、CORS、路由注册、默认规则初始化
  app/database.py         SQLite 与 SQLAlchemy 初始化
  app/models/             论文项目、文件、版本、章节、图表、引用、批注、返工、审查、记忆、错误、规则模型
  app/schemas/            Pydantic API 数据结构
  app/routes/             项目、上传、模板分析、大纲、章节、对话、记忆、错误、审查、DOCX API
  app/services/           状态机、模拟 Agent、对话意图解析
  app/agents/             后续真实 LLM Agent 扩展点
  app/docx_engine/        python-docx 最小精排示例
  app/memory_guard/       默认规则、错误转规则、最终导出闸门
frontend/                 Vue 3 + Vite + TypeScript + Element Plus 前端工作台
  src/pages/              项目列表、新建项目、工作台、模板、大纲、章节、记忆、错误、审查页面
  src/components/         左侧流程、右侧对话区、状态栏组件
  src/api/                后端 API 调用封装
  src/stores/             Pinia 项目状态
  src/router/             页面路由
```

## 2. 启动后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

健康检查：

```bash
curl http://127.0.0.1:8000/api/health
```

接口文档：

```text
http://127.0.0.1:8000/docs
```

FastAPI 启动时会自动创建 SQLite 数据库 `backend/data/thesis_agent.db`，并写入 MemoryGuard 默认规则。

## 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

浏览器访问：

```text
http://127.0.0.1:5173
```

前端开发服务器已通过 `vite.config.ts` 将 `/api` 代理到 `http://127.0.0.1:8000`。

## 4. 测试创建论文项目

```bash
curl -X POST http://127.0.0.1:8000/api/projects \
  -H 'Content-Type: application/json' \
  -d '{"title":"Thesis Agent v0.2 闭环示例论文","author":"学生姓名","major":"软件工程","school":"学校名称"}'
```

查询项目：

```bash
curl http://127.0.0.1:8000/api/projects
```

## 5. 测试模板分析

```bash
curl -X POST 'http://127.0.0.1:8000/api/templates/analyze?project_id=1'
```

接口会返回混合型模板识别、格式规则和冲突说明，并把项目状态推进到 `parsed`。

## 6. 测试大纲生成

```bash
curl -X POST 'http://127.0.0.1:8000/api/outlines/generate?project_id=1'
```

接口会返回第 1 章到第 6 章的模拟论文目录，并把项目状态推进到 `planned`。

## 7. 测试章节生成

```bash
curl -X POST 'http://127.0.0.1:8000/api/chapters/generate?project_id=1&chapter_no=1'
```

接口会生成第 1 章示例结构化内容，并把项目状态推进到 `writing`。

## 8. 测试右侧对话意图解析

记录历史错误并生成规则：

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"project_id":1,"message":"刚刚这个图线条交叉了，记住，以后不能再犯"}'
```

加入长期规则：

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"project_id":1,"message":"以后所有流程图都要有判断节点"}'
```

局部修改和格式保护：

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"project_id":1,"message":"只改第3章，只改内容，不要动格式，其他不要动"}'
```

## 9. 测试 MemoryGuard

触发禁止导出：

```bash
curl -X POST http://127.0.0.1:8000/api/reviews/run \
  -H 'Content-Type: application/json' \
  -d '{"project_id":1,"content":"流程图线条交叉，表格不是三线表，测试章节写成操作流水账"}'
```

预期返回：

- `passed: false`
- `allow_export: false`
- `blocked_reasons` 包含命中的高风险规则
- `matched_rules` 包含规则代码、名称、类型、严重级别和命中关键词
- `auto_fix_suggestions` 给出自动修复建议

通过审查：

```bash
curl -X POST http://127.0.0.1:8000/api/reviews/run \
  -H 'Content-Type: application/json' \
  -d '{"project_id":1,"content":"论文内容已保持原格式，流程图包含判断节点，表格均为三线表，测试章节按测试用例组织"}'
```

## 10. 测试 DOCX 生成

```bash
curl -X POST 'http://127.0.0.1:8000/api/docx/generate?project_id=1'
```

DOCX 会保存到：

```text
backend/storage/docx/project_1_sample.docx
```

接口会返回 `download_url`，例如：

```text
/api/docx/download/project_1_sample.docx
```

下载生成文件：

```bash
curl -L -o sample.docx http://127.0.0.1:8000/api/docx/download/project_1_sample.docx
```

生成内容包括论文标题、摘要占位、关键词占位、一级标题、正文段落、图 1-1 占位、表 1-1 三线表和参考文献占位。

## 11. 前端闭环验收

1. 打开 `http://127.0.0.1:5173`；
2. 新建论文任务；
3. 进入工作台；
4. 依次点击“模板分析”“大纲生成”“生成第1章”；
5. 在右侧对话区输入“刚刚这个图线条交叉了，记住，以后不能再犯”；
6. 点击“生成 DOCX”；
7. 点击“最终审查”查看允许导出结果；
8. 点击“模拟禁止导出”查看 MemoryGuard 阻断原因。

## 12. v0.2 完成内容

- 跑通第一条论文任务闭环：项目创建、模板分析、大纲生成、章节生成、右侧对话、DOCX 生成、最终审查、导出闸门。
- MemoryGuard 规则结构升级为 `rule_code/rule_name/rule_type/severity/trigger_keywords/correction_strategy/block_final_output`。
- 最终审查接口返回 `passed/allow_export/score/blocked_reasons/warnings/matched_rules/auto_fix_suggestions`。
- 右侧对话区增强为可识别局部修改、格式保护、长期规则、历史错误、章节重写和图表要求。
- DOCX 输出目录调整为 `backend/storage/docx/`，并增强摘要、关键词、图题、表题和三线表示例。

## 13. v0.3 建议方向

- 接入真实 DOCX 模板解析，提取页面、字体、段落、标题、页眉页脚和图表题规则。
- 实现老师批注 DOCX 读取，将批注转为返工任务并支持逐条确认。
- 将模拟 Agent 替换为真实 LLM Agent，并加入引用规划、图表规划和学术润色。
- 为 MemoryGuard 增加语义匹配、历史错误回归测试和导出前强制审查报告。
- 增加自动化测试，覆盖 API、状态机、DOCX 生成和前端核心交互。

---

## 14. v0.3 DOCX 模板解析引擎

v0.3 将模板分析从模拟结果升级为真实 DOCX 读取，新增 `backend/app/template_engine/`：

```text
backend/app/template_engine/
  docx_template_parser.py          # 统一解析入口，输出 template_rules JSON
  style_extractor.py               # 样式摘要提取
  section_extractor.py             # 页面尺寸、页边距、分节提取
  paragraph_rule_extractor.py      # 正文段落规则提取
  heading_rule_extractor.py        # 一级/二级/三级标题识别
  table_rule_extractor.py          # 图题、表题、表格和三线表倾向识别
  header_footer_extractor.py       # 页眉页脚提取
  reference_extractor.py           # 参考文献标题和编号样例识别
  instruction_rule_extractor.py    # 中文说明型规则正则抽取
  template_rule_merger.py          # 说明规则和样式规则合并
  template_conflict_detector.py    # 冲突检测
```

### 14.1 使用测试 DOCX 模板

仓库不提交成品 DOCX（二进制文件），只提交生成脚本。测试模板路径为：

```text
tests/fixtures/sample_template.docx
```

如果该文件不存在，`tests/test_template_parser.py` 会自动调用 `tests/scripts/create_sample_template.py` 生成；也可以手动生成：

```bash
python tests/scripts/create_sample_template.py
```

生成的 DOCX 包含格式说明文字、摘要、关键词、第1章、图题、表题、三线表、页眉页脚和参考文献样例，但不会提交到 Git。

### 14.2 调用真实模板解析接口

```bash
curl -X POST http://127.0.0.1:8000/api/thesis/templates/analyze-docx \
  -H 'Content-Type: application/json' \
  -d '{"project_id":1,"file_path":"tests/fixtures/sample_template.docx"}'
```

也可以先通过上传接口得到 `file_id`，再调用：

```bash
curl -X POST http://127.0.0.1:8000/api/thesis/templates/analyze-docx \
  -H 'Content-Type: application/json' \
  -d '{"project_id":1,"file_id":1}'
```

获取最近一次模板分析结果：

```bash
curl http://127.0.0.1:8000/api/thesis/templates/1/latest
```

### 14.3 template_rules JSON 字段说明

真实解析接口统一返回 `rules_json`，前端和 DOCX 生成不依赖零散字段：

- `template_type`：`instruction_only`、`sample_paper`、`mixed`、`unknown`；
- `confidence`：模板类型识别和规则抽取置信度；
- `page`：纸张大小、页面宽高、上下左右页边距、分节数量；
- `body`：中英文字体、字号、行距、首行缩进、对齐方式、段前段后；
- `headings`：标题级别、样式名、字体、字号、加粗、对齐、编号模式、段前段后；
- `figures`：图题位置、图题模式、字体、字号、对齐和样例；
- `tables`：表题位置、表题模式、三线表倾向、表格数量、边框摘要、表头和单元格样式；
- `header_footer`：页眉、页脚和页码信息；
- `references`：参考文献标题、编号样式和样例；
- `conflicts`：说明规则与样例样式不一致时的冲突列表；
- `warnings`：缺失或不确定规则；
- `source_evidence`：每条规则来源，例如“段落文本说明”“样式 Heading 1”。

### 14.4 在前端查看模板解析结果

1. 启动后端和前端；
2. 新建论文项目并进入工作台；
3. 点击“模板分析页”；
4. 使用默认路径 `tests/fixtures/sample_template.docx`；如果文件不存在，先运行 `python tests/scripts/create_sample_template.py` 生成；
5. 点击“真实解析 DOCX 模板”；
6. 页面会分区展示页面设置、正文规则、标题规则、图题规则、表格规则、页眉页脚、参考文献、冲突、warnings 和 source_evidence；
7. 点击“查看 JSON”可查看完整 `template_rules`。

### 14.5 应用模板规则到 DOCX 生成

应用最近一次分析结果：

```bash
curl -X POST http://127.0.0.1:8000/api/thesis/templates/apply \
  -H 'Content-Type: application/json' \
  -d '{"project_id":1,"analysis_id":1}'
```

之后调用 DOCX 生成：

```bash
curl -X POST 'http://127.0.0.1:8000/api/docx/generate?project_id=1'
```

当前 DOCX 生成会初步应用：页边距、正文字体、正文字号、正文行距、首行缩进、一级标题字号、一级标题对齐、图题样式、表题样式和三线表设置。

### 14.6 v0.3 测试脚本

```bash
PYTHONPATH=backend python tests/test_template_parser.py
```

该脚本会在 `tests/fixtures/sample_template.docx` 不存在时自动生成测试模板，并验证：

1. DOCX 模板解析可运行；
2. `template_rules` 包含必要字段；
3. 冲突检测可识别说明规则与样例样式差异；
4. 应用模板规则后 DOCX 生成不报错。

### 14.7 v0.3 当前能力边界

- 说明型规则使用正则和关键词识别，不依赖真实 LLM；
- 成品论文型规则基于 `python-docx` 可读取的信息，复杂编号、域代码页码、复杂 OOXML 边框仍需 v0.4 深化；
- 三线表判断目前是倾向识别，不等同于完整 Word 边框审计；
- 冲突检测先覆盖正文、图题、表题、三线表、参考文献和标题关键字段。

### 14.8 v0.4 建议方向

- 增强 OOXML 级别边框、页码域、目录域和多级编号读取；
- 支持直接上传多个模板并生成模板冲突报告；
- 将 template_rules 与 DocxEngine 的 StyleManager、TableManager、FigureManager 深度打通；
- 引入真实老师批注解析，并将批注约束写入 MemoryGuard；
- 增加 pytest/API/前端 E2E 测试，覆盖完整模板解析和 DOCX 精排闭环。
