import re


def parse_chat_message(message: str) -> dict:
    """将右侧对话区自然语言解析为 MVP 任务意图，后续可替换为 Intent Agent。"""

    intent = "supplement_requirement"
    scope = None
    protect_others = False
    protect_format = "不动格式" in message or "格式保护" in message or "只改内容" in message
    memory_action = None

    chapter_match = re.search(r"第\s*(\d+)\s*章", message)
    if chapter_match:
        scope = f"chapter_{chapter_match.group(1)}"

    if "只改" in message or "局部" in message:
        intent = "partial_edit"
        protect_others = "其他不要动" in message or "不要动其他" in message
        protect_format = True
    elif "三线表" in message or "页边距" in message or "格式" in message:
        intent = "format_protection"
        protect_format = True
    elif "以后不能再犯" in message or "记录错误" in message:
        intent = "record_error"
        memory_action = "create_error_memory"
    elif "长期规则" in message or "加入规则" in message or "以后都" in message:
        intent = "add_long_term_rule"
        memory_action = "create_rule_memory"

    return {
        "message": message,
        "intent": intent,
        "scope": scope,
        "protect_others": protect_others,
        "protect_format": protect_format,
        "memory_action": memory_action,
        "parsed_task": {
            "scope": scope or "current_step",
            "protectOthers": protect_others,
            "protectFormat": protect_format,
            "rawMessage": message,
        },
        "agent_reply": "已解析为任务意图，MVP 阶段会记录指令并交给对应模拟 Agent。",
    }
