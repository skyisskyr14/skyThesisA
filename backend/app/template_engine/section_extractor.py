from __future__ import annotations

from docx.document import Document as DocxDocument

from app.template_engine.utils import cm_value


def extract_page_rules(document: DocxDocument) -> tuple[dict, list[dict]]:
    section = document.sections[0]
    width = cm_value(section.page_width)
    height = cm_value(section.page_height)
    paper_size = "A4" if width and height and abs(width - 21.0) < 0.4 and abs(height - 29.7) < 0.4 else "custom"
    page = {
        "paper_size": paper_size,
        "width_cm": width,
        "height_cm": height,
        "margin_top_cm": cm_value(section.top_margin),
        "margin_bottom_cm": cm_value(section.bottom_margin),
        "margin_left_cm": cm_value(section.left_margin),
        "margin_right_cm": cm_value(section.right_margin),
        "section_count": len(document.sections),
    }
    evidence = [{"field": "page", "source": "sections", "text": f"检测到 {len(document.sections)} 个分节"}]
    return page, evidence
