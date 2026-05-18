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
