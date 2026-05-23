from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.llm.llm_client import openai_compatible_chat
from app.llm.llm_context_builder import build_chat_context
from app.llm.llm_prompt_builder import build_right_chat_prompts
from app.llm.llm_provider_service import get_provider_api_key
from app.llm.llm_response_parser import parse_llm_response
from app.llm.llm_router import resolve_step_binding
from app.memory_guard.service import create_rule_from_chat
from app.models.entities import ChatMessage, ChatSession, LLMCallLog, LLMModel, LLMProvider, RevisionTask
from app.schemas.common import ChatIntent, ChatRequest, ChatSendRequest
from app.services.chat_parser import parse_chat_message

router = APIRouter(tags=["chat"])

@router.post('/api/chat', response_model=ChatIntent)
def parse_chat(payload: ChatRequest, db: Session = Depends(get_db)):
    return parse_chat_message(payload.message)

@router.post('/api/thesis/chat/send')
def send_chat(payload: ChatSendRequest, db: Session = Depends(get_db)):
    binding = resolve_step_binding(db, 'right_chat')
    if not binding:
        raise HTTPException(400, '未配置右侧对话模型，请先到模型配置中心配置 right_chat 使用的模型。')
    provider = db.get(LLMProvider, binding.provider_id)
    model = db.get(LLMModel, binding.model_id)
    context = build_chat_context(db, payload.project_id, payload.current_step, payload.current_chapter_id)
    messages = build_right_chat_prompts(context, payload.message, binding.system_prompt)
    resp = openai_compatible_chat(provider.base_url, get_provider_api_key(provider), model.model_name, messages, binding.temperature, binding.max_tokens)
    content = resp['raw'].get('choices', [{}])[0].get('message', {}).get('content', '')
    assistant_message, parsed_intent = parse_llm_response(content)
    session = db.query(ChatSession).filter(ChatSession.project_id == payload.project_id).first()
    if not session:
        session = ChatSession(project_id=payload.project_id, title='默认会话', current_step=payload.current_step)
        db.add(session); db.commit(); db.refresh(session)
    log = LLMCallLog(project_id=payload.project_id, step_key='right_chat', provider_id=provider.id, model_id=model.id, request_summary=payload.message[:500], response_summary=assistant_message[:1000], latency_ms=resp['latency_ms'], success=True)
    db.add(log); db.commit(); db.refresh(log)
    db.add(ChatMessage(session_id=session.id, project_id=payload.project_id, role='user', content=payload.message, step_key=payload.current_step))
    action_result = {"created_task": False, "task_type": "", "message": ""}
    if parsed_intent.get('should_write_memory'):
        create_rule_from_chat(db, payload.project_id, parsed_intent.get('requirement') or payload.message, parsed_intent.get('target') or 'chat_rule')
    if parsed_intent.get('should_create_task'):
        db.add(RevisionTask(project_id=payload.project_id, task=parsed_intent.get('requirement') or payload.message))
        action_result = {"created_task": True, "task_type": "rewrite", "message": "已创建返修任务草稿"}
    db.add(ChatMessage(session_id=session.id, project_id=payload.project_id, role='assistant', content=assistant_message, step_key=payload.current_step, parsed_intent_json=parsed_intent, action_result_json=action_result, llm_call_log_id=log.id))
    db.commit()
    return {"assistant_message": assistant_message, "parsed_intent": parsed_intent, "action_result": action_result, "llm_call_log_id": log.id}
