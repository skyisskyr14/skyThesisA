# Thesis Agent 论文智能体工作台

## 一、项目简介

Thesis Agent 是一个面向毕业论文、课程论文、开题报告、中期报告、答辩材料的多 Agent 自动化论文工作台。

本项目的目标不是简单生成论文内容，而是构建一个完整的论文生产系统，让 AI 能够像论文助理团队一样完成资料解析、模板分析、论文写作、DOCX 排版、老师批注返修、图表生成、引用处理、最终审查、版本管理、记忆纠错等工作。

系统最终要实现：

- 自动分析学校论文模板；
- 自动识别纯说明模板、成品论文模板、混合型模板；
- 自动提取论文格式规则；
- 自动生成论文大纲；
- 自动分章节写作；
- 自动生成或规划流程图、架构图、ER 图、测试表、字段表；
- 自动处理参考文献引用；
- 自动使用 python-docx 精准排版 DOCX；
- 自动读取老师批注并生成返工任务；
- 自动根据批注修改论文；
- 自动执行多轮审查；
- 自动保存历史错误和成功经验；
- 自动避免重复犯错；
- 最终导出 DOCX、PDF、审查报告和修改记录。

本系统的核心目标是：

```text
把论文写作、排版、返工、审查全部流程化、自动化、可追踪化。
```

---

## 二、核心设计理念

本系统不是一个单体聊天机器人，而是一个多 Agent 协作系统。

整体流程如下：

```text
用户上传资料
    ↓
文件识别
    ↓
模板分析
    ↓
论文规划
    ↓
分章写作
    ↓
图表规划
    ↓
参考文献处理
    ↓
DOCX 精准排版
    ↓
老师批注解析
    ↓
自动返工
    ↓
多 Agent 审查
    ↓
最终导出
```

系统必须遵守以下原则：

1. AI 负责理解、写作、规划、审查；
2. 程序负责格式、结构、版本、规则和校验；
3. DOCX 不能直接由 AI 随机生成，必须通过结构化数据和 python-docx 精准生成；
4. 所有论文内容都必须先转化为结构化 JSON，再进入 DOCX 排版引擎；
5. 用户可以在任意流程阶段通过对话追加要求；
6. 系统必须支持局部修改，例如“只改第3章，其他不要动”；
7. 系统必须支持格式保护，例如“只改内容，不动原格式”；
8. 系统必须具备记忆功能和纠错能力；
9. 老师批注、返工原因、错误类型、修正策略都必须保存；
10. 犯过的错误必须转化为规则，后续同类任务中自动拦截。

---

## 三、目标用户与使用场景

本系统主要服务于以下场景：

- 毕业论文撰写；
- 开题报告生成；
- 中期报告生成；
- 论文初稿扩写；
- 论文全文缩写；
- 论文格式排版；
- 老师批注返修；
- 参考文献插入；
- 流程图、架构图、ER 图生成；
- 三线表生成；
- 答辩材料辅助整理；
- 最终论文审查。

典型使用方式：

```text
上传论文初稿 + 学校模板 + 老师批注文档
    ↓
系统自动识别文件类型
    ↓
系统分析模板格式
    ↓
系统解析老师批注
    ↓
系统生成返工任务
    ↓
用户确认或补充要求
    ↓
系统自动修改论文
    ↓
系统重新排版 DOCX
    ↓
系统进行最终审查
    ↓
导出最终论文
```

---

## 四、系统总体架构

建议采用前后端分离架构。

```text
thesis-agent/
├── frontend/              # 前端工作台
├── backend/               # 后端 API 服务
├── docx-engine/           # DOCX 精排引擎
├── agents/                # 多 Agent 逻辑
├── storage/               # 文件存储目录
├── memory/                # 记忆库、错误库、规则库
├── docs/                  # 项目文档
├── tests/                 # 测试与回归用例
└── README.md
```

推荐技术栈：

```text
前端：
Vue 3 + Vite + TypeScript + Element Plus

后端：
FastAPI + Python 3.11+

文档处理：
python-docx
lxml
mammoth
Pillow
LibreOffice headless

数据存储：
SQLite 起步，后续可迁移 MySQL

任务状态：
本地同步任务起步，后续可接 Celery + Redis

图表生成：
SVG 优先
Mermaid / Graphviz 可作为辅助方案
```

---

## 五、前端工作台设计

前端必须采用流程化界面，不允许只做一个普通聊天框。

推荐布局：

