"""Export an explicitly selected DOCX reading packet, without the rest of the paper."""
import argparse, hashlib, json, posixpath, zipfile
from pathlib import Path
from lxml import etree as E
from review_docx import read_package, paragraphs, text, sha, NS

R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
A='http://schemas.openxmlformats.org/drawingml/2006/main'

def build(source, selection, out):
    source=Path(source);out=Path(out)
    if out.exists():raise ValueError('Use a new output directory')
    if set(selection)-{'source_sha256','paragraphs','purpose'}:raise ValueError('Unknown selection fields')
    if selection.get('source_sha256')!=sha(source.read_bytes()):raise ValueError('Source hash differs')
    _,parts,root=read_package(source)
    ps={f'P{i:04d}':p for i,p in enumerate(paragraphs(root),1)}
    rules=selection.get('paragraphs')
    if not isinstance(rules,list) or not rules:raise ValueError('Explicit paragraph selection required')
    rels={}
    if 'word/_rels/document.xml.rels' in parts:
        for rel in E.fromstring(parts['word/_rels/document.xml.rels']):rels[rel.get('Id')]=rel
    selected=[];images={};seen=set();warnings=[]
    for rule in rules:
        if set(rule)!={'id','text_sha256'}:raise ValueError('Each selection needs id and text_sha256')
        pid=rule['id']
        if pid not in ps or pid in seen:raise ValueError('Unknown or duplicate paragraph: '+pid)
        seen.add(pid);p=ps[pid];value=text(p)
        if sha(value.encode())!=rule['text_sha256']:raise ValueError('Paragraph hash differs: '+pid)
        if p.xpath('.//w:ins | .//w:del | .//w:moveFrom | .//w:moveTo',namespaces=NS):raise ValueError('Tracked revision requires an explicit reading view')
        refs=[]
        for blip in p.iter('{'+A+'}blip'):
            if blip.get('{'+R+'}link'):raise ValueError('External image requires separate review')
            rid=blip.get('{'+R+'}embed');rel=rels.get(rid)
            if rel is None or rel.get('TargetMode')=='External':raise ValueError('Missing or external image relationship')
            target=posixpath.normpath('word/'+rel.get('Target',''))
            if not target.startswith('word/media/') or target not in parts:raise ValueError('Image target outside media')
            suffix=Path(target).suffix.lower()
            if suffix not in {'.png','.jpg','.jpeg','.gif','.svg','.bmp','.tif','.tiff'}:raise ValueError('Image format needs native review: '+suffix)
            name='image-'+sha(parts[target])[:16]+suffix;images[name]=parts[target];refs.append(name)
        if p.xpath('.//m:oMath',namespaces=NS):warnings.append(pid+': math is text-extracted; use original rendered equation for mathematical review')
        if p.xpath('.//w:pict | .//w:fldSimple | .//w:instrText',namespaces=NS):warnings.append(pid+': legacy image or field needs a separate rendered crop')
        selected.append({'id':pid,'text':value,'text_sha256':rule['text_sha256'],'images':refs})
    # Validate everything before creating any output. No full DOCX or inventory is copied.
    out.mkdir(parents=True)
    chunks=['# 定范围审阅材料','本材料仅包含下列明确选定的段落和其中的嵌入图片。段落编号不是页码；此文件不复现 Word 排版。']
    for item in selected:
        chunks.extend(['## '+item['id'],item['text']])
        chunks.extend('![选定段落图片]('+n+')' for n in item['images'])
    (out/'reading.md').write_text('\n\n'.join(chunks)+'\n',encoding='utf-8')
    for n,data in images.items():(out/n).write_bytes(data)
    record={'source_sha256':selection['source_sha256'],
        'selected':selected,'warnings':warnings,'excluded_content_copied':False,
        'reading_status':'NOT_READ','blind_review_status':'NOT_ESTABLISHED',
        'limits':['The caller selects a fair reading scope. This tool does not decide it.',
                  'Do not give reviewers the full source or editing rationale before first-read answers.',
                  'An already informed reviewer must be recorded as a locating review.'],
        'files':{p.name:sha(p.read_bytes()) for p in out.iterdir() if p.is_file()}}
    (out/'manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    return record

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('selection',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    try:
        r=build(a.source,json.loads(a.selection.read_text(encoding='utf-8')),a.out)
        print(json.dumps({'status':'PASS','selected_paragraphs':len(r['selected']),'warnings':r['warnings'],'review':'NOT_READ'},ensure_ascii=False));return 0
    except (OSError,ValueError,KeyError,zipfile.BadZipFile,E.XMLSyntaxError) as e:p.exit(2,str(e)+'\n')
if __name__=='__main__':raise SystemExit(main())
