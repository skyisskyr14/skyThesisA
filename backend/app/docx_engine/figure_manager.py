from __future__ import annotations

from typing import Any

from docx.document import Document as DocxDocument
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Pt

from app.docx_engine.common import ALIGNMENT_MAP


class FigureManager:
    def __init__(self, rules: dict[str, Any]) -> None:
        self.rules = rules.get("figures", {})

    def add_placeholder(self, document: DocxDocument, chapter_no: int, index: int, title: str) -> None:
        caption = self._caption(chapter_no, index, title)
        if self.rules.get("caption_position", "below") == "above":
            self._add_caption(document, caption)
        p = document.add_paragraph(f"【此处插入：{title}】")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(12)
        if self.rules.get("caption_position", "below") == "below":
            self._add_caption(document, caption)
        # TODO(v0.5): 在此扩展真实图片/SVG 插入能力。

    def _caption(self, chapter_no: int, index: int, title: str) -> str:
        pattern = self.rules.get("caption_pattern", "图{chapter}-{index} {title}")
        return pattern.replace("{chapter}", str(chapter_no)).replace("{index}", str(index)).replace("{title}", title)

    def _add_caption(self, document: DocxDocument, text: str) -> None:
        p = document.add_paragraph(text)
        p.alignment = ALIGNMENT_MAP.get(self.rules.get("alignment", "center"))
        for run in p.runs:
            run.font.name = self.rules.get("font_name", "宋体")
            run._element.rPr.rFonts.set(qn("w:eastAsia"), self.rules.get("font_name", "宋体"))
            run.font.size = Pt(float(self.rules.get("font_size_pt", 10.5)))
