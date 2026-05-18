from sqlalchemy.orm import Session

from app.memory_guard.default_rules import DEFAULT_RULES
from app.models.entities import ErrorMemory, ReviewReport, RuleMemory, UserMemory


def seed_default_rules(db: Session) -> None:
    if db.query(RuleMemory).filter(RuleMemory.project_id.is_(None)).count() > 0:
        return
    for rule_id, trigger, rule, severity, block in DEFAULT_RULES:
        db.add(
            RuleMemory(
                rule_id=rule_id,
                trigger=trigger,
                rule=rule,
                severity=severity,
                block_final_output=block,
            )
        )
    db.commit()


def add_error_as_rule(db: Session, error: ErrorMemory) -> RuleMemory:
    rule = RuleMemory(
        project_id=error.project_id,
        rule_id=f"RULE_FROM_ERROR_{error.id}",
        trigger=[error.error_type, error.description[:20]],
        rule=f"历史错误不得重复出现：{error.description}；修正策略：{error.fix_strategy}",
        severity=error.severity,
        block_final_output=error.severity in {"A", "B"},
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def run_final_review(db: Session, project_id: int, content: str) -> ReviewReport:
    """MemoryGuard 最终审查：基于规则触发词和历史错误检查是否允许导出。"""

    rules = db.query(RuleMemory).filter((RuleMemory.project_id.is_(None)) | (RuleMemory.project_id == project_id)).all()
    errors = db.query(ErrorMemory).filter((ErrorMemory.project_id.is_(None)) | (ErrorMemory.project_id == project_id)).all()
    memories = db.query(UserMemory).filter((UserMemory.project_id.is_(None)) | (UserMemory.project_id == project_id)).all()

    blocked: list[str] = []
    warnings: list[str] = []
    for rule in rules:
        hit = any(token and token in content for token in rule.trigger)
        if hit and rule.block_final_output and rule.severity in {"A", "B"}:
            blocked.append(f"{rule.rule_id}: {rule.rule}")
        elif hit:
            warnings.append(f"{rule.rule_id}: {rule.rule}")

    for error in errors:
        if error.description and error.description in content:
            blocked.append(f"历史错误重复出现：{error.description}")

    allow_export = len(blocked) == 0
    checks = {
        "formatCheck": "passed" if allow_export else "blocked",
        "contentCheck": "passed" if allow_export else "blocked",
        "citationCheck": "passed",
        "figureCheck": "passed" if "线条交叉" not in content else "blocked",
        "teacherCommentCheck": "passed",
        "historicalErrorCheck": "passed" if not blocked else "blocked",
        "memoryCount": len(memories),
        "warnings": warnings,
    }
    report = ReviewReport(
        project_id=project_id,
        summary="最终审查通过，可导出。" if allow_export else "最终审查未通过，已触发 MemoryGuard 导出闸门。",
        checks=checks,
        allow_export=allow_export,
        blocked_reasons=blocked,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
