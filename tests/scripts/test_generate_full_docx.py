"""v0.4 完整 DOCX 精排冒烟测试。

运行方式：
    PYTHONPATH=backend python tests/scripts/test_generate_full_docx.py
"""
from __future__ import annotations

import runpy
from pathlib import Path

from fastapi.testclient import TestClient

from app.database import init_db
from app.docx_engine import DocxEngine, build_mock_paper
from app.main import app
from app.template_engine import DocxTemplateParser

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "sample_template.docx"


def ensure_fixture() -> Path:
    if not FIXTURE.exists():
        runpy.run_path(str(ROOT / "tests" / "scripts" / "create_sample_template.py"), run_name="__main__")
    return FIXTURE


def test_engine_without_template_rules() -> None:
    paper = build_mock_paper("无模板规则完整 DOCX", "学生姓名", "学校名称", "软件工程")
    result = DocxEngine(ROOT / "backend" / "storage" / "docx").generate_full(1001, paper, None)
    assert Path(result["docx_path"]).exists()
    assert "format_validation" in result and "score" in result["format_validation"]


def test_engine_with_template_rules() -> None:
    rules = DocxTemplateParser().parse(ensure_fixture())
    paper = build_mock_paper("有模板规则完整 DOCX", "学生姓名", "学校名称", "软件工程")
    result = DocxEngine(ROOT / "backend" / "storage" / "docx").generate_full(1002, paper, rules)
    assert Path(result["docx_path"]).exists()
    assert result["used_template_rules"] is True
    assert result["format_validation"]["checks"]


def test_generate_full_api() -> None:
    init_db()
    with TestClient(app) as client:
        project = client.post(
            "/api/projects",
            json={"title": "generate-full API 测试", "author": "学生姓名", "major": "软件工程", "school": "学校名称"},
        )
        assert project.status_code == 200, project.text
        project_id = project.json()["id"]
        response = client.post(
            "/api/thesis/docx/generate-full",
            json={"project_id": project_id, "use_template_rules": False, "use_mock_content": True},
        )
        assert response.status_code == 200, response.text
        payload = response.json()
        assert payload["format_validation"]["checks"]
        assert Path(payload["docx_path"]).exists()


if __name__ == "__main__":
    test_engine_without_template_rules()
    test_engine_with_template_rules()
    test_generate_full_api()
    print("full docx generation smoke tests passed")
