"""Rebuild a fixed, original cartridge DEMO. This is an example, not a figure template.

Uses editable vector primitives in SVG and PDF. No raster content, network, hidden
fonts or absolute workspace paths. The projection conveys containment and motion;
it is not a measured 3D geometry or a flow simulation.
"""
from pathlib import Path
import argparse, hashlib, json, math, subprocess
from html import escape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import toColor

W,H=960,430
S=160/W*72/25.4
C={'ink':'#263B46','line':'#607580','body':'#E7EEF1','top':'#F6F9FA','side':'#BCD0D8',
   'frame':'#27728D','frame_light':'#C4E2E8','seal':'#936288','one':'#E2B454',
   'one_edge':'#A98128','two':'#79B5AA','two_edge':'#427F76','ghost':'#A7B7C0'}

class Figure:
    def __init__(self,out,font,bold):
        pdfmetrics.registerFont(TTFont('regular',str(font)));pdfmetrics.registerFont(TTFont('bold',str(bold)))
        self.c=canvas.Canvas(str(out/'figure.pdf'),pagesize=(W*S,H*S))
        self.c.setTitle('Filter replacement DEMO');self.svg=[];self.i=0
    def style(self,fill,stroke,sw):
        if fill:self.c.setFillColor(toColor(fill))
        if stroke:self.c.setStrokeColor(toColor(stroke))
        self.c.setLineWidth(sw*S)
    def emit(self,kind,attrs,entity='',extra=''):
        self.i+=1
        st=' '.join(f'{k}="{escape(str(v),quote=True)}"' for k,v in attrs.items())
        self.svg.append(f'<{kind} id="mark-{self.i}" data-entity="{entity}" {st}>{extra}</{kind}>')
    def poly(self,pts,fill=None,stroke=C['line'],sw=1.3,entity=''):
        self.style(fill,stroke,sw);p=self.c.beginPath();p.moveTo(pts[0][0]*S,(H-pts[0][1])*S)
        for x,y in pts[1:]:p.lineTo(x*S,(H-y)*S)
        p.close();self.c.drawPath(p,fill=bool(fill),stroke=bool(stroke))
        self.emit('polygon',{'points':' '.join(f'{x},{y}' for x,y in pts),'fill':fill or 'none','stroke':stroke or 'none','stroke-width':sw},entity)
    def line(self,pts,color=C['line'],sw=1.3,dash=False,entity=''):
        self.style(None,color,sw);self.c.setDash([4*S,4*S] if dash else [])
        p=self.c.beginPath();p.moveTo(pts[0][0]*S,(H-pts[0][1])*S)
        for x,y in pts[1:]:p.lineTo(x*S,(H-y)*S)
        self.c.drawPath(p);self.c.setDash([])
        a={'points':' '.join(f'{x},{y}' for x,y in pts),'fill':'none','stroke':color,'stroke-width':sw,'stroke-linecap':'round','stroke-linejoin':'round'}
        if dash:a['stroke-dasharray']='4 4'
        self.emit('polyline',a,entity)
    def rect(self,x,y,w,h,fill=None,stroke=C['line'],sw=1.3,r=0,entity=''):
        self.style(fill,stroke,sw);self.c.roundRect(x*S,(H-y-h)*S,w*S,h*S,r*S,fill=bool(fill),stroke=bool(stroke))
        self.emit('rect',{'x':x,'y':y,'width':w,'height':h,'rx':r,'fill':fill or 'none','stroke':stroke or 'none','stroke-width':sw},entity)
    def ellipse(self,x,y,rx,ry,fill,stroke=C['line'],sw=1.3,entity=''):
        self.style(fill,stroke,sw);self.c.ellipse((x-rx)*S,(H-y-ry)*S,(x+rx)*S,(H-y+ry)*S,fill=bool(fill),stroke=bool(stroke))
        self.emit('ellipse',{'cx':x,'cy':y,'rx':rx,'ry':ry,'fill':fill or 'none','stroke':stroke or 'none','stroke-width':sw},entity)
    def text(self,x,y,s,size=20,bold=False,anchor='start',entity='',color=C['ink']):
        self.c.setFillColor(toColor(color));self.c.setFont('bold' if bold else 'regular',size*S)
        {'start':self.c.drawString,'middle':self.c.drawCentredString,'end':self.c.drawRightString}[anchor](x*S,(H-y)*S,s)
        self.emit('text',{'x':x,'y':y,'font-family':'Arial','font-size':size,'font-weight':'bold' if bold else 'normal','text-anchor':anchor,'fill':color},entity,escape(s))
    def arrow(self,a,b,entity):
        self.line([a,b],C['ink'],2.2,entity=entity);dx=b[0]-a[0];dy=b[1]-a[1];n=math.hypot(dx,dy);u=(dx/n,dy/n);v=(-u[1],u[0]);k=11
        self.poly([b,(b[0]-k*u[0]+4.7*v[0],b[1]-k*u[1]+4.7*v[1]),(b[0]-k*u[0]-4.7*v[0],b[1]-k*u[1]-4.7*v[1])],C['ink'],None,entity=entity)
    def save(self,out):
        self.c.showPage();self.c.save()
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="160mm" height="{H/W*160}mm" viewBox="0 0 {W} {H}"><title>Filter replacement with flow stopped</title><desc>Illustrative cutaway of one candidate housing and one translated cartridge; ghost outline denotes its seated position. No flow is shown.</desc><rect width="{W}" height="{H}" fill="white"/>'+''.join(self.svg)+'</svg>'
        (out/'figure.svg').write_text(svg,encoding='utf8')

