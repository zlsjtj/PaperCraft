#!/usr/bin/env python3
"""Rebuild the fictional, two-layer curved-strip schematic.

Python 3 + reportlab, Pillow, numpy, pypdf; Poppler pdftoppm is external.
Supply fonts and pdftoppm explicitly. No bundled font or private skill dependency.
All lengths below are arbitrary design millimetres, never measurements.
The output directory must not exist. First output is therefore never overwritten.
"""
from __future__ import annotations
import argparse, hashlib, json, math, platform, subprocess, sys
from pathlib import Path
from xml.sax.saxutils import escape
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
import reportlab
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from pypdf import PdfReader

W, H, MM = 160.0, 85.0, 72.0 / 25.4
CX, CY, R_OUT, R_INTERFACE, R_IN = 62.0, 77.0, 48.0, 45.4, 36.4
A_START, A_END = 151.0, 35.0
DEPTH = (-4.0, -10.0)
INK = '#27343a'
EDGE = '#315d65'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def point(r, a, depth=False):
    a = math.radians(a)
    return (CX + r * math.cos(a) + (DEPTH[0] if depth else 0),
            CY - r * math.sin(a) + (DEPTH[1] if depth else 0))

def arc(r, begin, end, depth=False, move=True):
    """Shared cubic approximation; <= 30-degree segments, same seam coordinates."""
    n = math.ceil(abs(end - begin) / 30)
    angles = np.linspace(begin, end, n + 1)
    result = [('M' if move else 'L', *point(r, begin, depth))]
    for a, b in zip(angles[:-1], angles[1:]):
        ar, br = math.radians(a), math.radians(b)
        k = 4.0 / 3.0 * math.tan((br - ar) / 4.0)
        p, q = point(r, a, depth), point(r, b, depth)
        result.append(('C', p[0] - k*r*math.sin(ar), p[1] - k*r*math.cos(ar),
                       q[0] + k*r*math.sin(br), q[1] + k*r*math.cos(br), *q))
    return result

def band(ro, ri):
    return arc(ro, A_START, A_END) + arc(ri, A_END, A_START, move=False) + [('Z',)]

def surface(r):
    return arc(r, A_START, A_END) + arc(r, A_END, A_START, True, False) + [('Z',)]

def polygon(points):
    return [('M', *points[0])] + [('L', *p) for p in points[1:]] + [('Z',)]

def face(ro, ri):
    return [point(ro,A_END), point(ro,A_END,True), point(ri,A_END,True), point(ri,A_END)]

