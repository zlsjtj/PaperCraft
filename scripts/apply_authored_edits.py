"""Apply authored text and verified paragraph split/join operations.

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

def join_next(p, expected_next, expected_after, text, separator=' '):
    """Join adjacent equal-format prose paragraphs by moving existing nodes.

    This changes a paragraph boundary, not node order or bookmark ranges.
    It deliberately does not implement relocation or format normalization.
    """
    other=p.getnext()
    if other is None or other.tag!=Q('p') or other.getparent()!=p.getparent():
        raise ValueError('Join requires an immediately adjacent paragraph')
    if text(other)!=expected_next:raise ValueError('Join next paragraph differs from authored source')
    if separator not in ('',' '):raise ValueError('Join separator must be empty or one ordinary space')
    forbidden=('.//w:fldChar|.//w:fldSimple|.//w:ins|.//w:del|.//w:moveFrom|.//w:moveTo|'
               './/w:pPrChange|.//w:rPrChange|.//w:sectPr|.//w:commentReference|'
               './/w:commentRangeStart|.//w:commentRangeEnd|.//w:br|.//w:drawing|.//w:pict|.//w:object|.//m:oMath')
    if any(n.xpath(forbidden,namespaces=NS) for n in (p,other)):
        raise ValueError('Join of field, revision, section, comment, break or non-prose objects is unsupported')
    def props(n):
        pp=n.find('w:pPr',NS)
        return E.tostring(pp,method='c14n') if pp is not None else None
    if props(p)!=props(other):raise ValueError('Join requires identical paragraph properties')
    before=text(p)+separator+text(other)
    if before!=expected_after:raise ValueError('Join after text must preserve both paragraphs verbatim')
    nodes=[n for n in other if n.tag!=Q('pPr')]
    signatures=[E.tostring(n,method='c14n') for n in nodes]
    if separator:
        run=E.Element(Q('r'));t=E.SubElement(run,Q('t'));t.text=separator
        t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');p.append(run)
    for n in nodes:other.remove(n);p.append(n)
    other.getparent().remove(other)
    if text(p)!=expected_after:raise AssertionError('Join changed visible text')
    if [E.tostring(n,method='c14n') for n in nodes]!=signatures:
        raise AssertionError('Join changed a retained child node')
    return other

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
    declared_sha=edits.get('source_sha256') if isinstance(edits,dict) else None
    if isinstance(edits,dict) and edits.get('source_sha256') and edits['source_sha256']!=sha(a.source):
        raise ValueError('Authored edits name a different source revision')
    edits=edits.get('edits',edits) if isinstance(edits,dict) else edits
    authored=[];joins=[]
    inv=D.inventory(a.source);lookup={p['id']:p for p in inv['paragraphs']}
    infos,parts,original=D.read_package(a.source);ops=[];splits={};records=[]
    for i,e in enumerate(edits,1):
        pid=e['paragraph_id'];before=e['before'];after=e['after'];kind=e['operation'];row=lookup[pid]
        if kind=='join_next':
            if declared_sha!=sha(a.source) or before!=row['text']:
                raise ValueError('Join requires the exact source hash and paragraph text')
            if e.get('split_after') or '\n' in after or not e.get('reason') or not e.get('source'):
                raise ValueError('Join needs a reason/source and cannot also split')
            joins.append(e);records.append(e);continue
        if '\n' in after:
            pieces=after.split('\n\n')
            if len(pieces)<2 or any(not s.strip() or '\n' in s for s in pieces):
                raise ValueError('Only explicit paragraph separators are supported')
            splits.setdefault(pid,[]).extend(pieces[:-1])
            after=' '.join(pieces)
        if kind=='replace_paragraph' and before!=row['text']:raise ValueError('Source paragraph changed: '+pid)
        if kind=='rewrite_prose_preserving_runs':
            if declared_sha!=sha(a.source):raise ValueError('Authored run rewrite requires the exact source_sha256')
            if not isinstance(e.get('reason'),str) or not e['reason'].strip() or not e.get('source'):
                raise ValueError('Authored run rewrite requires a reason and source evidence')
            if before!=row['text']:raise ValueError('Source paragraph changed: '+pid)
            if e.get('split_after') or '\n' in e['after']:raise ValueError('Authored run rewrite cannot also split a paragraph')
            if any(x['paragraph_id']==pid for x in authored):raise ValueError('Repeated authored paragraph')
            authored.append(e);records.append(e);continue
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
    if {e['paragraph_id'] for e in authored} & ({o['target'] for o in ops}|set(splits)):
        raise ValueError('Do not combine authored run rewrite and span/split editing on one paragraph')
    if joins and (authored or ops or splits):
        raise ValueError('Apply joins in a separate inspected pass')
    if len({e['paragraph_id'] for e in joins})!=len(joins):raise ValueError('Repeated join target')
    rp_spec=importlib.util.spec_from_file_location('authored_runs',a.skill/'scripts/rewrite_prose_runs.py')
    RP=importlib.util.module_from_spec(rp_spec);rp_spec.loader.exec_module(RP)
    a.out.mkdir(parents=True)
    versions={}
    for label,highlight in [('clean',False),('review',True)]:
        root,changes=D.apply_plan(original,plan,highlight) if ops else (copy.deepcopy(original),[])
        nodes={f'P{i:04d}':p for i,p in enumerate(D.paragraphs(root),1)}
        field_set=D.SPAN.field_runs(root)[0]
        for e in authored:
            pid=e['paragraph_id']
            try:diffs=RP.rewrite(nodes[pid],e['after'],highlight,D.SPAN,field_set)
            except ValueError as exc:raise ValueError(pid+': '+str(exc)) from exc
            changes.append({'old_location':pid,'new_location':pid,'type':e['operation'],
                            'before':e['before'],'after':e['after'],'purpose':e['reason'],
                            'evidence':e['source'],'text_diffs':diffs})
        mapping={pid:[node] for pid,node in nodes.items()}
        for pid,markers in splits.items():
            current=nodes[pid]
            for marker in markers:
                current=split_once(current,marker,D.text);mapping[pid].append(current)
        joined_nodes=set()
        for e in joins:
            pid=e['paragraph_id'];node=nodes[pid];other=node.getnext()
            if node in joined_nodes or other in joined_nodes or node.getparent() is None:
                raise ValueError('Overlapping joins require a separate inspected pass')
            removed=join_next(node,e['next_before'],e['after'],D.text,e.get('separator',' '))
            joined_nodes.update((node,removed))
            for old_pid,old_nodes in mapping.items():
                mapping[old_pid]=[node if n is removed else n for n in old_nodes]
            changes.append({'old_location':pid,'type':'join_next','before':[e['before'],e['next_before']],
                            'after':e['after'],'purpose':e['reason'],'evidence':e['source'],
                            'preservation':'Existing child nodes moved unchanged; equal pPr; no relocation'})
        for tag in D.PROTECTED:
            if [D.canonical(x) for x in original.xpath('//'+tag,namespaces=NS)] != [D.canonical(x) for x in root.xpath('//'+tag,namespaces=NS)]:raise ValueError('Protected object changed: '+tag)
        out=a.out/(label+'.docx');D.write_package(out,infos,parts,root);check=D.verify_pair(a.source,out)
        final=D.paragraphs(root)
        mapped={pid:[f'P{final.index(n)+1:04d}' for n in ns] for pid,ns in mapping.items()}
        versions[label]={'sha256':sha(out),'checks':check,'paragraph_map':mapped,'text_changes':changes}
        (a.out/(label+'.txt')).write_text('\n\n'.join(D.text(p) for p in final),encoding='utf-8')
    assert (a.out/'clean.txt').read_bytes()==(a.out/'review.txt').read_bytes()
    receipt={'source_sha256':sha(a.source),'edit_file_sha256':sha(a.edits),'builder_sha256':sha(__file__),'skill_helper_sha256':sha(a.skill/'scripts/review_docx.py'),'authored_run_helper_sha256':sha(a.skill/'scripts/rewrite_prose_runs.py'),'versions':versions,'edits':records,'yellow':'New ordinary text only; deleted text remains in text_diffs, splits are mapped, not native Track Changes.','visual_review':'NOT_RUN'}
    (a.out/'build.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'changes':len(edits),'split_paragraphs':len(splits),'status':'PROTECTED_OBJECTS_PRESERVED'}))

if __name__=='__main__':main()
