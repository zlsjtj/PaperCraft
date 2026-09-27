from pathlib import Path
import copy,json,sys,tempfile,unittest,importlib.util,subprocess,os
from lxml import etree as E
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from review_docx import read_package,apply_plan,build,verify_pair,NS,canonical,text
from docx_spans import protected_history,field_runs
spec=importlib.util.spec_from_file_location('fixture',ROOT/'examples/complex-word/build_fixture.py');fixture=importlib.util.module_from_spec(spec);spec.loader.exec_module(fixture)

class ComplexSpans(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.dir=Path(self.temp.name);self.doc,self.plan=fixture.build(self.dir/'source');self.root=read_package(self.doc)[2]
    def tearDown(self):self.temp.cleanup()
    def test_safe_local_prose_with_history_fields_math_and_styles(self):
        for highlight in (False,True):
            revised,changes=apply_plan(self.root,self.plan,highlight)
            self.assertEqual(protected_history(self.root),protected_history(revised))
            self.assertEqual(field_runs(self.root)[1],field_runs(revised)[1])
            for query in ['//m:oMath','//w:hyperlink','//w:tbl','//w:r[w:rPr/w:i]','//w:r[w:rPr/w:highlight[@w:val="green"]]']:
                self.assertEqual([canonical(x) for x in self.root.xpath(query,namespaces=NS)],[canonical(x) for x in revised.xpath(query,namespaces=NS)])
            self.assertIn(self.plan['operations'][0]['spans'][0]['after'],changes[0]['after'])
            self.assertEqual(len(revised.xpath('//w:highlight[@w:val="yellow"]',namespaces=NS)),int(highlight))
    def test_build_preserves_package_and_compact_report(self):
        out=self.dir/'built';payload=build(self.doc,self.dir/'source/plan.json',out,True)
        for name in ['input_包装审阅版.docx','input_清洁候选稿.docx']:self.assertEqual(verify_pair(self.doc,out/name)['status'],'PASS')
        report=read_package(out/'input_诊断报告.docx')[2];rt=text(report)
        self.assertIn('局部修改记录',rt);self.assertNotIn('主贡献与标题',rt);self.assertNotIn('贡献与证据',rt)
    def refuse(self,before):
        plan=copy.deepcopy(self.plan);plan['operations'][0]['spans'][0]['before']=before
        with self.assertRaises(ValueError):apply_plan(self.root,plan,True)
    def test_refuse_formula(self):self.refuse('T = R × P')
    def test_refuse_field_result(self):self.refuse('Table 1')
    def test_refuse_hyperlink(self):self.refuse('the model note')
    def test_refuse_history(self):self.refuse('Prior insertion.')
    def test_refuse_existing_highlight(self):self.refuse('Measurement pending.')
    def test_refuse_cross_style(self):self.refuse('T is defined')
    def test_wrong_expected_text_leaves_input_unchanged(self):
        old=self.doc.read_bytes();self.plan['operations'][0]['expect']='wrong';p=self.dir/'bad.json';p.write_text(json.dumps(self.plan),encoding='utf8')
        with self.assertRaises(ValueError):build(self.doc,p,self.dir/'bad-output',True)
        self.assertEqual(old,self.doc.read_bytes());self.assertFalse((self.dir/'bad-output').exists())
    def test_verify_rejects_silent_acceptance_of_history(self):
        from review_docx import write_package
        infos,parts,root=read_package(self.doc);ins=root.xpath('//w:ins',namespaces=NS)[0];ins.getparent().remove(ins)
        out=self.dir/'accepted.docx';write_package(out,infos,parts,root)
        with self.assertRaises(ValueError):verify_pair(self.doc,out)
    def test_same_style_split_run_span(self):
        root=copy.deepcopy(self.root);p=root.xpath('//w:body/w:p',namespaces=NS)[2];r=p[0];r.find('w:t',NS).text='The design ';r2=copy.deepcopy(r);r2.find('w:t',NS).text='proves better cooling. ';p.insert(1,r2)
        revised,_=apply_plan(root,self.plan,False);self.assertIn('temperature rise',text(revised))
    def test_cli_unicode_output_does_not_fail_after_publishing(self):
        out=self.dir/'cli-output';cmd=[sys.executable,'-B',str(ROOT/'scripts/review_docx.py'),'build',str(self.doc),str(self.dir/'source/plan.json'),str(out),'--clean']
        r=subprocess.run(cmd,capture_output=True,env=dict(os.environ,PYTHONIOENCODING='ascii',PYTHONUTF8='0'))
        self.assertEqual(r.returncode,0,r.stderr.decode('utf8',errors='replace'))
        receipt=json.loads(r.stdout.decode('utf8'));self.assertEqual(receipt['checks']['status'],'PASS')
        self.assertTrue((out/'input_清洁候选稿.docx').exists())
if __name__=='__main__':unittest.main()
