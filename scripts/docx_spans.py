"""Exact prose spans in complex paragraphs; preserve fields and tracked history.

Only direct ordinary text runs are eligible. Spans cannot cross style changes,
fields, links, equations, old highlights or revisions. This is intentionally a
bounded OOXML editor, not a general accept/reject or equation rewriting tool.
"""
from __future__ import annotations
import copy,re
from lxml import etree as E

W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS={'w':W};Q=lambda s:'{'+W+'}'+s
XMLSPACE='{http://www.w3.org/XML/1998/namespace}space'
def c14n(n):return E.tostring(n,method='c14n')

def field_runs(root):
    """Return protected run IDs and complete field payloads, across paragraphs."""
    depth=0;protected=set();groups=[];current=[]
    for run in root.iter(Q('r')):
        was=depth
        for fc in run.findall('.//w:fldChar',NS):
            kind=fc.get(Q('fldCharType'))
            if kind=='begin':depth+=1
            elif kind=='end':
                if not depth:raise ValueError('Unmatched field end; no edits applied')
                depth-=1
            elif kind=='separate' and not depth:raise ValueError('Unmatched field separator; no edits applied')
        if was or depth or run.find('.//w:fldChar',NS) is not None:
            protected.add(run);current.append(c14n(run))
            if depth==0:groups.append(current);current=[]
    if depth:raise ValueError('Unclosed complex field; no edits applied')
    return protected,groups

def eligible(run,field_set):
    if run.tag!=Q('r') or run in field_set:return False
    if any(c.tag not in (Q('rPr'),Q('t')) for c in run):return False
    if len(run.findall('w:t',NS))!=1:return False
    if run.find('w:rPr/w:highlight',NS) is not None:return False
    if run.find('w:rPr/w:rPrChange',NS) is not None:return False
    return True

def groups(p,field_set):
    result=[];group=[];style=None
    for run in p:
        if not eligible(run,field_set):
            if group:result.append(group)
            group=[];style=None;continue
        rp=run.find('w:rPr',NS);key=c14n(rp) if rp is not None else b''
        if group and key!=style:result.append(group);group=[]
        group.append(run);style=key
    if group:result.append(group)
    return result

def run_text(r):return r.find('w:t',NS).text or ''
def new_run(run,value,highlight=False):
    r=copy.deepcopy(run);r.find('w:t',NS).text=value;r.find('w:t',NS).set(XMLSPACE,'preserve')
    if highlight:
        rp=r.find('w:rPr',NS)
        if rp is None:rp=E.Element(Q('rPr'));r.insert(0,rp)
        h=E.Element(Q('highlight'));h.set(Q('val'),'yellow')
        # Use the schema-aware run-property helper to maintain OOXML ordering.
        from docx.oxml import parse_xml
        ordered=parse_xml(E.tostring(rp));r.replace(rp,ordered)
        ordered.get_or_add_highlight().set(Q('val'),'yellow')
    return r

def replace_span(p,before,after,highlight,field_set):
    if not isinstance(before,str) or not before or not isinstance(after,str):raise ValueError('Span before must be nonempty and after must be text')
    if any(c in before+after for c in '\r\n\t'):raise ValueError('Multiline spans are unsupported; original retained')
    candidates=[]
    for group in groups(p,field_set):
        s=''.join(run_text(r) for r in group)
        candidates.extend((group,m.start()) for m in re.finditer('(?='+re.escape(before)+')',s))
    if len(candidates)!=1:
        raise ValueError(f'Span has {len(candidates)} eligible matches; it is absent, ambiguous, or crosses protected content/style: {before!r}')
    group,start=candidates[0];end=start+len(before);offset=0;inserted=False
    for run in group:
        value=run_text(run);a=offset;b=a+len(value);offset=b
        if b<=start or a>=end:continue
        prefix=value[:max(0,start-a)];suffix=value[max(0,end-a):] if end<b else ''
        replacement=[]
        if prefix:replacement.append(new_run(run,prefix))
        if not inserted:
            if after:replacement.append(new_run(run,after,highlight))
            inserted=True
        if suffix:replacement.append(new_run(run,suffix))
        index=p.index(run)
        for n in replacement:p.insert(index,n);index+=1
        p.remove(run)

def protected_history(root):
    tags=('ins','del','moveFrom','moveTo','pPrChange','rPrChange','sectPrChange','tblPrChange','trPrChange','tcPrChange','moveFromRangeStart','moveFromRangeEnd','moveToRangeStart','moveToRangeEnd')
    return {tag:[c14n(n) for n in root.iter(Q(tag))] for tag in tags}

def apply_span_plan(source,plan,highlight,*,paragraphs,text,protected,namespaces,canonical):
    root=copy.deepcopy(source);base=paragraphs(root);lookup={f'P{i:04d}':p for i,p in enumerate(base,1)}
    old_fields=field_runs(source)[1];history=protected_history(source)
    old_highlights=[c14n(n) for n in source.xpath('//w:r[w:rPr/w:highlight]',namespaces=NS)]
    field_set=field_runs(root)[0];changes=[];ids=set();targets=set()
    for op in plan['operations']:
        cid=op['id'];pid=op['target']
        if op['kind']!='replace_span':raise ValueError('Use one span plan for complex edits; do not combine paragraph replacement')
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*',cid) or cid in ids:raise ValueError('Invalid or duplicate change ID')
        if pid not in lookup or pid in targets:raise ValueError('Unknown/repeated direct-body paragraph; combine spans for one target')
        if not op.get('purpose') or not op.get('evidence') or not isinstance(op.get('confirm'),bool):raise ValueError('Each change needs purpose, evidence and Boolean confirm')
        ids.add(cid);targets.add(pid);p=lookup[pid];before=text(p)
        if op.get('expect')!=before:raise ValueError('Expected source text differs for '+pid)
        if p.find('w:pPr/w:sectPr',NS) is not None:raise ValueError(pid+': section boundary; retained')
        spans=op.get('spans')
        if not isinstance(spans,list) or not spans:raise ValueError('replace_span needs a nonempty spans list')
        for span in spans:
            try:replace_span(p,span['before'],span['after'],highlight,field_set)
            except ValueError as exc:raise ValueError(pid+': '+str(exc)) from exc
        changes.append({'id':cid,'old_location':pid,'new_location':pid,'type':'replace_span','before':before,'after':text(p),'purpose':op['purpose'],'evidence':op['evidence'],'author_confirmation_needed':op['confirm'],'spans':copy.deepcopy(spans)})
    for tag in protected:
        if [canonical(n) for n in source.xpath('//'+tag,namespaces=namespaces)]!=[canonical(n) for n in root.xpath('//'+tag,namespaces=namespaces)]:raise ValueError('Protected object changed: '+tag)
    if history!=protected_history(root):raise ValueError('Existing tracked history changed')
    if old_fields!=field_runs(root)[1]:raise ValueError('Field content/result changed')
    remaining=[c14n(n) for n in root.xpath('//w:r[w:rPr/w:highlight]',namespaces=NS)]
    # Existing highlighted runs are an ordered subsequence; only new yellow runs may be added.
    at=0
    for value in remaining:
        if at<len(old_highlights) and old_highlights[at]==value:at+=1
    if at!=len(old_highlights):raise ValueError('Existing highlighted text changed')
    return root,changes
