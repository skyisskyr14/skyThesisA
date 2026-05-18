from sqlalchemy.orm import Session

from app.memory_guard.default_rules import DEFAULT_RULES
from app.models.entities import ErrorMemory, ReviewReport, RuleMemory, UserMemory


def seed_default_rules(db: Session) -> None:
    if db.query(RuleMemory).filter(RuleMemory.project_id.is_(None)).count() > 0:
        return
    for rule in DEFAULT_RULES:
        db.add(RuleMemory(**rule))
    db.commit()


def add_error_as_rule(db: Session, error: ErrorMemory) -> RuleMemory:
    rule = RuleMemory(
        project_id=error.project_id,
        rule_code=f"RULE_FROM_ERROR_{error.id}",
        rule_name=f"历史错误不得重复：{error.error_type}",
        rule_type="historical_error",
        trigger_keywords=[error.error_type, error.description[:30]],
        correction_strategy=f"避免重复出现：{error.description}；修正策略：{error.fix_strategy}",
        severity=error.severity,
        block_final_output=error.severity in {"A", "B"},
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def create_rule_from_chat(db: Session, project_id: int | None, requirement: str, rule_type: str = "chat_rule") -> RuleMemory:
    rule = RuleMemory(
        project_id=project_id,
        rule_code="RULE_USER_CHAT_REQUIREMENT",
        rule_name="用户对话长期规则",
        rule_type=rule_type,
        severity="A",
        trigger_keywords=_extract_keywords(requirement),
        correction_strategy=requirement,
        block_final_output=True,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def run_final_review(db: Session, project_id: int, content: str) -> dict:
    """MemoryGuard 最终审查：返回导出闸门需要的完整结构。"""

    rules = db.query(RuleMemory).filter((RuleMemory.project_id.is_(None)) | (RuleMemory.project_id == project_id)).all()
    errors = db.query(ErrorMemory).filter((ErrorMemory.project_id.is_(None)) | (ErrorMemory.project_id == project_id)).all()
    memories = db.query(UserMemory).filter((UserMemory.project_id.is_(None)) | (UserMemory.project_id == project_id)).all()

    blocked_reasons: list[str] = []
    warnings: list[str] = []
    matched_rules: list[dict] = []
    auto_fix_suggestions: list[str] = []

    for rule in rules:
        matched_keywords = [keyword for keyword in rule.trigger_keywords if keyword and keyword in content]
        if not matched_keywords:
            continue
        rule_payload = {
            "rule_code": rule.rule_code,
            "rule_name": rule.rule_name,
            "rule_type": rule.rule_type,
            "severity": rule.severity,
            "matched_keywords": matched_keywords,
            "block_final_output": rule.block_final_output,
        }
        matched_rules.append(rule_payload)
        auto_fix_suggestions.append(rule.correction_strategy)
        reason = f"{rule.rule_code}: {rule.rule_name}（命中：{', '.join(matched_keywords)}）"
        if rule.block_final_output and rule.severity in {"A", "B"}:
            blocked_reasons.append(reason)
        else:
            warnings.append(reason)

    for error in errors:
        if error.description and error.description in content:
            blocked_reasons.append(f"历史错误重复出现：{error.description}")
            auto_fix_suggestions.append(error.fix_strategy)
            matched_rules.append(
                {
                    "rule_code": f"ERROR_MEMORY_{error.id}",
                    "rule_name": "历史错误记忆",
                    "rule_type": error.error_type,
                    "severity": error.severity,
                    "matched_keywords": [error.description],
                    "block_final_output": error.severity in {"A", "B"},
                }
            )

    passed = len(blocked_reasons) == 0
    score = max(0, 100 - len(blocked_reasons) * 18 - len(warnings) * 5)
    checks = {
        "formatCheck": "passed" if passed else "blocked",
        "contentCheck": "passed" if passed else "blocked",
        "citationCheck": "passed" if not any(rule["rule_type"] == "citation" for rule in matched_rules) else "blocked",
        "figureCheck": "passed" if not any(rule["rule_type"] == "figure" for rule in matched_rules) else "blocked",
        "teacherCommentCheck": "passed" if not any(rule["rule_type"] == "teacher_comment" for rule in matched_rules) else "blocked",
        "historicalErrorCheck": "passed" if not blocked_reasons else "blocked",
        "memoryCount": len(memories),
    }
    report = ReviewReport(
        project_id=project_id,
        summary="最终审查通过，可导出。" if passed else "最终审查未通过，已触发 MemoryGuard 导出闸门。",
        checks={
            **checks,
            "passed": passed,
            "score": score,
            "warnings": warnings,
            "matched_rules": matched_rules,
            "auto_fix_suggestions": auto_fix_suggestions,
        },
        allow_export=passed,
        blocked_reasons=blocked_reasons,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return {
        "report_id": report.id,
        "project_id": project_id,
        "passed": passed,
        "allow_export": passed,
        "score": score,
        "blocked_reasons": blocked_reasons,
        "warnings": warnings,
        "matched_rules": matched_rules,
        "auto_fix_suggestions": auto_fix_suggestions,
        "checks": checks,
    }


def _extract_keywords(requirement: str) -> list[str]:
    candidates = [
        "线条交叉",
        "判断节点",
        "三线表",
        "流水账",
        "格式",
        "老师批注",
        "引用",
        "白底黑字",
    ]
    hits = [keyword for keyword in candidates if keyword in requirement]
    return hits or [requirement[:30]]