def pipe(f,x0,x1,y,entity):
    f.rect(x0,y-13,x1-x0,26,C['body'],entity=entity)
    f.rect(x0,y-11,x1-x0,5,C['top'],None,entity=entity)
    f.ellipse(x1,y,5,13,C['side'],entity=entity)
    f.ellipse(x1,y,2.5,8,'white',entity=entity)

def conventional(f):
    # One lifted housing. Open couplings below belong to the stationary pipe.
    pipe(f,18,76,316,'fixed-left-pipe');pipe(f,222,291,316,'fixed-right-pipe')
    f.ellipse(222,316,5,13,C['side'],entity='fixed-right-pipe')
    f.ellipse(222,316,2.5,8,'white',entity='fixed-right-pipe')
    for x in [86,212]:f.line([(x,280),(x,350)],C['ghost'],1.1,True,'previous-housing-position')
    f.line([(86,280),(212,280)],C['ghost'],1.1,True,'previous-housing-position')
    f.line([(86,350),(212,350)],C['ghost'],1.1,True,'previous-housing-position')
    x,y,w,h,dx,dy=86,233,126,109,36,-23
    pipe(f,61,90,y-h/2,'moving-housing-interface');pipe(f,208,244,y-h/2,'moving-housing-interface')
    f.poly([(x,y-h),(x+dx,y-h+dy),(x+w+dx,y-h+dy),(x+w,y-h)],C['top'],entity='conventional-housing')
    f.poly([(x+w,y-h),(x+w+dx,y-h+dy),(x+w+dx,y+dy),(x+w,y)],C['side'],entity='conventional-housing')
    f.rect(x,y-h,w,h,C['body'],r=5,entity='conventional-housing')
    f.rect(x+12,y-h+14,w-24,h-28,'#F4F7F8','#C1CDD2',1,4,'conventional-housing')
    f.line([(x+19,y-21),(x+w-19,y-21)],'#ABBCC5',1,entity='conventional-housing')
    f.arrow((149,291),(149,247),'housing-motion')
    f.text(155,404,'Housing detached',19,anchor='middle')

