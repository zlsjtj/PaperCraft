"""Read-only DOCX preservation audit. Equality is not scientific or visual validation."""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re
import zipfile

from lxml import etree as E

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
R = 'http://schemas.openxmlformats.org/package/2006/relationships'
NS = {'w': W, 'm': M}


def digest(value):
    data = value if isinstance(value, bytes) else json.dumps(value, ensure_ascii=False, sort_keys=True).encode('utf-8')
    return hashlib.sha256(data).hexdigest()


def canonical(node):
    node = deepcopy(node)
    node.tail = None
    return E.tostring(node, method='c14n', exclusive=True, with_comments=False)


def math_content(node):
    """Keep math structure, strings and attributes; exclude run display properties only."""
    if node.tag in {f'{{{W}}}rPr', f'{{{M}}}ctrlPr'}:
        return None
    attrs = {k: v for k, v in node.attrib.items() if not k.startswith(f'{{{W}}}rsid')}
    children = [value for child in node if isinstance(child.tag, str) and (value := math_content(child)) is not None]
    return [node.tag, attrs, node.text if node.tag in {f'{{{M}}}t', f'{{{W}}}t'} else None, children]


def visible_text(node):
    return ''.join(node.xpath('.//w:t/text() | .//m:t/text()', namespaces=NS))


def table_content(table):
    rows = []
    for row in table.xpath('.//w:tr', namespaces=NS):
        if row.xpath('ancestor::w:tbl[1]', namespaces=NS)[0] is not table:
            continue
        cells = []
        for cell in row.findall(f'{{{W}}}tc'):
            props = cell.find(f'{{{W}}}tcPr')
            merge = [] if props is None else [canonical(x).decode() for x in props if E.QName(x).localname in {'gridSpan', 'vMerge', 'hMerge'}]
            # Paragraph boundaries and tabs matter for a table's data, not just concatenated text.
            paragraphs = []
            for paragraph in cell.xpath('./w:p', namespaces=NS):
                tokens = []
                for n in paragraph.iter():
                    if n.tag in {f'{{{W}}}t', f'{{{M}}}t'}:
                        tokens.append(['text', n.text or ''])
                    elif n.tag in {f'{{{W}}}tab', f'{{{W}}}br'}:
                        tokens.append([E.QName(n).localname])
                paragraphs.append(tokens)
            cells.append({'merge': merge, 'paragraphs': paragraphs,
                          'math': [math_content(n) for n in cell.xpath('.//m:oMath', namespaces=NS)]})
        rows.append(cells)
    return rows


def inventory(path):
    path = Path(path).resolve()
    with zipfile.ZipFile(path) as archive:
        if archive.testzip():
            raise ValueError('Corrupt DOCX ZIP')
        parts = {n: archive.read(n) for n in archive.namelist()}
    if 'word/document.xml' not in parts:
        raise ValueError('Missing word/document.xml')
    parser = E.XMLParser(resolve_entities=False, no_network=True)
    trees = {n: E.fromstring(data, parser) for n, data in parts.items()
             if n.startswith('word/') and n.endswith('.xml')}
    # Include equations and protected structures in notes/headers, not only the main body.
    maths, tables, fields, bookmarks, refs, hyperlinks, paragraph_records = [], [], [], [], [], [], []
    drawings = 0
    for part, root in sorted(trees.items()):
        for i, n in enumerate(root.xpath('//m:oMath', namespaces=NS)):
            maths.append({'part': part, 'index': i, 'content': digest(math_content(n)), 'xml': digest(canonical(n))})
        for n in root.xpath('//w:tbl', namespaces=NS):
            tables.append([part, table_content(n)])
        for n in root.xpath('//w:fldSimple | //w:instrText | //w:fldChar', namespaces=NS):
            fields.append([part, E.QName(n).localname, n.text, dict(n.attrib)])
        for n in root.xpath('//w:bookmarkStart | //w:bookmarkEnd', namespaces=NS):
            bookmarks.append([part, E.QName(n).localname, dict(n.attrib)])
        for n in root.xpath('//w:footnoteReference | //w:endnoteReference | //w:commentReference', namespaces=NS):
            refs.append([part, E.QName(n).localname, dict(n.attrib)])
        for n in root.xpath('//w:hyperlink', namespaces=NS):
            hyperlinks.append([part, dict(n.attrib), visible_text(n)])
        drawings += len(root.xpath('//w:drawing', namespaces=NS))
        for n in root.xpath('//w:p', namespaces=NS):
            paragraph_records.append({'part': part, 'text': visible_text(n), 'xml': digest(canonical(n))})
    relationships = []
    for part, data in sorted(parts.items()):
        if part.endswith('.rels'):
            root = E.fromstring(data, parser)
            for n in root:
                # Image relationships can legitimately change during figure revision.
                if n.get('Type', '').endswith(('/hyperlink', '/footnotes', '/endnotes', '/comments', '/bibliography')):
                    relationships.append([part, dict(n.attrib)])
    protected_parts = {n: digest(data) for n, data in parts.items()
                       if re.match(r'^word/(?:footnotes|endnotes|comments|bibliography)(?:\d+)?\.xml$', n)
                       or n.startswith('customXml/') and b'bibliography' in data[:2000]}
    citations = sorted(Counter(re.findall(r'\[\d+(?:\s*(?:[,;–-])\s*\d+)*\]', '\n'.join(x['text'] for x in paragraph_records))).items())
    return {'path': str(path), 'sha256': digest(path.read_bytes()), 'math': maths, 'tables': tables,
            'fields': fields, 'bookmarks': bookmarks, 'references': refs, 'hyperlinks': hyperlinks, 'relationships': relationships,
            'drawings': drawings, 'protected_parts': protected_parts,
            'paragraphs': paragraph_records, 'numeric_citation_tokens': citations}


