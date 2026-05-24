import json
import re

def parse_llm_response(text: str) -> tuple[str, dict]:
    m = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", text)
    if m:
        try:
            return text.replace(m.group(0), "").strip(), json.loads(m.group(1))
        except Exception:
            pass
    return text.strip(), {
        "intent": "general_chat",
        "scope": "unknown",
        "target": "",
        "protect_format": False,
        "requirement": "",
        "should_create_task": False,
        "should_write_memory": False,
        "need_user_confirm": False,
    }