def frame(f,x,y,ghost=False):
    # Front plane x-z, depth projects (+38,-25). Plates are transverse to x.
    w,h,dx,dy=153,86,38,-25
    if ghost:
        color=C['ghost']
        for pts in [[(x,y),(x+w,y),(x+w,y-h),(x,y-h),(x,y)],[(x,y-h),(x+dx,y-h+dy),(x+w+dx,y-h+dy),(x+w,y-h)],[(x+w,y),(x+w+dx,y+dy),(x+w+dx,y-h+dy)]]:
            f.line(pts,color,1.3,True,'cartridge-seated-reference')
        for xi,num in [(x+22,'1'),(x+99,'2')]:
            f.line([(xi,y-7),(xi+dx,y+dy-7),(xi+dx,y-h+dy+7),(xi,y-h+7),(xi,y-7)],'#8198A4',1.1,True,'seated-filter-reference-'+num)
            f.text(xi+dx/2+2,y-h/2+3,num,19,False,'middle','seated-filter-reference-'+num,color='#6D8794')
        return
    # Back rails precede the two plates; front rails cover plate edges correctly.
    f.line([(x+dx,y+dy),(x+w+dx,y+dy),(x+w+dx,y-h+dy),(x+dx,y-h+dy),(x+dx,y+dy)],C['frame'],5,entity='cartridge-frame')
    for xi,role,num in [(x+22,'one','1'),(x+99,'two','2')]:
        pts=[(xi,y-7),(xi+dx,y+dy-7),(xi+dx,y-h+dy+7),(xi,y-h+7)]
        f.poly(pts,C[role],C[role+'_edge'],1.5,'filter-'+num)
        f.poly([(xi,y-h+7),(xi+dx,y-h+dy+7),(xi+dx+6,y-h+dy+7),(xi+6,y-h+7)],'#F6E5B8' if role=='one' else '#D1E9E2',C[role+'_edge'],1,'filter-'+num)
        f.poly([(xi,y-7),(xi+6,y-7),(xi+6,y-h+7),(xi,y-h+7)],C[role+'_edge'],None,entity='filter-'+num)
        f.text(xi+dx/2+2,y-h/2+3,num,21,True,'middle','filter-'+num)
    for a,b in [((x,y),(x+dx,y+dy)),((x+w,y),(x+w+dx,y+dy)),((x,y-h),(x+dx,y-h+dy)),((x+w,y-h),(x+w+dx,y-h+dy))]:f.line([a,b],C['frame'],5,entity='cartridge-frame')
    f.rect(x,y-h,w,h,None,C['frame'],6,2,'cartridge-frame')

def candidate(f,view):
    shift=155 if view=='spatial' else 0
    x,y,w,h,dx,dy=453+shift,278,180,116,49,-31
    pipe(f,365+shift,451+shift,220,'candidate-inlet');pipe(f,634+shift,738+shift,220,'candidate-outlet')
    # Cutaway opening exposes a position reference, not a second cartridge.
    f.poly([(x,y-h),(x+dx,y-h+dy),(x+w+dx,y-h+dy),(x+w,y-h)],C['top'],entity='candidate-housing')
    f.poly([(x+w,y-h),(x+w+dx,y-h+dy),(x+w+dx,y+dy),(x+w,y)],C['side'],entity='candidate-housing')
    f.poly([(x+12,y-12),(x+dx,y+dy-12),(x+w+dx-12,y+dy-12),(x+w-12,y-12)],'#D3E1E6',entity='candidate-housing')
    f.rect(x,y-h,w,h,C['body'],None,entity='candidate-housing')
    frame(f,466+shift,263,ghost=True)
    f.rect(x+8,y-h+12,w-16,h-22,None,C['seal'],4.5,6,'fixed-seal')
    f.line([(x,y-h),(x+w,y-h),(x+w,y),(x,y),(x,y-h)],C['line'],1.4,entity='candidate-housing')
    if view=='spatial':
        # Translate along the negative depth axis; no rotation or lateral slide.
        frame(f,481,263+140*25/38)
        f.arrow((505,244),(461,244+44*25/38),'cartridge-motion')
        f.line([(759,174),(840,125)],C['line'],1.1,entity='seal-label')
        f.text(848,129,'Seal stays',19)
        f.line([(816,241),(875,279)],C['line'],1.1,entity='housing-label')
        f.text(927,307,'Housing stays',19,anchor='end')
        f.text(577,408,'Cartridge',20,anchor='middle')
        f.text(700,108,'Seated position',19,anchor='middle')
        f.text(526,197,'Inlet',19)
        f.text(899,197,'Outlet',19,anchor='end')
    else:
        # Alternative: detached state alongside, same logical cartridge.
        frame(f,746,373)
        f.arrow((661,309),(733,343),'cartridge-motion')
        f.text(829,408,'Cartridge',20,anchor='middle')
        f.text(544,336,'Housing stays',19,anchor='middle')
        f.text(550,111,'Seal stays',19,anchor='middle')
        f.line([(550,117),(555,174)],C['line'],1.1,entity='seal-label')

