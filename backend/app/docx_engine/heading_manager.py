from __future__ import annotations

from typing import Any

from docx.document import Document as DocxDocument
from docx.oxml.ns import qn
from docx.shared import Pt

from app.docx_engine.common import ALIGNMENT_MAP
from app.docx_engine.rule_resolver import heading_rule


class HeadingManager:
    def __init__(self, rules: dict[str, Any]) -> None:
        self.rules = rules

    def add_heading(self, document: DocxDocument, text: str, level: int):
        paragraph = document.add_heading(text, level=level)
        rule = heading_rule(self.rules, level)
        paragraph.alignment = ALIGNMENT_MAP.get(rule.get("alignment", "left"))
        paragraph.paragraph_format.space_before = Pt(float(rule.get("space_before_pt", 0)))
        paragraph.paragraph_format.space_after = Pt(float(rule.get("space_after_pt", 0)))
        for run in paragraph.runs:
            run.font.name = rule.get("font_name", "黑体")
            run._element.rPr.rFonts.set(qn("w:eastAsia"), rule.get("font_name", "黑体"))
            run.font.size = Pt(float(rule.get("font_size_pt", 16)))
            run.font.bold = bool(rule.get("bold", False))
        return paragraph
