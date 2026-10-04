"""Rebuild the three CONSTRUCTED_DEMO figures without overwriting existing output.

Requires reportlab, Pillow, numpy, pypdf, Arial fonts and Poppler pdftoppm.
Python build_figures.py --data sources --out NEW_DIRECTORY --font FONT.ttf
    --bold BOLD.ttf --pdftoppm /path/to/pdftoppm
"""
from __future__ import annotations
import argparse, csv, hashlib, html, json, math, subprocess
from pathlib import Path
import numpy as np
from PIL import Image
from pypdf import PdfReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

W = 160*72/25.4
C = {'ink':'#213547','muted':'#52616F','blue':'#086FA2','bluefill':'#DCEFF7',
     'red':'#AD4147','redfill':'#F6D8D5','purple':'#745A99','grey':'#768797',
     'pale':'#F4F7F9','line':'#B8C5CE','white':'#FFFFFF','clip':'#CBAB5C'}

class Drawing:
    def __init__(self, name, out, height):
        self.name, self.out, self.h = name, out, height
        self.svg=[]; self.labels=[]; self.n=0
        self.pdf=canvas.Canvas(str(out/f'{name}.pdf'),pagesize=(W,height),invariant=1)
        self.pdf.setTitle(f'{name} — CONSTRUCTED_DEMO; zero physical experiments')
        self.rect(0,0,W,height,C['white'],None)
    def uid(self, prefix): self.n+=1; return f'{self.name}-{prefix}-{self.n}'
    def rect(self,x,y,w,h,fill=None,stroke=C['line'],sw=.7,dash=None):
        ident=self.uid('rect'); ds=f' stroke-dasharray="{dash}"' if dash else ''
        self.svg.append(f'<rect id="{ident}" x="{x:.4f}" y="{y:.4f}" width="{w:.4f}" height="{h:.4f}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{sw}"{ds}/>')
        self.pdf.setLineWidth(sw); self.pdf.setDash([float(v) for v in dash.split()] if dash else [])
        if fill: self.pdf.setFillColor(HexColor(fill))
        if stroke: self.pdf.setStrokeColor(HexColor(stroke))
        self.pdf.rect(x,self.h-y-h,w,h,fill=bool(fill),stroke=bool(stroke))
    def line(self,pts,color=C['ink'],sw=.8,dash=None):
        ident=self.uid('line'); ds=f' stroke-dasharray="{dash}"' if dash else ''
        s=' '.join(f'{x:.4f},{y:.4f}' for x,y in pts)
        self.svg.append(f'<polyline id="{ident}" points="{s}" fill="none" stroke="{color}" stroke-width="{sw}"{ds}/>')
        self.pdf.setStrokeColor(HexColor(color)); self.pdf.setLineWidth(sw); self.pdf.setDash([float(v) for v in dash.split()] if dash else [])
        p=self.pdf.beginPath();p.moveTo(pts[0][0],self.h-pts[0][1])
        for x,y in pts[1:]: p.lineTo(x,self.h-y)
        self.pdf.drawPath(p)
    def poly(self,pts,fill,stroke=None,sw=.7):
        ident=self.uid('poly'); s=' '.join(f'{x:.4f},{y:.4f}' for x,y in pts)
        self.svg.append(f'<polygon id="{ident}" points="{s}" fill="{fill}" stroke="{stroke or "none"}" stroke-width="{sw}"/>')
        self.pdf.setFillColor(HexColor(fill));self.pdf.setLineWidth(sw);self.pdf.setDash([])
        if stroke:self.pdf.setStrokeColor(HexColor(stroke))
        p=self.pdf.beginPath();p.moveTo(pts[0][0],self.h-pts[0][1])
        for x,y in pts[1:]:p.lineTo(x,self.h-y)
        p.close();self.pdf.drawPath(p,fill=1,stroke=bool(stroke))
    def circle(self,x,y,r,fill=None,stroke=C['ink'],sw=.8):
        self.svg.append(f'<circle id="{self.uid("circle")}" cx="{x:.4f}" cy="{y:.4f}" r="{r}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{sw}"/>')
        self.pdf.setLineWidth(sw);self.pdf.setDash([])
        if fill:self.pdf.setFillColor(HexColor(fill))
        if stroke:self.pdf.setStrokeColor(HexColor(stroke))
        self.pdf.circle(x,self.h-y,r,fill=bool(fill),stroke=bool(stroke))
    def text(self,x,y,text,size=10,color=C['ink'],bold=False,align='left'):
        font='ArialBold' if bold else 'Arial'; width=pdfmetrics.stringWidth(text,font,size)
        ax={'left':'start','center':'middle','right':'end'}[align]
        self.svg.append(f'<text id="{self.uid("text")}" x="{x:.4f}" y="{y:.4f}" font-family="Arial" font-size="{size}" font-weight="{"bold" if bold else "normal"}" fill="{color}" text-anchor="{ax}">{html.escape(text)}</text>')
        self.pdf.setFont(font,size);self.pdf.setFillColor(HexColor(color))
        start=x if align=='left' else x-width/2 if align=='center' else x-width
        self.pdf.drawString(start,self.h-y,text)
        self.labels.append({'text':text,'pt':size,'bounds':[start,y-size,start+width,y+size*.22]})
    def arrow(self,a,b,color=C['ink'],sw=1,head=4):
        self.line([a,b],color,sw)
        angle=math.atan2(b[1]-a[1],b[0]-a[0]);p=[]
        for aa in (angle+2.65,angle-2.65):p.append((b[0]+head*math.cos(aa),b[1]+head*math.sin(aa)))
        self.poly([b,*p],color)
    def cross(self,x,y,size=3,color=C['red'],sw=1.2):
        self.line([(x-size,y-size),(x+size,y+size)],color,sw)
        self.line([(x-size,y+size),(x+size,y-size)],color,sw)
    def diamond(self,x,y,r=5,fill=C['red']):self.poly([(x,y-r),(x+r,y),(x,y+r),(x-r,y)],fill)
    def save(self,pdftoppm):
        self.pdf.showPage();self.pdf.save()
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="160mm" height="{self.h*25.4/72:.6f}mm" viewBox="0 0 {W:.6f} {self.h}">\n<title>CONSTRUCTED_DEMO — zero physical experiments</title>\n'+ '\n'.join(self.svg)+'\n</svg>\n'
        (self.out/f'{self.name}.svg').write_text(svg,encoding='utf-8')
        result=subprocess.run([str(pdftoppm),'-r','300','-singlefile','-png',str(self.out/f'{self.name}.pdf'),str(self.out/self.name)],capture_output=True,text=True)
        if result.returncode: raise RuntimeError(result.stderr)
        im=Image.open(self.out/f'{self.name}.png').convert('RGB')
        im.convert('L').save(self.out/f'{self.name}-gray.png')
        rgb=np.asarray(im,dtype=float)/255
        # Machado 2009 full-severity deuteranopia linear-RGB approximation.
        linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
        matrix=np.array([[.367322,.860646,-.227968],[.280085,.672501,.047413],[-.011820,.042940,.968881]])
        sim=np.clip(linear@matrix.T,0,1)
        sim=np.where(sim<=.0031308,sim*12.92,1.055*sim**(1/2.4)-.055)
        Image.fromarray(np.uint8(np.clip(sim*255,0,255))).save(self.out/f'{self.name}-deuteranopia.png')
        im.resize((round(160/25.4*96),round(self.h/72*96)),Image.Resampling.LANCZOS).save(self.out/f'{self.name}-160mm-96dpi.png')
        reader=PdfReader(self.out/f'{self.name}.pdf');p=reader.pages[0]
        dimensions=[float(p.mediabox.width)*25.4/72,float(p.mediabox.height)*25.4/72]
        assert abs(dimensions[0]-160)<1e-4 and dimensions[1]<=100
        bad=[v for v in self.labels if v['pt']<8 or v['bounds'][0]<-0.1 or v['bounds'][2]>W+.1 or v['bounds'][1]<0 or v['bounds'][3]>self.h]
        assert not bad,bad
        data={'technical_status':'PASS','width_mm':dimensions[0],'height_mm':dimensions[1],'min_label_pt':min(v['pt'] for v in self.labels),'label_count':len(self.labels),'raster_pixels':im.size,'searchable_pdf_text':bool(p.extract_text()),'label_bounds_within_canvas':True,'render_exit_code':result.returncode,'svg_independent_browser_render':'NOT_RUN','complete_collision_check':'NOT_RUN','visual_review':'PENDING','author_acceptance':'PENDING','overall_status':'REVIEW_REQUIRED','labels':self.labels}
        (self.out/f'{self.name}-technical.json').write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