class Figure:
    def __init__(self, out, font, bold):
        pdfmetrics.registerFont(TTFont('TaskArial', str(font)))
        pdfmetrics.registerFont(TTFont('TaskArialBold', str(bold)))
        self.out = out
        self.c = canvas.Canvas(str(out/'figure.pdf'), pagesize=(W*MM,H*MM), invariant=1)
        self.c.setTitle('Fictional curved two-layer strip — static structure')
        self.c.setAuthor('')
        self.c.setSubject('DEMO; not to scale; no bending or adhesion experiment')
        self.svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="160mm" height="85mm" viewBox="0 0 160 85">',
                    '<title>Fictional two-layer curved strip</title>',
                    '<desc>One continuous curved strip has a thin outer layer and a thicker inner support of the same width, bonded throughout. An opaque clamp conceals one end. A dashed detail link repeats the same free end. Static fictional schematic, not to scale.</desc>',
                    '<defs><linearGradient id="outer-matte" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#b47840"/><stop offset="0.48" stop-color="#e4bd80"/><stop offset="1" stop-color="#c68f4f"/></linearGradient></defs>',
                    '<rect id="page-background" width="160" height="85" fill="#ffffff"/>']
        self.texts = []
        self.c.setFillColor(HexColor('#ffffff')); self.c.rect(0,0,W*MM,H*MM,fill=1,stroke=0)

    def path(self, ident, commands, fill=None, stroke=None, sw=0.2, entity=None, role=None, gradient=False, dash=None):
        d=' '.join(cmd[0]+' '.join(f'{v:.5f}' for v in cmd[1:]) for cmd in commands)
        attrs=f'id="{ident}" d="{d}" fill="{("url(#outer-matte)" if gradient else fill) or "none"}" stroke="{stroke or "none"}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"'
        if entity: attrs += f' data-entity="{entity}"'
        if role: attrs += f' data-role="{role}"'
        if dash: attrs += ' stroke-dasharray="'+' '.join(map(str,dash))+'"'
        self.svg.append('<path '+attrs+'/>')
        p = self.c.beginPath()
        for cmd in commands:
            if cmd[0]=='M': p.moveTo(cmd[1]*MM,(H-cmd[2])*MM)
            elif cmd[0]=='L': p.lineTo(cmd[1]*MM,(H-cmd[2])*MM)
            elif cmd[0]=='C': p.curveTo(cmd[1]*MM,(H-cmd[2])*MM,cmd[3]*MM,(H-cmd[4])*MM,cmd[5]*MM,(H-cmd[6])*MM)
            elif cmd[0]=='Z': p.close()
        self.c.saveState()
        self.c.setLineWidth(sw*MM); self.c.setLineJoin(1); self.c.setLineCap(1)
        if dash:self.c.setDash([v*MM for v in dash])
        if gradient:
            self.c.saveState(); self.c.clipPath(p,stroke=0,fill=0)
            self.c.linearGradient(14*MM,0,102*MM,0,[HexColor(v) for v in ['#b47840','#e4bd80','#c68f4f']],positions=[0,.48,1],extend=True)
            self.c.restoreState()
        elif fill:self.c.setFillColor(HexColor(fill))
        if stroke:self.c.setStrokeColor(HexColor(stroke))
        self.c.drawPath(p,stroke=int(bool(stroke)),fill=int(bool(fill) and not gradient))
        self.c.restoreState()

    def text(self, ident, text, x, y, size=10.5, anchor='middle', bold=False, fill=INK):
        # y is the baseline, with millimetre geometry and point font sizes.
        self.svg.append(f'<text id="{ident}" x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" font-size="{size/MM:.6f}" font-weight="{700 if bold else 400}" fill="{fill}" text-anchor="{anchor}">{escape(text)}</text>')
        self.c.setFillColor(HexColor(fill)); self.c.setFont('TaskArialBold' if bold else 'TaskArial',size)
        fn={'middle':self.c.drawCentredString,'start':self.c.drawString,'end':self.c.drawRightString}[anchor]
        fn(x*MM,(H-y)*MM,text)
        self.texts.append(dict(id=ident,text=text,x_mm=x,y_mm=y,size_pt=size,owner=ident.removeprefix('label-')))

    def finish(self):
        self.svg.append('</svg>')
        (self.out/'figure.svg').write_text('\n'.join(self.svg)+'\n',encoding='utf-8')
        self.c.showPage(); self.c.save()

def ellipse_path(cx,cy,rx,ry):
    k=.5522847498307936
    return [('M',cx+rx,cy),('C',cx+rx,cy+k*ry,cx+k*rx,cy+ry,cx,cy+ry),
        ('C',cx-k*rx,cy+ry,cx-rx,cy+k*ry,cx-rx,cy),
        ('C',cx-rx,cy-k*ry,cx-k*rx,cy-ry,cx,cy-ry),
        ('C',cx+k*rx,cy-ry,cx+rx,cy-k*ry,cx+rx,cy),('Z',)]

