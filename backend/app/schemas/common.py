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
    protect_others: bool = False
    protect_format: bool = False
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
    rule_id: str
    trigger: list[str]
    rule: str
    severity: str = "A"
    block_final_output: bool = True


class RuleRead(ORMModel):
    id: int
    project_id: int | None
    rule_id: str
    trigger: list[str]
    rule: str
    severity: str
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


class MockResult(BaseModel):
    project_id: int
    status: StepStatus
    result: dict[str, Any]


class DocxResponse(BaseModel):
    project_id: int
    filename: str
    path: str
    download_url: str
