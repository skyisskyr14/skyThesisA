import time
import httpx
from app.llm.llm_errors import LLMRequestError

def openai_compatible_chat(base_url: str, api_key: str, model: str, messages: list[dict], temperature: float = 0.7, max_tokens: int = 1000, timeout: float = 60.0) -> dict:
    url = base_url.rstrip('/') + '/chat/completions'
    payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens}
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    t0 = time.perf_counter()
    try:
        with httpx.Client(timeout=timeout) as client:
            r = client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
    except Exception as e:
        raise LLMRequestError(str(e)) from e
    latency_ms = int((time.perf_counter() - t0) * 1000)
    return {"raw": data, "latency_ms": latency_ms}
