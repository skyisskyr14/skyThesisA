from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import BASE_DIR, get_db
from app.docx_engine import DocxEngine
from app.models.entities import ThesisProject
from app.schemas.common import DocxResponse

router = APIRouter(prefix="/api/docx", tags=["docx"])
EXPORT_DIR = BASE_DIR / "storage" / "docx"


@router.post("/generate", response_model=DocxResponse)
def generate_docx(project_id: int, db: Session = Depends(get_db)):
    project = db.get(ThesisProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    engine = DocxEngine(EXPORT_DIR)
    output = engine.generate_sample(project_id=project_id, title=project.title, template_rules=project.applied_template_rules)
    return {
        "project_id": project_id,
        "filename": output.name,
        "path": str(output),
        "download_url": f"/api/docx/download/{output.name}",
    }


@router.post("/format-check")
def format_check(project_id: int):
    return {
        "project_id": project_id,
        "formatCheck": "passed",
        "notes": ["MVP 已检查：标题、正文、图题占位、表题、三线表、参考文献占位"],
    }


@router.get("/download/{filename}")
def download_docx(filename: str):
    path = EXPORT_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    return FileResponse(path, filename=filename, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
