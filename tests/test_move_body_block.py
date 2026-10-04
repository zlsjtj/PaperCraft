import hashlib,importlib.util,sys,tempfile,unittest,zipfile
from pathlib import Path
from lxml import etree as E
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('move_body',ROOT/'scripts/move_body_block.py');M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
class BlockMoves(unittest.TestCase):
 def root(self,middle=''):
  return E.fromstring(('<w:document xmlns:w="'+M.W+'" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"><w:body><w:p><w:r><w:t>Before</w:t></w:r></w:p><w:p><w:r><w:t>Result</w:t></w:r>'+middle+'</w:p><w:tbl><w:tr><w:tc><w:p><w:r><w:t>Evidence</w:t></w:r></w:p></w:tc></w:tr></w:tbl><w:p><w:r><w:t>Interpretation</w:t></w:r></w:p><w:sectPr/></w:body></w:document>').encode())
 def plan(self,r,first=2,last=3,anchor=4):
  b=list(r.find('w:body',M.NS));return dict(first=first,last=last,anchor=anchor,placement='after',block_xml_sha256=[M.sha(M.canonical(x)) for x in b[first-1:last]],anchor_xml_sha256=M.sha(M.canonical(b[anchor-1])))
 def test_moves_formula_and_table_intact(self):
  r=self.root('<m:oMath><m:r><m:t>x+y</m:t></m:r></m:oMath>');n,order=M.move_root(r,self.plan(r));self.assertEqual(order,[1,4,2,3,5]);self.assertEqual(M.canonical(r[0][1]),M.canonical(n[0][2]))
 def test_rejects_stale_hash(self):
  r=self.root();p=self.plan(r);p['block_xml_sha256'][0]='bad'
  with self.assertRaisesRegex(ValueError,'contents differ'):M.move_root(r,p)
 def test_rejects_split_bookmark(self):
  r=self.root('<w:bookmarkStart w:id="1" w:name="result"/>');r[0][3].append(E.fromstring(('<w:bookmarkEnd xmlns:w="'+M.W+'" w:id="1"/>').encode()))
  with self.assertRaisesRegex(ValueError,'split a bookmark'):M.move_root(r,self.plan(r))
 def test_rejects_split_field(self):
  r=self.root('<w:r><w:fldChar w:fldCharType="begin"/></w:r>');r[0][3].append(E.fromstring(('<w:r xmlns:w="'+M.W+'"><w:fldChar w:fldCharType="end"/></w:r>').encode()))
  with self.assertRaisesRegex(ValueError,'split a complex field'):M.move_root(r,self.plan(r))
 def test_rejects_revision(self):
  r=self.root('<w:ins w:id="4"><w:r><w:t>Old revision</w:t></w:r></w:ins>')
  with self.assertRaisesRegex(ValueError,'Revision/comment'):M.move_root(r,self.plan(r))
 def test_rejects_field_payload_without_endpoints(self):
  r=self.root();r[0][0].append(E.fromstring(('<w:r xmlns:w="'+M.W+'"><w:fldChar w:fldCharType="begin"/></w:r>').encode()));r[0][3].append(E.fromstring(('<w:r xmlns:w="'+M.W+'"><w:fldChar w:fldCharType="end"/></w:r>').encode()))
  with self.assertRaisesRegex(ValueError,'split a complex field'):M.move_root(r,self.plan(r))
 def test_rejects_insertion_inside_bookmark(self):
  r=self.root('<w:bookmarkEnd w:id="9"/>');r[0][0].append(E.fromstring(('<w:bookmarkStart xmlns:w="'+M.W+'" w:id="9" w:name="a"/>').encode()))
  with self.assertRaisesRegex(ValueError,'Insertion point'):M.move_root(r,self.plan(r,first=3,last=3,anchor=1))
 def test_rejects_section(self):
  r=self.root('<w:pPr><w:sectPr/></w:pPr>')
  with self.assertRaisesRegex(ValueError,'Section boundaries'):M.move_root(r,self.plan(r))
 def test_preserves_zip_media_and_refuses_overwrite(self):
  with tempfile.TemporaryDirectory() as t:
   src=Path(t)/'in.docx';out=Path(t)/'out.docx';r=self.root()
   with zipfile.ZipFile(src,'w') as z:z.writestr('word/document.xml',E.tostring(r));z.writestr('word/media/a.png',b'raw fixture');z.writestr('word/_rels/document.xml.rels',b'rels fixture')
   p=self.plan(r);p['input_sha256']=M.sha(src.read_bytes());M.apply(src,p,out)
   with zipfile.ZipFile(out) as z:self.assertEqual(z.read('word/media/a.png'),b'raw fixture')
   with self.assertRaisesRegex(ValueError,'already exists'):M.apply(src,p,out)
if __name__=='__main__':unittest.main()
