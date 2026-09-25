"""Read-only binding of a main-body DOCX figure inventory to actual embedded bytes.

This verifies declared identities, placement and caption strings, not science or
visual quality. Unsupported drawing types are explicitly REVIEW_REQUIRED.
"""
import argparse
import hashlib
import json
from pathlib import Path
import posixpath
import zipfile
from xml.etree import ElementTree as E

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
      'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
      'v': 'urn:schemas-microsoft-com:vml',
      'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006'}

def sha(value): return hashlib.sha256(value).hexdigest()

def inspect(path):
    with zipfile.ZipFile(path) as z:
        if z.testzip(): raise ValueError('Corrupt DOCX ZIP')
        root = E.fromstring(z.read('word/document.xml'))
        rels = {r.attrib['Id']: r.attrib for r in E.fromstring(z.read('word/_rels/document.xml.rels'))}
        paragraphs = [''.join(n.text or '' for n in p.findall('.//w:t', NS)) for p in root.findall('.//w:p', NS)]
        drawings, unsupported = [], []
        for index, node in enumerate(root.findall('.//w:drawing', NS), 1):
            blips = node.findall('.//a:blip', NS)
            if len(blips) != 1:
                unsupported.append(f'drawing {index}: {len(blips)} primary blips')
                drawings.append({'index': index, 'status': 'REVIEW_REQUIRED'}); continue
            rid = blips[0].get('{'+NS['r']+'}embed')
            rel = rels.get(rid)
            if rel is None or rel.get('TargetMode') == 'External':
                raise ValueError(f'drawing {index}: missing or external image relationship')
            target = posixpath.normpath(posixpath.join('word', rel['Target']))
            if target.startswith('../') or target.startswith('/'):
                raise ValueError('Image target escapes package')
            extent = node.find('.//wp:extent', NS)
            if extent is None:
                unsupported.append(f'drawing {index}: no wp:extent')
                drawings.append({'index': index, 'status': 'REVIEW_REQUIRED'}); continue
            size = [int(extent.get(k, '0')) / 36000 for k in ('cx', 'cy')]
            if min(size) <= 0: raise ValueError('Non-positive figure extent')
            representations=[{'kind':'primary','part':target,'sha256':sha(z.read(target))}]
            svg_nodes=[n for n in node.iter() if n.tag=='{http://schemas.microsoft.com/office/drawing/2016/SVG/main}svgBlip']
            if len(svg_nodes)>1:unsupported.append(f'drawing {index}: multiple SVG alternatives')
            for svg in svg_nodes:
                svgrel=rels.get(svg.get('{'+NS['r']+'}embed'))
                if svgrel is None or svgrel.get('TargetMode')=='External':raise ValueError('Missing or external SVG relationship')
                svgpart=posixpath.normpath(posixpath.join('word',svgrel['Target']))
                if not svgpart.startswith('word/media/'):raise ValueError('SVG target escapes media directory')
                representations.append({'kind':'svg','part':svgpart,'sha256':sha(z.read(svgpart))})
            drawings.append({'index': index, 'part': target, 'sha256': sha(z.read(target)), 'representations':representations,
                             'width_mm': size[0], 'height_mm': size[1], 'status': 'AUDITABLE'})
        if root.findall('.//v:imagedata', NS): unsupported.append('VML images')
        if root.findall('.//mc:AlternateContent', NS): unsupported.append('AlternateContent fallback')
    return {'sha256': sha(Path(path).read_bytes()), 'drawings': drawings,
            'paragraphs': paragraphs, 'unsupported': unsupported}

