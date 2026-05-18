from app.models.enums import ProjectStatus, StepStatus

WORKFLOW_STEPS = [
    "upload",
    "template",
    "outline",
    "writing",
    "figures",
    "formatting",
    "comments",
    "review",
    "export",
]


def initial_step_statuses() -> dict[str, str]:
    return {step: StepStatus.pending.value for step in WORKFLOW_STEPS}


def advance_for_action(action: str) -> tuple[ProjectStatus, str, dict[str, str]]:
    statuses = initial_step_statuses()
    if action == "upload":
        statuses["upload"] = StepStatus.completed.value
        return ProjectStatus.uploaded, "template", statuses
    if action == "template":
        statuses["upload"] = StepStatus.completed.value
        statuses["template"] = StepStatus.completed.value
        return ProjectStatus.parsed, "outline", statuses
    if action == "outline":
        for step in ["upload", "template", "outline"]:
            statuses[step] = StepStatus.completed.value
        return ProjectStatus.planned, "writing", statuses
    if action == "writing":
        for step in ["upload", "template", "outline", "writing"]:
            statuses[step] = StepStatus.completed.value
        return ProjectStatus.writing, "figures", statuses
    return ProjectStatus.created, "upload", statuses
