"""Move one verified, contiguous block of DOCX body objects without rebuilding it.

This implements an editorial decision; it does not choose a better order or
renumber citations. Child indices refer to the exact input document, from one.
"""
from pathlib import Path
import argparse,copy,hashlib,json,zipfile
from lxml import etree as E

W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS={'w':W};Q=lambda s:'{'+W+'}'+s
sha=lambda b:hashlib.sha256(b).hexdigest()
canonical=lambda n:E.tostring(n,method='c14n')

def inspect(path):
    with zipfile.ZipFile(path) as z:
        root=E.fromstring(z.read('word/document.xml'))
    body=root.find('w:body',NS)
    return {'input_sha256':sha(Path(path).read_bytes()),'children':[
        {'index':i,'type':E.QName(n).localname,'xml_sha256':sha(canonical(n)),
         'text':''.join(n.xpath('.//w:t/text()',namespaces=NS))}
        for i,n in enumerate(body,1)]}

def move_root(root,plan):
    new=copy.deepcopy(root);body=new.find('w:body',NS);original=list(body)
    if new.xpath('//w:commentRangeStart|//w:commentRangeEnd|//w:moveFromRangeStart|//w:moveFromRangeEnd|//w:moveToRangeStart|//w:moveToRangeEnd',namespaces=NS):
        raise ValueError('Comment or tracked-move ranges require a separate supported workflow')
    first,last,anchor=plan['first'],plan['last'],plan['anchor']
    if any(type(v) is not int for v in (first,last,anchor)) or not 1<=first<=last<=len(original) or not 1<=anchor<=len(original):
        raise ValueError('Invalid one-based body indices')
    if first<=anchor<=last:raise ValueError('Anchor is inside the block')
    if plan.get('placement') not in ('before','after'):raise ValueError('Specify before or after')
    selected=original[first-1:last];target=original[anchor-1]
    if any(n.tag not in (Q('p'),Q('tbl')) or n.xpath('.//w:sectPr',namespaces=NS) for n in selected+[target]):
        raise ValueError('Section boundaries or unsupported body children cannot move')
    if [sha(canonical(n)) for n in selected]!=plan['block_xml_sha256'] or sha(canonical(target))!=plan['anchor_xml_sha256']:
        raise ValueError('Body contents differ from the inspected source')
    selected_nodes={n for child in selected for n in child.iter()}
    # A field or bookmark cannot be split by the move, including fields that
    # start outside and finish inside the selected block.
    stack=[];bookmarks={}
    for node in new.iter():
        inside=node in selected_nodes
        if stack and inside!=stack[-1]:raise ValueError('Move would split a complex field')
        if bookmarks and any(inside!=value for value in bookmarks.values()):raise ValueError('Move would split a bookmark')
        if node.tag==Q('fldChar'):
            kind=node.get(Q('fldCharType'))
            if kind=='begin':stack.append(inside)
            elif kind in ('separate','end'):
                if not stack:raise ValueError('Unbalanced complex field')
                if inside!=stack[-1]:raise ValueError('Move would split a complex field')
                if kind=='end':stack.pop()
        if node.tag==Q('bookmarkStart'):
            ident=node.get(Q('id'))
            if ident in bookmarks:raise ValueError('Duplicate bookmark start')
            bookmarks[ident]=inside
        elif node.tag==Q('bookmarkEnd'):
            ident=node.get(Q('id'))
            if ident not in bookmarks:raise ValueError('Unbalanced bookmark')
            if bookmarks.pop(ident)!=inside:raise ValueError('Move would split a bookmark')
        if inside and E.QName(node).localname in ('ins','del','moveFrom','moveTo','pPrChange','rPrChange','commentRangeStart','commentRangeEnd','commentReference') and E.QName(node).namespace==W:
            raise ValueError('Revision/comment-bearing block requires a separate supported workflow')
    if stack or bookmarks:raise ValueError('Unbalanced fields or bookmarks')
    # The insertion point must not lie inside a field/bookmark spanning body
    # children. A wholly self-contained field in the anchor is fine.
    boundary=anchor if plan['placement']=='after' else anchor-1
    active_fields=0;active_bookmarks=set()
    for child in original[:boundary]:
        for node in child.iter():
            if node.tag==Q('fldChar'):
                if node.get(Q('fldCharType'))=='begin':active_fields+=1
                elif node.get(Q('fldCharType'))=='end':active_fields-=1
            elif node.tag==Q('bookmarkStart'):active_bookmarks.add(node.get(Q('id')))
            elif node.tag==Q('bookmarkEnd'):active_bookmarks.discard(node.get(Q('id')))
    if active_fields or active_bookmarks:raise ValueError('Insertion point is inside a field or bookmark')
    for n in selected:body.remove(n)
    at=body.index(target)+(plan['placement']=='after')
    for offset,n in enumerate(selected):body.insert(at+offset,n)
    # Every original subtree remains byte-equivalent after canonicalization.
    if sorted(map(canonical,original))!=sorted(map(canonical,body)):
        raise AssertionError('A body subtree changed')
    mapping=[original.index(n)+1 for n in body]
    return new,mapping

def apply(source,plan,output):
    source,output=Path(source),Path(output)
    if output.exists():raise ValueError('Output already exists')
    if sha(source.read_bytes())!=plan['input_sha256']:raise ValueError('Different source revision')
    with zipfile.ZipFile(source) as z:
        if z.testzip():raise ValueError('Invalid input ZIP')
        infos=z.infolist();parts={i.filename:z.read(i.filename) for i in infos}
    root=E.fromstring(parts['word/document.xml']);new,mapping=move_root(root,plan)
    output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w') as z:
        for info in infos:
            value=E.tostring(new,xml_declaration=True,encoding='UTF-8',standalone=True) if info.filename=='word/document.xml' else parts[info.filename]
            z.writestr(info,value)
    with zipfile.ZipFile(output) as z:
        assert all(z.read(k)==v for k,v in parts.items() if k!='word/document.xml')
    receipt={'input_sha256':plan['input_sha256'],'output_sha256':sha(output.read_bytes()),
             'new_order_original_child_indices':mapping,'body_subtrees':'IDENTICAL_MULTISET',
             'other_zip_parts':'BYTE_IDENTICAL','effect_review':'NOT_RUN',
             'not_performed':['reference renumbering','field refresh','page rendering','scientific or reading assessment']}
    output.with_suffix(output.suffix+'.move.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),'utf8')
    return receipt

def main():
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='cmd',required=True)
    i=s.add_parser('inspect');i.add_argument('input',type=Path);i.add_argument('--out',type=Path,required=True)
    m=s.add_parser('move');m.add_argument('input',type=Path);m.add_argument('plan',type=Path);m.add_argument('output',type=Path)
    a=p.parse_args()
    if a.cmd=='inspect':a.out.write_text(json.dumps(inspect(a.input),ensure_ascii=False,indent=2),'utf8')
    else:print(json.dumps(apply(a.input,json.loads(a.plan.read_text('utf8')),a.output)))
if __name__=='__main__':main()
