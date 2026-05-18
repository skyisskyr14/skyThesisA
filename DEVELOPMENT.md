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

## 4. 测试 DOCX 生成

先创建项目：

```bash
curl -X POST http://127.0.0.1:8000/api/projects \
  -H 'Content-Type: application/json' \
  -d '{"title":"Thesis Agent MVP 示例论文","author":"学生姓名","major":"软件工程","school":"学校名称"}'
```

生成 DOCX：

```bash
curl -X POST 'http://127.0.0.1:8000/api/docx/generate?project_id=1'
```

下载接口返回的 `download_url`，即可获得包含论文标题、一级标题、正文段落、图题占位、表题、三线表与参考文献占位的 DOCX。

## 5. MemoryGuard 验证

运行最终审查：

```bash
curl -X POST http://127.0.0.1:8000/api/reviews/run \
  -H 'Content-Type: application/json' \
  -d '{"project_id":1,"content":"这里包含流程图线条交叉，需要触发历史规则"}'
```

当内容命中高风险规则或历史错误时，接口会返回 `allow_export: false` 和 `blocked_reasons`，表示最终导出闸门已拦截。

## 6. 后续接入真实 Agent 的位置

- `app/services/mock_agents.py`：当前返回确定性模拟结果，后续替换为 TemplateAnalyzerAgent、PaperStructureAgent、ChapterWriterAgent 等真实 Agent。
- `app/services/chat_parser.py`：当前使用关键词解析意图，后续替换为 Intent Agent。
- `app/docx_engine/generator.py`：当前为最小 DOCX 示例，后续拆分 StyleManager、SectionManager、TableManager、FigureManager、CitationManager、CommentManager、Validator、Exporter。
- `app/memory_guard/service.py`：当前基于触发词检查规则，后续接入语义检索、历史错误回归测试与导出前强制审查。
