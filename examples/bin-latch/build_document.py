"""Standalone document wrapper for the bin-latch DEMO; not a general Word editor."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,re
from docx import Document

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--font',type=Path,required=True);p.add_argument('--bold-font',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parent
    spec=importlib.util.spec_from_file_location('demo_document',root.parent/'heat-story/build_document.py');b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
    a.out.mkdir(parents=True,exist_ok=False)
    text=re.sub(r'^!\[[^\]]*\]\([^\n]+\)\s*$', '',(root/'manuscript.md').read_text(encoding='utf8'),flags=re.M)
    source=a.out/'manuscript.md';source.write_text(text,encoding='utf8')
    captions=[b.plain(x) for k,x in b.blocks(text) if k=='p' and re.match(r'^Figure 1[.:]\s',b.plain(x))];assert len(captions)==1
    figures=[{'asset':str(root/'figure.png'),'width_mm':160,'caption':captions[0]}]
    for mode in ['manuscript','review']:
        file=a.out/(mode+'.docx')
        b.build(source,file,base=root/'input/draft.md',review=mode=='review',figures=figures,font=a.font,font_bold=a.bold_font,compact=True)
        doc=Document(file);matches=[p for p in doc.paragraphs if p.text.startswith('4. The stronger corner')];assert len(matches)==1
        matches[0].paragraph_format.page_break_before=True;doc.save(file)
        receipt=file.with_suffix('.build.json');data=json.loads(receipt.read_text(encoding='utf8'));data['output_sha256']=hashlib.sha256(file.read_bytes()).hexdigest();data['layout_adjustment']='Results and interpretation start together; no scientific content change.';receipt.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
if __name__=='__main__':main()
