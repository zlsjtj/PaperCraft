"""Word pagination caches must not block prose or duplicate on highlighting."""
from pathlib import Path
import importlib.util,unittest
from lxml import etree as E

P=Path(__file__).resolve().parents[1]/'scripts/review_docx.py'
spec=importlib.util.spec_from_file_location('page_cache_review',P);D=importlib.util.module_from_spec(spec);spec.loader.exec_module(D)
W=D.W

class PageCacheTests(unittest.TestCase):
    def make(self,middle):
        return E.fromstring(f'<w:document xmlns:w="{W}"><w:body><w:p><w:r><w:rPr><w:i/></w:rPr>{middle}</w:r></w:p></w:body></w:document>')
    def edit(self,root,before='old',after='clearer',highlight=True):
        plan={'operations':[{'id':'C1','kind':'replace_span','target':'P0001','expect':D.text(D.paragraphs(root)[0]),'spans':[{'before':before,'after':after}],'purpose':'fix prose','evidence':'fixture','confirm':False}]}
        return D.apply_plan(root,plan,highlight)[0]
    def test_prefix_cache_and_new_highlight_once(self):
        root=self.make('<w:lastRenderedPageBreak/><w:t>prefix old suffix</w:t>')
        out=self.edit(root)
        self.assertEqual(D.text(out),'prefix clearer suffix')
        self.assertEqual(len(out.findall('.//w:lastRenderedPageBreak',D.NS)),1)
        self.assertEqual([D.text(r) for r in out.xpath('//w:r[w:rPr/w:highlight]',namespaces=D.NS)],['clearer'])
        self.assertTrue(all(r.find('w:rPr/w:i',D.NS) is not None for r in out.findall('.//w:r',D.NS)))
        p=D.paragraphs(out)[0];self.assertIsNotNone(p[0].find('w:lastRenderedPageBreak',D.NS))
    def test_both_sides_cache_deletion_retains_order(self):
        root=self.make('<w:lastRenderedPageBreak/><w:t>old</w:t><w:lastRenderedPageBreak/>')
        out=self.edit(root,after='')
        self.assertEqual(D.text(out),'')
        self.assertEqual(len(out.findall('.//w:lastRenderedPageBreak',D.NS)),2)
    def test_hard_break_remains_blocked(self):
        root=self.make('<w:br w:type="page"/><w:t>old</w:t>')
        with self.assertRaisesRegex(ValueError,'0 eligible'):self.edit(root)
    def test_old_highlight_remains_blocked(self):
        root=self.make('<w:lastRenderedPageBreak/><w:t>old</w:t>')
        E.SubElement(root.find('.//w:rPr',D.NS),D.Q('highlight')).set(D.Q('val'),'green')
        with self.assertRaisesRegex(ValueError,'0 eligible'):self.edit(root)
    def test_page_cache_not_crossed(self):
        root=self.make('<w:t>prefix </w:t>');p=D.paragraphs(root)[0]
        r=E.SubElement(p,D.Q('r'));E.SubElement(r,D.Q('lastRenderedPageBreak'));E.SubElement(r,D.Q('t')).text='old'
        with self.assertRaisesRegex(ValueError,'0 eligible'):self.edit(root,'prefix old')

if __name__=='__main__':unittest.main()
