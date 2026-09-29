"""Original editable projection of a stipulated six-particle DEMO.
Analytic surfaces, orthographic view and a coating-only planar opening.
No simulation, measured geometry or performance data.
"""
from pathlib import Path
import argparse, hashlib, html, json, math, subprocess
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from PIL import Image

MM=72/25.4
W,H=160,70
INK='#29404A'; LINE='#6E8189'
def unit(v):
    a=np.asarray(v,dtype=float);return a/np.linalg.norm(a)
LIGHT=unit([-.48,.60,.74])
def shade(col,n):
    rgb=np.array([int(col[i:i+2],16) for i in (1,3,5)],float)
    l=.70+.30*max(0,float(np.dot(unit(n),LIGHT)))
    # A restrained diffuse surface; no specular spotlight or data-field encoding.
    rgb=np.clip(rgb*l+18*max(0,float(np.dot(unit(n),LIGHT)))**5,0,255)
    return '#'+''.join(f'{int(x):02x}' for x in rgb)

class Draw:
    def __init__(self,out,font,bold):
        self.out=out;self.parts=[];self.labels=[]
        self.svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">', '<title>Six intact coated particles and a repeated coating-only cutaway of P6</title>', '<desc>DEMO. Geometric projection, not a measurement or simulation. One blue coating encloses one gold core in each particle; two support layers. The detail repeats P6.</desc>',f'<rect width="{W}" height="{H}" fill="white"/>']
        pdfmetrics.registerFont(TTFont('Body',str(font)));pdfmetrics.registerFont(TTFont('Strong',str(bold)))
        self.c=canvas.Canvas(str(out/'figure.pdf'),pagesize=(W*MM,H*MM));self.c.setTitle('Coating-only cutaway | DEMO')
    def group(self,ident,**attrs):
        self.svg.append('<g id="'+ident+'" '+ ' '.join(f'data-{k}="{html.escape(str(v))}"' for k,v in attrs.items())+'>')
    def end(self):self.svg.append('</g>')
    def poly(self,pts,fill,stroke=None,width=.08):
        self.svg.append('<polygon points="'+' '.join(f'{x:.4f},{y:.4f}' for x,y in pts)+f'" fill="{fill}" stroke="{stroke or fill}" stroke-width="{width}" stroke-linejoin="round"/>')
        c=self.c;p=c.beginPath();p.moveTo(pts[0][0]*MM,(H-pts[0][1])*MM)
        for x,y in pts[1:]:p.lineTo(x*MM,(H-y)*MM)
        p.close();c.setFillColor(HexColor(fill));c.setStrokeColor(HexColor(stroke or fill));c.setLineWidth(width*MM);c.drawPath(p,fill=1,stroke=1)
    def line(self,pts,color=LINE,width=.22,dashed=False):
        self.svg.append('<polyline points="'+' '.join(f'{x:.4f},{y:.4f}' for x,y in pts)+f'" fill="none" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="1.0 1.0"' if dashed else '')+'/>')
        c=self.c;c.setStrokeColor(HexColor(color));c.setLineWidth(width*MM);c.setDash([MM,MM] if dashed else [])
        p=c.beginPath();p.moveTo(pts[0][0]*MM,(H-pts[0][1])*MM)
        for x,y in pts[1:]:p.lineTo(x*MM,(H-y)*MM)
        c.drawPath(p);c.setDash([])
    def text(self,x,y,t,size=9.5,bold=False,anchor='start'):
        self.labels.append({'text':t,'pt':size,'x':x,'y':y})
        self.svg.append(f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size/MM:.4f}" font-weight="{700 if bold else 400}" text-anchor="{anchor}" fill="{INK}">{html.escape(t)}</text>')
        c=self.c;c.setFillColor(HexColor(INK));c.setFont('Strong' if bold else 'Body',size)
        fn={'start':c.drawString,'middle':c.drawCentredString,'end':c.drawRightString}[anchor];fn(x*MM,(H-y)*MM,t)
    def ellipse(self,cx,cy,rx,ry,color):
        pts=[(cx+rx*math.cos(t),cy+ry*math.sin(t)) for t in np.linspace(0,2*math.pi,80)];self.poly(pts,color,width=.015)
    def surface(self,loops,cx,cy,r,colors,ident):
        path=[];pp=self.c.beginPath()
        for pts in loops:
            path.append('M '+' L '.join(f'{x:.5f},{y:.5f}' for x,y in pts)+' Z')
            pp.moveTo(pts[0][0]*MM,(H-pts[0][1])*MM)
            for x,y in pts[1:]:pp.lineTo(x*MM,(H-y)*MM)
            pp.close()
        gx,gy,gr=cx-.20*r,cy-.30*r,1.40*r
        self.svg.append(f'<defs><clipPath id="clip-{ident}"><path d="'+ ' '.join(path)+'"/></clipPath>'+f'<radialGradient id="shade-{ident}" gradientUnits="userSpaceOnUse" cx="{gx}" cy="{gy}" r="{gr}">'+''.join(f'<stop offset="{pos}" stop-color="{c}"/>' for pos,c in zip([0,.47,1],colors))+'</radialGradient></defs>')
        self.svg.append(f'<rect x="{cx-r-1}" y="{cy-r-1}" width="{2*r+2}" height="{2*r+2}" fill="url(#shade-{ident})" clip-path="url(#clip-{ident})"/>')
        self.c.saveState();self.c.clipPath(pp,stroke=0,fill=0)
        self.c.radialGradient(gx*MM,(H-gy)*MM,gr*MM,[HexColor(c) for c in colors],[0,.47,1]);self.c.restoreState()
    def save(self):
        self.svg.append('</svg>');(self.out/'figure.svg').write_text('\n'.join(self.svg),encoding='utf8');self.c.save()

