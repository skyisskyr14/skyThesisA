import os, sys
from app.llm.llm_client import openai_compatible_chat
if __name__ == '__main__':
    model = sys.argv[1] if len(sys.argv) > 1 else 'deepseek-v4-flash'
    key = os.getenv('DEEPSEEK_API_KEY', '')
    if not key:
        raise SystemExit('缺少 DEEPSEEK_API_KEY')
    r = openai_compatible_chat('https://api.deepseek.com', key, model, [{"role":"user","content":"Reply only: OK"}], temperature=0, max_tokens=4)
    usage = r['raw'].get('usage', {})
    print({'message': r['raw'].get('choices',[{}])[0].get('message',{}).get('content',''), 'usage': usage, 'latency_ms': r['latency_ms']})
