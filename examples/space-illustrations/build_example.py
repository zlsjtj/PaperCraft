"""Rebuild a chosen fictional illustration and its three document pages."""
from pathlib import Path
import argparse,json,subprocess,sys
from document_page import build

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--case',choices=['particles','strip'],required=True)
    p.add_argument('--out',type=Path,required=True)
    for name in ['font','bold-font','pdftoppm']:p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();root=Path(__file__).resolve().parent/a.case
    if a.out.exists():p.error('Use a new output directory')
    for x in [a.font,a.bold_font,a.pdftoppm]:
        if not x.is_file():p.error('Missing dependency: '+str(x))
    a.out.mkdir(parents=True)
    cmd=[sys.executable,'-B',str(root/'rebuild.py'),'--out',str(a.out/'figure'),'--font',str(a.font),'--bold-font',str(a.bold_font),'--pdftoppm',str(a.pdftoppm)]
    subprocess.run(cmd,check=True)
    text=json.loads((root/'text.json').read_text(encoding='utf8'))
    checks=[]
    for mode in ['before','clean','review']:
        old=mode=='before'
        checks.append(build(a.out/(mode+'.docx'),text['title'],text['before'] if old else text['after'],text['before_caption'] if old else text['caption'],root/'before.png' if old else a.out/'figure/figure.png',mode=='review',text['before_caption']!=text['caption']))
    (a.out/'document-audit.json').write_text(json.dumps(checks,indent=2),encoding='utf8')
    print('DOCX created; use your documents renderer to inspect exact pages before acceptance.')
if __name__=='__main__':main()
