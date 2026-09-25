"""Exercise preservation failures that object counts alone would miss; synthetic documents only."""
import argparse
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
from unittest.mock import patch
import zipfile

from lxml import etree as E

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


A = load('preservation_under_test', ROOT / 'scripts/audit_preservation.py')
D = load('dependencies_under_test', ROOT / 'scripts/check_dependencies.py')
B = load('baseline_fixture', ROOT / 'tests/run_tests.py')


def run(work):
    work.mkdir(parents=True, exist_ok=False)
    source = B.make_fixture(work / 'fixture')
    with zipfile.ZipFile(source) as archive:
        base = {name: archive.read(name) for name in archive.namelist()}
    # Add a numeric citation without inventing any external literature.
    root = E.fromstring(base['word/document.xml'])
    first_text = root.xpath('//w:p/w:r/w:t', namespaces=A.NS)[0]
    first_text.text += ' [1]'
    link = E.SubElement(root.xpath('//w:p', namespaces=A.NS)[0], f'{{{A.W}}}hyperlink')
    link.set(f'{{{A.W}}}anchor', 'TeachingSource')
    E.SubElement(E.SubElement(link, f'{{{A.W}}}r'), f'{{{A.W}}}t').text = ' Teaching locator'
    base['word/document.xml'] = E.tostring(root)
    source = work / 'source.docx'

    def write(name, parts):
        target = work / name
        with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
            for key, value in parts.items():
                archive.writestr(key, value)
        return target

    write(source.name, base)
    source_hash = A.digest(source.read_bytes())
    declaration = 'Author information, funding and public-data status remain pending. No author approval is asserted.'
    policy = {'protected_paragraphs': [{'label': 'declaration', 'text': declaration, 'mode': 'xml'}], 'lock_citation_tokens': True}
    results = []

    def case(name, func):
        try:
            detail = func()
            results.append({'case': name, 'status': 'PASS', 'detail': detail})
        except Exception as exc:
            results.append({'case': name, 'status': 'FAIL', 'detail': repr(exc)})

    def mutate(name, change, part='word/document.xml'):
        parts = dict(base)
        tree = E.fromstring(parts[part])
        change(tree)
        parts[part] = E.tostring(tree)
        return write(name + '.docx', parts)

    def detected(name, change, key, part='word/document.xml'):
        candidate = mutate(name, change, part)
        report = A.audit(source, candidate, policy)
        assert report['technical_status'] == 'FAIL' and report['status'] == 'FAIL', report
        assert report['checks'][key]['status'] == 'FAIL', report
        if key in {'native_math_content', 'tables'}:
            assert report['counts']['source'] == report['counts']['candidate'], 'Test should keep object counts unchanged'
        (work / (name + '.json')).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        return f'{key} failure detected; top-level failure propagated'

    def unchanged():
        report = A.audit(source, source, policy)
        assert report['status'] == report['technical_status'] == 'PASS'
        assert report['scientific_correctness'] == report['visual_review'] == 'NOT_RUN'
        assert report['author_acceptance'] is False
        return report['counts']

    case('unchanged_content_and_status_separation', unchanged)

    def remove_math(tree):
        for node in tree.xpath('//m:oMath', namespaces=A.NS):node.getparent().remove(node)
    no_math = mutate('without-native-math', remove_math)
    def empty_math():
        report = A.audit(no_math, no_math, policy)
        assert report['technical_status'] == 'PASS'
        assert report['checks']['native_math_content']['status'] == report['checks']['native_math_xml']['status'] == 'NOT_EXERCISED'
        return 'Empty pair does not claim nonempty native-math coverage'
    case('zero_native_math_not_exercised', empty_math)
    def math_count_change(before, after):
        report = A.audit(before, after, policy)
        assert report['technical_status'] == report['status'] == 'FAIL'
        assert report['checks']['native_math_content']['status'] == 'FAIL'
        return 'Adding or deleting every formula remains a detected content change'
    case('all_native_math_deleted_still_fails', lambda: math_count_change(source, no_math))
    case('native_math_added_to_empty_still_fails', lambda: math_count_change(no_math, source))

    def adjacent_prose():
        def change(tree):
            math = tree.xpath('//m:oMath', namespaces=A.NS)[0]
            run = E.Element(f'{{{A.W}}}r')
            E.SubElement(run, f'{{{A.W}}}t').text = 'Meaning of the unchanged teaching formula: '
            math.addprevious(run)
        report = A.audit(source, mutate('adjacent-prose', change), policy)
        assert report['status'] == 'PASS', report
        return 'Native formula and protected content remain identical while adjacent prose changes'

    case('formula_adjacent_prose_edit_supported', adjacent_prose)
    case('same_count_formula_value_change_detected', lambda: detected('math-value', lambda t: setattr(t.xpath('//m:t', namespaces=A.NS)[0], 'text', 's = T_candidate / T_control'), 'native_math_content'))
    case('same_count_table_value_change_detected', lambda: detected('table-value', lambda t: setattr(t.xpath('//w:tbl//w:t', namespaces=A.NS)[4], 'text', '999'), 'tables'))

    def merge_change(tree):
        cell = tree.xpath('//w:tc', namespaces=A.NS)[0]
        props = cell.find(f'{{{A.W}}}tcPr')
        if props is None:
            props = E.Element(f'{{{A.W}}}tcPr')
            cell.insert(0, props)
        E.SubElement(props, f'{{{A.W}}}gridSpan').set(f'{{{A.W}}}val', '2')
    case('table_merge_change_detected', lambda: detected('table-merge', merge_change, 'tables'))
    case('field_target_change_detected', lambda: detected('field-target', lambda t: t.xpath('//w:fldSimple', namespaces=A.NS)[0].set(f'{{{A.W}}}instr', ' REF OtherSource '), 'fields'))
    case('bookmark_change_detected', lambda: detected('bookmark', lambda t: t.xpath('//w:bookmarkStart', namespaces=A.NS)[0].set(f'{{{A.W}}}name', 'OtherSource'), 'bookmarks'))
    case('hyperlink_anchor_change_detected', lambda: detected('hyperlink', lambda t: t.xpath('//w:hyperlink', namespaces=A.NS)[0].set(f'{{{A.W}}}anchor', 'OtherSource'), 'hyperlinks'))
    case('footnote_content_change_detected', lambda: detected('footnote', lambda t: setattr(t.xpath('//w:t', namespaces=A.NS)[0], 'text', 'Changed note'), 'protected_parts', 'word/footnotes.xml'))

    def declaration_change(tree):
        node = next(n for n in tree.xpath('//w:p', namespaces=A.NS) if A.visible_text(n) == declaration)
        node.xpath('.//w:t', namespaces=A.NS)[0].text = 'All authors have approved this submission.'
    case('protected_declaration_change_detected', lambda: detected('declaration', declaration_change, 'protected_paragraphs'))
    case('citation_token_change_detected', lambda: detected('citation', lambda t: setattr(t.xpath('//w:p/w:r/w:t', namespaces=A.NS)[0], 'text', 'An efficient execution method [2]'), 'numeric_citation_tokens'))

    def formatting_only():
        def change(tree):
            run = tree.xpath('//m:r', namespaces=A.NS)[0]
            prop = E.Element(f'{{{A.W}}}rPr')
            E.SubElement(prop, f'{{{A.W}}}color').set(f'{{{A.W}}}val', '334455')
            run.insert(0, prop)
        report = A.audit(source, mutate('math-format', change), policy)
        assert report['checks']['native_math_content']['status'] == 'PASS'
        assert report['checks']['native_math_xml']['status'] == 'REVIEW_REQUIRED'
        assert report['status'] == 'REVIEW_REQUIRED'
        return 'Formatting difference needs review; math equality alone does not produce overall PASS'
    case('math_format_difference_requires_review', formatting_only)

    def unconfigured():
        report = A.audit(source, source)
        assert report['status'] == 'REVIEW_REQUIRED'
        assert report['checks']['protected_paragraphs']['status'] == 'NOT_CONFIGURED'
        return 'No false declaration-preservation claim without explicit policy'
    case('missing_protection_policy_is_explicit', unconfigured)

    def bad_policy():
        try:
            A.audit(source, source, {'protected_paragraphs': [{'text': 'This paragraph is absent.'}]})
        except ValueError as exc:
            return str(exc)
        raise AssertionError('Source-absent policy was accepted')
    case('nonexistent_source_protection_rejected', bad_policy)

    def missing_dependency():
        original = D.importlib.util.find_spec
        with patch.object(D.importlib.util, 'find_spec', side_effect=lambda name: None if name == 'docx' else original(name)):
            report = D.check(ROOT, require=['docx'])
        assert report['status'] == 'FAIL' and report['missing_required_capabilities'] == ['docx']
        return 'Required docx dependency failure is explicit and affects the overall status'
    case('missing_required_import_fails', missing_dependency)

    def missing_renderer():
        report = D.check(ROOT, work / 'not-installed', work / 'absent-soffice.exe', require=['render'])
        assert report['status'] == 'FAIL' and report['missing_required_capabilities'] == ['render']
        assert report['render_execution'] == 'NOT_RUN'
        return 'Missing renderer and soffice fail dependency preflight without attempting or claiming render'
    case('missing_renderer_dependency_fails', missing_renderer)
    case('input_file_unchanged', lambda: 'Source SHA-256 unchanged' if A.digest(source.read_bytes()) == source_hash else (_ for _ in ()).throw(AssertionError('Source changed')))
    summary = {'passed': sum(r['status'] == 'PASS' for r in results), 'total': len(results), 'results': results,
               'scope': 'Synthetic structural/negative tests; no visual or manuscript-effect acceptance'}
    (work / 'test-results.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return all(r['status'] == 'PASS' for r in results)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work-dir', type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(0 if run(args.work_dir.resolve()) else 1)
