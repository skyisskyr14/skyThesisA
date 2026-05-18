from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.entities import ErrorMemory, RuleMemory, UserMemory
from app.models.enums import MemoryType
from app.schemas.common import ChatIntent, ChatRequest
from app.services.chat_parser import parse_chat_message

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatIntent)
def parse_chat(payload: ChatRequest, db: Session = Depends(get_db)):
    parsed = parse_chat_message(payload.message)
    if parsed["memory_action"] == "create_error_memory":
        db.add(
            ErrorMemory(
                project_id=payload.project_id,
                error_type="user_feedback",
                description=payload.message,
                severity="A",
            )
        )
    elif parsed["memory_action"] == "create_rule_memory":
        db.add(
            RuleMemory(
                project_id=payload.project_id,
                rule_id="RULE_USER_CHAT",
                trigger=[payload.message[:20]],
                rule=payload.message,
                severity="A",
                block_final_output=True,
            )
        )
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
