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

class FieldStructureError(ValueError):
    def __init__(self,message,node):
        self.location=node.getroottree().getpath(node)
        super().__init__(message+' at '+self.location+'; no edits applied')

def field_runs(root):
    """Return protected run IDs and complete field payloads, across paragraphs."""
    stack=[];protected=set();groups=[];current=[]
    for run in root.iter(Q('r')):
        was=bool(stack)
        for node in run.iter():
            if node.tag==Q('instrText'):
                if not stack:raise FieldStructureError('Field instruction outside a complex field',node)
                if stack[-1][1]:raise FieldStructureError('Field instruction after result separator',node)
            if node.tag!=Q('fldChar'):continue
            kind=node.get(Q('fldCharType'))
            if kind=='begin':stack.append([node,False])
            elif kind=='end':
                if not stack:raise FieldStructureError('Unmatched field end',node)
                stack.pop()
            elif kind=='separate':
                if not stack:raise FieldStructureError('Unmatched field separator',node)
                if stack[-1][1]:raise FieldStructureError('Repeated field separator',node)
                stack[-1][1]=True
            else:raise FieldStructureError('Unknown or missing field character type',node)
        if was or stack or run.find('.//w:fldChar',NS) is not None:
            protected.add(run);current.append(c14n(run))
            if not stack:groups.append(current);current=[]
    if stack:raise FieldStructureError('Unclosed complex field',stack[0][0])
    return protected,groups

def ineligible_reason(run,field_set):
    if run.tag!=Q('r'):return 'not a direct ordinary text run'
    if run in field_set:return 'complex field code or cached result'
    if any(c.tag not in (Q('rPr'),Q('t'),Q('lastRenderedPageBreak')) for c in run):return 'complex run content'
    if len(run.findall('w:t',NS))!=1:return 'ordinary span requires exactly one text node per run'
    if run.find('w:rPr/w:highlight',NS) is not None:return 'existing highlight'
    if run.find('w:rPr/w:rPrChange',NS) is not None:return 'existing run-property revision'
    return None

def eligible(run,field_set):return ineligible_reason(run,field_set) is None

def groups(p,field_set):
    result=[];group=[];style=None
    for run in p:
        if not eligible(run,field_set):
            if group:result.append(group)
            group=[];style=None;continue
        # Word's cached page marker is not a hard break or revision. Edit the
        # adjacent text, but keep this run separate so no span crosses its cache.
        if run.find('w:lastRenderedPageBreak',NS) is not None:
            if group:result.append(group)
            result.append([run]);group=[];style=None;continue
        rp=run.find('w:rPr',NS);key=c14n(rp) if rp is not None else b''
        if group and key!=style:result.append(group);group=[]
        group.append(run);style=key
    if group:result.append(group)
    return result

def run_text(r):return r.find('w:t',NS).text or ''

def span_matches(run_groups,before):
    """The same exact, overlapping match rule for inspect and apply."""
    if not before:return []
    return [(group,m.start()) for group in run_groups
            for m in re.finditer('(?='+re.escape(before)+')',''.join(run_text(r) for r in group))]

def paragraph_span_reason(p):
    if p.find('w:pPr/w:sectPr',NS) is not None:return 'section boundary; retained'
    return None

def span_text_reason(before,after):
    if not isinstance(before,str) or not before or not isinstance(after,str):return 'Span before must be nonempty and after must be text'
    if any(c in before+after for c in '\r\n\t'):return 'Multiline spans are unsupported; original retained'
    return None
def new_run(run,value,highlight=False):
    r=copy.deepcopy(run);r.find('w:t',NS).text=value;r.find('w:t',NS).set(XMLSPACE,'preserve')
    for marker in r.findall('w:lastRenderedPageBreak',NS):r.remove(marker)
    if highlight:
        rp=r.find('w:rPr',NS)
        if rp is None:rp=E.Element(Q('rPr'));r.insert(0,rp)
        h=E.Element(Q('highlight'));h.set(Q('val'),'yellow')
        # Use the schema-aware run-property helper to maintain OOXML ordering.
        from docx.oxml import parse_xml
        ordered=parse_xml(E.tostring(rp));r.replace(rp,ordered)
        ordered.get_or_add_highlight().set(Q('val'),'yellow')
    return r

def page_cache_runs(run):
    """Retain cached markers once, on the same side of the run's text.

    A cached position may be stale after an edit; Word recomputes pagination.
    Explicit w:br, fields and history are never admitted through this path.
    """
    before=[];after=[];seen_text=False
    for child in run:
        if child.tag==Q('t'):seen_text=True
        elif child.tag==Q('lastRenderedPageBreak'):
            anchor=copy.deepcopy(run)
            for node in list(anchor):
                if node.tag!=Q('rPr'):anchor.remove(node)
            anchor.append(copy.deepcopy(child))
            (after if seen_text else before).append(anchor)
    return before,after

def replace_span(p,before,after,highlight,field_set):
    reason=span_text_reason(before,after)
    if reason:raise ValueError(reason)
    candidates=span_matches(groups(p,field_set),before)
    if len(candidates)!=1:
        raise ValueError(f'Span has {len(candidates)} eligible matches; it is absent, ambiguous, or crosses protected content/style: {before!r}')
    group,start=candidates[0];end=start+len(before);offset=0;inserted=False
    for run in group:
        value=run_text(run);a=offset;b=a+len(value);offset=b
        if b<=start or a>=end:continue
        prefix=value[:max(0,start-a)];suffix=value[max(0,end-a):] if end<b else ''
        cache_before,cache_after=page_cache_runs(run)
        replacement=list(cache_before)
        if prefix:replacement.append(new_run(run,prefix))
        if not inserted:
            if after:replacement.append(new_run(run,after,highlight))
            inserted=True
        if suffix:replacement.append(new_run(run,suffix))
        replacement.extend(cache_after)
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
        reason=paragraph_span_reason(p)
        if reason:raise ValueError(pid+': '+reason)
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
