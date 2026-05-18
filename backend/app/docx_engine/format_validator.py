from __future__ import annotations

from pathlib import Path
from typing import Any

from docx import Document


class FormatValidator:
    def validate(self, path: Path, context: dict[str, Any]) -> dict[str, Any]:
        document = Document(str(path))
        texts = [p.text for p in document.paragraphs]
        full_text = "\n".join(texts)
        checks = [
            {"name": "page_margins", "passed": bool(context.get("page_applied"))},
            {"name": "body_style", "passed": bool(context.get("body_style_applied"))},
            {"name": "heading_style", "passed": bool(context.get("heading_style_applied"))},
            {"name": "figure_caption", "passed": "图1-1" in full_text or "图 1-1" in full_text},
            {"name": "table_caption", "passed": "表1-1" in full_text or "表 1-1" in full_text},
            {"name": "three_line_table", "passed": bool(context.get("three_line_table"))},
            {"name": "references", "passed": "参考文献" in full_text and "[1]" in full_text},
            {"name": "header_footer", "passed": bool(context.get("header_footer_applied"))},
            {"name": "used_template_rules", "passed": bool(context.get("used_template_rules"))},
        ]
        warnings = [f"检查未通过：{check['name']}" for check in checks if not check["passed"]]
        missing_rules = context.get("missing_rules", [])
        warnings.extend([f"缺失模板规则，使用默认值：{item}" for item in missing_rules])
        score = max(0, 100 - len(warnings) * 5)
        return {"passed": all(check["passed"] for check in checks if check["name"] != "used_template_rules"), "score": score, "warnings": warnings, "checks": checks}
