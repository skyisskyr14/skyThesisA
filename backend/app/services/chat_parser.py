import re


def parse_chat_message(message: str) -> dict:
    """将右侧对话区自然语言解析为结构化任务意图，后续可替换为 Intent Agent。"""

    intent = "supplement_requirement"
    scope = "current_step"
    target = _detect_target(message)
    protect_others = "其他不要动" in message or "不要动其他" in message
    protect_format = any(keyword in message for keyword in ["不动格式", "格式保护", "只改内容", "保持原来的字体", "保持原来的段落"])
    should_create_rule = False
    memory_action = None
    requirement = message.strip()

    chapter_match = re.search(r"第\s*(\d+)\s*章", message)
    if chapter_match:
        scope = f"chapter_{chapter_match.group(1)}"
        target = target or "chapter"

    if "只改" in message or "局部" in message or protect_others:
        intent = "partial_edit"
        protect_format = True
    if protect_format:
        intent = "format_protection" if intent == "supplement_requirement" else intent
    if any(keyword in message for keyword in ["长期规则", "加入规则", "以后所有", "以后都"]):
        intent = "add_long_term_rule"
        should_create_rule = True
        memory_action = "create_rule_memory"
        scope = "global"
    if any(keyword in message for keyword in ["以后不能犯", "以后不能再犯", "不能再出现", "记住"]):
        intent = "remember_error"
        should_create_rule = True
        memory_action = "create_error_memory"
        scope = "global" if scope == "current_step" else scope
    if chapter_match and any(keyword in message for keyword in ["重新写", "重写", "不要写成流水账"]):
        intent = "rewrite_chapter"
        target = "chapter"
    if any(keyword in message for keyword in ["流程图", "图", "白底黑字", "线不要交叉", "线条交叉", "字号小四"]):
        if intent == "supplement_requirement":
            intent = "figure_requirement"
        target = "figure"

    return {
        "message": message,
        "intent": intent,
        "scope": scope,
        "target": target,
        "requirement": requirement,
        "protect_others": protect_others,
        "protect_format": protect_format,
        "should_create_rule": should_create_rule,
        "memory_action": memory_action,
        "parsed_task": {
            "intent": intent,
            "scope": scope,
            "target": target,
            "requirement": requirement,
            "protectOthers": protect_others,
            "protectFormat": protect_format,
            "shouldCreateRule": should_create_rule,
        },
        "agent_reply": _reply(intent, should_create_rule),
    }


def _detect_target(message: str) -> str | None:
    if "表" in message or "三线表" in message:
        return "table"
    if "图" in message or "流程图" in message or "架构图" in message:
        return "figure"
    if "参考文献" in message or "引用" in message:
        return "citation"
    if "批注" in message or "老师" in message:
        return "teacher_comment"
    return None


def _reply(intent: str, should_create_rule: bool) -> str:
    suffix = "已写入记忆库/错误库并同步生成导出审查规则。" if should_create_rule else "已记录为当前论文任务补充要求。"
    return f"已解析意图：{intent}。{suffix}"
