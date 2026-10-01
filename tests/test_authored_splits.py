"""Actual XML boundaries: split ordinary text; retain or reject complex nodes."""
import importlib.util
from pathlib import Path
import unittest
from lxml import etree as E

ROOT = Path(__file__).resolve().parents[1]
def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    obj = importlib.util.module_from_spec(spec); spec.loader.exec_module(obj)
    return obj
A = module('apply_authored_edits'); D = module('review_docx')

def paragraph(inner):
    body = E.fromstring(('<w:body xmlns:w="' + A.W + '" xmlns:m="' + A.M + '"><w:p>' + inner + '</w:p></w:body>').encode())
    return body, body[0]

class AuthoredSplits(unittest.TestCase):
    def test_equation_and_italic_run_remain_exact(self):
        body, p = paragraph('<w:pPr><w:spacing w:after="80"/></w:pPr><w:r><w:t>Use </w:t></w:r><m:oMath><m:r><m:t>x</m:t></m:r></m:oMath><w:r><w:t> safely. Next decision.</w:t></w:r><w:r><w:rPr><w:i/></w:rPr><w:t>y</w:t></w:r>')
        math = E.tostring(p[2]); italic = E.tostring(p[-1]); original = D.text(p)
        tail = A.split_once(p, 'safely.', D.text)
        self.assertEqual(D.text(p) + D.text(tail), original)
        self.assertEqual(E.tostring(body.find('.//m:oMath', A.NS)), math)
        self.assertEqual(E.tostring(tail[-1]), italic)
        self.assertEqual(E.tostring(p[0]), E.tostring(tail[0]))

    def test_refuses_inside_equation(self):
        _, p = paragraph('<w:r><w:t>Value </w:t></w:r><m:oMath><m:r><m:t>xy</m:t></m:r></m:oMath><w:r><w:t> remains.</w:t></w:r>')
        before = E.tostring(p)
        with self.assertRaisesRegex(ValueError, 'protected or complex'): A.split_once(p, 'x', D.text)
        self.assertEqual(E.tostring(p), before)

    def test_refuses_history_and_fields(self):
        for node in ['<w:ins w:id="1"><w:r><w:t>old</w:t></w:r></w:ins>', '<w:fldSimple w:instr="REF x"><w:r><w:t>2</w:t></w:r></w:fldSimple>', '<w:r><w:fldChar w:fldCharType="begin"/></w:r>']:
            with self.subTest(node=node):
                _, p = paragraph('<w:r><w:t>Keep. Continue </w:t></w:r>' + node)
                before = E.tostring(p)
                with self.assertRaisesRegex(ValueError, 'unsupported'): A.split_once(p, 'Keep.', D.text)
                self.assertEqual(E.tostring(p), before)

    def test_refuses_ambiguous_or_empty_boundary(self):
        for marker in ['Keep', 'end.']:
            _, p = paragraph('<w:r><w:t>Keep Keep end.</w:t></w:r>')
            with self.assertRaises(ValueError): A.split_once(p, marker, D.text)

    def test_link_can_move_intact_but_not_be_sliced(self):
        _, p = paragraph('<w:r><w:t>Boundary. </w:t></w:r><w:hyperlink w:anchor="source"><w:r><w:t>Source link</w:t></w:r></w:hyperlink>')
        before = E.tostring(p[-1]); tail = A.split_once(p, 'Boundary.', D.text)
        self.assertEqual(E.tostring(tail[-1]), before)
        with self.assertRaisesRegex(ValueError, 'protected or complex'): A.split_once(tail, 'Source', D.text)

if __name__ == '__main__': unittest.main()