def build(out,font,bold,pop,view):
    if out.exists():raise ValueError('Use a new output directory; existing results are retained.')
    out.mkdir(parents=True)
    f=Figure(out,font,bold)
    f.text(10,31,'a',23,True);f.text(39,31,'Remove the housing',21,True)
    f.text(344,31,'b',23,True);f.text(376,31,'Withdraw the cartridge',21,True)
    f.text(10,72,'Both operations: flow stopped',19)
    conventional(f);candidate(f,view)
    f.save(out)
    cmd=[str(pop),'-png','-singlefile','-r','300',str(out/'figure.pdf'),str(out/'figure')]
    subprocess.run(cmd,check=True,capture_output=True)
    caption=('Figure 1. Replacement changes which assembly moves. Arrows denote component motion with flow stopped. The conventional housing is detached (a); the candidate housing, interfaces and opening seal stay fixed (b). Dashed frame and numbered layer outlines show the seated position of the same cartridge drawn in solid colour after withdrawal. Layers 1 and 2 retain their inlet-to-outlet order. The cutaway is a structural DEMO, not to scale; it does not represent pressurized replacement.')
    (out/'caption.txt').write_text(caption,encoding='utf8')
    manifest={'view':view,'size_mm':[160,82],'minimum_label_pt':19*S,'editable':'Separate vector geometry and text in SVG/PDF; PNG preview only','depth':'Illustrative 2.5D, no physical model','logical_objects':{'conventional':['housing','left-pipe','right-pipe'],'candidate':['housing','inlet','outlet','seal','cartridge-frame','filter-1','filter-2']},'repeated_reference':'Dashed seated cartridge position; same frame and layers, not extra inventory','no_performance_data':True,'fonts':{'regular':font.name,'bold':bold.name},'command':cmd,'files':{n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in ['figure.svg','figure.pdf','figure.png','caption.txt']},'quality':'REVIEW_REQUIRED'}
    manifest['size_mm']=[160,H/W*160]
    manifest['command']=['pdftoppm','-png','-singlefile','-r','300','figure.pdf','figure']
    manifest['candidate_state']='SELECTED_AFTER_REVIEW' if view=='spatial' else 'REJECTED_FOR_MOTION_AMBIGUITY'
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
    print(json.dumps({'out':str(out),'minimum_label_pt':19*S,'view':view}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--font',type=Path,required=True);p.add_argument('--bold-font',type=Path,required=True);p.add_argument('--pdftoppm',type=Path,required=True);p.add_argument('--view',choices=['spatial','separated'],default='spatial');a=p.parse_args()
    for f in [a.font,a.bold_font,a.pdftoppm]:
        if not f.is_file():p.error('Missing dependency: '+str(f))
    build(a.out,a.font,a.bold_font,a.pdftoppm,a.view)
