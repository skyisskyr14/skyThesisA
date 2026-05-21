from __future__ import annotations

from typing import Any

from docx.document import Document as DocxDocument
from docx.oxml.ns import qn
from docx.shared import Pt

from app.docx_engine.common import ALIGNMENT_MAP


class ParagraphManager:
    def __init__(self, rules: dict[str, Any]) -> None:
        self.body = rules.get("body", {})

    def add_body_paragraph(self, document: DocxDocument, text: str):
        paragraph = document.add_paragraph(text)
        paragraph.alignment = ALIGNMENT_MAP.get(self.body.get("alignment", "justify"))
        fmt = paragraph.paragraph_format
        size = float(self.body.get("font_size_pt", 12))
        fmt.first_line_indent = Pt(float(self.body.get("first_line_indent_chars", 2)) * size)
        fmt.line_spacing = float(self.body.get("line_spacing", 1.25))
        fmt.space_before = Pt(float(self.body.get("space_before_pt", 0)))
        fmt.space_after = Pt(float(self.body.get("space_after_pt", 0)))
        for run in paragraph.runs:
            run.font.name = self.body.get("font_en", "Times New Roman")
            run._element.rPr.rFonts.set(qn("w:eastAsia"), self.body.get("font_cn", "宋体"))
            run.font.size = Pt(size)
        return paragraph
