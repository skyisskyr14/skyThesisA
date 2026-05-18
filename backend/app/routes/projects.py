from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entities import ThesisProject, ThesisVersion
from app.schemas.common import ProjectCreate, ProjectRead
from app.services.state_machine import initial_step_statuses

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectRead)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = ThesisProject(
        title=payload.title,
        author=payload.author,
        major=payload.major,
        school=payload.school,
        step_statuses=initial_step_statuses(),
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    db.add(ThesisVersion(project_id=project.id, version_no="v0.1", summary="项目创建"))
    db.commit()
    return project


@router.get("", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)):
    return db.query(ThesisProject).order_by(ThesisProject.created_at.desc()).all()


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.get(ThesisProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project
