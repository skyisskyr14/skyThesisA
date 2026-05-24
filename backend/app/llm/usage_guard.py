from sqlalchemy.orm import Session
from app.models.entities import LLMCallLog

def is_duplicate_request(db: Session, request_id: str | None) -> bool:
    if not request_id:
        return False
    hit = db.query(LLMCallLog).filter(LLMCallLog.request_summary.like(f"[request_id:{request_id}]%"), LLMCallLog.success == True).first()
    return hit is not None
