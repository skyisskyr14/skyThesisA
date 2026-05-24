import sys,requests
if len(sys.argv)<3: raise SystemExit('用法: python scripts/import_real_paper_and_generate_docx.py <project_id> <docx_path>')
project_id=int(sys.argv[1]); path=sys.argv[2]
with open(path,'rb') as f:
    files={'file':(path.split('/')[-1],f,'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
    data={'project_id':str(project_id),'file_role':'existing_draft'}
    fr=requests.post('http://127.0.0.1:8000/api/thesis/files/upload',files=files,data=data,timeout=60).json()
ir=requests.post('http://127.0.0.1:8000/api/thesis/papers/import-docx',json={'project_id':project_id,'file_id':fr['id']},timeout=60).json()
dr=requests.post('http://127.0.0.1:8000/api/thesis/docx/generate-full',json={'project_id':project_id,'paper_version_id':ir['version_id'],'use_template_rules':True},timeout=120).json()
print({'import':ir,'docx':{'docx_path':dr.get('docx_path'),'score':dr.get('format_validation',{}).get('score')}})
