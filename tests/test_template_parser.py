"""v0.3 DOCX 模板解析冒烟测试。

运行方式：
    PYTHONPATH=backend python tests/test_template_parser.py
"""
from __future__ import annotations

from pathlib import Path
import runpy

from app.docx_engine import DocxEngine
from app.template_engine import DocxTemplateParser
from app.template_engine.template_conflict_detector import detect_conflicts

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "sample_template.docx"


def ensure_fixture() -> Path:
    if not FIXTURE.exists():
        runpy.run_path(str(ROOT / "tests" / "scripts" / "create_sample_template.py"), run_name="__main__")
    return FIXTURE


def test_parse_docx_template() -> dict:
    result = DocxTemplateParser().parse(ensure_fixture(), template_id=1)
    for key in ["template_type", "confidence", "page", "body", "headings", "figures", "tables", "header_footer", "references", "conflicts", "warnings", "source_evidence"]:
        assert key in result, f"missing template_rules key: {key}"
    assert result["template_type"] in {"instruction_only", "sample_paper", "mixed", "unknown"}
    assert result["body"]["font_cn"] == "宋体"
    assert result["tables"]["use_three_line_table"] is True
    return result


def test_conflict_detector() -> None:
    conflicts = detect_conflicts({"body": {"font_size_pt": 12}}, {"body": {"font_size_pt": 10.5}})
    assert conflicts and conflicts[0]["field"] == "body.font_size_pt"


def test_docx_generation_with_template_rules() -> None:
    rules = test_parse_docx_template()
    output = DocxEngine(ROOT / "backend" / "storage" / "docx").generate_sample(999, "模板规则应用测试", rules)
    assert output.exists(), output


if __name__ == "__main__":
    test_parse_docx_template()
    test_conflict_detector()
    test_docx_generation_with_template_rules()
    print("template parser smoke tests passed")
