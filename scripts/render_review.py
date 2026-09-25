"""Adapter to an explicitly located documents renderer; does not perform visual review."""
import argparse,hashlib,importlib.util,json,os
from pathlib import Path

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('source',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--documents-skill',type=Path,required=True);p.add_argument('--soffice',type=Path,required=True)
    p.add_argument('--poppler-dir',type=Path);p.add_argument('--dpi',type=int,default=150)
    a=p.parse_args();script=a.documents_skill/'render_docx.py'
    if not a.source.is_file() or not script.is_file() or not a.soffice.is_file():p.error('Source, renderer and soffice must be existing files')
    if a.output.exists():p.error('Render output directory must be new')
    if a.poppler_dir:
        if not a.poppler_dir.is_dir():p.error('Poppler directory missing')
        os.environ['PATH']=str(a.poppler_dir.resolve())+os.pathsep+os.environ.get('PATH','')
    spec=importlib.util.spec_from_file_location('pef_documents_renderer',script);renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer)
    if not callable(getattr(renderer,'rasterize',None)) or not hasattr(renderer,'_resolve_soffice'):
        p.error('Renderer API differs: use its documented CLI and record the actual invocation')
    renderer._resolve_soffice=lambda:str(a.soffice.resolve())
    pages=renderer.rasterize(str(a.source.resolve()),str(a.output.resolve()),a.dpi,False,True)
    digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
    result={'source':str(a.source.resolve()),'source_sha256':digest(a.source),'renderer':str(script.resolve()),
      'renderer_sha256':digest(script),'soffice':str(a.soffice.resolve()),'pages':len(pages),'dpi':a.dpi,
      'artifacts':{f.name:digest(f) for f in a.output.iterdir() if f.suffix.lower() in ('.png','.pdf')},
      'render_status':'PASS','visual_review':'NOT_RUN','author_acceptance':False}
    (a.output/'render-record.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'render_status':'PASS','pages':len(pages),'output':str(a.output),'visual_review':'NOT_RUN'},ensure_ascii=False))
if __name__=='__main__':main()