def clipped(poly,n,d):
    out=[]
    for i,a in enumerate(poly):
        b=poly[(i+1)%len(poly)];fa=float(np.dot(n,a)-d);fb=float(np.dot(n,b)-d)
        if fa<=0:out.append(a)
        if (fa<=0)!=(fb<=0):out.append(a+(b-a)*fa/(fa-fb))
    return out

def sphere(radius,color,cut=None):
    faces=[]
    # View from +z. Only front-facing patches need to be rendered.
    for ti in range(32):
        th0=ti*math.pi/64;th1=(ti+1)*math.pi/64
        for pi in range(100):
            ph0=pi*2*math.pi/100;ph1=(pi+1)*2*math.pi/100
            pts=[radius*np.array([math.sin(th)*math.cos(ph),math.sin(th)*math.sin(ph),math.cos(th)]) for th,ph in [(th0,ph0),(th1,ph0),(th1,ph1),(th0,ph1)]]
            if cut:pts=clipped(pts,*cut)
            if len(pts)<3:continue
            mid=np.mean(pts,axis=0);faces.append((float(mid[2]),pts,shade(color,mid)))
    return faces

def particle(d,cx,cy,r,ident,cutaway=False):
    n=unit([.906,.10,.422]);plane=.15;core=.65
    faces=sphere(1,'#83B7D2',(n,plane) if cutaway else None)
    d.group(ident,entity='P6' if cutaway else ident,representation='repeated-detail' if cutaway else 'primary',operation='coating-only-opening' if cutaway else 'intact')
    loops=[[(cx+r*p[0],cy-r*p[1]) for p in pts] for _,pts,col in faces]
    d.surface(loops,cx,cy,r,['#DCECF0','#86B6CE','#426E87'],ident+'-shell')
    if cutaway:
        u=unit(np.cross(n,[0,0,1]));v=np.cross(n,u)
        ro=math.sqrt(1-plane**2);ri=math.sqrt(core**2-plane**2)
        for a,b in zip(np.linspace(0,2*math.pi,181)[:-1],np.linspace(0,2*math.pi,181)[1:]):
            pts=[plane*n+rr*(math.cos(t)*u+math.sin(t)*v) for rr,t in [(ro,a),(ro,b),(ri,b),(ri,a)]]
            d.poly([(cx+r*p[0],cy-r*p[1]) for p in pts],'#B7D7E5',width=.10)
        for rr in (ro,ri):
            edge=[plane*n+rr*(math.cos(t)*u+math.sin(t)*v) for t in np.linspace(0,2*math.pi,241)]
            d.line([(cx+r*p[0],cy-r*p[1]) for p in edge],color='#739BAD',width=.11)
        # Only the core cap in front of the opening is visible. Draw after the rim
        # because its curved surface protrudes through the flat annular opening.
        front=sphere(core,'#ECD483',(-n,-plane))
        loops=[[(cx+r*p[0],cy-r*p[1]) for p in pts] for _,pts,col in front]
        d.surface(loops,cx,cy,r*core,['#FFF3C8','#E5C36C','#93713D'],ident+'-core')
    d.end()
    return {'id':ident,'center':[cx,cy],'radius_mm':r,'detail_of':'P6' if cutaway else None,'cut_normal':n.tolist() if cutaway else None,'cut_offset_in_outer_radius':plane if cutaway else None,'core_radius_ratio':core,'front_surface_patch_count':len(faces)}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);ap.add_argument('--font',type=Path,required=True);ap.add_argument('--bold-font',type=Path,required=True);ap.add_argument('--pdftoppm',type=Path,required=True);a=ap.parse_args()
    if a.out.exists():ap.error('Use a new output directory')
    for p in [a.font,a.bold_font,a.pdftoppm]:
        if not p.is_file():ap.error('Missing dependency: '+str(p))
    a.out.mkdir(parents=True);d=Draw(a.out,a.font,a.bold_font)
    d.text(5,7,'Six intact particles',10.5,True);d.text(112,7,'P6 cutaway',10.5,True)
    def proj(x,y,z):return (8+13*x+4*y,56-8*y-13*z)
    # Shared corners keep the two solid slabs contiguous.
    layers=[('lower-layer',-.155,-.415,'#A9B9AF','#788E80','#8DA397'),('upper-layer',0,-.155,'#E7E3EA','#BBB2C6','#CEC5D7')]
    for ident,top,bottom,col,side,front in layers:
        d.group(ident,entity=ident,representation='primary')
        d.poly([proj(0,0,top),proj(5.4,0,top),proj(5.4,3.4,top),proj(0,3.4,top)],col)
        d.poly([proj(5.4,0,top),proj(5.4,3.4,top),proj(5.4,3.4,bottom),proj(5.4,0,bottom)],side)
        d.poly([proj(0,0,top),proj(5.4,0,top),proj(5.4,0,bottom),proj(0,0,bottom)],front)
        d.end()
    centers=[(.9,2.65),(2.6,2.65),(4.3,2.65),(.9,.85),(2.6,.85),(4.3,.85)]
    for x,y in centers:
        px,py=proj(x,y,0);d.ellipse(px+.25,py+.1,4.0,.65,'#C5C7CA')
    specs=[]
    for k,(x,y) in enumerate(centers,1):
        px,py=proj(x,y,.68);specs.append(particle(d,px,py,8.84,f'P{k}'))
    px,py=specs[-1]['center'];d.text(px,py+1.1,'P6',9.5,True,'middle')
    # This is an identity connector, not transport.
    d.line([(px+9,py),(98,py),(104,40)],dashed=True)
    specs.append(particle(d,126,34,22,'P6-detail',True))
    d.line([(107,18),(112,24)]);d.text(110,15,'Coating',9.5,False,'end')
    d.line([(135,39),(150,51)]);d.text(155,55,'Core',9.5,False,'end')
    d.line([(57,57),(57,63)]);d.text(57,68,'Upper layer',9.5,False,'middle')
    d.line([(19,60),(19,63)]);d.text(19,68,'Lower layer',9.5,False,'middle')
    d.text(126,63,'Same P6',9.5,False,'middle')
    d.save()
    subprocess.run([str(a.pdftoppm),'-png','-singlefile','-r','300',str(a.out/'figure.pdf'),str(a.out/'figure')],check=True,capture_output=True)
    im=Image.open(a.out/'figure.png').convert('RGB');im.convert('L').save(a.out/'figure-gray.png')
    arr=np.asarray(im,dtype=float)/255
    mat=np.array([[.367,.861,-.228],[.280,.673,.047],[-.012,.043,.969]])
    Image.fromarray(np.uint8(np.clip(arr@mat.T,0,1)*255)).save(a.out/'figure-deuteranopia.png')
    cap='Structural DEMO, not to scale. Six intact coated particles sit on two contiguous support layers. The undirected dashed link identifies a repeated view of the same front-right P6. Only an illustrative cap of its coating is removed; the core remains intact and curved. The flat coating rim and the curved core meet at the same plane. Surface shading indicates illustrative shape, not a measured field. Geometry, particle arrangement and layer thicknesses are schematic; no transport or performance is represented.'
    (a.out/'caption.txt').write_text(cap,encoding='utf8')
    record={'evidence':'DEMO_STIPULATED','width_mm':W,'height_mm':H,'primary_particle_ids':[f'P{i}' for i in range(1,7)],'support_layers':2,'repeated_detail':'P6','geometry':'analytic surfaces projected to editable vectors; not a measured model or physical simulation','surface_parameters':specs,'light_direction':LIGHT.tolist(),'labels':d.labels,'scientific_review':'REQUIRED','visual_review':'REQUIRED','author_acceptance':'NOT_OBTAINED','builder_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (a.out/'scene.json').write_text(json.dumps(record,indent=2),encoding='utf8');print(a.out)
if __name__=='__main__':main()
