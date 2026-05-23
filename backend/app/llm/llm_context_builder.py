from sqlalchemy.orm import Session
from app.models.entities import ThesisProject, PaperChapter, RuleMemory, RevisionTask, ChatMessage

def build_chat_context(db: Session, project_id: int, current_step: str, current_chapter_id: int | None = None) -> str:
    p = db.get(ThesisProject, project_id)
    chapters = db.query(PaperChapter).filter(PaperChapter.project_id == project_id).limit(3).all()
    rules = db.query(RuleMemory).filter(RuleMemory.project_id.in_([project_id, None])).order_by(RuleMemory.created_at.desc()).limit(5).all()
    tasks = db.query(RevisionTask).filter(RevisionTask.project_id == project_id).limit(5).all()
    chats = db.query(ChatMessage).filter(ChatMessage.project_id == project_id).order_by(ChatMessage.created_at.desc()).limit(10).all()
    parts = [f"项目:{p.title if p else project_id}", f"步骤:{current_step}"]
    if current_chapter_id:
        parts.append(f"当前章节ID:{current_chapter_id}")
    parts.append("章节:" + " | ".join([f"第{c.chapter_no}章:{c.title}" for c in chapters]))
    parts.append("规则:" + " | ".join([r.rule_name for r in rules]))
    parts.append("任务:" + " | ".join([t.task for t in tasks]))
    parts.append("最近对话:" + " | ".join([f"{m.role}:{m.content[:40]}" for m in chats]))
    return "\n".join(parts)
