from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.memory_guard.service import add_error_as_rule
from app.models.entities import ErrorMemory, RuleMemory, UserMemory
from app.schemas.common import ErrorCreate, ErrorRead, MemoryCreate, MemoryRead, RuleCreate, RuleRead

router = APIRouter(tags=["memory"])


@router.get("/api/memory", response_model=list[MemoryRead])
def list_memory(project_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(UserMemory)
    if project_id is not None:
        query = query.filter((UserMemory.project_id.is_(None)) | (UserMemory.project_id == project_id))
    return query.order_by(UserMemory.created_at.desc()).all()


@router.post("/api/memory", response_model=MemoryRead)
def create_memory(payload: MemoryCreate, db: Session = Depends(get_db)):
    memory = UserMemory(**payload.model_dump())
    db.add(memory)
    db.commit()
    db.refresh(memory)
    return memory


@router.get("/api/errors", response_model=list[ErrorRead])
def list_errors(project_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(ErrorMemory)
    if project_id is not None:
        query = query.filter((ErrorMemory.project_id.is_(None)) | (ErrorMemory.project_id == project_id))
    return query.order_by(ErrorMemory.created_at.desc()).all()


@router.post("/api/errors", response_model=ErrorRead)
def create_error(payload: ErrorCreate, db: Session = Depends(get_db)):
    error = ErrorMemory(**payload.model_dump())
    db.add(error)
    db.commit()
    db.refresh(error)
    add_error_as_rule(db, error)
    return error


@router.get("/api/rules", response_model=list[RuleRead])
def list_rules(project_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(RuleMemory)
    if project_id is not None:
        query = query.filter((RuleMemory.project_id.is_(None)) | (RuleMemory.project_id == project_id))
    return query.order_by(RuleMemory.created_at.desc()).all()


@router.post("/api/rules", response_model=RuleRead)
def create_rule(payload: RuleCreate, db: Session = Depends(get_db)):
    rule = RuleMemory(**payload.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule
