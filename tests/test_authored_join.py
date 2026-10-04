"""Regression for the actual adjacent-prose join needed by the long introduction."""
from pathlib import Path
import importlib.util,unittest
from lxml import etree as E

spec=importlib.util.spec_from_file_location('authored_adapter',Path(__file__).resolve().parents[1]/'scripts/apply_authored_edits.py')
A=importlib.util.module_from_spec(spec);spec.loader.exec_module(A)
W=A.W;Q=A.Q
def text(n):return ''.join(n.xpath('.//w:t/text()',namespaces=A.NS))
def fixture():
 body=E.Element(Q('body'),nsmap={'w':W})
 for words in ['Injection precedent.',' Host stability precedent.']:
  p=E.SubElement(body,Q('p'));pp=E.SubElement(p,Q('pPr'));E.SubElement(pp,Q('spacing')).set(Q('line'),'480')
  r=E.SubElement(p,Q('r'));E.SubElement(r,Q('t')).text=words
 return body
class JoinTests(unittest.TestCase):
 def test_adjacent_equal_properties_retains_child_identity_and_bookmark(self):
  body=fixture();left,right=list(body)
  start=E.Element(Q('bookmarkStart'));start.set(Q('id'),'7');start.set(Q('name'),'host')
  end=E.Element(Q('bookmarkEnd'));end.set(Q('id'),'7')
  right.insert(1,start);right.append(end)
  children=list(right)[1:];signatures=[E.tostring(n,method='c14n') for n in children]
  A.join_next(left,text(right),text(left)+text(right),text,'')
  self.assertEqual(len(body),1)
  self.assertEqual(text(left),'Injection precedent. Host stability precedent.')
  self.assertTrue(all(n.getparent() is left for n in children))
  self.assertEqual([E.tostring(n,method='c14n') for n in children],signatures)
 def test_rejects_format_difference_without_mutation(self):
  body=fixture();left,right=list(body);right.find('w:pPr/w:spacing',A.NS).set(Q('line'),'240')
  before=E.tostring(body)
  with self.assertRaisesRegex(ValueError,'identical paragraph properties'):
   A.join_next(left,text(right),text(left)+text(right),text,'')
  self.assertEqual(E.tostring(body),before)
 def test_rejects_field_revision_and_section(self):
  for tag in ['fldChar','ins','sectPr','br','drawing']:
   with self.subTest(tag=tag):
    body=fixture();left,right=list(body);E.SubElement(right,Q(tag));before=E.tostring(body)
    with self.assertRaisesRegex(ValueError,'unsupported'):
     A.join_next(left,text(right),text(left)+text(right),text,'')
    self.assertEqual(E.tostring(body),before)
 def test_cannot_jump_over_table(self):
  body=fixture();left,right=list(body);body.insert(1,E.Element(Q('tbl')))
  with self.assertRaisesRegex(ValueError,'immediately adjacent'):
   A.join_next(left,text(right),text(left)+text(right),text,'')
 def test_exact_text_required_before_any_mutation(self):
  body=fixture();left,right=list(body);before=E.tostring(body)
  for nxt,after in [('wrong',text(left)+text(right)),(text(right),'omitted study')]:
   with self.assertRaises(ValueError):A.join_next(left,nxt,after,text,'')
   self.assertEqual(E.tostring(body),before)
if __name__=='__main__':unittest.main()
