from __future__ import annotations

from pathlib import Path
from typing import Any

from docx import Document

from app.docx_engine.abstract_manager import AbstractManager
from app.docx_engine.cover_manager import CoverManager
from app.docx_engine.docx_models import PaperDocument, build_mock_paper
from app.docx_engine.figure_manager import FigureManager
from app.docx_engine.format_validator import FormatValidator
from app.docx_engine.header_footer_manager import HeaderFooterManager
from app.docx_engine.heading_manager import HeadingManager
from app.docx_engine.paragraph_manager import ParagraphManager
from app.docx_engine.reference_manager import ReferenceManager
from app.docx_engine.rule_resolver import resolve_template_rules
from app.docx_engine.section_manager import SectionManager
from app.docx_engine.style_manager import StyleManager
from app.docx_engine.table_manager import TableManager
from app.docx_engine.toc_manager import TocManager


class DocxEngine:
    """DOCX 精排引擎主入口：从结构化论文数据和 template_rules 生成论文 DOCX。"""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_sample(self, project_id: int, title: str, template_rules: dict[str, Any] | None = None) -> Path:
        paper = build_mock_paper(title=title, author="学生姓名", school="学校名称", major="软件工程")
        result = self.generate_full(project_id=project_id, paper=paper, template_rules=template_rules, filename_suffix="sample")
        return Path(result["docx_path"])

    def generate_full(
        self,
        project_id: int,
        paper: PaperDocument,
        template_rules: dict[str, Any] | None = None,
        filename_suffix: str = "full",
    ) -> dict[str, Any]:
        rules, applied_rules, missing_rules, used_template_rules = resolve_template_rules(template_rules)
        document = Document()
        section_manager = SectionManager(rules)
        page_applied = section_manager.apply_page_setup(document)
        style_applied = StyleManager(rules).apply_styles(document)
        heading_manager = HeadingManager(rules)
        paragraph_manager = ParagraphManager(rules)
        header_footer_applied = HeaderFooterManager(rules, paper.meta.title).apply(document)

        CoverManager().add_cover(document, paper.meta)
        AbstractManager(heading_manager, paragraph_manager).add_abstracts(document, paper.abstract)
        TocManager(heading_manager).add_toc_placeholder(document)
        self._add_chapters(document, paper, heading_manager, paragraph_manager, FigureManager(rules), TableManager(rules))
        ReferenceManager(rules, heading_manager).add_references(document, paper.references)

        output = self.output_dir / f"project_{project_id}_{filename_suffix}.docx"
        document.save(output)
        context = {
            "page_applied": bool(page_applied),
            "body_style_applied": "body style" in style_applied,
            "heading_style_applied": any(item.startswith("heading") for item in style_applied),
            "three_line_table": rules.get("tables", {}).get("use_three_line_table", True),
            "header_footer_applied": bool(header_footer_applied),
            "used_template_rules": used_template_rules,
            "missing_rules": missing_rules,
        }
        format_validation = FormatValidator().validate(output, context)
        return {
            "docx_path": str(output),
            "download_url": f"/api/docx/download/{output.name}",
            "used_template_rules": used_template_rules,
            "applied_rules_summary": sorted(set(applied_rules + page_applied + style_applied + header_footer_applied)),
            "missing_rules": missing_rules,
            "format_validation": format_validation,
        }

    def _add_chapters(
        self,
        document: Document,
        paper: PaperDocument,
        heading_manager: HeadingManager,
        paragraph_manager: ParagraphManager,
        figure_manager: FigureManager,
        table_manager: TableManager,
    ) -> None:
        for chapter in paper.chapters:
            heading_manager.add_heading(document, f"第{chapter.chapter_no}章 {chapter.title}", 1)
            figure_index = 1
            table_index = 1
            for section_index, section in enumerate(chapter.sections, start=1):
                heading_manager.add_heading(document, f"{chapter.chapter_no}.{section_index} {section.title}", section.level)
                for block in section.blocks:
                    if block.type == "paragraph" and block.text:
                        paragraph_manager.add_body_paragraph(document, block.text)
                    elif block.type == "figure_placeholder" and block.title:
                        figure_manager.add_placeholder(document, chapter.chapter_no, figure_index, block.title)
                        figure_index += 1
                    elif block.type == "table" and block.title:
                        table_manager.add_table(document, chapter.chapter_no, table_index, block.title, block.columns, block.rows)
                        table_index += 1
            document.add_page_break()
