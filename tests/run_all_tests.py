"""Current PaperCraft technical coverage; no automatic editorial verdict."""
from pathlib import Path
import argparse,ast,hashlib,json,subprocess,sys,importlib.util
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);root=Path(__file__).resolve().parents[1]
    sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();sources={f.relative_to(root).as_posix():sha(f) for f in root.rglob('*.py') if '.git' not in f.parts and a.out.resolve() not in f.resolve().parents}
    failures=[]
    for f in sources:
        try:ast.parse((root/f).read_text(encoding='utf-8-sig'),filename=f)
        except (SyntaxError,UnicodeError) as e:failures.append({'file':f,'error':str(e)})
    cases=[('basic','run_tests.py','--work-dir'),('preservation','run_preservation_tests.py','--work-dir'),('integration','run_integration_tests.py','--out'),('effect','run_effect_record_tests.py','--out'),('review-packet','run_review_packet_tests.py','--out'),('representations','run_representation_tests.py','--out'),('units','run_unit_tests.py','--out')]
    rows=[{'suite':'syntax','status':'FAIL' if failures else 'PASS','failures':failures}]
    missing=[m for m in ['docx','lxml'] if importlib.util.find_spec(m) is None]
    if missing:
        (a.out/'test-summary.json').write_text(json.dumps({'status':'MISSING_DEPENDENCY','missing':missing,'unexecuted':[c[0] for c in cases],'suites':rows},indent=2),encoding='utf8');return 2
    for name,script,flag in cases:
        cmd=[sys.executable,'-B','-X','utf8',str(root/'tests'/script),flag,str(a.out/name)]
        try:r=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=240)
        except subprocess.TimeoutExpired:
            rows.append({'suite':name,'command':cmd,'status':'TIMEOUT'});continue
        status='PASS' if r.returncode==0 else 'MISSING_DEPENDENCY' if 'ModuleNotFoundError' in r.stderr else 'FAIL'
        row={'suite':name,'command':cmd,'status':status,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
        rp=a.out/name/'results.json'
        if name=='units' and rp.exists():row['unit_result']=json.loads(rp.read_text(encoding='utf8'));row['status']=row['unit_result']['status']
        rows.append(row)
    # README source fixture -> public build -> verify, including a compact report.
    cmds=[('readme-fixture',[root/'examples/complex-word/build_fixture.py','--out',a.out/'readme-source']),('readme-build',[root/'scripts/review_docx.py','build',a.out/'readme-source/input.docx',a.out/'readme-source/plan.json',a.out/'readme-output','--clean']),('readme-verify',[root/'scripts/review_docx.py','verify',a.out/'readme-source/input.docx',a.out/'readme-output/input_清洁候选稿.docx'])]
    for name,args in cmds:
        cmd=[sys.executable,'-B','-X','utf8',*map(str,args)];r=subprocess.run(cmd,cwd=a.out,capture_output=True,text=True,encoding='utf8',errors='replace');rows.append({'suite':name,'command':cmd,'status':'PASS' if r.returncode==0 else 'FAIL','exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
    unchanged=all((root/f).is_file() and sha(root/f)==h for f,h in sources.items())
    data={'status':'PASS' if all(r['status']=='PASS' for r in rows) and unchanged else 'FAIL','suites':rows,'source_hashes':sources,'source_unchanged':unchanged,'effect_review':'NOT_TESTED_BY_SUITES','visual_review':'NOT_RUN_BY_SCRIPT'}
    (a.out/'test-summary.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'status':data['status'],'suites':[(r['suite'],r['status']) for r in rows]}));return int(data['status']!='PASS')
if __name__=='__main__':raise SystemExit(main())
