from __future__ import annotations

from docx.document import Document as DocxDocument
from docx.enum.text import WD_ALIGN_PARAGRAPH

from app.docx_engine.heading_manager import HeadingManager


class TocManager:
    def __init__(self, heading_manager: HeadingManager) -> None:
        self.heading_manager = heading_manager

    def add_toc_placeholder(self, document: DocxDocument) -> None:
        self.heading_manager.add_heading(document, "目  录", 1)
        p = document.add_paragraph("请在 Word/WPS 中更新目录域。")
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        # TODO(v0.5): 使用 OOXML TOC 域生成可更新目录。
        document.add_page_break()