```text
┌──────────────────────────────────────────────┐
│ 顶部：论文项目名称 / 当前版本 / 导出按钮       │
├──────────────┬─────────────────┬─────────────┤
│ 左侧流程导航  │ 中间工作区        │ 右侧对话区   │
│              │                 │             │
│ 1 上传资料    │ 当前步骤内容      │ 和论文Agent聊 │
│ 2 解析模板    │ 结果预览/修改     │ 实时补要求    │
│ 3 生成大纲    │ 审查问题/确认     │ Agent提问     │
│ 4 分章写作    │ DOCX预览         │ 用户插话      │
│ 5 图表生成    │                 │             │
│ 6 格式排版    │                 │             │
│ 7 批注返修    │                 │             │
│ 8 最终审查    │                 │             │
│ 9 导出论文    │                 │             │
└──────────────┴─────────────────┴─────────────┘
```

核心页面包括：

1. 论文项目列表页；
2. 新建论文任务页；
3. 文件上传与识别页；
4. 模板分析页；
5. 大纲规划页；
6. 分章写作页；
7. 图表管理页；
8. 参考文献管理页；
9. DOCX 排版页；
10. 老师批注返修页；
11. 终审报告页；
12. 版本管理页；
13. 导出中心页；
14. 记忆库 / 错误库页面。

---

## 六、对话交互设计

右侧对话区必须与当前论文任务绑定，不能是无上下文聊天。

用户可以随时输入：

```text
第3章写得太多了，精简一点。
这个流程图要白底黑字，不要交叉线。
只改第5章，其他不要动。
参考文献每处只引用一个。
表格全部改成三线表。
这条老师批注的意思是测试章节不要写成流水账。
```

系统需要将用户对话解析为任务指令：

```json
{
  "message": "只改第5章，其他不要动",
  "intent": "partial_edit",
  "scope": "chapter_5",
  "protectOthers": true,
  "protectFormat": true
}
```

Agent 也必须能主动提问：

```text
我发现第5章标题是“系统测试”，但你提供的视频主要是系统功能界面。
是否将第5章调整为“系统实现与测试”，还是保留“系统测试”？
```

---

## 七、多 Agent 设计

系统至少包含以下 Agent：

| Agent | 职责 |
|---|---|
| FileRouterAgent | 判断上传文件类型和用途 |
| TemplateAnalyzerAgent | 分析学校模板、格式规范、成品论文样式 |
| PaperStructureAgent | 规划论文目录和章节结构 |
| ProjectCoreAgent | 提取项目核心清单 |
| ChapterWriterAgent | 分章节生成论文内容 |
| AcademicPolishAgent | 学术润色、降低口语化和 AI 味 |
| FigurePlannerAgent | 规划流程图、架构图、ER 图、表格 |
| TableBuilderAgent | 生成三线表、字段表、测试用例表 |
| CitationAgent | 处理参考文献引用和编号 |
| DocxFormatAgent | 控制 DOCX 格式、页眉页脚、段落、表格、图片 |
| TeacherCommentAgent | 读取老师批注并生成返工任务 |
| RevisionAgent | 根据批注和审查结果执行返工 |
| FinalReviewAgent | 最终审查全文 |
| MemoryGuardAgent | 记忆与纠错，防止重复犯错 |

---

## 八、论文结构化数据设计

AI 不能直接生成 DOCX，必须先生成统一结构化 JSON。

示例：

```json
{
  "meta": {
    "title": "论文题目",
    "author": "学生姓名",
    "major": "软件工程",
    "school": "学校名称"
  },
  "abstract": {
    "zh": [
      "第一段背景",
      "第二段研究内容",
      "第三段结果"
    ],
    "keywords": ["Spring Boot", "Vue", "绩效考核", "管理系统"]
  },
  "chapters": [
    {
      "chapterNo": 1,
      "title": "第1章 绪论",
      "blocks": [
        {
          "type": "heading",
          "level": 1,
          "text": "第1章 绪论"
        },
        {
          "type": "paragraph",
          "text": "随着企业数字化管理水平不断提升……"
        }
      ]
    }
  ],
  "figures": [],
  "tables": [],
  "references": []
}
```

所有写作、图表、引用、DOCX 排版都必须围绕这个 JSON 进行。

---

## 九、DOCX 精排引擎设计

DOCX 精排引擎是本项目核心模块之一。

必须支持：

- 页面设置；
- 页边距；
- 分节符；
- 页眉页脚；
- 页码；
- 标题样式；
- 多级标题编号；
- 正文字体；
- 中英文字体；
- 段落缩进；
- 行距；
- 段前段后；
- 三线表；
- 图题；
- 表题；
- 图片插入；
- SVG/PNG 插入；
- 目录占位；
- 参考文献格式；
- 老师批注读取；
- 局部替换内容；
- 尽量保护原 DOCX 格式。

推荐模块：

