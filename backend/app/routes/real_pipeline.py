import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.llm.context_trimmer import trim_text
from app.llm.llm_client import openai_compatible_chat
from app.llm.llm_provider_service import get_provider_api_key
from app.llm.llm_router import resolve_step_binding
from app.models.entities import LLMCallLog, LLMModel, LLMProvider, Outline, PaperChapter, ThesisProject

router = APIRouter(prefix="/api/thesis", tags=["real-pipeline"])

def _call_step_model(db: Session, project_id: int, step_key: str, user_prompt: str, max_tokens_override: int | None = None):
    binding = resolve_step_binding(db, step_key)
    if not binding:
        raise HTTPException(400, f"未配置步骤模型: {step_key}")
    provider = db.get(LLMProvider, binding.provider_id)
    model = db.get(LLMModel, binding.model_id)
    api_key = get_provider_api_key(provider)
    if not api_key:
        raise HTTPException(400, "尚未配置 DeepSeek 密钥，请在后端环境变量设置 DEEPSEEK_API_KEY")
    messages = [{"role": "system", "content": "返回严格 JSON。"}, {"role": "user", "content": trim_text(user_prompt)}]
    r = openai_compatible_chat(provider.base_url, api_key, model.model_name, messages, binding.temperature, max_tokens_override or binding.max_tokens)
    raw = r['raw']
    text = raw.get('choices', [{}])[0].get('message', {}).get('content', '')
    usage = raw.get('usage', {})
    log = LLMCallLog(project_id=project_id, step_key=step_key, provider_id=provider.id, model_id=model.id, request_summary=user_prompt[:500], response_summary=text[:1000], prompt_tokens=usage.get('prompt_tokens', 0), completion_tokens=usage.get('completion_tokens', 0), total_tokens=usage.get('total_tokens', 0), latency_ms=r['latency_ms'], success=True, user_triggered=True)
    db.add(log); db.commit(); db.refresh(log)
    return text, log

@router.post('/outline/generate-real')
def generate_real_outline(payload: dict, db: Session = Depends(get_db)):
    project_id = int(payload.get('project_id', 0))
    p = db.get(ThesisProject, project_id)
    if not p: raise HTTPException(404, '项目不存在')
    prompt = f"项目:{p.title};作者:{p.author};请输出论文大纲JSON，字段:title,chapters,figure_plan,table_plan,warnings。"
    text, log = _call_step_model(db, project_id, 'outline_generation', prompt)
    try:
        data = json.loads(text)
    except Exception:
        raise HTTPException(400, '大纲JSON解析失败，请重试')
    db.add(Outline(project_id=project_id, title=data.get('title') or p.title, items=data.get('chapters', []))); db.commit()
    return {'success': True, 'outline': data, 'llm_call_log_id': log.id, 'tokens': log.total_tokens, 'model_id': log.model_id}

@router.post('/chapters/generate-real')
def generate_real_chapter(payload: dict, db: Session = Depends(get_db)):
    project_id = int(payload.get('project_id', 0)); chapter_no = int(payload.get('chapter_no', 1))
    p = db.get(ThesisProject, project_id)
    if not p: raise HTTPException(404, '项目不存在')
    prompt = f"项目:{p.title};生成第{chapter_no}章结构化JSON: title,sections[].{ '{' }title,blocks[]{ '{' }block_type,text{'}'}{'}'}"
    text, log = _call_step_model(db, project_id, 'chapter_writing', prompt)
    try: data = json.loads(text)
    except Exception: raise HTTPException(400, '章节JSON解析失败，请重试')
    content = '\n'.join([b.get('text','') for s in data.get('sections',[]) for b in s.get('blocks',[]) if b.get('block_type')=='paragraph'])
    db.add(PaperChapter(project_id=project_id, chapter_no=chapter_no, title=data.get('title', f'第{chapter_no}章'), content=content, blocks=data.get('sections', []))); db.commit()
    return {'success': True, 'chapter': data, 'llm_call_log_id': log.id, 'tokens': log.total_tokens, 'model_id': log.model_id}
