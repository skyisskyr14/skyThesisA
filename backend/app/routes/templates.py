from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import BASE_DIR, get_db
from app.models.entities import PaperFile, TemplateAnalysisResult, ThesisProject
from app.schemas.common import AnalyzeDocxTemplateRequest, ApplyTemplateRulesRequest, ApplyTemplateRulesResponse, TemplateAnalysisRead
from app.template_engine import DocxTemplateParser

router = APIRouter(prefix="/api/thesis/templates", tags=["templates"])


@router.post("/analyze-docx", response_model=TemplateAnalysisRead)
def analyze_docx_template(payload: AnalyzeDocxTemplateRequest, db: Session = Depends(get_db)):
    project = db.get(ThesisProject, payload.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    file_id = payload.file_id
    path = _resolve_template_path(payload, db)
    parser = DocxTemplateParser()
    rules_json = parser.parse(path)
    result = TemplateAnalysisResult(
        project_id=payload.project_id,
        file_id=file_id,
        template_type=rules_json["template_type"],
        confidence=rules_json["confidence"],
        rules_json=rules_json,
        conflicts_json=rules_json.get("conflicts", []),
        warnings_json=rules_json.get("warnings", []),
        source_evidence_json=rules_json.get("source_evidence", []),
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    rules_with_id = {**result.rules_json, "template_id": result.id}
    result.rules_json = rules_with_id
    db.commit()
    db.refresh(result)
    return result


@router.get("/{project_id}/latest", response_model=TemplateAnalysisRead)
def latest_template_result(project_id: int, db: Session = Depends(get_db)):
    result = (
        db.query(TemplateAnalysisResult)
        .filter(TemplateAnalysisResult.project_id == project_id)
        .order_by(TemplateAnalysisResult.created_at.desc())
        .first()
    )
    if not result:
        raise HTTPException(status_code=404, detail="尚无模板分析结果")
    return result


@router.post("/apply", response_model=ApplyTemplateRulesResponse)
def apply_template_rules(payload: ApplyTemplateRulesRequest, db: Session = Depends(get_db)):
    project = db.get(ThesisProject, payload.project_id)
    result = db.get(TemplateAnalysisResult, payload.analysis_id)
    if not project or not result or result.project_id != payload.project_id:
        raise HTTPException(status_code=404, detail="项目或模板分析结果不存在")
    project.applied_template_rules = result.rules_json
    result.applied = True
    db.commit()
    return {"project_id": payload.project_id, "analysis_id": payload.analysis_id, "applied": True, "message": "模板规则已应用到当前论文项目"}


def _resolve_template_path(payload: AnalyzeDocxTemplateRequest, db: Session) -> Path:
    if payload.file_id:
        paper_file = db.get(PaperFile, payload.file_id)
        if not paper_file:
            raise HTTPException(status_code=404, detail="文件不存在")
        path = Path(paper_file.path)
    elif payload.file_path:
        path = Path(payload.file_path)
        if not path.is_absolute():
            repo_root = BASE_DIR.parent
            path = repo_root / path
    else:
        raise HTTPException(status_code=400, detail="必须提供 file_id 或 file_path")
    if not path.exists() or path.suffix.lower() != ".docx":
        raise HTTPException(status_code=400, detail=f"DOCX 模板文件不存在或类型不正确：{path}")
    return path