```text
DocxEngine
├── StyleManager
├── SectionManager
├── HeaderFooterManager
├── ParagraphManager
├── HeadingManager
├── TableManager
├── FigureManager
├── CitationManager
├── CommentManager
├── TocManager
├── Validator
└── Exporter
```

要求：

1. 常规格式使用 python-docx；
2. python-docx 无法处理的高级格式，使用 lxml 操作 OOXML；
3. 不允许为了修改一段内容而重建整篇论文；
4. 必须优先支持“只替换文字，不破坏格式”；
5. 输出 DOCX 后必须生成格式审查报告。

---

## 十、模板分析能力

系统必须能够识别三种模板：

### 1. 纯说明型模板

例如：

```text
正文宋体小四；
行距1.25倍；
一级标题黑体三号；
表格采用三线表；
图题在图下方；
表题在表上方。
```

系统需要从说明文字中提取规则。

### 2. 成品论文型模板

系统需要从已有 DOCX 样例中提取：

- 页面尺寸；
- 页边距；
- 正文样式；
- 标题样式；
- 页眉页脚；
- 页码；
- 图表题格式；
- 表格格式；
- 参考文献格式。

### 3. 混合型模板

既有说明文档，又有成品论文。

规则冲突时：

```text
说明文档优先；
成品论文作为实际样式参考；
冲突项必须生成冲突报告；
等待用户确认或按默认优先级处理。
```

---

## 十一、图表生成规则

本系统面向论文图表，默认规则如下：

1. 图必须白底黑字；
2. 线条必须黑色；
3. 不允许线条交叉；
4. 不允许节点重叠；
5. 不允许花哨颜色；
6. 中文标签优先；
7. 流程图必须包含必要判断节点；
8. ER 图必须标明实体关系；
9. 架构图必须分层清晰；
10. 表格默认采用三线表；
11. 图题在图下方；
12. 表题在表上方。

支持图表类型：

- 系统架构图；
- 功能结构图；
- 用例图；
- 流程图；
- 泳道图；
- ER 图；
- 数据库关系图；
- 硬件连接图；
- 模块引脚图；
- 测试流程图；
- 三线表；
- 数据库字段说明表；
- 测试用例表。

---

## 十二、老师批注返修能力

系统必须支持读取老师批注并生成返工任务。

批注类型包括：

- 格式类；
- 内容类；
- 结构类；
- 图表类；
- 引用类；
- 表达类；
- 逻辑类。

示例数据：

```json
{
  "commentId": "cmt_001",
  "targetText": "本系统具有较强实用价值",
  "chapter": "第1章 绪论",
  "type": "content_logic",
  "teacherRequest": "这里需要结合项目背景说明，不要空泛",
  "revisionTask": "重写该段，补充项目实际背景"
}
```

返工时必须支持：

```text
格式类问题可自动处理；
内容类问题可让用户逐条确认；
图表类问题可重新生成图；
引用类问题可重新排序参考文献；
不明确批注必须主动问用户。
```

---

## 十三、记忆功能与纠错能力

本项目必须内置 MemoryGuard 论文记忆纠错系统。

目标：

```text
犯过的错不能重复犯。
```

不能只靠 AI 记住，必须通过工程机制实现：

```text
记忆库 + 错误库 + 规则库 + 自动审查 + 回归测试 + 最终导出闸门
```

### 记忆类型

系统至少保存以下记忆：

1. 用户偏好记忆；
2. 项目记忆；
3. 老师批注意见记忆；
4. 错误模式记忆；
5. 成功案例记忆；
6. 审查结果记忆；
7. DOCX 格式规则记忆。

### 错误转规则机制

例如用户指出：

```text
这个流程图线条交叉了，以后不能再犯。
```

系统必须转成规则：

```json
{
  "ruleId": "RULE_FIGURE_NO_CROSS_LINE",
  "trigger": ["流程图", "架构图", "ER图"],
  "rule": "连接线不得交叉，节点不得重叠，必须使用分层布局",
  "severity": "A",
  "blockFinalOutput": true
}
```

### 最终导出闸门

导出最终 DOCX 前必须检查：

```json
{
  "formatCheck": "passed",
  "contentCheck": "passed",
  "citationCheck": "passed",
  "figureCheck": "passed",
  "teacherCommentCheck": "passed",
  "historicalErrorCheck": "passed",
  "allowExport": true
}
```

如果历史错误再次出现，禁止导出最终版。

---

## 十四、默认内置错误规则

系统初始必须内置以下错误规则：

