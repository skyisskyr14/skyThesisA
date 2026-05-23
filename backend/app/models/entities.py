from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import MemoryType, ProjectStatus, StepStatus


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ThesisProject(TimestampMixin, Base):
    __tablename__ = "thesis_project"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    author: Mapped[str] = mapped_column(String(100), default="学生姓名")
    major: Mapped[str] = mapped_column(String(100), default="软件工程")
    school: Mapped[str] = mapped_column(String(200), default="学校名称")
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), default=ProjectStatus.created)
    current_step: Mapped[str] = mapped_column(String(60), default="upload")
    step_statuses: Mapped[dict] = mapped_column(JSON, default=dict)
    applied_template_rules: Mapped[dict] = mapped_column(JSON, default=dict)

    files: Mapped[list["PaperFile"]] = relationship(back_populates="project")
    versions: Mapped[list["ThesisVersion"]] = relationship(back_populates="project")
    chapters: Mapped[list["PaperChapter"]] = relationship(back_populates="project")
    memories: Mapped[list["UserMemory"]] = relationship(back_populates="project")
    errors: Mapped[list["ErrorMemory"]] = relationship(back_populates="project")
    rules: Mapped[list["RuleMemory"]] = relationship(back_populates="project")
    reports: Mapped[list["ReviewReport"]] = relationship(back_populates="project")
    template_results: Mapped[list["TemplateAnalysisResult"]] = relationship(back_populates="project")


class TemplateAnalysisResult(TimestampMixin, Base):
    __tablename__ = "template_analysis_result"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("thesis_project.id"))
    file_id: Mapped[int | None] = mapped_column(ForeignKey("thesis_file.id"), nullable=True)
    template_type: Mapped[str] = mapped_column(String(60), default="unknown")
    confidence: Mapped[float] = mapped_column(default=0.0)
    rules_json: Mapped[dict] = mapped_column(JSON, default=dict)
    conflicts_json: Mapped[list] = mapped_column(JSON, default=list)
    warnings_json: Mapped[list] = mapped_column(JSON, default=list)
    source_evidence_json: Mapped[list] = mapped_column(JSON, default=list)
    applied: Mapped[bool] = mapped_column(Boolean, default=False)

    project: Mapped[ThesisProject] = relationship(back_populates="template_results")

class PaperFile(TimestampMixin, Base):
    __tablename__ = "thesis_file"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("thesis_project.id"))
    filename: Mapped[str] = mapped_column(String(255))
    file_type: Mapped[str] = mapped_column(String(60), default="unknown")
    purpose: Mapped[str] = mapped_column(String(120), default="待识别")
    path: Mapped[str] = mapped_column(String(500), default="")
    status: Mapped[StepStatus] = mapped_column(Enum(StepStatus), default=StepStatus.completed)

    project: Mapped[ThesisProject] = relationship(back_populates="files")


class ThesisVersion(TimestampMixin, Base):
    __tablename__ = "thesis_version"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("thesis_project.id"))
    version_no: Mapped[str] = mapped_column(String(40), default="v0.1")
    summary: Mapped[str] = mapped_column(Text, default="MVP 初始版本")
    structured_json: Mapped[dict] = mapped_column(JSON, default=dict)

    project: Mapped[ThesisProject] = relationship(back_populates="versions")


class Outline(TimestampMixin, Base):
    __tablename__ = "thesis_outline"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("thesis_project.id"))
    title: Mapped[str] = mapped_column(String(200))
    items: Mapped[list] = mapped_column(JSON, default=list)


class PaperChapter(TimestampMixin, Base):
    __tablename__ = "thesis_chapter"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("thesis_project.id"))
    chapter_no: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text, default="")
    blocks: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[StepStatus] = mapped_column(Enum(StepStatus), default=StepStatus.pending)

    project: Mapped[ThesisProject] = relationship(back_populates="chapters")


class Figure(TimestampMixin, Base):
    __tablename__ = "thesis_figure"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("thesis_project.id"))
    title: Mapped[str] = mapped_column(String(200))
    figure_type: Mapped[str] = mapped_column(String(80), default="流程图")
    spec: Mapped[dict] = mapped_column(JSON, default=dict)


class ThesisTable(TimestampMixin, Base):
    __tablename__ = "thesis_table"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("thesis_project.id"))
    title: Mapped[str] = mapped_column(String(200))
    columns: Mapped[list] = mapped_column(JSON, default=list)
    rows: Mapped[list] = mapped_column(JSON, default=list)
    is_three_line: Mapped[bool] = mapped_column(Boolean, default=True)


class Reference(TimestampMixin, Base):
    __tablename__ = "thesis_reference"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("thesis_project.id"))
    citation_no: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)


class TeacherComment(TimestampMixin, Base):
    __tablename__ = "thesis_comment"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("thesis_project.id"))
    target_text: Mapped[str] = mapped_column(Text)
    chapter: Mapped[str] = mapped_column(String(120), default="未定位")
    comment_type: Mapped[str] = mapped_column(String(80), default="content_logic")
    teacher_request: Mapped[str] = mapped_column(Text)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)


class RevisionTask(TimestampMixin, Base):
    __tablename__ = "thesis_revision_task"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("thesis_project.id"))
    comment_id: Mapped[int | None] = mapped_column(ForeignKey("thesis_comment.id"), nullable=True)
    task: Mapped[str] = mapped_column(Text)
    status: Mapped[StepStatus] = mapped_column(Enum(StepStatus), default=StepStatus.pending)


