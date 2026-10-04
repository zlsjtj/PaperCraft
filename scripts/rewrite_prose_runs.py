"""Bounded authored paragraph diffs, keeping existing ordinary run nodes.

This is an explicit continuation, not a fallback that bypasses span refusal.
It diffs authored prose, checks each changed interval, and changes only ordinary
text. The only formatting equivalence is an eastAsia font hint on ASCII runs
with explicit, identical ASCII and hAnsi fonts. Semantic formatting and every
nonordinary boundary remain barriers. This module does not infer prose.
"""
from __future__ import annotations
import copy, difflib, re
from lxml import etree as E

W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M='http://schemas.openxmlformats.org/officeDocument/2006/math'
NS={'w':W,'m':M}; Q=lambda n:'{'+W+'}'+n
SPACE='{http://www.w3.org/XML/1998/namespace}space'

def visible(n): return ''.join(n.xpath('.//w:t/text() | .//m:t/text()',namespaces=NS))
def raw_style(r):
    p=r.find('w:rPr',NS)
    return E.tostring(p,method='c14n') if p is not None else b''

def checked_style(r):
    """Ignore only an unused font hint for explicitly Western ASCII prose."""
    p=r.find('w:rPr',NS)
    if p is None:return b''
    p=copy.deepcopy(p)
    f=p.find('w:rFonts',NS)
    value=r.find('w:t',NS).text or ''
    if (value.isascii() and f is not None and f.get(Q('ascii'))
            and f.get(Q('hAnsi'))==f.get(Q('ascii'))
            and f.get(Q('hint')) in ('eastAsia','default')):
        f.attrib.pop(Q('hint'),None)
    return E.tostring(p,method='c14n')

def changes(before,after):
    # Whole words keep a small rewrite from pairing unrelated single letters.
    pat=r'\w+|\s+|[^\w\s]'
    a=re.findall(pat,before); b=re.findall(pat,after)
    aa=[0];bb=[0]
    for t in a:aa.append(aa[-1]+len(t))
    for t in b:bb.append(bb[-1]+len(t))
    return [(aa[i],aa[j],after[bb[k]:bb[l]]) for tag,i,j,k,l in
            difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes() if tag!='equal']

def rewrite(p,after,highlight,span,field_set):
    before=visible(p)
    if not isinstance(after,str) or not after.strip() or any(x in after for x in '\r\n\t'):
        raise ValueError('Authored prose must be nonempty single-paragraph text')
    reason=span.paragraph_span_reason(p)
    if reason:raise ValueError(reason)
    if p.xpath('.//w:ins|.//w:del|.//w:moveFrom|.//w:moveTo|.//w:rPrChange|.//w:pPrChange',namespaces=NS):
        raise ValueError('Authored paragraph diff does not edit a revision-bearing paragraph')
    rows=[];barriers=[];offset=0
    for child in p:
        if child.tag==Q('pPr'):continue
        text=visible(child); end=offset+len(text)
        if span.eligible(child,field_set) and child.find('w:lastRenderedPageBreak',NS) is None:
            rows.append((offset,end,child))
        else:barriers.append((offset,end))
        offset=end
    ops=[]
    for start,end,value in changes(before,after):
        if any((start<a<end) or (start<b<end) or (a<end and start<b)
               for a,b in barriers):
            raise ValueError('Authored change crosses protected content or an XML boundary')
        touched=[r for a,b,r in rows if a<end and start<b]
        if start==end:
            # Prefer the following run at a shared text boundary; at paragraph
            # end, the preceding run supplies the retained style.
            hits=[r for a,b,r in rows if a<=start<b]
            if not hits:hits=[r for a,b,r in rows if a<start==b]
            touched=hits[-1:] if hits else []
        if not touched:raise ValueError('Authored change has no ordinary-text anchor')
        keys={checked_style(r) for r in touched}
        if len(keys)!=1:raise ValueError('Authored change crosses semantic run formatting')
        raw={raw_style(r) for r in touched}
        if len(raw)>1 and not (before[start:end]+value).isascii():
            raise ValueError('Font-hint equivalence is limited to ASCII prose')
        if len(raw)>1:
            for r in touched:
                f=r.find('w:rPr/w:rFonts',NS)
                if f is None or not f.get(Q('ascii')) or f.get(Q('ascii'))!=f.get(Q('hAnsi')):
                    raise ValueError('Font-hint equivalence requires explicit Western fonts')
        # New wording cannot acquire a numeric superscript or other text effect
        # merely because its insertion point abuts one.
        if value and any(r.xpath('./w:rPr/w:vertAlign|./w:rPr/w:sym|./w:rPr/w:vanish',namespaces=NS) for r in touched):
            raise ValueError('Authored prose cannot be written into special text formatting')
        ops.append((start,end,value,touched))
    # All refusal checks run before mutation; reverse order retains offsets.
    for start,end,value,touched in reversed(ops):
        first=touched[0]
        for a,b,r in reversed(rows):
            if r not in touched:continue
            t=r.find('w:t',NS);original=t.text or ''
            left=max(0,start-a);right=min(len(original),max(0,end-a))
            prefix=original[:left];suffix=original[right:]
            if r is first:
                if not highlight:
                    t.text=prefix+value+suffix;t.set(SPACE,'preserve')
                else:
                    t.text=prefix;t.set(SPACE,'preserve')
                    at=p.index(r)+1
                    if value:
                        p.insert(at,span.new_run(r,value,True));at+=1
                    if suffix:p.insert(at,span.new_run(r,suffix,False))
            else:t.text=prefix+suffix;t.set(SPACE,'preserve')
    if visible(p)!=after:raise ValueError('Authored prose result differs from exact selected paragraph')
    return [{'start':a,'end':b,'before':before[a:b],'after':v} for a,b,v,_ in ops]
