from __future__ import annotations

from typing import Any

from docx.document import Document as DocxDocument
from docx.oxml.ns import qn
from docx.shared import Pt

from app.docx_engine.common import ALIGNMENT_MAP
from app.docx_engine.rule_resolver import heading_rule


class StyleManager:
    def __init__(self, rules: dict[str, Any]) -> None:
        self.rules = rules

    def apply_styles(self, document: DocxDocument) -> list[str]:
        applied = []
        body = self.rules.get("body", {})
        normal = document.styles["Normal"]
        font_cn = body.get("font_cn", "宋体")
        normal.font.name = body.get("font_en") or "Times New Roman"
        normal._element.rPr.rFonts.set(qn("w:eastAsia"), font_cn)
        normal.font.size = Pt(float(body.get("font_size_pt", 12)))
        normal.paragraph_format.line_spacing = float(body.get("line_spacing", 1.25))
        normal.paragraph_format.space_before = Pt(float(body.get("space_before_pt", 0)))
        normal.paragraph_format.space_after = Pt(float(body.get("space_after_pt", 0)))
        normal.paragraph_format.first_line_indent = Pt(float(body.get("first_line_indent_chars", 2)) * float(body.get("font_size_pt", 12)))
        applied.append("body style")
        for level in [1, 2, 3]:
            rule = heading_rule(self.rules, level)
            style_name = f"Heading {level}"
            if style_name in document.styles:
                style = document.styles[style_name]
                font_name = rule.get("font_name", "黑体")
                style.font.name = font_name
                style._element.rPr.rFonts.set(qn("w:eastAsia"), font_name)
                style.font.size = Pt(float(rule.get("font_size_pt", 16)))
                style.font.bold = bool(rule.get("bold", False))
                style.paragraph_format.alignment = ALIGNMENT_MAP.get(rule.get("alignment", "left"))
                style.paragraph_format.space_before = Pt(float(rule.get("space_before_pt", 0)))
                style.paragraph_format.space_after = Pt(float(rule.get("space_after_pt", 0)))
                applied.append(f"heading {level} style")
        return applied
