"""Portable fixed-artifact rebuild. This is not a second natural-language trial.

python rebuild.py --input INPUT --paper-skill PAPERCRAFT --figure-skill FIGURECRAFT
                  --font Arial.ttf --pdftoppm pdftoppm --out NEW_DIRECTORY
Runs the actual generic PaperCraft text/image/report tools and FigureCraft renderer.
The source table remains the native table in source.docx; no table values are rebuilt.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ['input','paper-skill','figure-skill','font','pdftoppm','out']:p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args();o=a.out.resolve();o.mkdir(parents=True,exist_ok=False);here=Path(__file__).resolve().parent
 a.input=a.input.resolve();a.paper_skill=a.paper_skill.resolve();a.figure_skill=a.figure_skill.resolve();a.font=a.font.resolve();a.pdftoppm=a.pdftoppm.resolve()
 calls=[]
 def run(script,*args):
  cmd=[sys.executable,str(script),*[str(v) for v in args]]
  proc=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',errors='replace')
  calls.append({'command':cmd,'returncode':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr,'script_sha256':sha(script)})
  (o/'rebuild-commands.json').write_text(json.dumps(calls,indent=2,ensure_ascii=False),encoding='utf-8')
  if proc.returncode:raise RuntimeError(proc.stderr or proc.stdout)
 run(here/'author_trial.py','--input',a.input,'--out',o/'first-authored-complete')
 def text_and_figure(stage):
  authored=o/('first-authored-complete' if stage=='first' else 'final-authored')
  run(a.paper_skill/'scripts/apply_authored_edits.py','--source',a.input/'source.docx','--edits',authored/'authored-edits.json','--skill',a.paper_skill,'--out',o/(stage+'-text'))
  run(a.figure_skill/'scripts/render_figure.py',authored/'figure_spec.json','--out',o/(stage+'-figure'),'--font',a.font,'--pdftoppm',a.pdftoppm,'--qa-views')
  run(here/'integrate.py','--paper-skill',a.paper_skill,'--source',a.input/'source.docx','--text-dir',o/(stage+'-text'),'--figure-dir',o/(stage+'-figure'),'--caption',authored/'caption.txt','--out',o/('first-complete-v1' if stage=='first' else 'final-complete'))
 text_and_figure('first')
 run(a.figure_skill/'scripts/render_figure.py',o/'first-authored-complete/alternative-spec.json','--out',o/'alternative-figure','--font',a.font,'--pdftoppm',a.pdftoppm,'--qa-views')
 run(here/'self_review_and_repair.py','--first',o/'first-authored-complete','--out',o/'final-authored')
 text_and_figure('final')
 for label in ['clean','review']:
  run(here/'finish_table.py','--source',o/'final-complete'/(label+'.docx'),'--out',o/'final-delivery'/(label+'.docx'),'--receipt',o/'final-delivery'/(label+'-table-receipt.json'))
 run(here/'finish_records.py','--input',a.input,'--root',o,'--paper-skill',a.paper_skill,'--figure-skill',a.figure_skill,'--font',a.font,'--pdftoppm',a.pdftoppm)
 run(a.figure_skill/'vendor/nature-figure/audit_pdf_text.py',o/'final-figure/figure.pdf','--min-pt','8','--json')
 (o/'rebuild-note.txt').write_text('Fixed authored content regenerated using explicit CLI dependencies. Not another independent natural-language generation or new efficacy evidence. Word-to-PDF page rendering requires the host documents runtime and is separate.',encoding='utf-8')
 print(json.dumps({'out':str(o),'steps':len(calls),'status':'FIXED_ARTIFACT_REBUILD_COMPLETE'}))
if __name__=='__main__':main()
