from __future__ import annotations

from pydantic import BaseModel, Field


class PaperMeta(BaseModel):
    title: str
    author: str = "学生姓名"
    school: str = "学校名称"
    major: str = "专业名称"
    class_name: str = "软件工程 1 班"
    student_no: str = "2026000000"
    teacher: str = "指导教师"
    date: str = "2026 年 5 月"


class PaperAbstract(BaseModel):
    zh: list[str] = Field(default_factory=list)
    zh_keywords: list[str] = Field(default_factory=list)
    en: list[str] = Field(default_factory=list)
    en_keywords: list[str] = Field(default_factory=list)


class PaperBlock(BaseModel):
    type: str
    text: str | None = None
    title: str | None = None
    columns: list[str] = Field(default_factory=list)
    rows: list[list[str]] = Field(default_factory=list)


class PaperSection(BaseModel):
    level: int = 2
    title: str
    blocks: list[PaperBlock] = Field(default_factory=list)


class PaperChapter(BaseModel):
    chapter_no: int
    title: str
    sections: list[PaperSection] = Field(default_factory=list)


class PaperReference(BaseModel):
    index: int
    text: str


class PaperDocument(BaseModel):
    meta: PaperMeta
    abstract: PaperAbstract
    chapters: list[PaperChapter]
    references: list[PaperReference]


def build_mock_paper(title: str, author: str, school: str, major: str) -> PaperDocument:
    return PaperDocument(
        meta=PaperMeta(title=title, author=author, school=school, major=major),
        abstract=PaperAbstract(
            zh=[
                "本文围绕 Thesis Agent 论文智能体工作台的需求展开，构建覆盖模板解析、论文写作、DOCX 精排、记忆纠错和最终审查的 MVP 流程。",
                "系统通过结构化论文数据驱动 DOCX 生成，并结合模板规则完成页面、标题、正文、图表和参考文献等关键格式的自动应用。",
            ],
            zh_keywords=["Thesis Agent", "DOCX 精排", "模板解析", "MemoryGuard"],
            en=["This paper presents a placeholder English abstract for the Thesis Agent workbench and its DOCX formatting pipeline."],
            en_keywords=["Thesis Agent", "DOCX", "template rules"],
        ),
        chapters=[
            PaperChapter(
                chapter_no=1,
                title="绪论",
                sections=[
                    PaperSection(
                        level=2,
                        title="研究背景与意义",
                        blocks=[
                            PaperBlock(type="paragraph", text="随着高校论文管理和格式审查要求不断提高，论文写作系统需要同时兼顾内容结构、模板规则和最终导出质量。"),
                            PaperBlock(type="figure_placeholder", title="系统总体流程图"),
                        ],
                    ),
                    PaperSection(
                        level=2,
                        title="系统功能需求",
                        blocks=[
                            PaperBlock(type="paragraph", text="本系统需要支持项目创建、模板解析、大纲规划、章节生成、DOCX 精排、记忆纠错和最终审查等核心流程。"),
                            PaperBlock(
                                type="table",
                                title="系统功能需求表",
                                columns=["功能模块", "功能说明"],
                                rows=[
                                    ["模板解析", "读取 DOCX 模板并生成 template_rules"],
                                    ["DOCX 精排", "根据结构化论文数据生成规范文档"],
                                    ["MemoryGuard", "记录历史错误并在导出前拦截"],
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            PaperChapter(
                chapter_no=2,
                title="系统设计",
                sections=[
                    PaperSection(
                        level=2,
                        title="总体架构设计",
                        blocks=[PaperBlock(type="paragraph", text="系统采用前后端分离架构，后端负责模型、规则和文档生成，前端负责流程化工作台交互。")],
                    )
                ],
            ),
        ],
        references=[
            PaperReference(index=1, text="张三. 论文格式自动化处理研究[J]. 软件工程, 2024."),
            PaperReference(index=2, text="李四. 基于 DOCX 的文档排版方法[J]. 计算机应用, 2023."),
            PaperReference(index=3, text="Thesis Agent Team. Template Rules for DOCX Generation[EB/OL]. 2026."),
        ],
    )
