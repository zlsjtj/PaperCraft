"""从固定修改文本重建 Word；不调用模型，也不重新提炼贡献。"""
from pathlib import Path
import argparse, importlib.util, json, zipfile
from lxml import etree
E=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--condition',choices=['plain','skill','selected'],default='selected');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
if a.out.exists():raise SystemExit('输出目录已存在，拒绝覆盖。')
spec=importlib.util.spec_from_file_location('review',E.parents[1]/'scripts/review_docx.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
source=E/'input/rough.docx';infos,parts,root=m.read_package(source);ps=m.paragraphs(root)
edits=json.loads((E/a.condition/'edits.json').read_text('utf-8'))
display={str(x['index']):x['text'] for x in json.loads((E/'input/paragraphs.json').read_text('utf-8'))}
ops=[]
for k,v in edits.items():
    i=int(k)
    if i in {1,9,14,19}:
        if v!=display[k]:raise ValueError('受保护段不一致：'+k)
        continue
    old=m.text(ps[i-1])
    if v!=old:ops.append({'id':f'E{i:03}','kind':'replace','target':f'P{i:04}','expect':old,'text':v,'purpose':'固定构造示例重建','evidence':'input/implementation.md 与 results.csv','confirm':True})
plan={'input_sha256':m.sha(source.read_bytes()),'scope':'full','operations':ops}
a.out.mkdir(parents=True)
record={}
for name,yellow in [('clean',False),('review',True)]:
    out,changes=m.apply_plan(root,plan,yellow)
    styles=etree.fromstring(parts['word/styles.xml'])
    for e in styles.xpath('//w:pBdr',namespaces=m.NS):e.getparent().remove(e)
    final_parts=dict(parts);final_parts['word/styles.xml']=etree.tostring(styles,xml_declaration=True,encoding='UTF-8',standalone=True)
    target=a.out/(name+'.docx');m.write_package(target,infos,final_parts,out)
    for tag in m.PROTECTED:
        assert [m.canonical(x) for x in root.xpath('//'+tag,namespaces=m.NS)]==[m.canonical(x) for x in out.xpath('//'+tag,namespaces=m.NS)],tag
    record[name]={'sha256':m.sha(target.read_bytes()),'protected_xml':'EXACT_MATCH','highlight':'yellow' if yellow else 'none','native_track_changes':False}
(a.out/'rebuild-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':'WRITTEN','out':str(a.out),'render':'NOT_RUN'},ensure_ascii=False))
