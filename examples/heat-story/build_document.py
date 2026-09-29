"""Common typography for all trial conditions; does not edit their wording."""
from pathlib import Path
import argparse, json, re, hashlib
from docx import Document
from docx.shared import Mm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def blocks(text):
    lines=text.splitlines(); result=[]; i=0
    while i<len(lines):
        s=lines[i].strip()
        if not s:i+=1;continue
        if s.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                cells=[v.strip() for v in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-{2,}:?',v or '?') for v in cells):rows.append(cells)
                i+=1
            assert rows and all(len(r)==len(rows[0]) for r in rows), rows
            result.append(('table',rows));continue
        if s.startswith('#'):
            m=re.match(r'^(#{1,3})\s+(.+)',s);assert m,s
            result.append(('h'+str(len(m[1])),m[2]));i+=1;continue
        if s.startswith('Equation:'):
            result.append(('math',s.removeprefix('Equation:').strip()));i+=1;continue
        if s.startswith(('```','$$','![')):
            raise ValueError('Use the documented plain math/Markdown subset; unsupported block: '+s)
        para=[s];i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(('#','|','Equation:')):
            para.append(lines[i].strip());i+=1
        result.append(('p',' '.join(para)))
    return result

def plain(s):
    s=re.sub(r'\*\*(.+?)\*\*',r'\1',s)
    s=re.sub(r'\*([^*]+)\*',r'\1',s)
    return re.sub(r'`([^`]+)`',r'\1',s)
def inline(p,s,yellow=False):
    for token in re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)',s):
        if not token:continue
        r=p.add_run(token.strip('*`') if token.startswith(('*','`')) else token)
        if token.startswith('**'):r.bold=True
        elif token.startswith('*'):r.italic=True
        if yellow:
            h=OxmlElement('w:highlight');h.set(qn('w:val'),'yellow');r._element.get_or_add_rPr().append(h)

