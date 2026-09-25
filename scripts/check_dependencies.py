"""Check actual files/imports; no installation, networking or manuscript mutation."""
import argparse,importlib.util,json,re,shutil,sys
from pathlib import Path

def check(root,documents=None,soffice=None,require=None):
    root=Path(root).resolve();missing=[];links=0
    for p in root.rglob('*.md'):
        content=re.sub(r'```.*?```','',p.read_text(encoding='utf-8'),flags=re.S)
        for target in re.findall(r'\]\(([^)]+)\)',content):
            target=target.strip('<>').split('#')[0]
            if not target or re.match(r'^[a-zA-Z]+:',target):continue
            links+=1
            if not (p.parent/target).exists():missing.append({'source':str(p.relative_to(root)),'target':target})
    modules={n:importlib.util.find_spec(n) is not None for n in ['lxml','docx','yaml','PIL','pypdf']}
    doc=Path(documents).resolve() if documents else None
    renderer=doc/'render_docx.py' if doc else None
    office=soffice or shutil.which('soffice')
    ready={'docx':modules['lxml'] and modules['docx'],
           'preservation':modules['lxml'],
           'official':modules['yaml'],
           'render':bool(doc and (doc/'SKILL.md').is_file() and renderer.is_file() and office and Path(office).is_file() and modules['PIL'])}
    requested=list(require or [])
    if set(requested)-set(ready):raise ValueError('Unknown required capability')
    missing_required=[name for name in requested if not ready[name]]
    return {'python':sys.executable,'python_version':sys.version.split()[0],
      'skill_root':str(root),'entrypoint_present':(root/'SKILL.md').is_file(),
      'local_links_checked':links,'missing_local_links':missing,'modules':modules,
      'documents_skill_present':bool(doc and (doc/'SKILL.md').is_file()),
      'render_docx_present':bool(renderer and renderer.is_file()),
      'render_docx_path':str(renderer) if renderer else None,
      'soffice':office,'soffice_file_present':bool(office and Path(office).is_file()),
      'capability_dependencies':{k:'FILES_AND_IMPORTS_PRESENT' if v else 'MISSING' for k,v in ready.items()},
      'required_capabilities':requested,'missing_required_capabilities':missing_required,
      'status':'FAIL' if missing or missing_required or not (root/'SKILL.md').is_file() else 'PASS',
      'render_execution':'NOT_RUN','semantic_validation':'NOT_RUN',
      'limits':'Presence/import checks only; render capability must still execute with its real PDF backend.'}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('root');p.add_argument('--documents-skill');p.add_argument('--soffice');p.add_argument('--out')
    p.add_argument('--require',action='append',choices=['docx','preservation','official','render'],default=[],help='Fail if this capability lacks a dependency; repeat for several capabilities')
    a=p.parse_args();r=check(a.root,a.documents_skill,a.soffice,a.require);t=json.dumps(r,ensure_ascii=False,indent=2)
    if a.out:Path(a.out).write_text(t,encoding='utf-8')
    print(t)
    if r['status']=='FAIL':raise SystemExit(1)
if __name__=='__main__':main()
