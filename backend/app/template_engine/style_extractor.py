from __future__ import annotations

from typing import Any

from docx.document import Document as DocxDocument

from app.template_engine.utils import alignment_name, get_font_name, pt_value


def extract_style_summary(document: DocxDocument) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for style in document.styles:
        if not getattr(style, "name", None):
            continue
        font = getattr(style, "font", None)
        paragraph_format = getattr(style, "paragraph_format", None)
        summary[style.name] = {
            "font_name": get_font_name(style),
            "font_size_pt": pt_value(font.size) if font else None,
            "bold": font.bold if font else None,
            "alignment": alignment_name(paragraph_format.alignment) if paragraph_format else None,
        }
    return summary
