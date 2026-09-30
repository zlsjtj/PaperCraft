"""Bind untouched CSV rows and figure to trial text using shared typography.
This is a DEMO authoring workflow, not a generic editor for complex Word files.
"""
from pathlib import Path
import argparse,csv,json,re,importlib.util,hashlib
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

def load(path):
    spec=importlib.util.spec_from_file_location('doc_builder',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def linked_inline(p,s,yellow=False):
    for token in re.split(r'(\[[^\]]+\]\(https?://[^)]+\)|\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)',s):
        if not token:continue
        link=re.fullmatch(r'\[([^\]]+)\]\((https?://[^)]+)\)',token)
        if link:
            h=OxmlElement('w:hyperlink');h.set(qn('r:id'),p.part.relate_to(link[2],RT.HYPERLINK,is_external=True));r=OxmlElement('w:r');pr=OxmlElement('w:rPr')
            color=OxmlElement('w:color');color.set(qn('w:val'),'1F4E79');pr.append(color)
            if yellow:
                hi=OxmlElement('w:highlight');hi.set(qn('w:val'),'yellow');pr.append(hi)
            r.append(pr);t=OxmlElement('w:t');t.text=link[1];r.append(t);h.append(r);p._p.append(h)
        else:
            r=p.add_run(token.strip('*`') if token.startswith(('*','`')) else token)
            r.bold=token.startswith('**');r.italic=token.startswith('*') and not token.startswith('**')
            if yellow:
                hi=OxmlElement('w:highlight');hi.set(qn('w:val'),'yellow');r._element.get_or_add_rPr().append(hi)

def table(rows):
    keys=['workload','policy','hit_ratio_pct','origin_mib','budget_bypasses','mean_examinations','max_examinations_one_request']
    heads=['Scenario','Policy','Hits (%)','Fetched (MiB)','Bypasses','Mean exams','Max exams']
    return '\n'.join(['| '+' | '.join(heads)+' |','| '+' | '.join(['---']*7)+' |']+['| '+' | '.join(row[k] for k in keys)+' |' for row in rows])

def prepare(text,rows):
    text=re.sub(r'<!-- CSV_(?:TABLE_)?BINDING.*?-->',lambda m:table(rows),text,flags=re.S)
    return text

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--paper-skill',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--font',type=Path,required=True);p.add_argument('--bold-font',type=Path,required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False);m=load(a.paper_skill/'examples/heat-story/build_document.py');m.inline=linked_inline
    rows=list(csv.DictReader((a.root/'material-paper/fixed_results.csv').open(encoding='utf-8')))
    source_new=a.root/'paper-new/delivery.md'
    if not source_new.exists():raise FileNotFoundError('Wait for the reviewed delivery text')
    originals={'before':a.root/'paper-old/final.md','clean':source_new}
    caption='Figure 1. Allocation of the reference-examination allowance. Bar length represents the specified maximum, not elapsed time or observed work. The reserve variants use separate limits of 48 foreground and 16 maintenance examinations; maintenance seeks a soft free-space target and may stop earlier or leave it unmet.'
    fig=a.root/'cache-figure/figure.png'
    for name,path in originals.items():
        t=prepare(path.read_text(encoding='utf-8'),rows)
        # Insert one common explanatory diagram after the opening section, to
        # avoid giving one trial a figure unavailable to the other.
        t=t.replace('## 2.',caption+'\n\n## 2.',1)
        (a.out/(name+'.md')).write_text(t,encoding='utf-8')
    for name,src,review in [('before','before',False),('clean','clean',False),('review','clean',True)]:
        m.build(a.out/(src+'.md'),a.out/(name+'.docx'),base=a.out/'before.md',review=review,figures=[dict(caption=caption,asset=str(fig),width_mm=160)],font=a.font,font_bold=a.bold_font)
        d=Document(a.out/(name+'.docx'))
        # Use natural pagination with the builder's repeated table header and
        # intact five-row scenario groups. A whole-table page reservation had
        # left a short definitions page unnecessarily empty in the first build.
        d.save(a.out/(name+'.docx'))
        receipt_path=a.out/(name+'.build.json')
        receipt=json.loads(receipt_path.read_text(encoding='utf-8'))
        receipt['output_sha256']=hashlib.sha256((a.out/(name+'.docx')).read_bytes()).hexdigest()
        receipt['postprocessing']='Shared natural pagination with repeated headers and intact scenario groups; native hyperlinks preserved'
        receipt_path.write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    record={'inputs':{str(x.relative_to(a.root)):hashlib.sha256(x.read_bytes()).hexdigest() for x in [source_new,originals['before'],a.root/'material-paper/fixed_results.csv',fig]},'shared_figure':str(fig),'yellow':'new or rewritten paragraphs relative to baseline skill output; not Word native revisions','table_rows':len(rows)}
    (a.out/'binding.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
if __name__=='__main__':main()
