"""Audit the exact assembled DEMO documents; does not judge writing or art."""
from pathlib import Path
from zipfile import ZipFile
import argparse, hashlib, json, re
from lxml import etree as E
from assemble_demo import blocks, plain

NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'm':'http://schemas.openxmlformats.org/officeDocument/2006/math',
    'wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
def sha(b):return hashlib.sha256(b).hexdigest()
def math_text(node):
    tag=E.QName(node).localname
    if tag=='t':return node.text or ''
    if tag in ('sSub','sSup','sSubSup'):
        values={E.QName(c).localname:math_text(c) for c in node}
        s=values['e']
        if 'sub' in values:s+='_{'+values['sub']+'}'
        if 'sup' in values:s+='^{'+values['sup']+'}'
        return s
    return ''.join(map(math_text,node))
def norm(s):return re.sub(r'\s+','',s).rstrip('.')
def main():
    p=argparse.ArgumentParser();p.add_argument('--dir',type=Path,required=True);p.add_argument('--manuscript',type=Path,required=True);p.add_argument('--kind',choices=['development','transfer'],default='development');a=p.parse_args()
    receipt=json.loads((a.dir/'assembly.json').read_text('utf8'))
    md=a.manuscript.read_text('utf8'); expected_tables=[v for k,v in blocks(md) if k=='table']
    roots={}; records={}
    for mode in ['clean','review']:
        path=a.dir/f'manuscript_{mode}.docx'
        with ZipFile(path) as z:
            root=E.fromstring(z.read('word/document.xml'));roots[mode]=root
            image_hashes=sorted(sha(z.read(n)) for n in z.namelist() if n.startswith('word/media/'))
        assert image_hashes==sorted(receipt['figure_sha256'].values()),'Embedded figures differ'
        tables=[]
        for table in root.xpath('//w:tbl',namespaces=NS):
            tables.append([[ ''.join(c.xpath('.//w:t/text()',namespaces=NS)) for c in row.xpath('./w:tc',namespaces=NS)] for row in table.xpath('./w:tr',namespaces=NS)])
        assert tables==[[list(map(plain,row)) for row in t] for t in expected_tables], 'Table content changed during assembly'
        widths=[int(n.get('cx')) for n in root.xpath('//wp:extent',namespaces=NS)]
        assert all(abs(w/36000-160)<.001 for w in widths)
        text='\n'.join(root.xpath('//w:t/text()',namespaces=NS))
        assert '[FIGURE_' not in text and '[TABLE_' not in text
        assert 'DEMO' in text
        math=[norm(math_text(n)) for n in root.xpath('//m:oMath',namespaces=NS)]
        # These five identities are independently transcribed from the frozen
        # apparatus source. Equality checks coefficients, operators and indices.
        expected=['b_{j}=0.004x_{j}^{2}+0.005y_{j}^{2}',
                  'p_{e}(x,y)=a_{e}x+b_{e}y+c_{e}',
                  'error_{ej}=b_{j}+d_{ej}-q_{ej}',
                  'T_{local}=L/80+0.75N+0.74R',
                  'T_{cycle}=5.0+T_{local}+8.59s']
        if a.kind=='transfer':expected=[]
        assert math==expected,{'actual':math,'expected':expected}
        records[mode]={'sha256':sha(path.read_bytes()),'image_hashes':image_hashes,
            'figure_width_mm':[w/36000 for w in widths], 'table_contents':tables,
            'math_identities':math,'math_c14n_hashes':[sha(E.tostring(n,method='c14n')) for n in root.xpath('//m:oMath',namespaces=NS)],
            'highlight_runs':len(root.xpath('//w:highlight',namespaces=NS)),
            'native_revision_objects':len(root.xpath('//w:ins|//w:del',namespaces=NS))}
    assert records['clean']['highlight_runs']==0
    assert records['review']['highlight_runs']>0
    for r in roots.values():
        for n in r.xpath('//w:highlight',namespaces=NS):n.getparent().remove(n)
    assert E.tostring(roots['clean'],method='c14n')==E.tostring(roots['review'],method='c14n'), 'Clean/review content differs beyond highlight'
    report={'status':'PASS','scope':'Exact DOCX prose equality except yellow; present source equations including indices; all table cells; image bytes and placement',
            'documents':records,'limitations':['New DEMO document, not an existing revision-history preservation trial',
             'Does not establish claim correctness or visual quality; those require separate source and page review']}
    (a.dir/'document-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'status':report['status'],'equations':len(expected),'tables':len(expected_tables),'figures':len(receipt['figure_sha256'])}))
if __name__=='__main__':main()
