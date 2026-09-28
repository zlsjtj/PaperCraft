"""Rebuild the membrane-fixture schematic; no measured geometry or data.

Usage: python build_figure.py --out NEW_DIR --font Arial.ttf
       --bold-font Arial-Bold.ttf --pdftoppm /path/to/pdftoppm
"""
import argparse, hashlib, json, math, subprocess
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image, ImageOps

W, H = 160*72/25.4, 88*72/25.4
INK='#213A44'; EDGE='#536D79'; CAP='#DBE7EC'; SIDE='#A4BBC5'
BASE='#E8EEF1'; BSIDE='#B8C9D1'; ACTIVE='#4A9F9A'; ASIDE='#327E7B'
SUPPORT='#D8AF69'; SEDGE='#987443'; WHITE='#FFFFFF'

def hx(c): return tuple(int(c[i:i+2],16)/255 for i in (1,3,5))
def arc(x,y,rx,ry,start=0,end=360,n=80):
    return [(x+rx*math.cos(math.radians(start+(end-start)*i/n)),
             y+ry*math.sin(math.radians(start+(end-start)*i/n))) for i in range(n+1)]

class Drawing:
    def __init__(self,pdf):
        self.pdf=canvas.Canvas(str(pdf),pagesize=(W,H),pageCompression=1)
        self.pdf.setTitle('Illustrative membrane fixture: two observation states')
        self.pdf.setAuthor('Original structural demonstration')
        self.pdf.translate(0,H)
        self.pdf.scale(1,-1)
        self.svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="160mm" height="88mm" viewBox="0 0 {W:.6f} {H:.6f}">',
          '<title>Two states of one membrane observation fixture</title>',
          '<desc>The cap is removed while the same bilayer membrane remains on the annular base. Conceptual geometry, not to scale.</desc>',
          f'<rect width="{W}" height="{H}" fill="white"/>']
        self.labels=[]
    def path(self,id,loops,fill,stroke=EDGE,lw=.8,dash=None,entity=None):
        p=self.pdf.beginPath(); ss=[]
        for pts,closed in loops:
            p.moveTo(*pts[0]); ss.append('M '+' '.join(f'{v:.3f}' for v in pts[0]))
            for pt in pts[1:]:
                p.lineTo(*pt); ss.append('L '+' '.join(f'{v:.3f}' for v in pt))
            if closed:p.close();ss.append('Z')
        self.pdf.setFillColorRGB(*hx(fill or WHITE)); self.pdf.setStrokeColorRGB(*hx(stroke or WHITE))
        self.pdf.setLineWidth(lw); self.pdf.setLineJoin(1)
        self.pdf.setDash(dash or [])
        self.pdf.drawPath(p,stroke=int(stroke is not None),fill=int(fill is not None),fillMode=0)
        self.pdf.setDash([])
        attrs=f' id="{id}" data-entity="{entity or id}" d="{" ".join(ss)}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{lw}" stroke-linejoin="round" fill-rule="evenodd"'
        if dash:attrs+=' stroke-dasharray="'+' '.join(str(v) for v in dash)+'"'
        self.svg.append('<path'+attrs+'/>')
    def poly(self,id,pts,fill,stroke=EDGE,lw=.8,entity=None):
        self.path(id,[(pts,True)],fill,stroke,lw,entity=entity)
    def line(self,id,pts,color=EDGE,lw=.7,dash=None):
        self.path(id,[(pts,False)],None,color,lw,dash)
    def ellipse(self,id,x,y,rx,ry,fill,stroke=EDGE,lw=.8,entity=None):
        self.poly(id,arc(x,y,rx,ry),fill,stroke,lw,entity)
    def text(self,id,x,y,s,size=10.5,bold=False,anchor='start',color=INK):
        font='ArialBold' if bold else 'Arial'
        width=pdfmetrics.stringWidth(s,font,size)
        xx=x-width/2 if anchor=='middle' else x-width if anchor=='end' else x
        self.pdf.saveState(); self.pdf.translate(xx,y); self.pdf.scale(1,-1)
        self.pdf.setFont(font,size);self.pdf.setFillColorRGB(*hx(color));self.pdf.drawString(0,0,s);self.pdf.restoreState()
        self.svg.append(f'<text id="{id}" x="{x}" y="{y}" font-family="Arial" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}" fill="{color}">{escape(s)}</text>')
        self.labels.append({'id':id,'text':s,'font_pt':size,'bounds':[xx,y-size,xx+width,y+size*.25]})
    def ring(self,id,x,y,rx,ry,irx,iry,h,top,side):
        # Front outside wall, then rear inside wall, then top annulus.
        self.poly(id+'-outer-wall',arc(x,y,rx,ry,0,180)+arc(x,y+h,rx,ry,180,0),side,entity=id)
        self.poly(id+'-inner-wall',arc(x,y,irx,iry,180,360)+arc(x,y+h,irx,iry,360,180),'#8FA8B5',entity=id)
        self.path(id+'-annulus',[(arc(x,y,rx,ry),True),(arc(x,y,irx,iry),True)],top,entity=id)
    def disc(self,id,x,y,rx,ry,h,top,side,edge):
        self.poly(id+'-front',arc(x,y,rx,ry,0,180)+arc(x,y+h,rx,ry,180,0),side,edge,.7,id)
        self.ellipse(id+'-top',x,y,rx,ry,top,edge,.7,id)
    def arrow(self,id,x,y1,y2):
        self.line(id+'-shaft',[(x,y1),(x,y2+6)],INK,1.35)
        self.poly(id+'-head',[(x,y2),(x-3,y2+7),(x+3,y2+7)],INK,None,0)
    def finish(self,svg):
        self.svg.append('</svg>');Path(svg).write_text('\n'.join(self.svg),encoding='utf-8')
        self.pdf.showPage();self.pdf.save()