def draw(fig):
    # One physical strip. First draw the outer exposed surface; the near faces
    # and terminal face then occlude its exact shared edges.
    fig.path('strip-outer-surface',surface(R_OUT),stroke='#946333',sw=.19,entity='strip',role='outer-layer',gradient=True)
    fig.path('strip-support-near-face',band(R_INTERFACE,R_IN),fill='#477f8b',stroke=EDGE,sw=.22,entity='strip',role='support-layer')
    fig.path('strip-outer-near-face',band(R_OUT,R_INTERFACE),fill='#b47840',stroke='#89592e',sw=.19,entity='strip',role='outer-layer')
    fig.path('free-end-support',polygon(face(R_INTERFACE,R_IN)),fill='#aacbd0',stroke=EDGE,sw=.22,entity='strip',role='support-layer')
    fig.path('free-end-outer',polygon(face(R_OUT,R_INTERFACE)),fill='#dfb372',stroke='#89592e',sw=.19,entity='strip',role='outer-layer')

    # The opaque clamp is drawn last and covers the physical initial ends of
    # BOTH layers across their full shared width. No hidden layer is displayed.
    a=math.radians(A_START); n=(math.cos(a),-math.sin(a)); t=(math.sin(a),math.cos(a))
    cp=point((R_OUT+R_IN)/2,A_START)
    def q(u,v):return (cp[0]+u*n[0]+v*t[0],cp[1]+u*n[1]+v*t[1])
    near=[q(8,9),q(-8,9),q(-8,-9),q(8,-9)]
    far=[(x+DEPTH[0]*1.10,y+DEPTH[1]*1.10) for x,y in near]
    fig.path('clamp-top',polygon([far[0],far[1],near[1],near[0]]),fill='#aeb6bb',stroke='#626e75',sw=.23,entity='clamp',role='clamp')
    fig.path('clamp-left-side',polygon([far[3],far[0],near[0],near[3]]),fill='#738089',stroke='#626e75',sw=.23,entity='clamp',role='clamp')
    fig.path('clamp-near-face',polygon(near),fill='#929ea5',stroke='#626e75',sw=.25,entity='clamp',role='clamp')

    # Exact repeat of the same terminal face (uniform scale + translation).
    # It is not a second strip and is not an exploded view.
    bounds=face(R_OUT,R_IN)
    dc=(sum(p[0] for p in bounds)/4,sum(p[1] for p in bounds)/4)
    target=(135.0,51.0); scale=1.85
    def detail(points):return [(target[0]+scale*(x-dc[0]),target[1]+scale*(y-dc[1])) for x,y in points]
    fig.path('detail-support-same-free-end',polygon(detail(face(R_INTERFACE,R_IN))),fill='#aacbd0',stroke=EDGE,sw=.25,entity='strip',role='detail-support-layer')
    fig.path('detail-outer-same-free-end',polygon(detail(face(R_OUT,R_INTERFACE))),fill='#dfb372',stroke='#89592e',sw=.23,entity='strip',role='detail-outer-layer')
    fig.path('detail-selection',ellipse_path(dc[0],dc[1],12.5,10.5),stroke='#8b969c',sw=.16,role='detail-selection',dash=[1.15,1.2])
    detail_left=min(detail(face(R_OUT,R_IN)), key=lambda p:p[0])
    fig.path('detail-identity-link',[('M',dc[0]+12.5,dc[1]),('L',detail_left[0]-.8,detail_left[1])],stroke='#8b969c',sw=.16,role='same-object-detail',dash=[1.15,1.2])

    fig.path('leader-outer',[('M',57,13),('L',57,23.9)],stroke='#59666e',sw=.18,role='label-leader')
    fig.text('label-outer-layer','Outer layer',57,10.6)
    fig.path('leader-support',[('M',58,57.7),('L',58,38.0)],stroke='#59666e',sw=.18,role='label-leader')
    fig.text('label-support-layer','Support layer',58,63.0)
    fig.path('leader-clamp',[('M',21,70.9),('L',21,64.5)],stroke='#59666e',sw=.18,role='label-leader')
    fig.text('label-clamp','Clamp',21,76.0)
    fig.text('label-detail','Same free end',135,26.0,10.5)
    fig.text('label-detail-enlarged','(enlarged)',135,31.0,9,fill='#59666e')
    fig.text('label-scale','Not to scale',155,81.0,8.5,anchor='end',fill='#59666e')
    return {'main_free_end_center_mm':list(dc),'detail_center_mm':list(target),'detail_scale':scale,
            'shared_outer_radius_design_mm':R_OUT,'shared_interface_radius_design_mm':R_INTERFACE,
            'shared_inner_radius_design_mm':R_IN,'width_projection_mm':list(DEPTH),
            'angles_degrees':[A_START,A_END],'note':'Arbitrary diagram geometry, not measurements.'}

