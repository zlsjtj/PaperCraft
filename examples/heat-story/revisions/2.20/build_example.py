"""Rebuild the fixed fictional case, not a manuscript-generation quality test."""
from pathlib import Path
import argparse, json, shutil, subprocess, sys

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--figure-font',type=Path,required=True)
    p.add_argument('--figure-bold',type=Path,required=True)
    p.add_argument('--table-font',type=Path,required=True)
    p.add_argument('--table-bold',type=Path,required=True)
    p.add_argument('--pdftoppm',type=Path,required=True)
    a=p.parse_args();root=Path(__file__).resolve().parent;out=a.out.resolve()
    if out.exists():p.error('Output must be a new directory: '+str(out))
    for f in [a.figure_font,a.figure_bold,a.table_font,a.table_bold,a.pdftoppm]:
        if not f.is_file():p.error('Missing dependency: '+str(f))
    out.mkdir(parents=True)
    def run(*args):subprocess.run([sys.executable,'-B','-X','utf8',*map(str,args)],check=True)
    run(root/'build_figures.py','--input',root/'input','--out',out/'figures','--font',a.figure_font.resolve(),'--bold-font',a.figure_bold.resolve(),'--pdftoppm',a.pdftoppm.resolve(),'--revision','final')
    for n in ['manuscript.md','baseline.md','figures.json']:shutil.copy2(root/n,out/n)
    for n,extra in [('manuscript.docx',[]),('review.docx',['--review'])]:
        run(root/'build_document.py',out/'manuscript.md',out/n,'--baseline',out/'baseline.md','--figures',out/'figures.json','--font',a.table_font.resolve(),'--font-bold',a.table_bold.resolve(),*extra)
    (out/'README.txt').write_text('DEMO FICTION. No experiment was run. These files rebuild a fixed, feedback-refined example. Render both Word files with the documents skill and inspect every page; a successful build is not visual approval.\n',encoding='utf8')
    print(json.dumps({'out':str(out),'fixed_source_rebuild':'complete','word_pdf_render':'not performed by this command','new_material_generation':'not tested by this command'}))

if __name__=='__main__':main()
