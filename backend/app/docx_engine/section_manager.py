from __future__ import annotations

from typing import Any

from docx.document import Document as DocxDocument
from docx.shared import Cm


class SectionManager:
    def __init__(self, rules: dict[str, Any]) -> None:
        self.page_rules = rules.get("page", {})

    def apply_page_setup(self, document: DocxDocument) -> list[str]:
        applied: list[str] = []
        for section in document.sections:
            for key, attr in [
                ("margin_top_cm", "top_margin"),
                ("margin_bottom_cm", "bottom_margin"),
                ("margin_left_cm", "left_margin"),
                ("margin_right_cm", "right_margin"),
            ]:
                value = self.page_rules.get(key)
                if value is not None:
                    setattr(section, attr, Cm(float(value)))
                    applied.append(f"page.{key}={value}cm")
            if self.page_rules.get("width_cm") and self.page_rules.get("height_cm"):
                section.page_width = Cm(float(self.page_rules["width_cm"]))
                section.page_height = Cm(float(self.page_rules["height_cm"]))
                applied.append("page.paper_size")
        return applied

    def add_page_break(self, document: DocxDocument) -> None:
        document.add_page_break()
