from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt


class DocxEngine:
    """最小 DOCX 精排引擎示例，后续拆分 StyleManager/TableManager/FigureManager 等模块。"""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_sample(self, project_id: int, title: str) -> Path:
        document = Document()
        self._setup_styles(document)

        heading = document.add_paragraph()
        heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = heading.add_run(title)
        run.bold = True
        run.font.size = Pt(18)

        document.add_heading("第1章 绪论", level=1)
        document.add_paragraph("本示例 DOCX 由 python-docx 生成，后续将接入结构化 JSON、模板规则与局部替换能力。")
        document.add_paragraph("图 1-1 系统架构图占位：白底黑字、线条不交叉、节点不重叠。")

        caption = document.add_paragraph("表 1-1 MVP 三线表示例")
        caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
        table = document.add_table(rows=4, cols=3)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.style = "Table Grid"
        headers = ["模块", "职责", "后续扩展"]
        for index, text in enumerate(headers):
            table.cell(0, index).text = text
        rows = [
            ["TemplateAnalyzerAgent", "模板分析", "接入真实 DOCX 样式提取"],
            ["DocxEngine", "精准排版", "支持局部替换和格式保护"],
            ["MemoryGuard", "记忆纠错", "阻止历史错误重复导出"],
        ]
        for row_index, row in enumerate(rows, start=1):
            for col_index, text in enumerate(row):
                table.cell(row_index, col_index).text = text
        self._apply_three_line_table(table)

        document.add_heading("参考文献", level=1)
        document.add_paragraph("[1] 后续由 CitationAgent 根据引用位置自动生成。")

        output = self.output_dir / f"project_{project_id}_sample.docx"
        document.save(output)
        return output

    def _setup_styles(self, document: Document) -> None:
        normal = document.styles["Normal"]
        normal.font.name = "宋体"
        normal._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
        normal.font.size = Pt(12)

    def _apply_three_line_table(self, table) -> None:
        for row_index, row in enumerate(table.rows):
            for cell in row.cells:
                tc_pr = cell._tc.get_or_add_tcPr()
                borders = OxmlElement("w:tcBorders")
                top = OxmlElement("w:top")
                bottom = OxmlElement("w:bottom")
                for border in [top, bottom]:
                    border.set(qn("w:val"), "nil")
                if row_index in {0, len(table.rows) - 1}:
                    bottom.set(qn("w:val"), "single")
                    bottom.set(qn("w:sz"), "12")
                if row_index == 0:
                    top.set(qn("w:val"), "single")
                    top.set(qn("w:sz"), "12")
                borders.append(top)
                borders.append(bottom)
                tc_pr.append(borders)
