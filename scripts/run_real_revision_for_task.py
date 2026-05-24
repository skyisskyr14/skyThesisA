import os, sys
if len(sys.argv)<3: raise SystemExit('用法: python scripts/run_real_revision_for_task.py <project_id> <task_id>')
if not os.getenv('DEEPSEEK_API_KEY'): raise SystemExit('缺少 DEEPSEEK_API_KEY')
print({'project_id': sys.argv[1], 'task_id': sys.argv[2], 'note': '请通过API触发真实返修生成与执行'})
