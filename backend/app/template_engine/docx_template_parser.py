from __future__ import annotations

from pathlib import Path

from docx import Document

from app.template_engine.header_footer_extractor import extract_header_footer_rules
from app.template_engine.heading_rule_extractor import extract_heading_rules
from app.template_engine.instruction_rule_extractor import extract_instruction_rules
from app.template_engine.paragraph_rule_extractor import extract_body_rules
from app.template_engine.reference_extractor import extract_reference_rules
from app.template_engine.section_extractor import extract_page_rules
from app.template_engine.table_rule_extractor import extract_caption_and_table_rules
from app.template_engine.template_rule_merger import merge_rules

INSTRUCTION_KEYWORDS = ["格式要求", "正文", "标题", "字体", "字号", "页边距", "行距", "宋体", "黑体", "三线表"]
PAPER_KEYWORDS = ["摘要", "关键词", "目录", "第1章", "第一章", "参考文献"]


class DocxTemplateParser:
    """真实 DOCX 模板解析入口，输出统一 template_rules JSON。"""

    def parse(self, file_path: str | Path, template_id: int | None = None) -> dict:
        path = Path(file_path)
        document = Document(str(path))
        paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]
        full_text = "\n".join(paragraphs)

        page, page_evidence = extract_page_rules(document)
        body, body_evidence = extract_body_rules(document)
        headings, heading_evidence = extract_heading_rules(document)
        figures, tables, table_evidence = extract_caption_and_table_rules(document)
        header_footer, hf_evidence = extract_header_footer_rules(document)
        references, ref_evidence = extract_reference_rules(document)
        instruction_rules, instruction_evidence = extract_instruction_rules(full_text)

        sample_rules = {
            "page": page,
            "body": body,
            "headings": headings,
            "figures": figures,
            "tables": tables,
            "header_footer": header_footer,
            "references": references,
        }
        merged, conflicts, warnings = merge_rules(sample_rules, instruction_rules)
        template_type = self._detect_template_type(full_text)
        confidence = self._confidence(template_type, conflicts, full_text)
        source_evidence = page_evidence + body_evidence + heading_evidence + table_evidence + hf_evidence + ref_evidence + instruction_evidence
        result = {
            "template_id": template_id,
            "template_type": template_type,
            "confidence": confidence,
            **merged,
            "conflicts": conflicts,
            "warnings": warnings,
            "source_evidence": source_evidence,
        }
        return result

    def _detect_template_type(self, text: str) -> str:
        instruction_score = sum(1 for keyword in INSTRUCTION_KEYWORDS if keyword in text)
        paper_score = sum(1 for keyword in PAPER_KEYWORDS if keyword in text)
        if instruction_score >= 4 and paper_score >= 3:
            return "mixed"
        if instruction_score >= 4:
            return "instruction_only"
        if paper_score >= 3:
            return "sample_paper"
        return "unknown"

    def _confidence(self, template_type: str, conflicts: list[dict], text: str) -> float:
        base = {"mixed": 0.85, "instruction_only": 0.78, "sample_paper": 0.76, "unknown": 0.45}[template_type]
        if conflicts:
            base -= min(0.2, len(conflicts) * 0.03)
        if len(text) < 100:
            base -= 0.1
        return round(max(0.1, min(base, 0.95)), 2)
