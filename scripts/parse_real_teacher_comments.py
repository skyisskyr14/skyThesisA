import sys, zipfile
import xml.etree.ElementTree as ET
if len(sys.argv)<2: raise SystemExit('用法: python scripts/parse_real_teacher_comments.py <commented_docx_path>')
with zipfile.ZipFile(sys.argv[1]) as z:
    data = z.read('word/comments.xml')
root = ET.fromstring(data)
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
comments=root.findall('.//w:comment',ns)
print({'comments_count': len(comments)})
