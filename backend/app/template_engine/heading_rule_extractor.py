from __future__ import annotations

import re

from docx.document import Document as DocxDocument

from app.template_engine.utils import alignment_name, get_font_name, pt_value


def extract_heading_rules(document: DocxDocument) -> tuple[list[dict], list[dict]]:
    headings: list[dict] = []
    evidence: list[dict] = []
    seen: set[int] = set()
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        style_name = paragraph.style.name if paragraph.style else ""
        level = _detect_level(text, style_name)
        if not level or level in seen:
            continue
        seen.add(level)
        run = next((r for r in paragraph.runs if r.text.strip()), None)
        font = run.font if run else paragraph.style.font
        fmt = paragraph.paragraph_format
        rule = {
            "level": level,
            "style_name": style_name,
            "font_name": get_font_name(run) if run else get_font_name(paragraph.style) or "黑体",
            "font_size_pt": pt_value(font.size) or (16 if level == 1 else 15 if level == 2 else 14),
            "bold": bool(font.bold) if font.bold is not None else False,
            "alignment": alignment_name(fmt.alignment) or ("center" if level == 1 else "left"),
            "numbering_pattern": _numbering_pattern(text, level),
            "space_before_pt": pt_value(fmt.space_before) or 0,
            "space_after_pt": pt_value(fmt.space_after) or 0,
        }
        headings.append(rule)
        evidence.append({"field": f"headings[{level}]", "source": f"段落样式 {style_name}", "text": text[:80]})
    if not headings:
        headings.append(_default_heading())
        evidence.append({"field": "headings", "source": "fallback", "text": "未检测到标题，使用默认一级标题规则"})
    return sorted(headings, key=lambda item: item["level"]), evidence


def _detect_level(text: str, style_name: str) -> int | None:
    lower = style_name.lower()
    match = re.search(r"heading\s*(\d)", lower)
    if match:
        return int(match.group(1))
    if re.match(r"第[一二三四五六七八九十\d]+章", text):
        return 1
    if re.match(r"\d+\.\d+\s*", text):
        return 2
    if re.match(r"\d+\.\d+\.\d+\s*", text):
        return 3
    return None


def _numbering_pattern(text: str, level: int) -> str:
    if re.match(r"第[一二三四五六七八九十\d]+章", text):
        return "第{n}章"
    if level == 2:
        return "{chapter}.{n}"
    if level == 3:
        return "{chapter}.{section}.{n}"
    return ""


def _default_heading() -> dict:
    return {
        "level": 1,
        "style_name": "Heading 1",
        "font_name": "黑体",
        "font_size_pt": 16,
        "bold": False,
        "alignment": "center",
        "numbering_pattern": "第{n}章",
        "space_before_pt": 12,
        "space_after_pt": 12,
    }
