"""Regression for bounded authored prose through fragmented Western runs."""
from pathlib import Path
import copy, importlib.util, json, subprocess, sys, tempfile, unittest
from lxml import etree as E
from docx import Document

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import review_docx as D
import rewrite_prose_runs as R

class AuthoredRunRewrite(unittest.TestCase):
    def paragraph(self,values=('The old cl', 'aim holds.')):
        p=E.Element(D.Q('p'))
        for i,s in enumerate(values):
            r=E.SubElement(p,D.Q('r'));rp=E.SubElement(r,D.Q('rPr'))
            f=E.SubElement(rp,D.Q('rFonts'));f.set(D.Q('ascii'),'Times New Roman');f.set(D.Q('hAnsi'),'Times New Roman')
            if i%2:f.set(D.Q('hint'),'eastAsia')
            t=E.SubElement(r,D.Q('t'));t.text=s
        return p
    def edit(self,p,value,highlight=False):
        return R.rewrite(p,value,highlight,D.SPAN,set())
    def test_ascii_hint_bridge_preserves_original_nodes(self):
        p=self.paragraph();nodes=list(p);props=[D.canonical(r.find('w:rPr',D.NS)) for r in p]
        changes=self.edit(p,'The revised explanation holds.')
        self.assertEqual(list(p),nodes)
        self.assertEqual([D.canonical(r.find('w:rPr',D.NS)) for r in p],props)
        self.assertEqual(R.visible(p),'The revised explanation holds.')
        self.assertTrue(changes)
    def test_yellow_only_insertions_and_deletion_receipt(self):
        p=self.paragraph();ds=self.edit(p,'The revised explanation holds.',True)
        yellows=p.xpath('./w:r[w:rPr/w:highlight]/w:t/text()',namespaces=D.NS)
        self.assertEqual(yellows,['revised','explanation'])
        self.assertEqual([x['before'] for x in ds],['old','claim'])
        self.assertEqual(R.visible(p),'The revised explanation holds.')
    def test_real_format_boundaries_rejected_without_mutation(self):
        for tag,attrs in [('i',{}),('vertAlign',{'val':'superscript'}),('highlight',{'val':'green'}),('lang',{'val':'fr-FR'}),('rStyle',{'val':'Emphasis'})]:
            with self.subTest(tag=tag):
                p=self.paragraph();rp=p[1].find('w:rPr',D.NS);n=E.SubElement(rp,D.Q(tag))
                for k,v in attrs.items():n.set(D.Q(k),v)
                original=D.canonical(p)
                with self.assertRaises(ValueError):self.edit(p,'The revised explanation holds.')
                self.assertEqual(D.canonical(p),original)
    def test_font_change_and_nonascii_hint_rejected(self):
        p=self.paragraph();p[1].find('w:rPr/w:rFonts',D.NS).set(D.Q('hAnsi'),'Arial')
        with self.assertRaises(ValueError):self.edit(p,'The revised explanation holds.')
        p=self.paragraph(('The old cl', 'áim holds.'))
        with self.assertRaises(ValueError):self.edit(p,'The revised explanation holds.')
    def test_protected_boundaries_rejected(self):
        for xml in [f'<w:bookmarkStart xmlns:w="{D.W}" w:id="1" w:name="a"/>',
                    f'<w:r xmlns:w="{D.W}"><w:lastRenderedPageBreak/></w:r>',
                    f'<w:r xmlns:w="{D.W}"><w:fldChar w:fldCharType="begin"/></w:r>',
                    f'<m:oMath xmlns:m="{D.M}"/>']:
            p=self.paragraph();p.insert(1,E.fromstring(xml));original=D.canonical(p)
            with self.assertRaises(ValueError):self.edit(p,'The revised explanation holds.')
            self.assertEqual(D.canonical(p),original)
    def test_unchanged_protected_neighbour_retained(self):
        p=self.paragraph(('The old claim holds.',' More text.'))
        marker=E.fromstring(f'<w:bookmarkStart xmlns:w="{D.W}" w:id="1" w:name="a"/>');p.insert(1,marker)
        sig=D.canonical(marker)
        self.edit(p,'The revised claim holds. More text.')
        self.assertEqual(D.canonical(marker),sig)
    def test_visible_math_is_not_duplicated_or_editable(self):
        p=self.paragraph(('The old claim.',' More text.'))
        math=E.fromstring(f'<m:oMath xmlns:m="{D.M}"><m:r><m:t>x</m:t></m:r></m:oMath>');p.insert(1,math)
        sig=D.canonical(math)
        self.edit(p,'The revised claim.x More text.')
        self.assertEqual(R.visible(p),'The revised claim.x More text.')
        self.assertEqual(D.canonical(math),sig)
        original=D.canonical(p)
        with self.assertRaises(ValueError):self.edit(p,'The revised claim.y More text.')
        self.assertEqual(D.canonical(p),original)
    def test_cli_expect_hash_and_repeated_text(self):
        with tempfile.TemporaryDirectory() as folder:
            folder=Path(folder);src=folder/'input.docx';doc=Document();doc.add_paragraph('The old claim. The old claim.');doc.save(src)
            inv=D.inventory(src);row=inv['paragraphs'][0]
            self.assertTrue(row['authored_prose_diff']['available'])
            before=src.read_bytes()
            edit={'paragraph_id':'P0001','operation':'rewrite_prose_preserving_runs','before':row['text'],'after':'The revised claim. The old claim.','reason':'test exact paragraph','source':['fixture']}
            plan=folder/'edits.json';plan.write_text(json.dumps({'source_sha256':D.sha(before),'edits':[edit]}),encoding='utf8')
            cmd=[sys.executable,'-B',str(ROOT/'scripts/apply_authored_edits.py'),'--source',str(src),'--edits',str(plan),'--skill',str(ROOT),'--out',str(folder/'out')]
            r=subprocess.run(cmd,capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr)
            self.assertEqual((folder/'out/clean.txt').read_text(),edit['after'])
            self.assertEqual(src.read_bytes(),before)
            edit['before']='Stale text';plan.write_text(json.dumps({'source_sha256':D.sha(before),'edits':[edit]}),encoding='utf8');cmd[-1]=str(folder/'bad')
            r=subprocess.run(cmd,capture_output=True,text=True);self.assertNotEqual(r.returncode,0)
            self.assertEqual(src.read_bytes(),before);self.assertFalse((folder/'bad/clean.docx').exists())
            edit['before']=row['text'];plan.write_text(json.dumps({'edits':[edit]}),encoding='utf8');cmd[-1]=str(folder/'no-hash')
            r=subprocess.run(cmd,capture_output=True,text=True);self.assertNotEqual(r.returncode,0)
            self.assertEqual(src.read_bytes(),before);self.assertFalse((folder/'no-hash/clean.docx').exists())

if __name__=='__main__':unittest.main()
