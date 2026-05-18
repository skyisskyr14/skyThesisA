from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entities import Outline, PaperChapter, ThesisProject
from app.models.enums import ProjectStatus, StepStatus
from app.schemas.common import MockResult
from app.services.mock_agents import analyze_teacher_comments, analyze_template, generate_chapter, generate_outline

router = APIRouter(tags=["pipeline"])


def require_project(project_id: int, db: Session) -> ThesisProject:
    project = db.get(ThesisProject, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    return project


@router.post("/api/templates/analyze", response_model=MockResult)
def template_analyze(project_id: int, db: Session = Depends(get_db)):
    project = require_project(project_id, db)
    result = analyze_template(project.title)
    project.status = ProjectStatus.parsed
    project.current_step = "outline"
    project.step_statuses = {**project.step_statuses, "template": StepStatus.completed.value}
    db.commit()
    return {"project_id": project_id, "status": StepStatus.completed, "result": result}


@router.post("/api/outlines/generate", response_model=MockResult)
def outline_generate(project_id: int, db: Session = Depends(get_db)):
    project = require_project(project_id, db)
    result = generate_outline(project.title)
    db.add(Outline(project_id=project_id, title=project.title, items=result["chapters"]))
    project.status = ProjectStatus.planned
    project.current_step = "writing"
    project.step_statuses = {**project.step_statuses, "outline": StepStatus.completed.value}
    db.commit()
    return {"project_id": project_id, "status": StepStatus.completed, "result": result}


@router.post("/api/chapters/generate", response_model=MockResult)
def chapter_generate(project_id: int, chapter_no: int = 1, db: Session = Depends(get_db)):
    project = require_project(project_id, db)
    result = generate_chapter(project.title, chapter_no)
    chapter = PaperChapter(
        project_id=project_id,
        chapter_no=chapter_no,
        title=result["title"],
        content=result["blocks"][1]["text"],
        blocks=result["blocks"],
        status=StepStatus.completed,
    )
    db.add(chapter)
    project.status = ProjectStatus.writing
    project.current_step = "figures"
    project.step_statuses = {**project.step_statuses, "writing": StepStatus.completed.value}
    db.commit()
    return {"project_id": project_id, "status": StepStatus.completed, "result": result}


@router.post("/api/chapters/rewrite", response_model=MockResult)
def chapter_rewrite(project_id: int, chapter_no: int, instruction: str, db: Session = Depends(get_db)):
    project = require_project(project_id, db)
    result = generate_chapter(project.title, chapter_no)
    result["rewriteInstruction"] = instruction
    result["contentProtection"] = "仅修改指定章节，保护其他章节和原格式"
    return {"project_id": project_id, "status": StepStatus.completed, "result": result}


@router.post("/api/comments/analyze")
def comments_analyze(project_id: int, db: Session = Depends(get_db)):
    require_project(project_id, db)
    return analyze_teacher_comments()
