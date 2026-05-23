from sqlalchemy.orm import Session
from app.models.entities import LLMProvider, LLMModel, LLMStepBinding
from app.llm.llm_security import decrypt_api_key, encrypt_api_key, mask_api_key

def create_provider(db: Session, payload):
    item = LLMProvider(provider_name=payload.provider_name, provider_type=payload.provider_type, base_url=payload.base_url, api_key_encrypted=encrypt_api_key(payload.api_key), api_key_masked=mask_api_key(payload.api_key), default_model=payload.default_model, is_active=payload.is_active)
    db.add(item); db.commit(); db.refresh(item); return item

def update_provider(db: Session, provider, payload):
    provider.provider_name = payload.provider_name
    provider.provider_type = payload.provider_type
    provider.base_url = payload.base_url
    if payload.api_key:
        provider.api_key_encrypted = encrypt_api_key(payload.api_key)
        provider.api_key_masked = mask_api_key(payload.api_key)
    provider.default_model = payload.default_model
    provider.is_active = payload.is_active
    db.commit(); db.refresh(provider); return provider

def create_model(db: Session, payload):
    m = LLMModel(**payload.model_dump())
    db.add(m); db.commit(); db.refresh(m); return m

def create_binding(db: Session, payload):
    b = LLMStepBinding(**payload.model_dump())
    db.add(b); db.commit(); db.refresh(b); return b

def get_provider_api_key(provider: LLMProvider) -> str:
    return decrypt_api_key(provider.api_key_encrypted)
