import os
from sqlalchemy.orm import Session
from app.models.entities import LLMModel, LLMProvider, LLMStepBinding

DEFAULT_STEPS = [
    ("right_chat", "右侧真实对话", 0.3, 800, True),
    ("outline_generation", "论文大纲生成", 0.3, 2000, True),
    ("chapter_writing", "章节写作", 0.35, 5000, True),
    ("academic_polish", "学术润色", 0.25, 3500, True),
    ("teacher_comment_analysis", "老师批注意图分析", 0.1, 1200, True),
    ("revision_task_generation", "返修文本生成", 0.2, 4000, True),
    ("memory_guard_reasoning", "记忆纠错推理", 0.1, 1000, True),
    ("final_review", "语义终审", 0.1, 3000, False),
]

def ensure_default_deepseek(db: Session) -> None:
    provider = db.query(LLMProvider).filter(LLMProvider.provider_name == "DeepSeek Default").first()
    if not provider:
        provider = LLMProvider(provider_name="DeepSeek Default", provider_type="deepseek", base_url="https://api.deepseek.com", api_key_encrypted="", api_key_masked="", default_model="deepseek-v4-flash", api_key_source="environment_variable", api_key_env_name="DEEPSEEK_API_KEY", is_active=True)
        db.add(provider); db.commit(); db.refresh(provider)
    model = db.query(LLMModel).filter(LLMModel.provider_id == provider.id, LLMModel.model_name == provider.default_model).first()
    if not model:
        model = LLMModel(provider_id=provider.id, model_name=provider.default_model, display_name="DeepSeek Flash", max_output_tokens=5000)
        db.add(model); db.commit(); db.refresh(model)
    for k,n,t,m,e in DEFAULT_STEPS:
        b = db.query(LLMStepBinding).filter(LLMStepBinding.step_key == k).first()
        if not b:
            db.add(LLMStepBinding(step_key=k, step_name=n, provider_id=provider.id, model_id=model.id, temperature=t, max_tokens=m, enabled=e))
    db.commit()