def build(source,out,base=None,review=False,figures=None,font=None,font_bold=None):
    if out.exists():raise FileExistsError('Use a new output path: '+str(out))
    if not font or not font_bold:raise ValueError('Provide --font and --font-bold for actual table text measurement')
    bs=blocks(source.read_text(encoding='utf8'))
    old={plain(str(x)) for k,x in blocks(base.read_text(encoding='utf8')) if k!='table'} if base else set()
    d=Document(); sec=d.sections[0]
    sec.page_width=Mm(210);sec.page_height=Mm(297)
    sec.left_margin=sec.right_margin=Mm(22);sec.top_margin=Mm(21);sec.bottom_margin=Mm(20)
    table_width=166  # Fit complete table identifiers and header words at 9.5 pt.
    for name,size in [('Normal',11),('Title',16),('Heading 1',12.5),('Heading 2',11.5),('Caption',10)]:
        st=d.styles[name];st.font.name='Times New Roman';st.font.size=Pt(size);st.font.color.rgb=RGBColor(0,0,0)
        fonts=st._element.get_or_add_rPr().get_or_add_rFonts()
        fonts.set(qn('w:eastAsia'),'Microsoft YaHei')
        for attr in ['asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme']:
            fonts.attrib.pop(qn('w:'+attr),None)
        st.paragraph_format.line_spacing=1.12;st.paragraph_format.space_after=Pt(6)
        st.paragraph_format.widow_control=True
        if name!='Normal':st.paragraph_format.keep_with_next=True
        for node in list(st._element.xpath('.//w:pBdr')):node.getparent().remove(node)
    d.styles['Title'].paragraph_format.space_after=Pt(12)
    d.styles['Caption'].font.bold=False
    d.styles['Caption'].font.italic=False
    for n in ['Heading 1','Heading 2']:d.styles[n].paragraph_format.space_before=Pt(10)
    h=sec.header.paragraphs[0];h.text='Synthetic research example — no real measurements';h.style='Caption'
    for r in h.runs:r.font.size=Pt(8.5);r.font.color.rgb=RGBColor.from_string('666666')
    f=sec.footer.paragraphs[0];f.alignment=WD_ALIGN_PARAGRAPH.CENTER
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');f._p.append(field)
    changed=[]
    for j,(kind,value) in enumerate(bs):
        yellow=review and kind not in ('table','math') and plain(str(value)) not in old
        if kind=='table':
            t=d.add_table(rows=1,cols=len(value[0]));t.autofit=False
            chars=[max(len(plain(r[c])) for r in value) for c in range(len(value[0]))]
            weights=[min(32,max(10,n)) for n in chars];total=sum(weights)
            widths=[table_width*w/total for w in weights]
            if len(value[0])>8:
                from PIL import ImageFont
                face=ImageFont.truetype(str(font),38)
                bold=ImageFont.truetype(str(font_bold),38)
                minimum=[max([bold.getlength(s) for s in plain(value[0][c]).split()]+[face.getlength(s) for row in value[1:] for s in plain(row[c]).split()])*25.4/288+1.2 for c in range(len(value[0]))]
                body_min=[max(face.getlength(s) for row in value[1:] for s in plain(row[c]).split())*25.4/288+1.2 for c in range(len(value[0]))]
                if sum(body_min)>table_width:
                    raise ValueError('The data cannot fit at 9.5 pt with intact numeric tokens; redesign its column groups instead of shrinking text.')
                if sum(minimum)<=table_width:
                    widths=[w+(table_width-sum(minimum))/len(minimum) for w in minimum]
                else:
                    # Let words in the header wrap; never cut numeric data to fit.
                    fraction=(table_width-sum(body_min))/(sum(minimum)-sum(body_min))
                    widths=[b+(m-b)*fraction for b,m in zip(body_min,minimum)]
            for c,w in enumerate(widths):t.columns[c].width=Mm(w)
            pr=t._tbl.tblPr; borders=OxmlElement('w:tblBorders')
            for side in ['top','bottom','left','right','insideH','insideV']:
                edge=OxmlElement('w:'+side);edge.set(qn('w:val'),'single');edge.set(qn('w:sz'),'4');edge.set(qn('w:color'),'D9D9D9');borders.append(edge)
            pr.append(borders)
            for ri,row in enumerate(value):
                cells=t.rows[0].cells if ri==0 else t.add_row().cells
                trpr=cells[0]._tc.getparent().get_or_add_trPr()
                nosplit=OxmlElement('w:cantSplit');trpr.append(nosplit)
                if ri==0:trpr.append(OxmlElement('w:tblHeader'))
                for ci,s in enumerate(row):
                    cell=cells[ci];p=cell.paragraphs[0];p.paragraph_format.space_before=Pt(4);p.paragraph_format.space_after=Pt(4);p.paragraph_format.line_spacing=1.02
                    cell.width=Mm(widths[ci])
                    # Preserve adjacent repeated-key comparison groups across a page break.
                    # Unique first-column values do not create an arbitrary whole-table keep chain.
                    p.paragraph_format.keep_with_next=ri==0 or (ri+1<len(value) and value[ri][0]==value[ri+1][0])
                    numeric=bool(re.fullmatch(r'[\d.,%+−\-–/ ()]+',plain(s)))
                    p.alignment=WD_ALIGN_PARAGRAPH.RIGHT if numeric and ri else WD_ALIGN_PARAGRAPH.LEFT
                    inline(p,s)
                    for run in p.runs:run.font.size=Pt(9.5);run.bold=ri==0
                    tcpr=cell._tc.get_or_add_tcPr();va=OxmlElement('w:vAlign');va.set(qn('w:val'),'center');tcpr.append(va)
                    # Retain table font size while preventing identifiers/numbers from
                    # losing most of their width to Word's default cell padding.
                    if len(row)>8:
                        mar=OxmlElement('w:tcMar')
                        for side in ['left','right']:
                            edge=OxmlElement('w:'+side);edge.set(qn('w:w'),'30');edge.set(qn('w:type'),'dxa');mar.append(edge)
                        tcpr.append(mar)
                        if ri and re.fullmatch(r'[\d.eE+−\-]+',plain(s)):
                            tcpr.append(OxmlElement('w:noWrap'))
                    if ri==0:shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'EDF0F3');tcpr.append(shade)
            p=d.add_paragraph();p.paragraph_format.space_after=Pt(0);p.paragraph_format.space_before=Pt(0);p.paragraph_format.line_spacing=1;p.add_run().font.size=Pt(3)
            continue
        if kind=='math':
            p=d.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
            obj=OxmlElement('m:oMath');run=OxmlElement('m:r')
            # The inputs use explicit linear notation. Preserve it as math text;
            # LibreOffice otherwise reparses "abs(...)" into broken delimiters.
            props=OxmlElement('m:rPr');props.append(OxmlElement('m:nor'));run.append(props)
            txt=OxmlElement('m:t');txt.text=value;run.append(txt);obj.append(run);p._p.append(obj)
            continue
        style={'h1':'Title','h2':'Heading 1','h3':'Heading 2'}.get(kind,'Caption' if re.match(r'^(Table|Figure) \d+[.:]\s',plain(value)) else 'Normal')
        p=d.add_paragraph(style=style);inline(p,value,yellow)
        if yellow:changed.append({'block':j,'kind':kind,'text':value,'mark':'whole rewritten/reorganized block, not a word-level redline'})
    bound=[]
    for item in figures or []:
        found=[p for p in d.paragraphs if p.text==item['caption']]
        if len(found)!=1:raise ValueError('Expected one exact figure caption: '+item['caption'])
        caption=found[0];caption.paragraph_format.keep_with_next=False
        pic=d.add_paragraph();pic.alignment=WD_ALIGN_PARAGRAPH.CENTER;pic.paragraph_format.keep_with_next=True
        pic.paragraph_format.space_after=Pt(4)
        asset=Path(item['asset']);width=float(item.get('width_mm',160))
        pic.add_run().add_picture(str(asset),width=Mm(width))
        caption._p.addprevious(pic._p)
        bound.append({'asset':str(asset),'sha256':hashlib.sha256(asset.read_bytes()).hexdigest(),'width_mm':width,'caption':caption.text})
    out.parent.mkdir(parents=True,exist_ok=True);d.save(out)
    receipt={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output':str(out),'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'shared_typography':True,'text_rewriting_by_renderer':False,'yellow_scope':'New or rewritten text blocks relative to the supplied baseline; unchanged math/tables and pure moves not highlighted. Not native tracked changes.','changed_blocks':changed,'blocks':len(bs),'figures':bound}
    out.with_suffix('.build.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:receipt[k] for k in ['output','output_sha256','blocks']}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path);p.add_argument('--baseline',type=Path);p.add_argument('--review',action='store_true');p.add_argument('--figures',type=Path);p.add_argument('--font',type=Path,required=True);p.add_argument('--font-bold',type=Path,required=True);a=p.parse_args()
    figures=json.loads(a.figures.read_text(encoding='utf8')) if a.figures else []
    for item in figures:item['asset']=str((a.figures.parent/item['asset']).resolve())
    build(a.source,a.output,a.baseline,a.review,figures,a.font,a.font_bold)