1. 禁止破坏原 DOCX 格式；
2. 禁止修改用户未授权章节；
3. 禁止图表线条交叉；
4. 禁止流程图缺少必要判断节点；
5. 禁止表格不是三线表；
6. 禁止参考文献编号错乱；
7. 禁止一处引用多个文献；
8. 禁止论文题目、技术栈、硬件型号前后不一致；
9. 禁止摘要写成一整段无结构内容；
10. 禁止结论写成各章小结；
11. 禁止测试章节写成操作流水账；
12. 禁止数据库表字段说明过长；
13. 禁止需求分析写成系统实现；
14. 禁止相关技术写成百科介绍；
15. 禁止正文中出现明显口语化表达；
16. 禁止生成与项目不符的功能模块；
17. 禁止忽略老师批注；
18. 禁止最终导出前不做审查。

---

## 十五、数据库设计建议

初期可以使用 SQLite，后续迁移 MySQL。

建议核心表：

```text
thesis_project
thesis_file
thesis_version
thesis_outline
thesis_chapter
thesis_block
thesis_figure
thesis_table
thesis_reference
thesis_comment
thesis_revision_task
thesis_review_report
user_preference_memory
project_memory
error_memory
teacher_feedback_memory
success_case_memory
rule_memory
```

---

## 十六、任务状态设计

项目状态：

```text
created
uploaded
parsed
planned
writing
formatting
reviewing
revision
completed
failed
paused
```

步骤状态：

```text
pending
running
waiting_user
completed
failed
skipped
```

系统必须清楚展示当前卡在哪一步。

---

## 十七、后端接口规划

基础接口：

```text
POST /api/projects
GET  /api/projects
GET  /api/projects/{project_id}

POST /api/files/upload
POST /api/files/analyze

POST /api/templates/analyze
POST /api/outlines/generate
POST /api/chapters/generate
POST /api/chapters/rewrite

POST /api/figures/plan
POST /api/tables/generate
POST /api/references/plan

POST /api/docx/generate
POST /api/docx/format-check

POST /api/comments/analyze
POST /api/revisions/run

POST /api/reviews/run
GET  /api/reviews/{project_id}

POST /api/chat

GET  /api/memory
POST /api/memory
GET  /api/errors
POST /api/errors

POST /api/export/docx
POST /api/export/pdf
```

---

## 十八、开发要求

开发时必须遵守：

1. 先做可运行 MVP；
2. 不要只写空壳页面；
3. 每个页面必须有模拟数据和基础交互；
4. 后端接口必须有清晰的数据模型；
5. DOCX 引擎必须有最小可用示例；
6. 记忆库和错误库必须可增删查；
7. 对话区必须能把用户输入解析成任务意图；
8. 所有核心数据结构必须使用 JSON Schema 或 Pydantic Model；
9. 代码必须模块化；
10. 每个模块必须有注释；
11. 不允许把所有逻辑写在一个文件里；
12. 不允许省略 README 中定义的核心模块；
13. 不允许为了演示而跳过记忆纠错能力；
14. 不允许忽视 DOCX 格式保护能力。

---

## 十九、MVP 开发目标

第一阶段 MVP 先实现：

1. 前端论文项目列表；
2. 新建论文任务；
3. 文件上传页面；
4. 流程化工作台；
5. 右侧对话区；
6. 模板分析模拟结果；
7. 大纲生成模拟结果；
8. 分章写作模拟结果；
9. 记忆库页面；
10. 错误库页面；
11. 后端 FastAPI 基础接口；
12. SQLite 数据库；
13. 最小 DOCX 生成示例；
14. 简单错误规则检查；
15. 最终审查报告模拟。

MVP 的目标不是一次实现全部 AI，而是先把系统骨架、流程、数据结构、页面和 DOCX 引擎跑通。

---

## 二十、后续版本规划

### v1.0

完成基础工作台、项目管理、流程状态、模拟 Agent、最小 DOCX 生成。

### v1.1

接入真实 DOCX 解析、模板样式提取、论文结构化 JSON。

### v1.2

接入真实 LLM Agent，完成分章写作、润色、图表规划。

### v1.3

实现老师批注读取、返工任务生成、局部内容替换。

### v1.4

实现 MemoryGuard，完善错误库、规则库、成功案例库。

### v2.0

实现完整论文生成、审查、返工、导出闭环。

---

## 二十一、最终目标

最终系统应当做到：

```text
用户上传资料后，系统自动完成论文生成、格式排版、批注返修、审查导出；
用户可以随时对话补充要求；
系统可以记住历史错误；
系统可以自动避免重复犯错；
系统可以像论文助理团队一样持续改进。
```

一句话总结：

```text
Thesis Agent 是一个以 DOCX 精排引擎为核心，以多 Agent 审查返工为闭环，以记忆纠错为保障的论文生产工作台。
```
