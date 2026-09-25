"""Reject stale alternate SVG even when a new PNG fallback is embedded."""
import argparse,copy,json,sys,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_figure_integration import audit,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);rows=[]
    def fixture(path,png,svg,external=False):
        xml='''<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:asvg="http://schemas.microsoft.com/office/drawing/2016/SVG/main"><w:body><w:p><w:r><w:drawing><wp:inline><wp:extent cx="5760000" cy="3600000"/><a:blip r:embed="r1"><a:extLst><a:ext><asvg:svgBlip r:embed="r2"/></a:ext></a:extLst></a:blip></wp:inline></w:drawing></w:r></w:p><w:p><w:r><w:t>Figure 1. Example.</w:t></w:r></w:p></w:body></w:document>'''
        rel='<Relationships><Relationship Id="r1" Target="media/p.png"/><Relationship Id="r2" Target="media/s.svg"'+(' TargetMode="External"' if external else '')+'/></Relationships>'
        with zipfile.ZipFile(path,'w') as z:
            for n,b in [('word/document.xml',xml.encode()),('word/_rels/document.xml.rels',rel.encode()),('word/media/p.png',png),('word/media/s.svg',svg)]:z.writestr(n,b)
    old=a.out/'old.docx';new=a.out/'new.docx';stale=a.out/'stale.docx'
    fixture(old,b'old png',b'old svg');fixture(new,b'new png',b'new svg');fixture(stale,b'new png',b'old svg')
    (a.out/'p.png').write_bytes(b'new png');(a.out/'s.svg').write_bytes(b'new svg')
    base={'scope':'all-main-document-drawings','figures':[{'id':'Figure 1','drawing_index':1,'disposition':'revised','media_sha256':sha(b'new png'),'placement_width_mm':160,'caption_exact':'Figure 1. Example.','caption_contains':'Figure 1.','source_asset':'p.png','source_asset_sha256':sha(b'new png'),'representations':[{'kind':k,'media_sha256':sha(v),'source_asset':f,'source_asset_sha256':sha(v)} for k,v,f in [('primary',b'new png','p.png'),('svg',b'new svg','s.svg')]]}]}
    def case(name,doc,mut,expected):
        spec=copy.deepcopy(base);mut(spec['figures'][0]);f=a.out/(name+'.json');f.write_text(json.dumps(spec),encoding='utf-8');r=audit(doc,f,old);rows.append({'name':name,'status':'PASS' if r['technical_status']==expected else 'FAIL','actual':r['technical_status']})
    case('both-representations-updated',new,lambda r:None,'PASS')
    case('stale-svg-with-new-png',stale,lambda r:None,'FAIL')
    case('legacy-manifest-needs-review',new,lambda r:r.pop('representations'),'REVIEW_REQUIRED')
    case('incomplete-representation-set',new,lambda r:r['representations'].pop(),'FAIL')
    case('duplicate-representation',new,lambda r:r['representations'].append(r['representations'][0]),'FAIL')
    case('missing-svg-export',new,lambda r:r['representations'][1].update(source_asset='absent.svg'),'FAIL')
    case('unbound-svg-export',new,lambda r:r['representations'][1].pop('source_asset'),'REVIEW_REQUIRED')
    bad=a.out/'external.docx';fixture(bad,b'new png',b'new svg',True)
    try:audit(bad,a.out/'both-representations-updated.json',old);ok=False
    except ValueError:ok=True
    rows.append({'name':'external-svg-refused','status':'PASS' if ok else 'FAIL'})
    result={'status':'PASS' if all(r['status']=='PASS' for r in rows) else 'FAIL','count':len(rows),'tests':rows};(a.out/'results.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result));return result['status']!='PASS'
if __name__=='__main__':raise SystemExit(main())