def readcsv(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def figure1(out,fields,poppler):
    d=Drawing('figure1',out,278)
    d.text(10,13,'ROW3: local changes inside and outside a triggered row',10.5,bold=True)
    d.text(W-10,28,'CONSTRUCTED DEMO',8.5,C['muted'],align='right')
    for index,(event,title) in enumerate([('C01','Local change in refreshed row'),('C05','Local change in another row')]):
        left=12+index*227
        d.text(left,44,f'{event}  {title}',10,bold=True)
        gx=left+10;gy=58;s=1.9
        d.rect(gx,gy,96*s,76*s,C['pale'],C['line'])
        rows=[r for r in fields if r['event_id']==event and r['policy']=='ROW3']
        def pos(x,y):return gx+(x+48)*s,gy+(38-y)*s
        for row in 'SMN':
            r=next(r for r in rows if r['site_id']==row+'C')
            if r['row_triggered']=='1':
                _,py=pos(0,float(r['y_mm']))
                d.rect(gx+2,py-20,96*s-4,40,C['bluefill'],None)
        for r in rows:
            x,y=pos(float(r['x_mm']),float(r['y_mm']))
            d.circle(x,y,12,C['white'],C['line'])
            if r['was_probed']=='1':d.circle(x,y,15,None,C['blue'],1.7)
            d.text(x,y+3.3,r['site_id'],9.5,bold=True,align='center')
            if float(r['east_extra_um'])!=0:d.diamond(x+17,y-14,5)
        if event=='C01':
            x,y=pos(0,-24);d.text(x,y+23,'11.75 µm',9,C['blue'],align='center')
            d.text(left+101,227,'9/9 centers accepted',10.5,C['blue'],True,'center')
        else:
            x,y=pos(0,0);d.text(x,y+28,'12.85 µm',9,C['blue'],align='center')
            x,y=pos(0,24);d.text(x,y+22,'2.10 µm',9,C['muted'],align='center')
            x,y=pos(32,24);d.text(x,y+22,'18.0 µm error',8.5,C['red'],align='center')
            d.text(left+101,227,'8/9 centers accepted',10.5,C['red'],True,'center')
        d.text(left+101,244,'5 probes',9.5,C['muted'],align='center')
    d.circle(20,265,5,None,C['blue'],1.6);d.text(30,268,'Measured center',9)
    d.diamond(165,265,4);d.text(175,268,'Eastern-local offset',9)
    d.rect(320,258,12,12,C['bluefill'],None);d.text(339,268,'Row refreshed',9)
    d.save(poppler)

def figure2(out,poppler):
    d=Drawing('figure2',out,279)
    d.text(10,14,'Valid centers can still require a raised transfer',10.5,bold=True)
    d.text(W-10,29,'CONSTRUCTED DEMO',8.5,C['muted'],align='right')
    gx=25;gy=50;s=2.1
    def pos(x,y):return gx+(x+48)*s,gy+(38-y)*s
    d.text(25,41,'Carrier plan',10,bold=True)
    d.rect(gx,gy,96*s,76*s,C['pale'],C['line'])
    for row,y in [('N',24),('M',0),('S',-24)]:
        for col,x in [('W',-32),('C',0),('E',32)]:
            px,py=pos(x,y);d.rect(px-9*s,py-7*s,18*s,14*s,C['white'],C['line'])
            d.rect(px-4*s,py-3*s,8*s,6*s,C['bluefill'],None)
    kx,ky=pos(-16,21);d.rect(kx,ky,32*s,18*s,None,C['red'],1,'3 2')
    cx,cy=pos(-10,15);d.rect(cx,cy,20*s,6*s,C['clip'],C['muted'])
    # All four segments in the complete three-sentinel route; two are raised.
    route=[(-40,-30),(0,-24),(0,0),(0,24),(-40,-30)]
    for i,(a,b) in enumerate(zip(route,route[1:])):
        aa,bb=pos(*a),pos(*b);raised=i>=2
        d.arrow(aa,bb,C['red'] if raised else C['blue'],1.3,4)
    for lab,(x,y) in [('SC',(0,-24)),('MC',(0,0)),('NC',(0,24))]:
        px,py=pos(x,y);d.circle(px,py,3,C['blue'],None);d.text(px+10,py+3,lab,9.5,bold=True)
    for x,y in [(-43,-34),(43,-34)]:
        px,py=pos(x,y);d.rect(px-2.5,py-2.5,5,5,C['ink'],None)
    for x,y in [(-44,34),(44,34),(0,-34)]:
        px,py=pos(x,y);d.poly([(px,py-3),(px-3,py+3),(px+3,py+3)],C['purple'])
    px,py=pos(-40,-30);d.circle(px,py,3.2,C['white'],C['ink']);d.text(9,225,'PARK (−40, −30)',9)
    d.line([(45,218),(px,py+4)],C['muted'],.65)
    d.arrow((239,77),(239,54),C['muted'],.8,4);d.text(239,48,'N',9,align='center')
    d.line([(gx,237),(gx+96*s,237)],C['muted'],.6)
    d.line([(gx,234),(gx,240)],C['muted'],.6);d.line([(gx+96*s,234),(gx+96*s,240)],C['muted'],.6)
    d.text(gx+48*s,250,'96 mm',9,align='center')
    d.text(279,58,'x = 0 section',10,bold=True)
    # The supplied shoe underside and lateral envelope; unknown upper shape omitted.
    x0=278;scale_y=4.8;base=207;scale_z=20
    def section(y,z):return x0+y*scale_y,base-z*scale_z
    d.line([section(0,0),section(30,0)],C['muted'],.7)
    d.arrow(section(0,0),section(31,0),C['muted'],.7,3)
    d.text(424,219,'y',9)
    cl,ct=section(9,3.4);d.rect(cl,ct,6*scale_y,3.4*scale_z,C['clip'],C['muted'])
    d.text(cl+3*scale_y,191,'Clip',9,align='center')
    for z,color,dash in [(1.2,C['red'],'3 2'),(4.4,C['blue'],None)]:
        x,y=section(6,z);xx,_=section(18,z)
        d.line([(x,y-17),(x,y),(xx,y),(xx,y-17)],color,1.4,dash)
        d.text(391,y+3,f'{z:.1f} mm',9,color)
    d.text(281,91,'Shoe underside',9.5,C['blue'])
    d.text(278,234,'12 mm envelope in y',9)
    d.text(278,250,'Raise + lower: 0.74 s',9.5,bold=True)
    d.line([section(19,3.4),section(22,3.4)],C['muted'],.6)
    d.line([section(19,4.4),section(22,4.4)],C['muted'],.6)
    a=section(21,3.4);b=section(21,4.4);d.arrow(a,b,C['muted'],.7,3);d.arrow(b,a,C['muted'],.7,3)
    d.text(393,145,'1.0 mm',8.5,C['muted'])
    d.rect(13,264,10,6,C['clip'],C['muted']);d.text(29,271,'Clip',8.5)
    d.line([(78,267),(92,267)],C['red'],1,'3 2');d.text(98,271,'Center keepout',8.5)
    d.line([(200,267),(214,267)],C['red'],1.3);d.text(220,271,'Raised segment',8.5)
    d.rect(326,264,5,5,C['ink'],None);d.text(336,271,'Fiducial',8.5)
    d.poly([(393,263),(390,269),(396,269)],C['purple']);d.text(401,271,'Datum',8.5)
    d.save(poppler)

def figure3(out,runs,poppler):
    d=Drawing('figure3',out,279)
    events=[f'{k}{i:02}' for k in 'BEC' for i in range(1,9)]
    policies=['PLANE','ALL9','ROW3','SHIFT3']
    by={(r['event_id'],r['policy']):r for r in runs}
    xx=lambda j:68+j*14.3
    groups=[('Broad row',0),('Eastern local',8),('Combined',16)]
    d.text(W-10,12,'CONSTRUCTED DEMO',8.5,C['muted'],align='right')
    for lab,j in groups:
        d.text((xx(j)+xx(j+7))/2,29,lab,10,bold=True,align='center')
        d.line([(xx(j)-6,35),(xx(j+7)+6,35)],C['line'],.8)
    for i,p in enumerate(policies):
        y=47+i*17;d.text(56,y+3,p,9.5,bold=p=='ROW3',align='right')
        for j,e in enumerate(events):
            if by[e,p]['accepted_event']=='1':d.rect(xx(j)-3.4,y-3.4,6.8,6.8,C['blue'] if p=='ROW3' else C['ink'],None)
            else:d.cross(xx(j),y,3,C['red'],1.1)
    d.rect(68,113,6,6,C['ink'],None);d.text(80,120,'All 9 centers accepted',9)
    d.cross(237,116,3);d.text(247,120,'Event failed',9)
    top=149;bottom=247;yy=lambda t:bottom-(t-10)/20*(bottom-top)
    d.text(10,140,'Cycle (s)',9.5,bold=True)
    d.line([(xx(0)-5,top),(xx(0)-5,bottom),(xx(23)+5,bottom)],C['muted'],.7)
    for t in (10,15,20,25,30):
        y=yy(t);d.line([(xx(0)-5,y),(xx(23)+5,y)],C['line'],.5)
        d.text(xx(0)-10,y+3,str(t),8.5,align='right')
    for p,color in [('PLANE',C['grey']),('SHIFT3',C['purple']),('ALL9',C['ink'])]:
        t=float(by['B01',p]['total_cycle_s']); y=yy(t)
        d.line([(xx(0)-3,y),(xx(23)+3,y)],color,1,'4 2')
        d.text(xx(23)+9,y-2,p,9,color)
        d.text(xx(23)+9,y+9,f'{t:.2f} s',8.5,color)
    pts=[(xx(j),yy(float(by[e,'ROW3']['total_cycle_s']))) for j,e in enumerate(events)]
    for j,e in enumerate(events):
        x,y=pts[j]
        if by[e,'ROW3']['accepted_event']=='1':d.circle(x,y,2.5,C['blue'],None)
        else:d.cross(x,y,2.8,C['blue'],1.4)
    d.circle(158,138,2.5,C['blue'],None);d.text(174,141,'ROW3',9.5,C['blue'],True)
    d.text(278,141,'All attempts retained',9,C['muted'])
    for j,e in enumerate(events):d.text(xx(j),260,e[1:],8.5,align='center')
    for lab,j in [('B01–B08',0),('E01–E08',8),('C01–C08',16)]:
        d.text((xx(j)+xx(j+7))/2,275,lab,9,C['muted'],align='center')
    d.save(poppler)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',required=True,type=Path);ap.add_argument('--out',required=True,type=Path);ap.add_argument('--font',required=True,type=Path);ap.add_argument('--bold',required=True,type=Path);ap.add_argument('--pdftoppm',required=True,type=Path)
    a=ap.parse_args()
    if a.out.exists():raise SystemExit('Refusing to overwrite output; choose a new --out directory.')
    a.out.mkdir(parents=True)
    pdfmetrics.registerFont(TTFont('Arial',str(a.font)));pdfmetrics.registerFont(TTFont('ArialBold',str(a.bold)))
    fields=readcsv(a.data/'field_results.csv');runs=readcsv(a.data/'run_results.csv')
    assert len(fields)==864 and len(runs)==96
    figure1(a.out,fields,a.pdftoppm);figure2(a.out,a.pdftoppm);figure3(a.out,runs,a.pdftoppm)
    events=[f'{k}{i:02}' for k in 'BEC' for i in range(1,9)]
    spec={'provenance':'CONSTRUCTED_DEMO','actual_physical_experiments':0,'dimensions_mm':[160,'<=100'],'vector_status':'All SVG/PDF drawing primitives and text are vector; PNG is a rendered preview.','fonts':{'regular':str(a.font),'bold':str(a.bold),'pdf':'embedded subsets','svg':'requires Arial or compatible substitution'},'roles':C,'data_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(a.data.glob('*.csv'))},'figures':[
      {'id':'figure1','main_reading':'A local eastern change is measured only if its row triggers.','entities':['C01/'+s for s in ['SW','SC','SE','MW','MC','ME','NW','NC','NE']]+['C05/'+s for s in ['SW','SC','SE','MW','MC','ME','NW','NC','NE']],'aggregation':'Two explicit events; all nine sites each; not a whole-grid summary.','relations':'Coordinate position; probe rings; categorical row membership and local offset. No physical flow arrows.','locked_values':{'C01_observed_SC_um':11.75,'C05_observed_MC_um':12.85,'C05_observed_NC_um':2.10,'C05_NE_error_um':18.0},'sources':['field_results.csv','probe_trace.csv'],'depth':'D0'},
      {'id':'figure2','main_reading':'Safe endpoints do not imply a safe low-travel segment.','entities':['carrier','9 apertures','9 acquisition fields','clip','shoe envelope','2 fiducials','3 datums','PARK'],'relations':'Containment, center-envelope expansion and directional motion; side section is same x=0 geometry.','locked_values':{'carrier_mm':[96,76],'clip_xy_mm':[-10,10,9,15],'keepout_xy_mm':[-16,16,3,21],'shoe_xy_mm':[12,12],'z_low_mm':1.2,'z_clip_mm':3.4,'z_raised_mm':4.4,'raised_transfer_s':.74},'depth':'D0 top plan and y-z section; section has distinct labeled lateral/vertical scales'},
      {'id':'figure3','main_reading':'Qualification is conditional and ROW3 can be slower than ALL9.','entities':events,'aggregation':'All 24 paired events x 4 policies, no omitted failures.','relations':'Categorical acceptance matrix and quantitative 2D time ordinate, original event order.','locked_values':{'complete_runs':96,'event_accept_counts':{'PLANE':1,'ALL9':24,'ROW3':12,'SHIFT3':8}},'sources':['run_results.csv'],'depth':'D0'}],
      'allowable_changes':'Typography, layout and semantic styling; no altered source values, policy behavior, entity count, failure filtering or empirical claims.',
      'not_run':['Independent browser render of SVG','Word/PDF manuscript page review','Human author acceptance','Physical feasibility and performance','Literature novelty']}
    (a.out/'figure_spec.json').write_text(json.dumps(spec,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (a.out/'export_hashes.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(a.out.iterdir()) if p.is_file()},indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(a.out),'figures':3,'status':'RENDERED','visual_review':'PENDING'}))
if __name__=='__main__':main()