class ReviewReport(TimestampMixin, Base):
    __tablename__ = "thesis_review_report"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("thesis_project.id"))
    summary: Mapped[str] = mapped_column(Text)
    checks: Mapped[dict] = mapped_column(JSON, default=dict)
    allow_export: Mapped[bool] = mapped_column(Boolean, default=False)
    blocked_reasons: Mapped[list] = mapped_column(JSON, default=list)

    project: Mapped[ThesisProject] = relationship(back_populates="reports")


class UserMemory(TimestampMixin, Base):
    __tablename__ = "user_preference_memory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("thesis_project.id"), nullable=True)
    memory_type: Mapped[MemoryType] = mapped_column(Enum(MemoryType), default=MemoryType.user_preference)
    content: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(120), default="manual")

    project: Mapped[ThesisProject | None] = relationship(back_populates="memories")


class ErrorMemory(TimestampMixin, Base):
    __tablename__ = "error_memory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("thesis_project.id"), nullable=True)
    error_type: Mapped[str] = mapped_column(String(120), default="format")
    description: Mapped[str] = mapped_column(Text)
    fix_strategy: Mapped[str] = mapped_column(Text, default="转为规则并在最终审查中拦截")
    severity: Mapped[str] = mapped_column(String(10), default="B")

    project: Mapped[ThesisProject | None] = relationship(back_populates="errors")


class RuleMemory(TimestampMixin, Base):
    __tablename__ = "rule_memory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("thesis_project.id"), nullable=True)
    rule_code: Mapped[str] = mapped_column(String(120), index=True)
    rule_name: Mapped[str] = mapped_column(String(200))
    rule_type: Mapped[str] = mapped_column(String(80), default="general")
    severity: Mapped[str] = mapped_column(String(10), default="A")
    trigger_keywords: Mapped[list] = mapped_column(JSON, default=list)
    correction_strategy: Mapped[str] = mapped_column(Text)
    block_final_output: Mapped[bool] = mapped_column(Boolean, default=True)

    project: Mapped[ThesisProject | None] = relationship(back_populates="rules")


class LLMProvider(TimestampMixin, Base):
    __tablename__ = "llm_providers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider_name: Mapped[str] = mapped_column(String(120))
    provider_type: Mapped[str] = mapped_column(String(60))
    base_url: Mapped[str] = mapped_column(String(300))
    api_key_encrypted: Mapped[str] = mapped_column(Text, default="")
    api_key_masked: Mapped[str] = mapped_column(String(80), default="")
    default_model: Mapped[str] = mapped_column(String(120), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class LLMModel(TimestampMixin, Base):
    __tablename__ = "llm_models"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    provider_id: Mapped[int] = mapped_column(ForeignKey("llm_providers.id"))
    model_name: Mapped[str] = mapped_column(String(120))
    display_name: Mapped[str] = mapped_column(String(120), default="")
    context_window: Mapped[int] = mapped_column(Integer, default=8192)
    max_output_tokens: Mapped[int] = mapped_column(Integer, default=2000)
    supports_streaming: Mapped[bool] = mapped_column(Boolean, default=False)
    supports_json_mode: Mapped[bool] = mapped_column(Boolean, default=True)
    supports_vision: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class LLMStepBinding(TimestampMixin, Base):
    __tablename__ = "llm_step_bindings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    step_key: Mapped[str] = mapped_column(String(80), index=True)
    step_name: Mapped[str] = mapped_column(String(120), default="")
    provider_id: Mapped[int] = mapped_column(ForeignKey("llm_providers.id"))
    model_id: Mapped[int] = mapped_column(ForeignKey("llm_models.id"))
    temperature: Mapped[float] = mapped_column(default=0.7)
    max_tokens: Mapped[int] = mapped_column(Integer, default=2000)
    system_prompt: Mapped[str] = mapped_column(Text, default="")
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)


class LLMCallLog(TimestampMixin, Base):
    __tablename__ = "llm_call_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("thesis_project.id"), nullable=True)
    step_key: Mapped[str] = mapped_column(String(80), default="right_chat")
    provider_id: Mapped[int] = mapped_column(ForeignKey("llm_providers.id"))
    model_id: Mapped[int] = mapped_column(ForeignKey("llm_models.id"))
    request_summary: Mapped[str] = mapped_column(Text, default="")
    response_summary: Mapped[str] = mapped_column(Text, default="")
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[str] = mapped_column(Text, default="")


class ChatSession(TimestampMixin, Base):
    __tablename__ = "chat_sessions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("thesis_project.id"))
    title: Mapped[str] = mapped_column(String(200), default="默认会话")
    current_step: Mapped[str] = mapped_column(String(80), default="right_chat")


class ChatMessage(TimestampMixin, Base):
    __tablename__ = "chat_messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id"))
    project_id: Mapped[int] = mapped_column(ForeignKey("thesis_project.id"))
    role: Mapped[str] = mapped_column(String(30))
    content: Mapped[str] = mapped_column(Text)
    step_key: Mapped[str] = mapped_column(String(80), default="right_chat")
    parsed_intent_json: Mapped[dict] = mapped_column(JSON, default=dict)
    action_result_json: Mapped[dict] = mapped_column(JSON, default=dict)
    llm_call_log_id: Mapped[int | None] = mapped_column(ForeignKey("llm_call_logs.id"), nullable=True)
