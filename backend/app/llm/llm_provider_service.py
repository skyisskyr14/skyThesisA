import os
from sqlalchemy.orm import Session
from app.models.entities import LLMProvider, LLMModel, LLMStepBinding
from app.llm.llm_security import decrypt_api_key, encrypt_api_key, mask_api_key

def create_provider(db: Session, payload):
    source = payload.credential_source
    cipher = ""
    masked = "环境变量托管" if source == "environment_variable" else ""
    last4 = ""
    status = "missing"
    if source == "environment_variable":
        status = "available" if os.getenv(payload.credential_env_name or "", "") else "missing"
    else:
        if not payload.api_key:
            raise ValueError("encrypted_database 需要 api_key")
        cipher = encrypt_api_key(payload.api_key)
        masked = mask_api_key(payload.api_key)
        last4 = payload.api_key[-4:]
        status = "available"
    item = LLMProvider(provider_name=payload.provider_name, provider_type=payload.provider_type, base_url=payload.base_url, default_model=payload.default_model, is_active=payload.is_active, credential_source=source, credential_env_name=payload.credential_env_name or "", api_key_ciphertext=cipher, api_key_masked=masked, api_key_last_four=last4, credential_status=status)
    db.add(item); db.commit(); db.refresh(item); return item

def update_provider(db: Session, provider, payload):
    provider.provider_name = payload.provider_name
    provider.provider_type = payload.provider_type
    provider.base_url = payload.base_url
    provider.default_model = payload.default_model
    provider.is_active = payload.is_active
    provider.credential_source = payload.credential_source
    provider.credential_env_name = payload.credential_env_name or ""
    if payload.credential_source == 'environment_variable':
        provider.api_key_ciphertext = ''
        provider.api_key_masked = '环境变量托管'
        provider.api_key_last_four = ''
        provider.credential_status = 'available' if os.getenv(provider.credential_env_name or '', '') else 'missing'
    elif payload.api_key:
        provider.api_key_ciphertext = encrypt_api_key(payload.api_key)
        provider.api_key_masked = mask_api_key(payload.api_key)
        provider.api_key_last_four = payload.api_key[-4:]
        provider.credential_status = 'available'
    db.commit(); db.refresh(provider); return provider

def create_model(db: Session, payload):
    m = LLMModel(**payload.model_dump()); db.add(m); db.commit(); db.refresh(m); return m

def create_binding(db: Session, payload):
    b = LLMStepBinding(**payload.model_dump()); db.add(b); db.commit(); db.refresh(b); return b

def get_provider_api_key(provider: LLMProvider) -> str:
    if provider.credential_source == "environment_variable":
        return os.getenv(provider.credential_env_name, "")
    return decrypt_api_key(provider.api_key_ciphertext)
