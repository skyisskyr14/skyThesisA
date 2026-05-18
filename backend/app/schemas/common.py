from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models.enums import MemoryType, ProjectStatus, StepStatus


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(BaseModel):
    title: str
    author: str = "学生姓名"
    major: str = "软件工程"
    school: str = "学校名称"


class ProjectRead(ORMModel):
    id: int
    title: str
    author: str
    major: str
    school: str
    status: ProjectStatus
    current_step: str
    step_statuses: dict[str, Any]
    applied_template_rules: dict[str, Any]
    created_at: datetime
    updated_at: datetime


class FileRead(ORMModel):
    id: int
    project_id: int
    filename: str
    file_type: str
    purpose: str
    path: str
    status: StepStatus


class ChatRequest(BaseModel):
    project_id: int | None = None
    message: str


class ChatIntent(BaseModel):
    message: str
    intent: str
    scope: str | None = None
    target: str | None = None
    requirement: str
    protect_others: bool = False
    protect_format: bool = False
    should_create_rule: bool = False
    memory_action: str | None = None
    parsed_task: dict[str, Any]
    agent_reply: str


class MemoryCreate(BaseModel):
    project_id: int | None = None
    memory_type: MemoryType = MemoryType.user_preference
    content: str
    source: str = "manual"


class MemoryRead(ORMModel):
    id: int
    project_id: int | None
    memory_type: MemoryType
    content: str
    source: str
    created_at: datetime


class ErrorCreate(BaseModel):
    project_id: int | None = None
    error_type: str = "format"
    description: str
    fix_strategy: str = "转为规则并在最终审查中拦截"
    severity: str = "B"


class ErrorRead(ORMModel):
    id: int
    project_id: int | None
    error_type: str
    description: str
    fix_strategy: str
    severity: str
    created_at: datetime


class RuleCreate(BaseModel):
    project_id: int | None = None
    rule_code: str
    rule_name: str
    rule_type: str = "general"
    severity: str = "A"
    trigger_keywords: list[str]
    correction_strategy: str
    block_final_output: bool = True


class RuleRead(ORMModel):
    id: int
    project_id: int | None
    rule_code: str
    rule_name: str
    rule_type: str
    severity: str
    trigger_keywords: list[str]
    correction_strategy: str
    block_final_output: bool
    created_at: datetime


class ReviewRequest(BaseModel):
    project_id: int
    content: str = ""


class ReviewRead(ORMModel):
    id: int
    project_id: int
    summary: str
    checks: dict[str, Any]
    allow_export: bool
    blocked_reasons: list[str]
    created_at: datetime


class ReviewResult(BaseModel):
    report_id: int
    project_id: int
    passed: bool
    allow_export: bool
    score: int
    blocked_reasons: list[str]
    warnings: list[str]
    matched_rules: list[dict[str, Any]]
    auto_fix_suggestions: list[str]
    checks: dict[str, Any]


class MockResult(BaseModel):
    project_id: int
    status: StepStatus
    result: dict[str, Any]


class DocxResponse(BaseModel):
    project_id: int
    filename: str
    path: str
    download_url: str


class AnalyzeDocxTemplateRequest(BaseModel):
    project_id: int
    file_id: int | None = None
    file_path: str | None = None


class ApplyTemplateRulesRequest(BaseModel):
    project_id: int
    analysis_id: int


class TemplateAnalysisRead(ORMModel):
    id: int
    project_id: int
    file_id: int | None
    template_type: str
    confidence: float
    rules_json: dict[str, Any]
    conflicts_json: list[Any]
    warnings_json: list[Any]
    source_evidence_json: list[Any]
    applied: bool
    created_at: datetime


class ApplyTemplateRulesResponse(BaseModel):
    project_id: int
    analysis_id: int
    applied: bool
    message: str


class GenerateFullDocxRequest(BaseModel):
    project_id: int
    use_template_rules: bool = True
    use_mock_content: bool = True


class GenerateFullDocxResponse(BaseModel):
    project_id: int
    docx_path: str
    download_url: str
    used_template_rules: bool
    applied_rules_summary: list[str]
    missing_rules: list[str]
    format_validation: dict[str, Any]
