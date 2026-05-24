from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import BASE_DIR, get_db
from app.docx_engine import DocxEngine
from app.docx_engine.docx_models import PaperDocument
from app.models.entities import PaperVersion, ThesisProject
from app.schemas.common import GenerateFullDocxResponse

router = APIRouter(prefix="/api/thesis/docx", tags=["thesis-docx"])
EXPORT_DIR = BASE_DIR / "storage" / "docx"

@router.post('/generate-full', response_model=GenerateFullDocxResponse)
def generate_full_docx(payload: dict, db: Session = Depends(get_db)):
    project_id = int(payload.get('project_id', 0))
    paper_version_id = payload.get('paper_version_id')
    use_template_rules = bool(payload.get('use_template_rules', True))
    project = db.get(ThesisProject, project_id)
    if not project: raise HTTPException(404, '项目不存在')
    version = db.get(PaperVersion, int(paper_version_id)) if paper_version_id else db.query(PaperVersion).filter(PaperVersion.project_id==project_id, PaperVersion.is_current==True).first()
    if not version: raise HTTPException(400, '当前项目没有真实论文内容，请先导入论文初稿或通过 DeepSeek 生成章节。')
    paper = PaperDocument.model_validate(version.paper_document_json)
    template_rules = project.applied_template_rules if use_template_rules else None
    result = DocxEngine(EXPORT_DIR).generate_full(project_id=project.id, paper=paper, template_rules=template_rules)
    version.docx_path = result['docx_path']; db.commit()
    return {"project_id": project.id, **result}
