from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.memory_guard.service import create_rule_from_chat
from app.models.entities import ErrorMemory, UserMemory
from app.models.enums import MemoryType
from app.schemas.common import ChatIntent, ChatRequest
from app.services.chat_parser import parse_chat_message

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatIntent)
def parse_chat(payload: ChatRequest, db: Session = Depends(get_db)):
    parsed = parse_chat_message(payload.message)
    if parsed["memory_action"] == "create_error_memory":
        error = ErrorMemory(
            project_id=payload.project_id,
            error_type=parsed["target"] or "user_feedback",
            description=parsed["requirement"],
            fix_strategy="按用户对话生成长期规则，并在最终审查中检查同类问题。",
            severity="A",
        )
        db.add(error)
        db.commit()
        db.refresh(error)
        create_rule_from_chat(db, payload.project_id, parsed["requirement"], "historical_error")
    elif parsed["memory_action"] == "create_rule_memory":
        create_rule_from_chat(db, payload.project_id, parsed["requirement"], parsed["target"] or "chat_rule")
    else:
        db.add(
            UserMemory(
                project_id=payload.project_id,
                memory_type=MemoryType.user_preference,
                content=payload.message,
                source="chat",
            )
        )
        db.commit()
    return parsed
