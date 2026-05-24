from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.docx_engine import DocxEngine
from app.docx_engine.docx_models import PaperDocument
from app.models.entities import PaperVersion, ThesisProject
from app.database import BASE_DIR

router = APIRouter(prefix='/api/thesis/versions', tags=['versions'])

@router.get('/{project_id}')
def list_versions(project_id:int, db:Session=Depends(get_db)):
    return db.query(PaperVersion).filter(PaperVersion.project_id==project_id).order_by(PaperVersion.id.desc()).all()

@router.get('/detail/{version_id}')
def detail(version_id:int, db:Session=Depends(get_db)):
    v=db.get(PaperVersion,version_id)
    if not v: raise HTTPException(404,'version not found')
    return v

@router.post('/{version_id}/select-current')
def select_current(version_id:int, db:Session=Depends(get_db)):
    v=db.get(PaperVersion,version_id)
    if not v: raise HTTPException(404,'version not found')
    db.query(PaperVersion).filter(PaperVersion.project_id==v.project_id).update({PaperVersion.is_current:False})
    v.is_current=True; db.commit(); return {'ok':True}

@router.post('/{version_id}/generate-docx')
def gen_docx(version_id:int, db:Session=Depends(get_db)):
    v=db.get(PaperVersion,version_id); p=db.get(ThesisProject,v.project_id) if v else None
    if not v or not p: raise HTTPException(404,'version or project not found')
    paper = PaperDocument.model_validate(v.paper_document_json)
    result=DocxEngine(BASE_DIR/'storage'/'docx').generate_full(project_id=p.id,paper=paper,template_rules=p.applied_template_rules)
    v.docx_path=result['docx_path']; db.commit()
    return result
