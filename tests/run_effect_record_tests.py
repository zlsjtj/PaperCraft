"""Portable record binding controls; not tests of editorial quality."""
from pathlib import Path
import argparse, copy, hashlib, json, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from audit_effect_record import audit

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False)
    artifact=out/'candidate.txt';artifact.write_text('A real test artifact, not a manuscript quality claim.',encoding='utf-8')
    base={'schema_version':1,'reviewer':'Fixture author; metadata test only',
      'artifacts':[{'id':'candidate','path':'candidate.txt','sha256':hashlib.sha256(artifact.read_bytes()).hexdigest()}],
      'requirements':[{'id':'R1','requested_effect':'Make the mapped item locatable','baseline_observation':'No file binding',
      'candidate_observation':'File binding exists','assessment':'improved','remaining':[],
      'evidence':[{'artifact':'candidate','locator':'line 1'}]}]}
    rows=[]
    def case(name,mutate,expected):
        d=copy.deepcopy(base);mutate(d);p=out/(name+'.json');p.write_text(json.dumps(d),encoding='utf-8')
        result=audit(p);assert result['technical_status']==expected,(name,result)
        assert result['overall_status']=='REVIEW_REQUIRED'
        rows.append({'name':name,'status':'PASS','expected_technical':expected,'actual':result})
    case('valid_bindings_not_effect_certification',lambda d:None,'PASS')
    case('hash_mismatch',lambda d:d['artifacts'][0].update(sha256='0'*64),'FAIL')
    case('missing_file',lambda d:d['artifacts'][0].update(path='missing.txt'),'FAIL')
    case('unknown_evidence_artifact',lambda d:d['requirements'][0]['evidence'][0].update(artifact='absent'),'FAIL')
    case('missing_locator',lambda d:d['requirements'][0]['evidence'][0].update(locator=''),'FAIL')
    case('duplicate_requirement',lambda d:d['requirements'].append(copy.deepcopy(d['requirements'][0])),'FAIL')
    case('unresolved_without_reason',lambda d:d['requirements'][0].update(assessment='partial'),'FAIL')
    case('honest_partial_is_valid_record',lambda d:d['requirements'][0].update(assessment='partial',remaining=['Visual review still needed']),'PASS')
    source=out/'valid_bindings_not_effect_certification.json';protected=artifact.read_bytes()
    proc=subprocess.run([sys.executable,str(ROOT/'scripts/audit_effect_record.py'),str(source),'--out',str(artifact)],capture_output=True)
    assert proc.returncode!=0 and artifact.read_bytes()==protected
    rows.append({'name':'existing_output_refused','status':'PASS','exit_code':proc.returncode})
    (out/'test-results.json').write_text(json.dumps({'tests':rows,'passed':len(rows),'total':len(rows),'scope':__doc__},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'passed':len(rows),'total':len(rows)}))
if __name__=='__main__':main()