def draw(out):
    d=Drawing(out/'figure.pdf')
    # The repeated geometry depicts two temporal states of the same three objects.
    d.text('a-title',15,20,'a  Cap fitted',11.5,True)
    d.text('b-title',238,20,'b  Cap removed',11.5,True)
    for state,x in [('closed',106),('open',334)]:
        d.ring(state+'-base',x,165,65,23,38,13.45,18,BASE,BSIDE)
        # The two touching discs together represent ONE bilayer membrane.
        d.disc(state+'-support',x,159.8,58,20.52,5.2,SUPPORT,SUPPORT,SEDGE)
        d.disc(state+'-active',x,158,58,20.52,1.8,ACTIVE,ASIDE,ASIDE)
        # Hidden lower boundary of the aligned base aperture.
        d.line(state+'-hidden-base-aperture',arc(x,183,38,13.45,0,180,60),EDGE,.65,[3,2.4])
        if state=='closed':
            d.ring('closed-cap',x,148,65,23,38,13.45,10,CAP,SIDE)
        else:
            d.ring('removed-cap',x,71,65,23,38,13.45,10,CAP,SIDE)
    d.line('centre-leader',[(106,95),(106,153)],EDGE,.7)
    d.text('centre-label',106,86,'Central region',10.5,False,'middle')
    d.text('cap-label',427,68,'Cap',10.5,False,'end')
    d.line('cap-leader',[(414,75),(399,79)],EDGE,.7)
    d.arrow('cap-motion',414,142,103)
    d.text('active-label',200,115,'Active layer',10.5)
    d.line('active-leader',[(257,112),(276,112),(301,143)],EDGE,.7)
    d.text('support-label',195,197,'Support layer',10.5)
    d.line('support-leader',[(259,194),(274,185),(282,173)],EDGE,.7)
    d.text('base-label',49,229,'Annular base',10.5)
    d.line('base-leader',[(90,217),(81,200)],EDGE,.7)
    d.text('periphery-label',334,229,'Periphery revealed',10.5,True,'middle')
    d.line('periphery-leader',[(362,216),(371,194),(365,174)],EDGE,.7)
    d.finish(out/'figure.svg')
    return d.labels

