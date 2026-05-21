from app.models.enums import StepStatus


def analyze_template(project_title: str) -> dict:
    """模拟 TemplateAnalyzerAgent，后续替换为 DOCX 样式解析 + LLM 规则抽取。"""

    return {
        "templateType": "mixed",
        "priority": "说明文档优先，成品论文作为样式参考",
        "rules": [
            "正文宋体小四，1.25 倍行距",
            "一级标题黑体三号",
            "图题在图下方，表题在表上方",
            "表格采用三线表",
        ],
        "conflicts": ["页边距说明与样例略有差异，MVP 默认采用说明文档"],
        "projectTitle": project_title,
    }


def generate_outline(project_title: str) -> dict:
    """模拟 PaperStructureAgent，返回可进入结构化 JSON 的论文目录。"""

    chapters = [
        "第1章 绪论",
        "第2章 相关技术",
        "第3章 需求分析",
        "第4章 系统设计",
        "第5章 系统实现与测试",
        "第6章 总结与展望",
    ]
    return {"title": project_title, "chapters": chapters, "status": StepStatus.completed.value}


def generate_chapter(project_title: str, chapter_no: int) -> dict:
    """模拟 ChapterWriterAgent，后续接入真实分章写作、润色和引用 Agent。"""

    title = f"第{chapter_no}章 MVP 示例章节"
    content = (
        f"本章围绕《{project_title}》展开说明。MVP 阶段先生成结构化段落，"
        "后续将接入真实 LLM Agent、资料检索和引用校验模块。"
    )
    return {
        "chapterNo": chapter_no,
        "title": title,
        "blocks": [
            {"type": "heading", "level": 1, "text": title},
            {"type": "paragraph", "text": content},
        ],
    }


def analyze_teacher_comments() -> dict:
    """模拟 TeacherCommentAgent，为后续真实 DOCX 批注读取预留接口。"""

    return {
        "comments": [
            {
                "commentId": "cmt_001",
                "targetText": "本系统具有较强实用价值",
                "chapter": "第1章 绪论",
                "type": "content_logic",
                "teacherRequest": "结合项目背景说明，不要空泛",
                "revisionTask": "重写该段，补充项目实际背景",
            }
        ]
    }
