from sqlalchemy.orm import Session
from app.models.entities import LLMStepBinding

def resolve_step_binding(db: Session, step_key: str):
    return db.query(LLMStepBinding).filter(LLMStepBinding.step_key == step_key, LLMStepBinding.enabled == True).first()
