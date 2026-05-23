from app.llm.llm_client import openai_compatible_chat

def test_provider(base_url: str, api_key: str, model: str) -> dict:
    result = openai_compatible_chat(base_url, api_key, model, [{"role": "user", "content": "请回复 OK"}], temperature=0, max_tokens=16)
    content = result["raw"].get("choices", [{}])[0].get("message", {}).get("content", "")
    return {"success": True, "message": "模型连接成功", "model_response": content, "latency_ms": result["latency_ms"]}
