from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.llm.llm_provider_service import create_binding, create_model, create_provider, get_provider_api_key, update_provider
from app.llm.llm_test_service import test_provider
from app.models.entities import LLMCallLog, LLMModel, LLMProvider, LLMStepBinding
from app.schemas.common import LLMModelCreate, LLMModelRead, LLMProviderCreate, LLMProviderRead, LLMStepBindingCreate, LLMStepBindingRead

router = APIRouter(prefix="/api/thesis/llm", tags=["llm"])

@router.post('/providers', response_model=LLMProviderRead)
def add_provider(payload: LLMProviderCreate, db: Session = Depends(get_db)):
    try: return create_provider(db, payload)
    except Exception as e: raise HTTPException(400, str(e))

@router.get('/providers', response_model=list[LLMProviderRead])
def list_providers(db: Session = Depends(get_db)):
    return db.query(LLMProvider).all()

@router.put('/providers/{provider_id}', response_model=LLMProviderRead)
def edit_provider(provider_id: int, payload: LLMProviderCreate, db: Session = Depends(get_db)):
    provider = db.get(LLMProvider, provider_id)
    if not provider: raise HTTPException(404, 'provider not found')
    return update_provider(db, provider, payload)

@router.delete('/providers/{provider_id}')
def disable_provider(provider_id: int, db: Session = Depends(get_db)):
    provider = db.get(LLMProvider, provider_id)
    if not provider: raise HTTPException(404, 'provider not found')
    provider.is_active = False; db.commit(); return {'ok': True}

@router.post('/providers/{provider_id}/test')
def run_test(provider_id: int, db: Session = Depends(get_db)):
    provider = db.get(LLMProvider, provider_id)
    if not provider: raise HTTPException(404, 'provider not found')
    if not provider.default_model: raise HTTPException(400, 'default_model 未配置')
    return test_provider(provider.base_url, get_provider_api_key(provider), provider.default_model)

@router.post('/models', response_model=LLMModelRead)
def add_model(payload: LLMModelCreate, db: Session = Depends(get_db)):
    return create_model(db, payload)

@router.get('/models', response_model=list[LLMModelRead])
def list_models(db: Session = Depends(get_db)):
    return db.query(LLMModel).all()

@router.post('/step-bindings', response_model=LLMStepBindingRead)
def add_binding(payload: LLMStepBindingCreate, db: Session = Depends(get_db)):
    return create_binding(db, payload)

@router.get('/step-bindings', response_model=list[LLMStepBindingRead])
def list_bindings(db: Session = Depends(get_db)):
    return db.query(LLMStepBinding).all()

@router.put('/step-bindings/{binding_id}', response_model=LLMStepBindingRead)
def edit_binding(binding_id: int, payload: LLMStepBindingCreate, db: Session = Depends(get_db)):
    b = db.get(LLMStepBinding, binding_id)
    if not b: raise HTTPException(404, 'binding not found')
    for k, v in payload.model_dump().items(): setattr(b, k, v)
    db.commit(); db.refresh(b); return b

@router.get('/call-logs')
def list_logs(db: Session = Depends(get_db)):
    return db.query(LLMCallLog).order_by(LLMCallLog.created_at.desc()).limit(200).all()

@router.get('/usage/{project_id}')
def usage(project_id: int, db: Session = Depends(get_db)):
    rows = db.query(LLMCallLog).filter(LLMCallLog.project_id == project_id).all()
    return {
        'project_id': project_id,
        'total_calls': len(rows),
        'successful_calls': len([r for r in rows if r.success]),
        'failed_calls': len([r for r in rows if not r.success]),
        'prompt_tokens': sum(r.prompt_tokens for r in rows),
        'completion_tokens': sum(r.completion_tokens for r in rows),
        'total_tokens': sum(r.total_tokens for r in rows),
        'by_step': [],
        'by_model': []
    }
