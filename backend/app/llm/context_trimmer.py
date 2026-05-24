def trim_text(text: str, max_chars: int = 4000) -> str:
    if len(text) <= max_chars:
        return text
    head = text[: int(max_chars * 0.7)]
    tail = text[-int(max_chars * 0.3):]
    return head + "\n...[TRIMMED]...\n" + tail
