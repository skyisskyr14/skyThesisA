from __future__ import annotations

from docx.document import Document as DocxDocument

from app.docx_engine.docx_models import PaperAbstract
from app.docx_engine.heading_manager import HeadingManager
from app.docx_engine.paragraph_manager import ParagraphManager


class AbstractManager:
    def __init__(self, heading_manager: HeadingManager, paragraph_manager: ParagraphManager) -> None:
        self.heading_manager = heading_manager
        self.paragraph_manager = paragraph_manager

    def add_abstracts(self, document: DocxDocument, abstract: PaperAbstract) -> None:
        self.heading_manager.add_heading(document, "摘  要", 1)
        for text in abstract.zh:
            self.paragraph_manager.add_body_paragraph(document, text)
        self.paragraph_manager.add_body_paragraph(document, "关键词：" + "；".join(abstract.zh_keywords))
        document.add_page_break()
        self.heading_manager.add_heading(document, "Abstract", 1)
        for text in abstract.en:
            self.paragraph_manager.add_body_paragraph(document, text)
        self.paragraph_manager.add_body_paragraph(document, "Keywords: " + "; ".join(abstract.en_keywords))
        document.add_page_break()
