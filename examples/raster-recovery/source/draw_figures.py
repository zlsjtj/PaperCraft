"""Native editable SVG + vector PDF; PNG rendered from that PDF with Poppler."""
import math, json, subprocess, hashlib
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from PIL import Image, ImageOps
import numpy as np

W,H=1600,1120
INK='#20343D'; MUTED='#56636B'; LINE='#8D9AA0'; LIGHT='#EAF0F2'; TEAL='#11736A'; PALE='#D7EEEA'; GOLD='#E5AE45'; GOLDPALE='#FBECCA'; RED='#B2423A'; PURPLE='#68489A'; BLUE='#315D87'
class Figure:
    def __init__(self,path,font,bold):
        self.path=Path(path);self.path.parent.mkdir(parents=True,exist_ok=True)
        self.items=[];self.labels=[];self.entities=[];self.n=0
        pdfmetrics.registerFont(TTFont('Arial',str(font)));pdfmetrics.registerFont(TTFont('Arial-Bold',str(bold)))
        self.c=canvas.Canvas(str(self.path.with_suffix('.pdf')),pagesize=(160/25.4*72,112/25.4*72))
        self.c.scale(160/25.4*72/W,160/25.4*72/W)
        self.rect(0,0,W,H,'#FFFFFF',None)
    def ident(self,prefix='g'):
        self.n+=1;return f'{prefix}{self.n}'
    def rect(self,x,y,w,h,fill='none',stroke=LINE,sw=2,rx=0,id=None):
        id=id or self.ident(); self.items.append(f'<rect id="{id}" x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{sw}"/>')
        self.c.setLineWidth(sw)
        if fill and fill!='none':self.c.setFillColor(HexColor(fill))
        if stroke:self.c.setStrokeColor(HexColor(stroke))
        self.c.roundRect(x,H-y-h,w,h,rx,stroke=bool(stroke),fill=bool(fill and fill!='none'))
    def text(self,x,y,s,size=34,color=INK,bold=False,anchor='start',id=None):
        id=id or self.ident('label');self.labels.append({'id':id,'text':s,'font_size':size,'effective_pt':size*160/25.4*72/W,'x':x,'y':y})
        self.items.append(f'<text id="{id}" x="{x}" y="{y}" font-family="Arial" font-size="{size}" font-weight="{"bold" if bold else "normal"}" fill="{color}" text-anchor="{anchor}">{escape(s)}</text>')
        self.c.setFont('Arial-Bold' if bold else 'Arial',size);self.c.setFillColor(HexColor(color))
        getattr(self.c,{'start':'drawString','middle':'drawCentredString','end':'drawRightString'}[anchor])(x,H-y,s)
    def line(self,x1,y1,x2,y2,color=LINE,sw=3,dash=None,arrow=False):
        id=self.ident('line');d=f' stroke-dasharray="{dash}"' if dash else ''
        self.items.append(f'<line id="{id}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"{d}/>' )
        self.c.setStrokeColor(HexColor(color));self.c.setLineWidth(sw);self.c.setDash([float(v) for v in dash.split()] if dash else [])
        self.c.line(x1,H-y1,x2,H-y2);self.c.setDash([])
        if arrow:
            ang=math.atan2(y2-y1,x2-x1); l=12+sw;wid=6+sw/2
            pts=[(x2,y2),(x2-l*math.cos(ang)+wid*math.sin(ang),y2-l*math.sin(ang)-wid*math.cos(ang)),(x2-l*math.cos(ang)-wid*math.sin(ang),y2-l*math.sin(ang)+wid*math.cos(ang))]
            self.poly(pts,color)
    def poly(self,pts,fill,stroke=None):
        self.items.append(f'<polygon id="{self.ident()}" points="'+ ' '.join(f'{x},{y}' for x,y in pts)+f'" fill="{fill}" stroke="{stroke or "none"}"/>')
        p=self.c.beginPath();p.moveTo(pts[0][0],H-pts[0][1])
        for x,y in pts[1:]:p.lineTo(x,H-y)
        p.close();self.c.setFillColor(HexColor(fill));self.c.drawPath(p,fill=1,stroke=0)
    def circle(self,x,y,r,fill,stroke=LINE,sw=2,id=None):
        id=id or self.ident();self.items.append(f'<circle id="{id}" cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
        self.c.setFillColor(HexColor(fill));self.c.setStrokeColor(HexColor(stroke));self.c.setLineWidth(sw);self.c.circle(x,H-y,r,stroke=1,fill=1)
    def cross(self,x,y,r=10,color=RED,sw=4):
        self.line(x-r,y-r,x+r,y+r,color,sw);self.line(x-r,y+r,x+r,y-r,color,sw)
    def check(self,x,y,color=TEAL):
        self.line(x-9,y,x-2,y+7,color,3);self.line(x-2,y+7,x+12,y-10,color,3)
    def save(self,poppler):
        self.c.showPage();self.c.save()
        self.path.with_suffix('.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="160mm" height="112mm" viewBox="0 0 {W} {H}">\n<title>{self.path.stem}: synthetic DEMO</title>\n'+ '\n'.join(self.items)+'\n</svg>',encoding='utf-8')
        subprocess.run([str(poppler),'-singlefile','-png','-r','320',str(self.path.with_suffix('.pdf')),str(self.path)],check=True,capture_output=True)
        im=Image.open(self.path.with_suffix('.png')).convert('RGB')
        ImageOps.grayscale(im).save(self.path.parent/(self.path.stem+'_gray.png'))
        a=np.asarray(im).astype(float)/255
        a=np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
        # Single approximate deuteranopia simulation; a screening view, not certification.
        matrix=np.array([[.367322,.860646,-.227968],[.280085,.672501,.047413],[-.011820,.042940,.968881]])
        Image.fromarray((np.clip(np.where(np.clip(a@matrix.T,0,1)<=.0031308,12.92*np.clip(a@matrix.T,0,1),1.055*np.clip(a@matrix.T,0,1)**(1/2.4)-.055),0,1)*255).astype('uint8')).save(self.path.parent/(self.path.stem+'_deuteranopia.png'))
        self.path.with_suffix('.labels.json').write_text(json.dumps(self.labels,indent=2),encoding='utf-8')

def fig1(path,font,bold,poppler,final=False):
    f=Figure(path,font,bold)
    f.text(55,64,'1  Where does the next sample belong?',44,bold=True)
    f.text(1545,106,'SYNTHETIC DEMO',30,MUTED,anchor='end')
    # Full grid uses a common physical scale: dx 40 / 4 mm = dy 60 / 6 mm.
    x0,y0,dx,dy=105,190,40,60
    f.text(95,135,'12 × 16 centers' if final else '12 rows × 16 centers',34,bold=True)
    f.text(420,135,'60 × 66 mm extent',30,MUTED)
    f.text(70,170,'r',30,MUTED,anchor='end')
    f.text(104,170,'0',30,MUTED,anchor='middle');f.text(705,170,'15',30,MUTED,anchor='middle')
    f.text(385,170,'physical column c',30,MUTED,anchor='middle')
    # Continuous serpentine trajectory, drawn below center glyphs.
    for r in range(12):
        yy=y0+r*dy
        if r<11:
            edge=x0+15*dx if r%2==0 else x0
            f.line(edge,yy,edge,yy+dy,LINE,2,arrow=True)
        if r%2==0:f.line(x0,yy,x0+15*dx,yy,LINE,2,arrow=True)
        else:f.line(x0+15*dx,yy,x0,yy,LINE,2,arrow=True)
    f.rect(80,y0+5*dy-24,652,48,'#F6F3FA',PURPLE,2,12)
    for r in range(12):
        yy=y0+r*dy;f.text(67,yy+10,str(r),30,INK if r==5 else MUTED,bold=r==5,anchor='end')
        if final:f.text(763,yy+10,'→' if r%2==0 else '←',30,PURPLE if r==5 else MUTED,anchor='middle')
        for c in range(16):
            x=x0+c*dx;k=c if r%2==0 else 15-c
            fill='#FFFFFF';st=LINE
            if r<5:fill='#ACB9BC';st='#73858C'
            if r==5 and k<8:fill=TEAL;st=TEAL
            elif r==5 and k in (8,9):fill=GOLDPALE;st='#A66F18'
            elif r==5 and k==10:fill='#FFFFFF';st=RED
            f.circle(x,yy,11,fill,st,2,id=f'center-r{r}-c{c}')
            if r==5 and k==10:f.cross(x,yy,6,RED,2)
            if r==5 and k==8:f.circle(x,yy,18,'none' if False else GOLDPALE,PURPLE,4,id='restart-ring')
    f.circle(705,490,18,'#FFFFFF',INK,3,id='entry-ring');f.circle(705,490,10,TEAL,TEAL,2)
    f.line(120,881,693,881,MUTED,2)
    f.text(406,916,'x increases →',30,MUTED,anchor='middle')
    f.text(80,954,'Row 5 detail · same centers',34,bold=True)
    # Right side: a concise state ledger and two distinguishable physical points.
    f.text(815,195,'Checkpoint: next_row = 5',36,bold=True)
    f.text(815,236,'Epoch 7 · rows 0–4 complete',31,MUTED)
    f.line(815,269,1535,269,LIGHT,3)
    rows=[(322,TEAL,'Sealed','b0 + b1 · 8 records'),(406 if final else 389,GOLDPALE,'Volatile','k = 8, 9 · repeat after reset'),(490 if final else 456,'#FFFFFF','Interrupted','k = 10 · no completed sample')]
    for yy,fill,label,desc in rows:
        f.circle(833,yy-9,11,fill,RED if label=='Interrupted' else (TEAL if label=='Sealed' else '#A66F18'),2)
        if label=='Interrupted':f.cross(833,yy-9,6,RED,2)
        f.text(862,yy,label,34,bold=True)
        f.text(862,yy+37,desc,30,MUTED)
    f.rect(810,555,725,161,'#F6F3FA',None,rx=13)
    f.text(839,600,'Restart: q = 88',40,PURPLE,bold=True)
    f.text(839,645,'r = 5, k = 8 → c = 7',34)
    f.text(839,686,'(x, y) = (28, 30) mm',34)
    f.text(815,774,'Entry reference: c = 15',34,bold=True)
    f.text(815,815,'(60, 30) mm → anchor → q = 88',32)
    f.circle(833,869,11,'#FFFFFF',LINE,2)
    f.text(862,880,'Not yet acquired',32,INK)
    f.text(815,920,'Anchoring establishes position.',32,INK,bold=True)
    # Detail: physical columns remain ascending left to right; block index reversed.
    xx0,sp,yy=120,88,1030
    for b in range(4):
        lo=12-4*b;xx=xx0+lo*sp
        f.rect(xx-32,992,3*sp+64,73,PALE if b<2 else '#F8F9FA',TEAL if b<2 else LINE,2,8)
        f.text(xx+1.5*sp,983,f'b{b}',30,TEAL if b<2 else MUTED,anchor='middle')
    for c in range(16):
        k=15-c;x=xx0+c*sp
        fill=TEAL if k<8 else GOLDPALE if k in (8,9) else '#FFFFFF';stroke=TEAL if k<8 else RED if k==10 else LINE
        f.circle(x,yy,16,fill,stroke,2,id=f'row5-detail-c{c}')
        if k==10:f.cross(x,yy,9,RED,3)
        if k==8:f.circle(x,yy,24,GOLDPALE,PURPLE,4)
        if c==15:
            f.circle(x,yy,24,'#FFFFFF',INK,3)
            f.circle(x,yy,16,TEAL,TEAL,2)
        f.text(x,1100,str(c),30,INK,anchor='middle')
    f.text(56,1100,'c',30,MUTED)
    # Deliberate single final refinement: arrows show the reversed row directly.
    if final:
        f.line(1520,951,1280,951,PURPLE,3,arrow=True)
        f.text(1250,962,'row 5 traversal',30,PURPLE,anchor='end')
    f.save(poppler)

def fig2(path,font,bold,poppler,final=False):
    f=Figure(path,font,bold)
    f.text(55,64,'2  Sealed output and position recover separately',42,bold=True)
    f.text(1545,108,'SYNTHETIC DEMO',30,MUTED,anchor='end')
    f.text(55,155,'FORWARD',34,bold=True)
    # Distinct ordinal generation and known coordinate, joined at acquisition.
    f.rect(55,198,270,75,'#E9EFF7',BLUE,2,8);f.text(190,245,'Ordinal q = 16r + k',30,BLUE,anchor='middle')
    f.rect(55,296,270,75,'#F0ECF8',PURPLE,2,8);f.text(190,342,'Physical (x, y)',32,PURPLE,anchor='middle')
    f.line(325,236,400,236,BLUE,3,arrow=True);f.line(325,334,400,334,PURPLE,3,arrow=True)
    f.rect(400,199,285,173,GOLDPALE,'#A66F18',2,10)
    f.text(542,238,'Acquired records',32,bold=True,anchor='middle')
    for i in range(4):
        f.rect(418+i*64,258,57,55,'#FFFFFF','#A66F18',2,3)
    f.text(542,351,'RAM · 4 × 256 B',32,anchor='middle')
    f.text(542,413,'10 ms / acquisition',30,MUTED,anchor='middle')
    f.line(685,281,810,281,TEAL,4,arrow=True);f.text(748,259,'write',30,MUTED,anchor='middle')
    f.rect(810,198,360,90,PALE,TEAL,3,7)
    f.text(990,236,'Persistent payload',34,TEAL,bold=True,anchor='middle');f.text(990,274,'1024 B',30,TEAL,anchor='middle')
    f.rect(810,304,360,68,TEAL,TEAL,2,7);f.text(990,349,'Seal · 24 B',34,'#FFFFFF',bold=True,anchor='middle')
    f.line(990,288,990,302,TEAL,3,arrow=True)
    f.text(990,413,'2 ms combined event',30,MUTED,anchor='middle')
    f.line(1170,338 if final else 281,1260,338 if final else 281,TEAL,3,arrow=True)
    f.text(1357,188,'Row checkpoint',34,bold=True,anchor='middle')
    for i,n in enumerate(['A','B']):
        f.rect(1260+i*145,210,135,160,LIGHT,BLUE,2,8)
        f.text(1327+i*145,255,n,36,BLUE,bold=True,anchor='middle');f.text(1327+i*145,305,'64 B',30,anchor='middle')
        f.text(1327+i*145,350,'slot',30,MUTED,anchor='middle')
    f.text(1400,413,'after 4 blocks · 1 ms',30,MUTED,anchor='middle')
    f.line(55,468,1545,468,LINE,2,'9 8')
    f.cross(427,473,12,RED,4);f.text(455,513,'cut discards buffer',31,RED)
    f.text(55,579,'RESTART',34,bold=True)
    # Recovery sequence, with common q source and separate position path.
    f.rect(55,650,210,165,'#F0ECF8',PURPLE,2,10)
    f.text(160,703,'Home',36,PURPLE,bold=True,anchor='middle');f.text(160,749,'120 ms',32,anchor='middle');f.text(160,789,'known origin',30,MUTED,anchor='middle')
    f.line(265,733,347,733,INK,3,arrow=True)
    f.rect(347,624,463,253,'#F6F9FA',LINE,2,10)
    f.text(578,668,'Recovery reader · 6 ms',34,bold=True,anchor='middle')
    f.text(578,709,'checkpoint → row → seal scan',30,MUTED,anchor='middle')
    for b in range(4):
        xx=370+b*106;f.rect(xx,737,93,60,PALE if b<2 else '#FFFFFF',TEAL if b<2 else LINE,2,5)
        f.text(xx+46,775,f'b{b}',31,TEAL if b<2 else MUTED,anchor='middle')
        if b<2:f.check(xx+47,817)
        elif b==2:f.cross(xx+47,817,10,RED,3)
        else:f.line(xx+31,817,xx+62,817,LINE,3)
    f.text(578,856,'stop at first invalid / absent',30,RED,anchor='middle')
    f.line(810,733,900,733,BLUE,4,arrow=True);f.text(854,703,'q',32,BLUE,anchor='middle')
    f.rect(900,650,295,165,'#F0ECF8',PURPLE,2,10)
    f.text(1048,699,'Row anchor',36,PURPLE,bold=True,anchor='middle');f.text(1048,741,'30 ms',32,anchor='middle');f.text(1048,785,'travel to missing q',30,MUTED,anchor='middle')
    f.line(1195,733,1310,733,PURPLE,4,arrow=True)
    f.text(1252,695,'(x, y)',30,PURPLE,anchor='middle')
    f.rect(1310,650,235,165,PALE,TEAL,2,10)
    f.text(1428,704,'Acquire',36,TEAL,bold=True,anchor='middle');f.text(1428,749,'next sample',31,anchor='middle');f.text(1428,789,'10 ms',32,anchor='middle')
    f.line(578,877,578,949,BLUE,3)
    f.line(578,949,1428,949,BLUE,3,'10 6')
    f.line(1428,949,1428,815,BLUE,3,arrow=True)
    f.text(1000,934,'Logical label q = 88',33,BLUE,anchor='middle')
    f.text(57,1020,'Prefix acceptance: matching metadata + payload CRC',32,bold=True)
    f.text(57,1068,'Position acceptance: home + row anchor',32,PURPLE,bold=True)
    if final:
        # Clarify the stop boundary without adding another block or long paragraph.
        f.line(574,727,574,833,RED,3,'5 5')
        # Recovery reads both persistent objects; these lines carry metadata, not position.
        f.line(842,372,842,535,TEAL,2)
        f.line(1260,357,1230,357,BLUE,2)
        f.line(1230,357,1230,535,BLUE,2)
        f.line(788,535,1230,535,INK,2)
        f.line(788,535,788,624,INK,2,arrow=True)
        f.text(1137,507,'read durable state',30,MUTED,anchor='middle')
    f.save(poppler)

def build(out,font,bold,poppler,final=False):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    fig1(out/'figure_1',font,bold,poppler,final)
    fig2(out/'figure_2',font,bold,poppler,final)
