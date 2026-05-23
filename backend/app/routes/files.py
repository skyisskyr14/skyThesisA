from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import BASE_DIR, get_db
from app.models.entities import PaperFile, ThesisProject
from app.models.enums import ProjectStatus, StepStatus
from app.schemas.common import FileRead

router = APIRouter(prefix="/api/files", tags=["files"])
UPLOAD_DIR = BASE_DIR / "storage" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload", response_model=FileRead)
def upload_file(project_id: int = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    project = db.get(ThesisProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    target = UPLOAD_DIR / f"project_{project_id}_{file.filename}"
    target.write_bytes(file.file.read())
    paper_file = PaperFile(
        project_id=project_id,
        filename=file.filename,
        file_type=Path(file.filename).suffix.lower().lstrip(".") or "unknown",
        purpose="MVP 上传文件，后续由 FileRouterAgent 识别用途",
        path=str(target),
        status=StepStatus.completed,
    )
    project.status = ProjectStatus.uploaded
    project.current_step = "template"
    project.step_statuses = {**project.step_statuses, "upload": StepStatus.completed.value}
    db.add(paper_file)
    db.commit()
    db.refresh(paper_file)
    return paper_file


@router.post("/analyze")
def analyze_file(project_id: int):
    return {"project_id": project_id, "router": "FileRouterAgent", "purpose": "论文资料/学校模板/老师批注待进一步分类"}