def export_qa(out):
    img=Image.open(out/'figure.png').convert('RGB')
    img.convert('L').save(out/'figure-gray.png')
    # Single Machado et al. 2009 100% deuteranomaly simulation, applied to
    # linear RGB. This is a limited QA view, not universal accessibility proof.
    rgb=np.asarray(img,dtype=float)/255
    linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
    matrix=np.array([[.367322,.860646,-.227968],[.280085,.672501,.047413],[-.011820,.042940,.968881]])
    sim=np.clip(linear@matrix.T,0,1)
    sim=np.where(sim<=.0031308,12.92*sim,1.055*sim**(1/2.4)-.055)
    Image.fromarray((np.clip(sim,0,1)*255+.5).astype('uint8')).save(out/'figure-deuteranomaly.png')
    # 160 mm at 96 dpi is a nominal-size display aid; monitor scaling varies.
    size=(round(160/25.4*96),round(85/25.4*96))
    img.resize(size,Image.Resampling.LANCZOS).save(out/'figure-160mm-96dpi.png')

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',required=True,type=Path)
    ap.add_argument('--font',required=True,type=Path)
    ap.add_argument('--bold-font',required=True,type=Path)
    ap.add_argument('--pdftoppm',required=True,type=Path)
    args=ap.parse_args()
    for path in [args.font,args.bold_font,args.pdftoppm]:
        if not path.is_file():ap.error(f'Missing dependency: {path}')
    if args.out.exists():ap.error(f'Refusing to overwrite existing output: {args.out}')
    args.out.mkdir(parents=True)
    fig=Figure(args.out,args.font,args.bold_font); geometry=draw(fig);fig.finish()
    command=[str(args.pdftoppm),'-png','-r','300','-singlefile',str(args.out/'figure.pdf'),str(args.out/'figure')]
    run=subprocess.run(command,capture_output=True,text=True)
    if run.returncode:raise RuntimeError(f'Poppler exit {run.returncode}: {run.stderr}')
    export_qa(args.out)
    pdf=PdfReader(args.out/'figure.pdf');page=pdf.pages[0]
    root=ET.parse(args.out/'figure.svg').getroot()
    text=page.extract_text()
    dimensions=[float(page.mediabox.width)/MM,float(page.mediabox.height)/MM]
    checks={
        'pdf_pages':len(pdf.pages),'pdf_size_mm':dimensions,
        'pdf_contains_all_labels':all(t['text'] in text for t in fig.texts),
        'svg_text_nodes':len(root.findall('{http://www.w3.org/2000/svg}text')),
        'svg_raster_images':len(root.findall('.//{http://www.w3.org/2000/svg}image')),
        'pdf_image_xobjects':len(page.images),'min_label_size_pt':min(t['size_pt'] for t in fig.texts),
        'png_size_px':list(Image.open(args.out/'figure.png').size),
        'font_embedded': '/FontFile2' in repr(pdf.pages[0]['/Resources']['/Font']),
        'geometry_note':'Shared boundaries and exact terminal-face repeat implemented parametrically; visibility requires visual review.'}
    # Follow PDF font descriptors rather than relying on the resource repr.
    checks['font_embedded']=all('/FontFile2' in f.get_object().get('/FontDescriptor',{}).get_object()
        for f in page['/Resources']['/Font'].values() if f.get_object().get('/BaseFont') != '/Helvetica')
    checks['technical_status']='PASS' if (len(pdf.pages)==1 and abs(dimensions[0]-160)<.001 and abs(dimensions[1]-85)<.001 and checks['pdf_contains_all_labels'] and checks['svg_raster_images']==0 and checks['pdf_image_xobjects']==0 and checks['font_embedded']) else 'FAIL'
    checks['visual_review']='REVIEW_REQUIRED';checks['author_acceptance']='NOT_RUN'
    checks['overall_status']='REVIEW_REQUIRED'
    (args.out/'technical-checks.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf-8')
    (args.out/'geometry.json').write_text(json.dumps(geometry,indent=2)+'\n',encoding='utf-8')
    (args.out/'labels.json').write_text(json.dumps(fig.texts,indent=2)+'\n',encoding='utf-8')
    manifest={
        'python':sys.version,'platform':platform.platform(),'reportlab':reportlab.Version,
        'command':sys.argv,'render_command':command,'render_exit_code':run.returncode,
        'font':{'path':str(args.font.resolve()),'sha256':sha(args.font)},
        'bold_font':{'path':str(args.bold_font.resolve()),'sha256':sha(args.bold_font)},
        'rebuild_source_sha256':sha(__file__),
        'files':{p.name:sha(p) for p in sorted(args.out.iterdir()) if p.is_file()},
        'editability':'SVG native paths, gradients and text; PDF vector paths, gradient shading and embedded text. PNG and QA views are raster.',
        'limits':'No physical experiment, no human acceptance, no external editor roundtrip, no printing test.'}
    (args.out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'out':str(args.out),'technical_status':checks['technical_status'],'size_mm':dimensions,'min_label_pt':checks['min_label_size_pt']}))

if __name__=='__main__':main()