def audit(source, candidate, policy=None):
    a, b = inventory(source), inventory(candidate)
    policy = policy or {}
    if not isinstance(policy, dict):
        raise ValueError('Policy must be a JSON object')
    unknown = set(policy) - {'protected_paragraphs', 'lock_citation_tokens'}
    if unknown:
        raise ValueError(f'Unknown policy keys: {sorted(unknown)}')
    if 'lock_citation_tokens' in policy and not isinstance(policy['lock_citation_tokens'], bool):
        raise ValueError('lock_citation_tokens must be Boolean')
    checks = {}

    def compare(name, before, after):
        same = before == after
        checks[name] = {'status': 'PASS' if same else 'FAIL', 'source_sha256': digest(before), 'candidate_sha256': digest(after)}
        if not same and isinstance(before, list) and isinstance(after, list):
            checks[name]['different_indices'] = [i for i in range(max(len(before), len(after)))
                                                   if i >= len(before) or i >= len(after) or before[i] != after[i]]
        return same

    compare('native_math_content', [[n['part'], n['content']] for n in a['math']], [[n['part'], n['content']] for n in b['math']])
    exact = compare('native_math_xml', [[n['part'], n['xml']] for n in a['math']], [[n['part'], n['xml']] for n in b['math']])
    if not exact and checks['native_math_content']['status'] == 'PASS':
        checks['native_math_xml']['status'] = 'REVIEW_REQUIRED'
        checks['native_math_xml']['note'] = 'Math content equal; exact XML differs. Review formatting and rendering.'
    if not a['math'] and not b['math']:
        for key in ['native_math_content', 'native_math_xml']:
            checks[key]['status'] = 'NOT_EXERCISED'
            checks[key]['note'] = 'Neither file contains native math; this input does not exercise native-math preservation.'
    for key in ['tables', 'fields', 'bookmarks', 'references', 'hyperlinks', 'relationships', 'drawings', 'protected_parts']:
        compare(key, a[key], b[key])
    protected = policy.get('protected_paragraphs', [])
    if not isinstance(protected, list):
        raise ValueError('protected_paragraphs must be an array')
    passages = []
    for i, rule in enumerate(protected):
        if not isinstance(rule, dict) or not isinstance(rule.get('text'), str) or not rule['text']:
            raise ValueError(f'Protected paragraph {i} requires nonempty text')
        if set(rule) - {'label', 'text', 'mode'}:
            raise ValueError(f'Unknown protected paragraph fields: {i}')
        mode = rule.get('mode', 'text')
        if mode not in {'text', 'xml'}:
            raise ValueError(f'Unsupported protection mode: {mode}')
        original = [p for p in a['paragraphs'] if p['text'] == rule['text']]
        revised = [p for p in b['paragraphs'] if p['text'] == rule['text']]
        if not original:
            raise ValueError(f'Protected paragraph absent in source: {rule.get("label", i)}')
        equal = len(original) == len(revised)
        if mode == 'xml':
            equal = equal and Counter(p['xml'] for p in original) == Counter(p['xml'] for p in revised)
        passages.append({'label': rule.get('label', str(i)), 'mode': mode, 'source_count': len(original),
                         'candidate_count': len(revised), 'status': 'PASS' if equal else 'FAIL'})
    checks['protected_paragraphs'] = {'status': ('PASS' if all(p['status'] == 'PASS' for p in passages) else 'FAIL') if passages else 'NOT_CONFIGURED', 'items': passages}
    if policy.get('lock_citation_tokens', False):
        compare('numeric_citation_tokens', a['numeric_citation_tokens'], b['numeric_citation_tokens'])
    else:
        checks['numeric_citation_tokens'] = {'status': 'NOT_CONFIGURED', 'note': 'Manual citation review remains required; numeric bracket tokens are optional.'}
    states = [c['status'] for c in checks.values()]
    technical = 'FAIL' if 'FAIL' in states else 'PASS'
    status = 'FAIL' if technical == 'FAIL' else ('REVIEW_REQUIRED' if 'REVIEW_REQUIRED' in states or not passages else 'PASS')
    return {'tool': 'PaperCraft preservation audit 2.3.0', 'source': {k: a[k] for k in ['path', 'sha256']},
            'candidate': {k: b[k] for k in ['path', 'sha256']}, 'status': status,
            'technical_status': technical, 'checks': checks,
            'counts': {'source': {'native_math': len(a['math']), 'tables': len(a['tables']), 'drawings': a['drawings']},
                       'candidate': {'native_math': len(b['math']), 'tables': len(b['tables']), 'drawings': b['drawings']}},
            'scientific_correctness': 'NOT_RUN', 'visual_review': 'NOT_RUN', 'author_acceptance': False,
            'limits': ['Preservation does not establish mathematical correctness or equivalence of prose.',
                       'Figure content and every prose number require separate evidence/visual review.',
                       'Protected text covers only explicit policy rules; manual author-year citations are not parsed.',
                       'Authorized formula or table content changes require a separate located content audit.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('--policy', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    try:
        policy = json.loads(args.policy.read_text(encoding='utf-8')) if args.policy else None
        result = audit(args.source, args.candidate, policy)
    except (ValueError, zipfile.BadZipFile, E.XMLSyntaxError) as exc:
        parser.error(str(exc))
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        args.out.write_text(output + '\n', encoding='utf-8')
    print(output)
    return 1 if result['technical_status'] == 'FAIL' else 0


if __name__ == '__main__':
    raise SystemExit(main())
