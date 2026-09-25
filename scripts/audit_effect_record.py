"""Check requirement/artifact bindings, not persuasion, aesthetics or author approval."""
from pathlib import Path
import argparse, hashlib, json

ASSESSMENTS = {'improved', 'equivalent', 'partial', 'unmet', 'pending'}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def audit(record_path):
    record_path = Path(record_path).resolve()
    d = json.loads(record_path.read_text(encoding='utf-8-sig'))
    errors, inputs = [], []
    if d.get('schema_version') != 1:
        errors.append('Unsupported schema_version')
    artifacts = d.get('artifacts', [])
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError('artifacts must be a nonempty list')
    ids = [a.get('id') for a in artifacts]
    if any(not isinstance(i, str) or not i for i in ids) or len(ids) != len(set(ids)):
        errors.append('Artifact IDs must be nonempty and unique')
    for a in artifacts:
        path = a.get('path')
        if not isinstance(path, str) or not path:
            errors.append(f'Missing path: {a.get("id")}'); continue
        p = (record_path.parent / path).resolve()
        if not p.is_file():
            errors.append(f'Missing artifact: {a.get("id")}'); continue
        actual = sha(p)
        inputs.append({'id': a.get('id'), 'path': str(p), 'sha256': actual})
        if actual != a.get('sha256'):
            errors.append(f'Artifact hash mismatch: {a.get("id")}')
    rows = d.get('requirements', [])
    if not isinstance(rows, list) or not rows:
        raise ValueError('requirements must be a nonempty list')
    requirement_ids = [r.get('id') for r in rows]
    if any(not isinstance(i, str) or not i for i in requirement_ids) or len(requirement_ids) != len(set(requirement_ids)):
        errors.append('Requirement IDs must be nonempty and unique')
    for r in rows:
        label = r.get('id')
        for key in ['requested_effect', 'baseline_observation', 'candidate_observation']:
            if not isinstance(r.get(key), str) or not r[key].strip():
                errors.append(f'{label}: missing {key}')
        if r.get('assessment') not in ASSESSMENTS:
            errors.append(f'{label}: unrecognized assessment')
        remaining = r.get('remaining')
        if not isinstance(remaining, list) or any(not isinstance(x, str) or not x.strip() for x in remaining):
            errors.append(f'{label}: remaining must be a list of nonempty strings')
        if r.get('assessment') in {'partial', 'unmet', 'pending'} and not remaining:
            errors.append(f'{label}: unresolved outcome needs a stated remaining issue')
        ev = r.get('evidence', [])
        if not isinstance(ev, list) or not ev:
            errors.append(f'{label}: missing artifact evidence'); continue
        for e in ev:
            if e.get('artifact') not in ids:
                errors.append(f'{label}: unknown evidence artifact')
            if not isinstance(e.get('locator'), str) or not e['locator'].strip():
                errors.append(f'{label}: missing evidence locator')
    if not isinstance(d.get('reviewer'), str) or not d['reviewer'].strip():
        errors.append('Missing reviewer identity/scope')
    return {'technical_status': 'FAIL' if errors else 'PASS',
            'overall_status': 'REVIEW_REQUIRED',
            'scope': 'Record completeness and exact file bindings only. Does not judge observations, inspect locators semantically or verify author acceptance.',
            'record_sha256': sha(record_path), 'artifacts': inputs,
            'requirements_checked': len(rows), 'errors': errors,
            'recorded_assessments': {s: sum(r.get('assessment') == s for r in rows) for s in sorted(ASSESSMENTS)}}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('record', type=Path); ap.add_argument('--out', required=True, type=Path)
    a = ap.parse_args()
    if a.out.exists():
        ap.error('Output exists; use a new path')
    try:
        result = audit(a.record)
    except (ValueError, TypeError, AttributeError, OSError) as exc:
        result = {'technical_status': 'FAIL', 'overall_status': 'REVIEW_REQUIRED', 'errors': [str(exc)], 'scope': __doc__}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'technical_status': result['technical_status'], 'overall_status': result['overall_status'], 'errors': result['errors']}, ensure_ascii=False))
    return 0 if result['technical_status'] == 'PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
