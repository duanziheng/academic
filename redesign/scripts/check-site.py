"""Validate publication resources and navigation after a static build."""
from pathlib import Path
from urllib.parse import urlsplit,unquote
from html.parser import HTMLParser
import json,re,sys

ROOT=Path(__file__).resolve().parents[1]
OUT=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'netlify-dist'
data=json.loads((ROOT/'content/site.json').read_text())
class Page(HTMLParser):
    def __init__(self):super().__init__();self.ids=set();self.refs=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.add(a['id'])
        for key in ('href','src','data-cite'):
            if a.get(key):self.refs.append(a[key])
errors=[];count=0
for path in OUT.rglob('*.html'):
    page=Page();page.feed(path.read_text())
    for ref in page.refs:
        u=urlsplit(ref)
        if u.scheme in ('mailto','tel','data'):continue
        if u.netloc and u.netloc!='zihengduan.cn':continue
        target=OUT/unquote(u.path.lstrip('/')) if u.path.startswith('/') else path.parent/unquote(u.path)
        if not u.path:target=path
        if target.is_dir():target=target/'index.html'
        if not target.exists():errors.append(f'{path.relative_to(OUT)}: missing {ref}')
        elif u.fragment and target.suffix=='.html':
            doc=Page();doc.feed(target.read_text())
            if u.fragment not in doc.ids:errors.append(f'{path.relative_to(OUT)}: missing anchor {ref}')
for p in data['publications']:
    if not p['authors'] or any(a in ('Zhang Lab','et al.') for a in p['authors']):errors.append('Incomplete authors: '+p['title'])
    cites=[x for x in p['links'] if x['label']=='Cite']
    if len(cites)!=1:errors.append('Citation count: '+p['title']);continue
    f=OUT/cites[0]['url'].lstrip('/')
    if f.exists():
        text=f.read_text()
        if not re.match(r'\s*@(?:article|inproceedings|misc)\s*\{',text):errors.append('Invalid BibTeX: '+str(f))
        if not re.search(r'year\s*=\s*\{'+str(p['year'])+r'\}',text):errors.append('Citation year mismatch: '+p['title'])
        if 'Ziheng Duan' in p['authors'] and 'Ziheng' not in text:errors.append('Missing author in citation: '+p['title'])
    count+=1
cv=OUT/data['cv']['url'].lstrip('/')
if not cv.exists() or not cv.read_bytes().startswith(b'%PDF-'):errors.append('CV is not a readable PDF')
if errors:raise SystemExit('\n'.join(sorted(set(errors))))
print(f'Validated {count} publication citations, local resources, navigation anchors, and CV.')
