def build_right_chat_prompts(context_text: str, user_message: str, system_prompt_override: str | None = None) -> list[dict]:
    system_prompt = system_prompt_override or (
        "你是 Thesis Agent 的论文工作台助手。围绕当前项目回答；不能假装执行过未执行的操作；区分建议与已执行；"
        "识别修改范围；若用户说不要动格式则protect_format=true；尽量输出 JSON action block。"
    )
    return [
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": f"项目上下文:\n{context_text}"},
        {"role": "user", "content": user_message},
    ]
