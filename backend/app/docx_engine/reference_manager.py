from __future__ import annotations

from typing import Any

from docx.document import Document as DocxDocument

from app.docx_engine.docx_models import PaperReference
from app.docx_engine.heading_manager import HeadingManager


class ReferenceManager:
    def __init__(self, rules: dict[str, Any], heading_manager: HeadingManager) -> None:
        self.rules = rules.get("references", {})
        self.heading_manager = heading_manager

    def add_references(self, document: DocxDocument, references: list[PaperReference]) -> None:
        self.heading_manager.add_heading(document, self.rules.get("heading_text", "参考文献"), 1)
        style = self.rules.get("numbering_style", "[1]")
        for ref in references:
            prefix = f"[{ref.index}]" if style == "[1]" else f"{ref.index}."
            document.add_paragraph(f"{prefix} {ref.text}")
