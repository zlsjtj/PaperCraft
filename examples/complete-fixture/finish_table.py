"""Finish the known DEMO table header without changing any of its nine data rows.

This intentionally changes the table/header XML; it does not claim whole-table
preservation. It refuses other table identities and preserves every data-row XML
element, all non-table document content, media, and all other ZIP members.
"""
from pathlib import Path
import argparse,copy,hashlib,json,zipfile
from lxml import etree as E

W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS={'w':W};Q=lambda s:'{'+W+'}'+s
OLD=['condition','assembly','setup_min','max_abs_difference_kPa','leak_check']
NEW=['Condition','Assembly','Setup (min)','Max. absolute difference (kPa)','Leak check']
WIDTH_MM=[21,42,25,48,24]
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(x):return E.tostring(x,method='c14n',exclusive=True)
def get(node,tag):
 x=node.find('w:'+tag,NS)
 if x is None:
  x=E.Element(Q(tag))
  if tag in {'tblPr','trPr','tcPr','pPr','rPr'}:node.insert(0,x)
  else:node.append(x)
 return x
def text(n):return ''.join(n.xpath('.//w:t/text()',namespaces=NS))
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args()
 if a.out.exists() or a.receipt.exists():raise ValueError('Preserve existing outputs; choose new paths')
 with zipfile.ZipFile(a.source) as z:
  infos=z.infolist();parts={i.filename:z.read(i.filename) for i in infos}
 root=E.fromstring(parts['word/document.xml']);before=copy.deepcopy(root)
 tables=root.xpath('./w:body/w:tbl',namespaces=NS)
 if len(tables)!=1:raise ValueError('This example requires its one known table')
 table=tables[0];rows=table.findall('w:tr',NS)
 if len(rows)!=10:raise ValueError('Expected one header plus exactly nine DEMO records')
 cells=rows[0].findall('w:tc',NS)
 if [text(c) for c in cells]!=OLD:raise ValueError('Unexpected header identity')
 data_before=[canonical(r) for r in rows[1:]]
 if [text(r) for r in rows[1:]] != ['C1three hoses8.40.12pass','C1reference base3.10.13pass','C2three hoses8.00.11pass','C2reference base3.00.12pass','C3three hoses8.60.14pass','C3reference base3.30.14pass','C1base without pins2.7NAfail','C2base without pins2.6NAfail','C3base without pins2.80.15pass']:
  raise ValueError('Known fixed DEMO data changed')
 widths=[round(v*1440/25.4) for v in WIDTH_MM]
 props=get(table,'tblPr');tw=get(props,'tblW');tw.set(Q('w'),str(sum(widths)));tw.set(Q('type'),'dxa')
 get(props,'tblLayout').set(Q('type'),'fixed')
 grid=get(table,'tblGrid')
 for c in list(grid):grid.remove(c)
 for width in widths:E.SubElement(grid,Q('gridCol'),{Q('w'):str(width)})
 get(get(rows[0],'trPr'),'tblHeader')
 for cell,label,width in zip(cells,NEW,widths):
  ts=cell.xpath('./w:p/w:r/w:t',namespaces=NS)
  if len(ts)!=1 or cell.xpath('.//w:drawing|.//w:fldChar|.//w:hyperlink',namespaces=NS):raise ValueError('Header not an ordinary single-text cell')
  ts[0].text=label
  cp=get(cell,'tcPr');cw=get(cp,'tcW');cw.set(Q('w'),str(width));cw.set(Q('type'),'dxa')
  shade=get(cp,'shd');shade.set(Q('val'),'clear');shade.set(Q('color'),'auto');shade.set(Q('fill'),'E9EFF3')
  get(cp,'vAlign').set(Q('val'),'center')
  for run in cell.xpath('./w:p/w:r',namespaces=NS):
   rp=get(run,'rPr');get(rp,'b');get(rp,'sz').set(Q('val'),'20')
   get(rp,'color').set(Q('val'),'243A45')
 if [canonical(r) for r in rows[1:]]!=data_before:raise ValueError('Data-row XML changed')
 outside=copy.deepcopy(root);new_table=outside.xpath('./w:body/w:tbl',namespaces=NS)[0]
 new_table.getparent().replace(new_table,copy.deepcopy(before.xpath('./w:body/w:tbl',namespaces=NS)[0]))
 if canonical(outside)!=canonical(before):raise ValueError('Non-table body content changed')
 parts['word/document.xml']=E.tostring(root,encoding='UTF-8',xml_declaration=True,standalone=True)
 a.out.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(a.out,'w') as z:
  for i in infos:z.writestr(i,parts[i.filename])
 with zipfile.ZipFile(a.out) as z:
  rr=E.fromstring(z.read('word/document.xml')).xpath('./w:body/w:tbl/w:tr',namespaces=NS)
  assert [canonical(r) for r in rr[1:]]==data_before
  with zipfile.ZipFile(a.source) as old:
   assert all(z.read(n)==old.read(n) for n in old.namelist() if n!='word/document.xml')
 receipt={'technical_status':'PASS','source_sha256':sha(a.source.read_bytes()),'output_sha256':sha(a.out.read_bytes()),'script_sha256':sha(Path(__file__).read_bytes()),'trigger':'Lead editor examined the exact clean/review/report pages and found a code-style broken table header on page 3. This is a subsequent page-layout repair, after the first output and one self-review.','changed':{'header_before':OLD,'header_after':NEW,'column_width_mm':WIDTH_MM,'header_font_pt':10,'header_bold':True,'header_fill':'#E9EFF3','fixed_table_layout':True,'repeat_header':True},'preserved':{'data_rows':9,'entire_data_row_xml_identical':True,'data_row_sha256':[sha(v) for v in data_before],'non_table_document_content_identical':True,'all_media_and_other_zip_members_identical':True},'whole_table_xml_identical':False,'science_and_figure_changes':'none','final_page_rendering':'separate lead-editor step','author_acceptance':False}
 a.receipt.parent.mkdir(parents=True,exist_ok=True);a.receipt.write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps({'status':'PASS','preserved_data_rows':9,'out':str(a.out)}))
if __name__=='__main__':main()
