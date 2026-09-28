"""Create independent reviewable pages for the fixed structural DEMO."""
import argparse, hashlib, json
from pathlib import Path
from docx import Document
from docx.shared import Mm, Pt, RGBColor
from docx.enum.text import WD_COLOR_INDEX

def build(figdir, out, before=None):
    if out.exists(): raise ValueError('Use a new output directory.')
    data=json.loads((Path(__file__).parent/'text.json').read_text(encoding='utf8'))
    fig=figdir/'figure.png'
    if not fig.is_file(): raise FileNotFoundError(fig)
    if (figdir/'caption.txt').read_text(encoding='utf8')!=data['caption']:
        raise ValueError('Figure caption and document source differ; rebuild both from one version.')
    out.mkdir(parents=True)
    for name,review,original in [('manuscript',False,False),('review',True,False)]+([('before',False,True)] if before else []):
        d=Document();sec=d.sections[0];sec.page_width=Mm(210);sec.page_height=Mm(297)
        sec.left_margin=sec.right_margin=Mm(25);sec.top_margin=Mm(23);sec.bottom_margin=Mm(23)
        normal=d.styles['Normal'];normal.font.name='Arial';normal.font.size=Pt(10.5)
        normal.paragraph_format.space_after=Pt(8);normal.paragraph_format.line_spacing=1.15
        h=d.add_paragraph();r=h.add_run('STRUCTURAL DESIGN DEMO');r.font.size=Pt(8.5);r.font.color.rgb=RGBColor.from_string('607580')
        p=d.add_paragraph();r=p.add_run('Filter assembly' if original else data['title']);r.bold=True;r.font.size=Pt(16)
        p.paragraph_format.space_after=Pt(14)
        if review:r.font.highlight_color=WD_COLOR_INDEX.YELLOW
        p=d.add_paragraph();r=p.add_run(data['original'] if original else data['revised'])
        if review:r.font.highlight_color=WD_COLOR_INDEX.YELLOW
        p=d.add_paragraph();p.paragraph_format.space_before=Pt(10);p.paragraph_format.space_after=Pt(7)
        p.add_run().add_picture(str(before if original else fig),width=Mm(160))
        p=d.add_paragraph();r=p.add_run('Figure 1. Conventional and candidate replacement operations. Flow is stopped; the geometry is illustrative and not to scale.' if original else data['caption']);r.font.size=Pt(9.5)
        if review:r.font.highlight_color=WD_COLOR_INDEX.YELLOW
        p=d.add_paragraph();p.paragraph_format.space_before=Pt(8);r=p.add_run('Evidence available');r.bold=True
        p=d.add_paragraph(data['evidence'])
        if review:p.runs[0].font.highlight_color=WD_COLOR_INDEX.YELLOW
        d.save(out/(name+'.docx'))
    record={'files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in out.glob('*.docx')},'figure_sha256':hashlib.sha256(fig.read_bytes()).hexdigest(),'figure_width_mm':160,'review_marks':'Paragraph-level yellow changes; not native revisions. Figure change is shown by separate before/after images.','visual_review':'REQUIRES_RENDER_AND_VIEW','scope':'Constructed one-page example; no equations, tables or citations.'}
    (out/'build.json').write_text(json.dumps(record,indent=2),encoding='utf8')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--figure-dir',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--before-figure',type=Path);a=p.parse_args();build(a.figure_dir,a.out,a.before_figure)
