from app.llm.llm_client import openai_compatible_chat

def test_provider(base_url: str, api_key: str, model: str) -> dict:
    result = openai_compatible_chat(base_url, api_key, model, [{"role": "user", "content": "Reply only: OK"}], temperature=0, max_tokens=4)
    raw = result["raw"]
    content = raw.get("choices", [{}])[0].get("message", {}).get("content", "")
    usage = raw.get('usage', {})
    return {"success": True, "message": "模型连接成功", "model_response": content, "latency_ms": result["latency_ms"], "prompt_tokens": usage.get('prompt_tokens',0), "completion_tokens": usage.get('completion_tokens',0), "total_tokens": usage.get('total_tokens',0)}
