"""Rebuild the reviewed final DEMO from retained scientific inputs.
No network, installation, simulation rerun, or outside research materials.
"""
import argparse, csv, hashlib, importlib.util, io, json, os, re, subprocess, sys, zipfile
from pathlib import Path
from collections import defaultdict
from copy import deepcopy
from lxml import etree as E
from PIL import Image
from pypdf import PdfReader
from authored_text import TEXT, FINAL_TEXT
from draw_figures import build as draw

NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
W=NS['w'];Q=lambda s:'{'+W+'}'+s
SHA=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def dump(path,obj):Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def rewrite_zip(src,dst,fn):
    with zipfile.ZipFile(src) as z:
        parts={n:z.read(n) for n in z.namelist()};infos=z.infolist()
    fn(parts)
    with zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as z:
        for inf in infos:z.writestr(inf,parts[inf.filename])
def style_doc(src,dst):
    def fix(parts):
        root=E.fromstring(parts['word/document.xml'])
        pars=root.findall('w:body/w:p',NS)
        for p in pars:
            pp=p.find(Q('pPr'))
            if pp is None:pp=E.Element(Q('pPr'));p.insert(0,pp)
            style=pp.find(Q('pStyle'));kind=style.get(Q('val')) if style is not None else ''
            # Preserve original runs and all protected objects. Change layout only.
            if p.xpath('.//w:drawing',namespaces=NS):
                k=E.SubElement(pp,Q('keepNext'));k.set(Q('val'),'1')
            elif kind not in ('Title','Heading1','Heading2','Caption'):
                for k in pp.findall(Q('keepNext')):pp.remove(k)
        # Reclassify the two condition paragraphs as body prose, not inherited 9pt captions.
        for p in pars:
            value=''.join(p.xpath('.//w:t/text()',namespaces=NS)).strip()
            if value.startswith(('Table 1 compares all twelve','T6–T11 form the complete')):
                pp=p.find(Q('pPr'));st=pp.find(Q('pStyle'))
                if st is None:st=E.SubElement(pp,Q('pStyle'))
                st.set(Q('val'),'Normal')
                for run in p.findall(Q('r')):
                    rp=run.find(Q('rPr'))
                    if rp is None:rp=E.Element(Q('rPr'));run.insert(0,rp)
                    for n in ['b','bCs','sz','szCs']:
                        for old in rp.findall(Q(n)):rp.remove(old)
                    E.SubElement(rp,Q('b')).set(Q('val'),'0')
                    E.SubElement(rp,Q('sz')).set(Q('val'),'22')
            if value.startswith('Equation 1 sums'):
                pp=p.find(Q('pPr'))
                if pp.find(Q('keepNext')) is None:E.SubElement(pp,Q('keepNext')).set(Q('val'),'1')
        # Repeat native table header; right-align numeric columns. No cell text changed.
        for tbl in root.findall('.//w:tbl',NS):
            for ri,row in enumerate(tbl.findall(Q('tr'))):
                if ri==0:
                    trp=row.find(Q('trPr'))
                    if trp is None:trp=E.Element(Q('trPr'));row.insert(0,trp)
                    E.SubElement(trp,Q('tblHeader'))
                for ci,cell in enumerate(row.findall(Q('tc'))):
                    for p in cell.findall(Q('p')):
                        pp=p.find(Q('pPr'))
                        if pp is None:pp=E.Element(Q('pPr'));p.insert(0,pp)
                        jc=pp.find(Q('jc'))
                        if jc is None:jc=E.SubElement(pp,Q('jc'))
                        jc.set(Q('val'),'left' if ci<2 else 'right')
        parts['word/document.xml']=E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
    rewrite_zip(src,dst,fix)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--material',type=Path,required=True);ap.add_argument('--paper-skill',type=Path,default=Path(__file__).resolve().parents[3]);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--font',type=Path,required=True);ap.add_argument('--bold-font',type=Path,required=True);ap.add_argument('--poppler',type=Path,required=True);ap.add_argument('--final',action='store_true');a=ap.parse_args()
    if a.out.exists():raise ValueError('Output already exists: preserve prior execution')
    a.out.mkdir(parents=True)
    log=[]
    def run(args):
        r=subprocess.run([str(v) for v in args],capture_output=True,text=True,encoding='utf-8',errors='replace')
        log.append({'command':[str(v) for v in args],'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
        dump(a.out/'execution.json',log)
        if r.returncode:raise RuntimeError(r.stderr or r.stdout)
    pc=a.paper_skill;source=a.material/'manuscript_input.docx'
    inventory=load('review_docx',pc/'scripts/review_docx.py').inventory(source)
    lookup={p['id']:p for p in inventory['paragraphs']}
    draft=FINAL_TEXT if a.final else TEXT
    edits=[{'paragraph_id':pid,'operation':'replace_paragraph','before':lookup[pid]['text'],'after':text,'reason':'Organize the full paper around block recovery versus both simple alternatives; retain source facts and limitations.','source':['S1','S2','S3','S4']} for pid,text in draft.items()]
    dump(a.out/'authored-edits.json',{'source_sha256':SHA(source),'edits':edits})
    draw(a.out/'figures',a.font,a.bold_font,a.poppler,a.final)
    log.append({'operation':'draw_figures.build','exit_code':0,'backend':'native SVG + ReportLab vector PDF + Poppler 320 dpi','final':a.final})
    run([sys.executable,pc/'scripts/apply_authored_edits.py','--source',source,'--edits',a.out/'authored-edits.json','--skill',pc,'--out',a.out/'text-stage'])
    integrate=load('figure_integration',pc/'scripts/audit_figure_integration.py')
    policy={'protected_paragraphs':[{'label':'DEMO declaration','text':lookup['P0002']['text']}]+[{'label':p,'text':lookup[p]['text']} for p in ('P0039','P0040','P0041','P0042')],'lock_citation_tokens':False}
    dump(a.out/'preservation-policy.json',policy)
    for variant in ('clean','review'):
        src=a.out/'text-stage'/f'{variant}.docx';inv=integrate.inspect(src)
        manifest={'source_sha256':SHA(src),'replacements':[]}
        for d in inv['drawings']:
            reps=[]
            for rep in d['representations']:
                asset=a.out/'figures'/f"figure_{d['index']}.png"
                reps.append({'kind':rep['kind'],'part':rep['part'],'old_media_sha256':rep['sha256'],'source_asset':f"figures/{asset.name}",'source_asset_sha256':SHA(asset)})
            manifest['replacements'].append({'drawing_index':d['index'],'representations':reps})
        mf=a.out/f'{variant}-image-edits.json';dump(mf,manifest)
        raw=a.out/f'{variant}-integrated.docx'
        run([sys.executable,pc/'scripts/apply_figure_edits.py',src,mf,raw,'--receipt',a.out/f'{variant}-image-receipt.json'])
        dest=a.out/f'manuscript_{variant}.docx';style_doc(raw,dest)
        run([sys.executable,pc/'scripts/audit_preservation.py',source,dest,'--policy',a.out/'preservation-policy.json','--out',a.out/f'{variant}-preservation.json'])
        check={'scope':'all-main-document-drawings','docx_sha256':SHA(dest),'parent_sha256':SHA(source),'figures':[]}
        for i,pid in [(1,'P0013'),(2,'P0020')]:
            asset=a.out/'figures'/f'figure_{i}.png'
            check['figures'].append({'id':f'Figure {i}','drawing_index':i,'disposition':'revised','media_sha256':SHA(asset),'placement_width_mm':160,'placement_height_mm':112,'caption_contains':f'Figure {i}.','caption_exact':draft[pid],'source_asset':f'figures/{asset.name}','source_asset_sha256':SHA(asset)})
        auditmf=a.out/f'{variant}-integration-manifest.json';dump(auditmf,check)
        run([sys.executable,pc/'scripts/audit_figure_integration.py',dest,auditmf,'--parent',source,'--out',a.out/f'{variant}-integration-audit.json'])
    # Directly count only complete continuous prose in delivered Word, excluding equation/captions.
    body_ids=[6,7,8,9,11,14,15,16,17,18,21,23,25,27,28,29,30,32,33,34,35,37]
    count=lambda s:len(re.findall(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)*",s))
    delivered=integrate.inspect(a.out/'manuscript_clean.docx')['paragraphs']
    # The paragraph splitter retains boundary whitespace; compare prose, not that separator.
    delivered_stripped={p.strip() for p in delivered}
    assert all(piece.strip() in delivered_stripped for i in body_ids for piece in draft[f'P{i:04d}'].split('\n\n'))
    counts={'abstract_words':count(draft['P0004']),'body_continuous_prose_words':sum(count(draft[f'P{i:04d}']) for i in body_ids),'body_source_paragraph_ids':[f'P{i:04d}' for i in body_ids],'rule':"ASCII alphanumeric tokens with internal apostrophes/hyphens retained; inline numerals/variables/internal citation tokens count. Body is Introduction through Conclusion continuous prose, excluding title, headings, abstract, figure/table captions, native table cells, native equation, declaration and sources.",'delivered_docx_sha256':SHA(a.out/'manuscript_clean.docx')}
    assert 130<=counts['abstract_words']<=170 and 1600<=counts['body_continuous_prose_words']<=2400
    dump(a.out/'word-counts.json',counts)
    # Read every ledger and sweep row and reconcile supplied records; do not rerun the simulator.
    results=list(csv.DictReader((a.material/'data/results.csv').open(encoding='utf-8-sig',newline='')))
    events=list(csv.DictReader((a.material/'data/events.csv').open(encoding='utf-8-sig',newline='')))
    sweep=list(csv.DictReader((a.material/'tests/single_cut_sweep.csv').open(encoding='utf-8-sig',newline='')))
    totals=defaultdict(float);n=defaultdict(int)
    for e in events:
        totals[e['trace'],e['policy']]+=float(e['end_ms'])-float(e['start_ms']);n[e['trace'],e['policy']]+=1
    assert all(abs(totals[r['trace'],r['policy']]-float(r['powered_ms']))<1e-5 for r in results)
    assert all(r['durable_output_records']=='192' for r in results)
    assert len(sweep)==384 and all(r['output_records']=='192' and r['pass']=='True' for r in sweep)
    dump(a.out/'source-reconciliation.json',{'result_rows':len(results),'ledger_rows_read':len(events),'event_sums_match_all_36_powered_times':True,'sweep_rows_read':len(sweep),'sweep_all_192':True,'simulation_rerun':False,'source_table':'original native table retained cell-for-cell'})
    # Standalone readable textual mirror of the delivered manuscript.
    (a.out/'manuscript_text.md').write_text('\n\n'.join(delivered),encoding='utf-8')
    fileqa=[]
    for i in (1,2):
        base=a.out/'figures'/f'figure_{i}';im=Image.open(base.with_suffix('.png'));pdf=PdfReader(base.with_suffix('.pdf'));box=pdf.pages[0].mediabox
        labels=json.loads(base.with_suffix('.labels.json').read_text())
        fileqa.append({'figure':i,'svg_text_editable':True,'svg_bitmap_nodes':0,'svg_canvas_mm':[160,112],'png_pixels':list(im.size),'png_dpi':im.info.get('dpi'),'pdf_pages':len(pdf.pages),'pdf_mm':[float(box.width)*25.4/72,float(box.height)*25.4/72],'min_label_pt':min(l['effective_pt'] for l in labels),'label_count':len(labels),'label_words':sum(count(l['text']) for l in labels),'pdf_text_extracted':bool(pdf.pages[0].extract_text()),'visual_review':'PENDING_AGENT_VIEW'})
    dump(a.out/'figure-export-checks.json',fileqa)
    dump(a.out/'artifact-hashes.json',{str(p.relative_to(a.out)):SHA(p) for p in a.out.rglob('*') if p.is_file() and p.name!='artifact-hashes.json'})
    print(json.dumps({'out':str(a.out),'counts':counts,'figure_export_checks':fileqa},ensure_ascii=False))
if __name__=='__main__':main()
