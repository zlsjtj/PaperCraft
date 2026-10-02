"""Apply authored text spans, then split at verified ordinary-text boundaries.

This is a document adapter, not a scientific editor. Protected objects and
every non-document ZIP part must remain byte/content equivalent.
"""
from pathlib import Path
import argparse, copy, hashlib, importlib.util, json, re
from lxml import etree as E

W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M='http://schemas.openxmlformats.org/officeDocument/2006/math'
NS={'w':W,'m':M}; Q=lambda s:'{'+W+'}'+s
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def split_once(p, marker, text):
    value=text(p)
    if value.count(marker)!=1:raise ValueError('Split marker must occur exactly once')
    if p.xpath('.//w:fldChar|.//w:fldSimple|.//w:ins|.//w:del|./w:pPr/w:sectPr',namespaces=NS):
        raise ValueError('Splitting fields, revision-bearing or section paragraphs is unsupported')
    pos=value.index(marker)+len(marker)
    if not value[:pos].strip() or not value[pos:].strip():raise ValueError('Split must leave two nonempty paragraphs')
    new=E.Element(Q('p'))
    pp=p.find('w:pPr',NS)
    if pp is not None:new.append(copy.deepcopy(pp))
    cursor=0;found=False
    for node in list(p):
        if node.tag==Q('pPr'):continue
        nt=text(node);end=cursor+len(nt)
        if found:
            p.remove(node);new.append(node)
        elif cursor<=pos<=end and nt:
            cut=pos-cursor
            if cut<len(nt):
                # Never slice an equation, link, field or mixed-content run.
                ts=node.findall('w:t',NS)
                if node.tag!=Q('r') or len(ts)!=1 or any(c.tag not in (Q('rPr'),Q('t')) for c in node):
                    raise ValueError('Boundary falls inside a protected or complex object')
                left=nt[:cut];right=nt[cut:]
                tail=copy.deepcopy(node);tail.find('w:t',NS).text=right
                tail.find('w:t',NS).set('{http://www.w3.org/XML/1998/namespace}space','preserve')
                ts[0].text=left;ts[0].set('{http://www.w3.org/XML/1998/namespace}space','preserve')
                new.append(tail)
            found=True
        cursor=end
    if not found:raise ValueError('Split boundary not found')
    # Preserve all original text, including the leading space after the cut.
    if text(p)+text(new)!=value:raise ValueError('Text changed during split')
    p.addnext(new)
    return new

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--edits',type=Path,required=True);ap.add_argument('--skill',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    if a.out.exists():raise ValueError('Output must be new')
    spec=importlib.util.spec_from_file_location('revision_tool',a.skill/'scripts/review_docx.py');D=importlib.util.module_from_spec(spec);spec.loader.exec_module(D)
    edits=json.loads(a.edits.read_text(encoding='utf-8'))
    if isinstance(edits,dict) and edits.get('source_sha256') and edits['source_sha256']!=sha(a.source):
        raise ValueError('Authored edits name a different source revision')
    edits=edits.get('edits',edits) if isinstance(edits,dict) else edits
    inv=D.inventory(a.source);lookup={p['id']:p for p in inv['paragraphs']}
    infos,parts,original=D.read_package(a.source);ops=[];splits={};records=[]
    for i,e in enumerate(edits,1):
        pid=e['paragraph_id'];before=e['before'];after=e['after'];kind=e['operation'];row=lookup[pid]
        if '\n' in after:
            pieces=after.split('\n\n')
            if len(pieces)<2 or any(not s.strip() or '\n' in s for s in pieces):
                raise ValueError('Only explicit paragraph separators are supported')
            splits.setdefault(pid,[]).extend(pieces[:-1])
            after=' '.join(pieces)
        if kind=='replace_paragraph' and before!=row['text']:raise ValueError('Source paragraph changed: '+pid)
        if kind not in ('replace_paragraph','replace_span','split_after'):raise ValueError('Unknown edit operation')
        if before!=after:
            op=next((o for o in ops if o['target']==pid),None)
            if op is None:
                op={'id':'C'+str(i),'kind':'replace_span','target':pid,'expect':row['text'],'spans':[],
                    'purpose':e['reason'],'evidence':'; '.join(e['source']),'confirm':False};ops.append(op)
            op['spans'].append({'before':before,'after':after})
        if e.get('split_after'):splits.setdefault(pid,[]).extend(e['split_after'])
        records.append(e)
    plan={'input_sha256':sha(a.source),'scope':'continue','operations':ops}
    a.out.mkdir(parents=True)
    versions={}
    for label,highlight in [('clean',False),('review',True)]:
        root,changes=D.apply_plan(original,plan,highlight)
        nodes={f'P{i:04d}':p for i,p in enumerate(D.paragraphs(root),1)}
        mapping={pid:[node] for pid,node in nodes.items()}
        for pid,markers in splits.items():
            current=nodes[pid]
            for marker in markers:
                current=split_once(current,marker,D.text);mapping[pid].append(current)
        for tag in D.PROTECTED:
            if [D.canonical(x) for x in original.xpath('//'+tag,namespaces=NS)] != [D.canonical(x) for x in root.xpath('//'+tag,namespaces=NS)]:raise ValueError('Protected object changed: '+tag)
        out=a.out/(label+'.docx');D.write_package(out,infos,parts,root);check=D.verify_pair(a.source,out)
        final=D.paragraphs(root)
        mapped={pid:[f'P{final.index(n)+1:04d}' for n in ns] for pid,ns in mapping.items()}
        versions[label]={'sha256':sha(out),'checks':check,'paragraph_map':mapped,'text_changes':changes}
        (a.out/(label+'.txt')).write_text('\n\n'.join(D.text(p) for p in final),encoding='utf-8')
    assert (a.out/'clean.txt').read_bytes()==(a.out/'review.txt').read_bytes()
    receipt={'source_sha256':sha(a.source),'edit_file_sha256':sha(a.edits),'builder_sha256':sha(__file__),'skill_helper_sha256':sha(a.skill/'scripts/review_docx.py'),'versions':versions,'edits':records,'yellow':'New ordinary text only; splits are mapped, not native Track Changes.','visual_review':'NOT_RUN'}
    (a.out/'build.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'changes':len(edits),'split_paragraphs':len(splits),'status':'PROTECTED_OBJECTS_PRESERVED'}))

if __name__=='__main__':main()
