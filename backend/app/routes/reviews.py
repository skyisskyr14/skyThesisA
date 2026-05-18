from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.memory_guard.service import run_final_review
from app.models.entities import ReviewReport, ThesisProject
from app.schemas.common import ReviewRead, ReviewRequest, ReviewResult

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.post("/run", response_model=ReviewResult)
def run_review(payload: ReviewRequest, db: Session = Depends(get_db)):
    project = db.get(ThesisProject, payload.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    content = payload.content or project.title
    return run_final_review(db, payload.project_id, content)


@router.get("/{project_id}", response_model=list[ReviewRead])
def get_reviews(project_id: int, db: Session = Depends(get_db)):
    return db.query(ReviewReport).filter(ReviewReport.project_id == project_id).order_by(ReviewReport.created_at.desc()).all()