def audit(docx, manifest, parent=None):
    spec = json.loads(Path(manifest).read_text(encoding='utf-8-sig'))
    now = inspect(docx); before = inspect(parent) if parent else None
    errors, pending, checks = [], list(now['unsupported']), []
    if not now['drawings']:
        pending.append('No main-document DrawingML: integration NOT_EXERCISED')
    rows = spec.get('figures', [])
    if spec.get('scope') != 'all-main-document-drawings':
        errors.append('This helper requires a complete main-document drawing inventory')
    if spec.get('docx_sha256') and spec['docx_sha256'] != now['sha256']:
        errors.append('Manifest names another DOCX revision')
    if before and spec.get('parent_sha256') and spec['parent_sha256'] != before['sha256']:
        errors.append('Manifest names another parent revision')
    indices = [r.get('drawing_index') for r in rows]
    ids = [r.get('id') for r in rows]
    if sorted(x for x in indices if isinstance(x,int)) != list(range(1,len(now['drawings'])+1)) or len(indices)!=len(now['drawings']):
        errors.append('Missing, extra or duplicate drawing index')
    if not all(isinstance(i,str) and i for i in ids) or len(set(ids)) != len(ids):
        errors.append('Missing or duplicate figure id')
    if before and len(before['drawings']) != len(now['drawings']):
        errors.append('Changed drawing count requires a separately reviewed mapping')
    for row in rows:
        idx = row.get('drawing_index'); found=[]
        if not isinstance(idx,int) or not 1<=idx<=len(now['drawings']): continue
        d = now['drawings'][idx-1]
        if d['status'] != 'AUDITABLE':
            pending.append(f'{row.get("id")}: unsupported drawing');continue
        disposition = row.get('disposition')
        if disposition not in ('preserved','revised'): found.append('Invalid disposition')
        if row.get('media_sha256') != d['sha256']: found.append('Embedded image differs from declared final asset')
        width = row.get('placement_width_mm')
        if not isinstance(width,(int,float)) or width<=0 or abs(width-d['width_mm'])>0.05:
            found.append('Placement width does not match declaration within 0.05 mm')
        if 'placement_height_mm' in row and abs(row['placement_height_mm']-d['height_mm'])>0.05:
            found.append('Placement height does not match declaration within 0.05 mm')
        kind = row.get('kind','figure')
        if kind == 'figure':
            caption = row.get('caption_contains')
            if not caption or not any(caption in text for text in now['paragraphs']):
                found.append('Declared visible caption text not found')
            if row.get('caption_exact') and row['caption_exact'] not in now['paragraphs']:
                found.append('Full visible caption differs from declared final text')
        elif kind != 'decorative' or not row.get('reason'):
            found.append('Unsupported kind or missing decorative-item reason')
        if before and idx<=len(before['drawings']):
            old = before['drawings'][idx-1]
            if old['status'] != 'AUDITABLE': pending.append(f'{row.get("id")}: unsupported parent drawing')
            else:
                same = old['sha256']==d['sha256']
                if disposition=='preserved' and not same: found.append('Preserved figure bytes changed')
                if disposition=='revised' and same: found.append('Revised figure still contains parent image bytes')
        elif disposition == 'preserved': pending.append(f'{row.get("id")}: parent not supplied')
        if row.get('source_asset'):
            asset = Path(manifest).resolve().parent/row['source_asset']
            if not asset.is_file() or sha(asset.read_bytes()) != row.get('source_asset_sha256'):
                found.append('Source export is missing or its hash differs')
            elif row.get('source_asset_sha256') != d['sha256']:
                found.append('Source export bytes differ from embedded image')
        elif disposition=='revised': pending.append(f'{row.get("id")}: final export path not bound')
        # A PNG fallback and an SVG can render differently. Bind each explicitly.
        declared=row.get('representations')
        if declared is None and len(d['representations'])>1:
            pending.append(f'{row.get("id")}: every embedded representation must be declared; primary image alone is insufficient')
        elif declared is not None:
            actual={x['kind']:x for x in d['representations']}
            kinds=[x.get('kind') for x in declared]
            if len(kinds)!=len(set(kinds)) or set(kinds)!=set(actual):found.append('Missing, extra or duplicate embedded representation')
            for rep in declared:
                a=actual.get(rep.get('kind'))
                if a is None:continue
                if rep.get('media_sha256')!=a['sha256']:found.append('Embedded '+rep['kind']+' differs from declared final asset')
                if rep.get('source_asset'):
                    f=Path(manifest).resolve().parent/rep['source_asset']
                    if not f.is_file() or sha(f.read_bytes())!=rep.get('source_asset_sha256') or rep.get('source_asset_sha256')!=a['sha256']:
                        found.append('Source '+rep['kind']+' export missing or differs from embedded representation')
                elif disposition=='revised':pending.append(f'{row.get("id")}: {rep["kind"]} export path not bound')
            if before and disposition=='preserved' and idx<=len(before['drawings']):
                oldreps=before['drawings'][idx-1].get('representations',[])
                if oldreps!=d['representations']:found.append('Preserved alternative representation changed')
        checks.append({'id':row.get('id'), 'actual': d, 'status':'FAIL' if found else 'PASS', 'errors':found})
        errors += [f'{row.get("id")}: {e}' for e in found]
    status = 'FAIL' if errors else ('REVIEW_REQUIRED' if pending else 'PASS')
    return {'tool_version':'2.8.0','technical_status':status,'overall_status':'FAIL' if status=='FAIL' else 'REVIEW_REQUIRED',
            'docx_sha256':now['sha256'],'parent_sha256':before['sha256'] if before else None,
            'checks':checks,'errors':errors,'pending':pending,
            'limits':['Main-document DrawingML only; headers, text boxes and other parts require separate inventory.',
                      'Caption substring checks do not prove numbering, field updates, body references or scientific consistency.',
                      'Media bytes and extents do not establish effective font size, aspect ratio or page readability.',
                      'Scientific review, final page rendering and author acceptance remain separate.']}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('docx',type=Path);ap.add_argument('manifest',type=Path)
    ap.add_argument('--parent',type=Path);ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    if args.out.resolve() in {p.resolve() for p in (args.docx,args.manifest,args.parent) if p}:
        ap.error('Output cannot overwrite input')
    try: result=audit(args.docx,args.manifest,args.parent)
    except (ValueError,KeyError,OSError,zipfile.BadZipFile,E.ParseError,TypeError) as exc:
        result={'technical_status':'FAIL','overall_status':'REVIEW_REQUIRED','errors':[str(exc)]}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'technical_status':result['technical_status'],'receipt':str(args.out)}))
    return 1 if result['technical_status']=='FAIL' else 0

if __name__=='__main__': raise SystemExit(main())
