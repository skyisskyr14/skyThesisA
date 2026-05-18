from enum import Enum


class ProjectStatus(str, Enum):
    """论文项目生命周期状态机，后续可由真实工作流引擎驱动。"""

    created = "created"
    uploaded = "uploaded"
    parsed = "parsed"
    planned = "planned"
    writing = "writing"
    formatting = "formatting"
    reviewing = "reviewing"
    revision = "revision"
    completed = "completed"
    failed = "failed"
    paused = "paused"


class StepStatus(str, Enum):
    """流程步骤状态，前端工作台用于展示每一步卡点。"""

    pending = "pending"
    running = "running"
    waiting_user = "waiting_user"
    completed = "completed"
    failed = "failed"
    skipped = "skipped"


class MemoryType(str, Enum):
    user_preference = "user_preference"
    project_memory = "project_memory"
    teacher_feedback = "teacher_feedback"
    error_pattern = "error_pattern"
    success_case = "success_case"
    review_result = "review_result"
    docx_format_rule = "docx_format_rule"
