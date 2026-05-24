import os, sys
import requests
if len(sys.argv) < 2: raise SystemExit('用法: python scripts/verify_encrypted_provider.py <api_key>')
api_key = sys.argv[1]
payload={"provider_name":"TempEncrypted","provider_type":"deepseek","base_url":"https://api.deepseek.com","credential_source":"encrypted_database","credential_env_name":"","api_key":api_key,"default_model":"deepseek-v4-flash","is_active":True}
r=requests.post('http://127.0.0.1:8000/api/thesis/llm/providers',json=payload,timeout=30); data=r.json(); pid=data['id']
print({'provider_id':pid,'masked':data.get('api_key_masked','')})
tr=requests.post(f'http://127.0.0.1:8000/api/thesis/llm/providers/{pid}/test',timeout=60)
print({'test':tr.json()})
requests.delete(f'http://127.0.0.1:8000/api/thesis/llm/providers/{pid}',timeout=30)
