from __future__ import annotations

from collections import Counter

from docx.document import Document as DocxDocument

from app.template_engine.utils import alignment_name, get_font_name, pt_value


def extract_body_rules(document: DocxDocument) -> tuple[dict, list[dict]]:
    candidates = [p for p in document.paragraphs if p.text.strip() and not p.style.name.lower().startswith("heading")]
    if not candidates:
        return _default_body(), [{"field": "body", "source": "fallback", "text": "未检测到正文段落，使用默认规则"}]
    paragraph = max(candidates, key=lambda p: len(p.text.strip()))
    run = next((r for r in paragraph.runs if r.text.strip()), None)
    style = paragraph.style
    fmt = paragraph.paragraph_format
    font_name = get_font_name(run) if run else None
    style_font = get_font_name(style)
    size = pt_value(run.font.size) if run and run.font.size else pt_value(style.font.size)
    line_spacing = fmt.line_spacing if isinstance(fmt.line_spacing, (int, float)) else None
    first_line_indent_chars = None
    if fmt.first_line_indent is not None:
        try:
            first_line_indent_chars = round(fmt.first_line_indent.pt / 12, 1)
        except Exception:
            first_line_indent_chars = None
    fonts = Counter(filter(None, [font_name, style_font]))
    body = {
        "font_cn": fonts.most_common(1)[0][0] if fonts else "宋体",
        "font_en": "Times New Roman",
        "font_size_pt": size or 12,
        "line_spacing": line_spacing or 1.25,
        "first_line_indent_chars": first_line_indent_chars if first_line_indent_chars is not None else 2,
        "alignment": alignment_name(fmt.alignment) or "justify",
        "space_before_pt": pt_value(fmt.space_before) or 0,
        "space_after_pt": pt_value(fmt.space_after) or 0,
    }
    evidence = [{"field": "body", "source": f"段落样式 {style.name}", "text": paragraph.text[:80]}]
    return body, evidence


def _default_body() -> dict:
    return {
        "font_cn": "宋体",
        "font_en": "Times New Roman",
        "font_size_pt": 12,
        "line_spacing": 1.25,
        "first_line_indent_chars": 2,
        "alignment": "justify",
        "space_before_pt": 0,
        "space_after_pt": 0,
    }