TEXT={
  'title':'Revealing the membrane perimeter by removing the cap',
  'paragraph': 'This illustrative fixture changes the visible area of a single membrane by removing only its cap (Fig. 1). With the cap fitted, the aligned central openings of the annular cap and base expose the membrane centre while its perimeter is clamped between them. Lifting off the cap reveals the previously covered perimeter; the same circular membrane remains on the base, with its thin active layer attached to the support layer below. The example establishes a structural arrangement and an observation sequence, rather than a validated device: no experimental or performance results are supplied.',
  'caption': 'Figure 1. Two states of the same membrane observation fixture. (a) The fitted cap covers and clamps the perimeter. (b) The cap is fully removed while the membrane stays on the base, revealing its perimeter. Teal and ochre identify the active and support layers, respectively; the layers remain in contact. The upward arrow denotes cap motion, and dashed arcs indicate the hidden lower boundary of the base opening. Geometry and layer thicknesses are schematic and not to scale.',
  'evidence': 'Original structural demonstration only; not a report of published research. No dimensions, thickness ratio, fastening method, adhesive, pore microstructure or transport mechanism is provided. There are no assembly-time, leakage, pressure, optical, membrane-performance or clamping-force tests. No claim of improved performance, protected integrity or reliable sealing is made.'
}

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path);p.add_argument('--font',required=True);p.add_argument('--bold-font',required=True);p.add_argument('--pdftoppm',required=True);a=p.parse_args()
    if a.out.exists():raise SystemExit('Refusing to overwrite an existing output directory')
    a.out.mkdir(parents=True)
    pdfmetrics.registerFont(TTFont('Arial',a.font));pdfmetrics.registerFont(TTFont('ArialBold',a.bold_font))
    labels=draw(a.out)
    (a.out/'text.json').write_text(json.dumps(TEXT,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    subprocess.run([a.pdftoppm,'-png','-r','300','-singlefile',str(a.out/'figure.pdf'),str(a.out/'figure')],check=True,capture_output=True)
    im=Image.open(a.out/'figure.png').convert('RGB')
    ImageOps.grayscale(im).save(a.out/'figure-grayscale.png')
    # Approximate deuteranopia preview, for a limited colour-dependence check.
    m=(.367322,.860646,-.227968,0,.280085,.672501,.047413,0,-.011820,.042940,.968881,0)
    im.convert('RGB',m).save(a.out/'figure-deuteranopia.png')
    im.resize((round(160/25.4*144),round(88/25.4*144)),Image.Resampling.LANCZOS).save(a.out/'figure-placement-preview.png')
    spec={
      'evidence_status':'ORIGINAL_STRUCTURAL_DEMO_NO_MEASUREMENTS',
      'size_mm':[160,88], 'min_label_pt':min(v['font_pt'] for v in labels),
      'depth':'D1 editable 2.5D vector; orthographic elliptical projection, no 3D model',
      'main_reading':'Removing the cap reveals the perimeter of the same membrane, which stays on the base.',
      'entities':[{'id':'base','type':'annular base','count':1},{'id':'cap','type':'removable annular cap','count':1},{'id':'membrane','type':'circular membrane','count':1,'children':['active','support']},{'id':'active','type':'upper thin layer','count':1,'parent':'membrane'},{'id':'support','type':'lower layer','count':1,'parent':'membrane'}],
      'view_rule':'closed and open are two states of the same entities, not additional objects',
      'relations':['cap and base apertures aligned when closed','membrane perimeter clamped when cap fitted','active layer directly above and attached to support layer','membrane remains on base when cap is completely removed'],
      'unknowns':['all dimensions','thickness ratio','materials','fasteners','bonding mechanism'],
      'forbidden':['screws','motor','fluid flow','measured values','performance or integrity benefits'],
      'colour_roles':{'cap':CAP,'base':BASE,'active':ACTIVE,'support':SUPPORT},
      'exact_labels':[v['text'] for v in labels], 'labels':labels,
      'alt_text':'Two equal-scale schematic views show one annular fixture. On the left the cap hides the membrane perimeter while its central part is visible. On the right the cap is lifted clear and the same bilayer membrane rests on the base with its perimeter exposed. Teal active material lies directly on the ochre support. Dashed arcs show the concealed base opening.'
    }
    (a.out/'figure_spec.json').write_text(json.dumps(spec,indent=2)+'\n',encoding='utf-8')
    (a.out/'alt_text.txt').write_text(spec['alt_text']+'\n',encoding='utf-8')
    (a.out/'source.py').write_bytes(Path(__file__).read_bytes())
    receipt={'width_mm':160,'height_mm':88,'png_px':list(im.size),'min_label_pt':spec['min_label_pt'],'label_count':len(labels),'font':a.font,'bold_font':a.bold_font,'pdftoppm':a.pdftoppm,'technical_status':'EXPORTED_NOT_YET_VISUALLY_REVIEWED','scientific_status':'SELF_REVIEW_REQUIRED','visual_status':'SELF_REVIEW_REQUIRED','author_acceptance':'NOT_REQUESTED','outputs':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in a.out.iterdir() if f.is_file()}}
    (a.out/'export_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(a.out),'min_label_pt':spec['min_label_pt'],'png_px':list(im.size)}))

if __name__=='__main__':main()
