from pathlib import Path
import copy,hashlib,json,sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_effect_record import audit
class EffectDecisions(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);arts=[]
        for name,text in [('old','Clear but verbose'),('new','Short but ambiguous')]:
            p=self.root/(name+'.txt');p.write_text(text);arts.append({'id':name,'path':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        ev=[{'artifact':'old','locator':'whole paragraph'},{'artifact':'new','locator':'whole paragraph'}]
        self.base={'schema_version':2,'reviewer':'Unit fixture; not an actual reader','artifacts':arts,'requirements':[{'id':'R1','requested_effect':'Clearer reading','baseline_observation':'Verbose and precise','candidate_observation':'Short but implies unsupported cause','assessment':'mixed','remaining':['Clarify cause before use'],'evidence':ev,'dimensions':[{'name':'length burden','assessment':'improved','baseline_observation':'Repeated prose','candidate_observation':'One sentence','evidence':ev},{'name':'meaning','assessment':'regressed','baseline_observation':'Qualified association','candidate_observation':'Unqualified cause','evidence':ev}],'tradeoff':'Lower length does not compensate for wrong causal meaning','decision':{'action':'rollback','reason':'Keep the scientifically clear paragraph','chosen_artifact':'old','rollback_to':'old'}}]}
    def tearDown(self):self.temp.cleanup()
    def result(self,d):p=self.root/'record.json';p.write_text(json.dumps(d));return audit(p)
    def test_mixed_and_rollback_recorded_without_effect_approval(self):
        r=self.result(self.base);self.assertEqual(r['technical_status'],'PASS');self.assertEqual(r['overall_status'],'REVIEW_REQUIRED');self.assertEqual(r['recorded_decisions'][0]['decision']['chosen_artifact'],'old')
    def test_mixed_without_regression_dimension_is_invalid(self):
        d=copy.deepcopy(self.base);d['requirements'][0]['dimensions'].pop();self.assertEqual(self.result(d)['technical_status'],'FAIL')
    def test_rollback_to_missing_file_is_invalid(self):
        d=copy.deepcopy(self.base);d['requirements'][0]['decision']['rollback_to']='missing';self.assertEqual(self.result(d)['technical_status'],'FAIL')
    def test_explicit_regression_is_recordable(self):
        d=copy.deepcopy(self.base);d['requirements'][0]['assessment']='regressed';self.assertEqual(self.result(d)['technical_status'],'PASS')
    def test_missing_decision_is_not_silent_partial(self):
        d=copy.deepcopy(self.base);d['requirements'][0].pop('decision');self.assertEqual(self.result(d)['technical_status'],'FAIL')
if __name__=='__main__':unittest.main()
