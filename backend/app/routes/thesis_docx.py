from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import BASE_DIR, get_db
from app.docx_engine import DocxEngine, build_mock_paper
from app.models.entities import ThesisProject
from app.schemas.common import GenerateFullDocxRequest, GenerateFullDocxResponse

router = APIRouter(prefix="/api/thesis/docx", tags=["thesis-docx"])
EXPORT_DIR = BASE_DIR / "storage" / "docx"


@router.post("/generate-full", response_model=GenerateFullDocxResponse)
def generate_full_docx(payload: GenerateFullDocxRequest, db: Session = Depends(get_db)):
    project = db.get(ThesisProject, payload.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    template_rules = project.applied_template_rules if payload.use_template_rules else None
    paper = build_mock_paper(project.title, project.author, project.school, project.major)
    result = DocxEngine(EXPORT_DIR).generate_full(project_id=project.id, paper=paper, template_rules=template_rules)
    return {"project_id": project.id, **result}
