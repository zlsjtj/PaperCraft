"""Bind exports using PaperCraft's actual adapter, then audit the exact documents."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,subprocess,sys,os
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
 p=argparse.ArgumentParser();p.add_argument('--paper-skill',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--text-dir',type=Path,required=True);p.add_argument('--figure-dir',type=Path,required=True);p.add_argument('--caption',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 a.out.mkdir(parents=True,exist_ok=False)
 spec=importlib.util.spec_from_file_location('audit_figures',a.paper_skill/'scripts/audit_figure_integration.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 asset=(a.figure_dir/'figure.png').resolve(); asset_rel=Path(os.path.relpath(asset,a.out.resolve())).as_posix()
 for label in ['clean','review']:
  source=a.text_dir/(label+'.docx'); inv=mod.inspect(source);save(a.out/(label+'-source-inventory.json'),inv)
  reps=[{'kind':r['kind'],'part':r['part'],'old_media_sha256':r['sha256'],'source_asset':asset_rel,'source_asset_sha256':sha(asset)} for r in inv['drawings'][0]['representations']]
  manifest=a.out/(label+'-replacements.json');save(manifest,{'source_sha256':sha(source),'replacements':[{'drawing_index':1,'representations':reps}]})
  final=a.out/(label+'.docx')
  subprocess.run([sys.executable,str(a.paper_skill/'scripts/apply_figure_edits.py'),str(source),str(manifest),str(final),'--receipt',str(a.out/(label+'-image-receipt.json'))],check=True)
  binding={'scope':'all-main-document-drawings','docx_sha256':sha(final),'parent_sha256':sha(a.source),'figures':[{'id':'Fig. 1','drawing_index':1,'disposition':'revised','media_sha256':sha(asset),'placement_width_mm':160,'placement_height_mm':85,'caption_contains':'Fig. 1.','caption_exact':a.caption.read_text(encoding='utf-8'),'source_asset':asset_rel,'source_asset_sha256':sha(asset)}]}
  path=a.out/(label+'-figures.json');save(path,binding)
  subprocess.run([sys.executable,str(a.paper_skill/'scripts/audit_figure_integration.py'),str(final),str(path),'--parent',str(a.source),'--out',str(a.out/(label+'-integration-audit.json'))],check=True)
  subprocess.run([sys.executable,str(a.paper_skill/'scripts/audit_preservation.py'),str(a.source),str(final),'--out',str(a.out/(label+'-preservation-audit.json'))],check=True)
if __name__=='__main__':main()
