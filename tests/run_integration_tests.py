"""Negative fixtures for actually embedded assets; no claim of visual validity."""
from pathlib import Path
import argparse, copy, hashlib, importlib.util, json, subprocess, sys, zipfile

ROOT=Path(__file__).resolve().parents[1]
module=importlib.util.spec_from_file_location('integration',ROOT/'scripts/audit_figure_integration.py')
I=importlib.util.module_from_spec(module);module.loader.exec_module(I)
def sha(b):return hashlib.sha256(b).hexdigest()
def fixture(path, images, width=160, caption='Figure 1. Trace.', vml=False, external=False, drawings=True):
    ns=' '.join(f'xmlns:{k}="{v}"' for k,v in I.NS.items())
    drawing=f'<w:p><w:r><w:drawing><wp:inline><wp:extent cx="{int(width*36000)}" cy="3600000"/><a:blip r:embed="rId1"/></wp:inline></w:drawing></w:r></w:p>'
    xml=f'<w:document {ns}><w:body>{drawing if drawings else ""}<w:p><w:r><w:t>{caption}</w:t></w:r></w:p>'+('<w:p><v:imagedata/></w:p>' if vml else '')+'</w:body></w:document>'
    rel='<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="media/image.png"'+(' TargetMode="External"' if external else '')+'/></Relationships>'
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('word/document.xml',xml);z.writestr('word/_rels/document.xml.rels',rel);z.writestr('word/media/image.png',images)

def run(out):
    out.mkdir(parents=True,exist_ok=False);results=[]
    old=out/'old.docx';new=out/'new.docx';asset=out/'new.png'
    # Fake bytes exercise package identity, not image rendering; explicitly named here.
    fixture(old,b'old test bytes');fixture(new,b'new test bytes');asset.write_bytes(b'new test bytes')
    base={'scope':'all-main-document-drawings','figures':[{'id':'Figure 1','drawing_index':1,'disposition':'revised','media_sha256':sha(asset.read_bytes()),'placement_width_mm':160,'caption_contains':'Figure 1.','source_asset':'new.png','source_asset_sha256':sha(asset.read_bytes())}]}
    counter=0
    def audit(spec=None,doc=new,parent=old):
        nonlocal counter
        counter+=1;p=out/f'manifest-{counter}.json';p.write_text(json.dumps(spec or base),encoding='utf-8')
        return I.audit(doc,p,parent)
    def case(name,fn):
        try:fn();results.append({'case':name,'status':'PASS'})
        except Exception as e:results.append({'case':name,'status':'FAIL','detail':repr(e)})
    def expect(status,**kw):assert audit(**kw)['technical_status']==status
    def mutate(key,value):s=copy.deepcopy(base);s['figures'][0][key]=value;return s
    case('new_asset_really_embedded',lambda:expect('PASS'))
    case('standalone_export_but_old_word_detected',lambda:expect('FAIL',doc=old))
    case('wrong_expected_figure_bytes_detected',lambda:expect('FAIL',spec=mutate('media_sha256',sha(b'wrong'))))
    case('shrunk_placement_detected',lambda:expect('FAIL',spec=mutate('placement_width_mm',80)))
    case('wrong_drawing_index_detected',lambda:expect('FAIL',spec=mutate('drawing_index',2)))
    case('missing_caption_detected',lambda:expect('FAIL',spec=mutate('caption_contains','Figure 9.')))
    case('exact_caption_detects_lost_run_space',lambda:expect('FAIL',spec=mutate('caption_exact','Figure 1.Trace.')))
    case('matching_exact_caption_passes',lambda:expect('PASS',spec=mutate('caption_exact','Figure 1. Trace.')))
    case('unintended_change_to_preserved_figure_detected',lambda:expect('FAIL',spec=mutate('disposition','preserved')))
    case('missing_source_export_detected',lambda:expect('FAIL',spec=mutate('source_asset','absent.png')))
    def missing():s=copy.deepcopy(base);s['figures']=[];expect('FAIL',spec=s)
    case('incomplete_inventory_detected',missing)
    def duplicate():s=copy.deepcopy(base);s['figures']*=2;expect('FAIL',spec=s)
    case('duplicate_inventory_detected',duplicate)
    def wrongrevision():s=copy.deepcopy(base);s['docx_sha256']='0'*64;expect('FAIL',spec=s)
    case('stale_docx_manifest_detected',wrongrevision)
    def vml():p=out/'vml.docx';fixture(p,b'new test bytes',vml=True);expect('REVIEW_REQUIRED',doc=p)
    case('unsupported_vml_never_silent_pass',vml)
    def external():
        p=out/'external.docx';fixture(p,b'new test bytes',external=True)
        try:audit(doc=p)
        except ValueError:return
        raise AssertionError('External image accepted')
    case('external_image_rejected',external)
    def preserved():s=mutate('disposition','preserved');expect('PASS',spec=s,parent=new)
    case('genuine_preserved_image_passes',preserved)
    def decorative():s=mutate('kind','decorative');s['figures'][0]['reason']='Explicit logo fixture';s['figures'][0].pop('caption_contains');expect('PASS',spec=s)
    case('explicit_decorative_item_supported',decorative)
    def empty():
        p=out/'no-images.docx';fixture(p,b'not referenced',drawings=False)
        s={'scope':'all-main-document-drawings','figures':[]}
        result=audit(spec=s,doc=p,parent=p)
        assert result['technical_status']=='REVIEW_REQUIRED'
        assert 'NOT_EXERCISED' in ' '.join(result['pending'])
    case('zero_drawings_not_false_pass',empty)
    def cli():
        m=out/'cli-manifest.json';m.write_text(json.dumps(base));receipt=out/'cli-result.json'
        p=subprocess.run([sys.executable,str(ROOT/'scripts/audit_figure_integration.py'),str(new),str(m),'--parent',str(old),'--out',str(receipt)],capture_output=True,text=True)
        assert p.returncode==0,p.stderr
        assert json.loads(receipt.read_text())['overall_status']=='REVIEW_REQUIRED'
    case('actual_cli_preserves_review_boundary',cli)
    report={'passed':sum(r['status']=='PASS' for r in results),'total':len(results),'results':results,'scope':'Synthetic OOXML identity/placement cases; fake media bytes, not render or scientific tests'}
    (out/'test-results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'passed':report['passed'],'total':report['total']}))
    return report['passed']==report['total']

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    raise SystemExit(0 if run(a.out) else 1)
