"""Two original, data-bound DEMO figures. No solver or measured data is generated.

Dependencies: reportlab, pypdf, Pillow, numpy; Poppler pdftoppm, Arial-compatible TTFs.
All paths are parameters. The output directory must not already exist.
"""
from __future__ import annotations
import argparse, csv, hashlib, html, json, math, shutil, subprocess
from pathlib import Path
import numpy as np
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from pypdf import PdfReader

P = {'ink':'#213741', 'muted':'#52636C', 'line':'#B9C7CD', 'light':'#F1F5F6',
     'reuse':'#137C77', 'reuse_fill':'#E4F2EE', 'refresh':'#B47B12',
     'refresh_fill':'#F8EFDA', 'test':'#306EA0', 'test_fill':'#E9F1F8',
     'transport':'#CBD5DB', 'p4':'#656076', 'fail':'#AF3D40', 'white':'#FFFFFF'}
MM=72/25.4
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fmt(v): return f'{v:g}'

class Figure:
    def __init__(self, name, height, out, font, bold):
        self.name,self.w,self.h,self.out=name,160,height,out
        pdfmetrics.registerFont(TTFont('Main',str(font)))
        pdfmetrics.registerFont(TTFont('Bold',str(bold)))
        self.pdf=canvas.Canvas(str(out/(name+'.pdf')),pagesize=(160*MM,height*MM))
        self.pdf.setTitle(name+' | DEMO FICTION')
        self.svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="160mm" height="{height}mm" viewBox="0 0 160 {height}">',
                  '<title>DEMO FICTION: owner-consistent heat-conductance reuse</title>',
                  '<desc>Constructed design and stipulated accounting; no solver was executed.</desc>']
        self.texts=[]
        self.box(0,0,160,height,P['white'],None)
    def box(self,x,y,w,h,fill,stroke=P['line'],lw=.28,r=0):
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{lw}"/>')
        c=self.pdf
        c.setLineWidth(lw*MM)
        if fill:c.setFillColor(HexColor(fill))
        if stroke:c.setStrokeColor(HexColor(stroke))
        c.roundRect(x*MM,(self.h-y-h)*MM,w*MM,h*MM,r*MM,stroke=bool(stroke),fill=bool(fill))
    def line(self,x1,y1,x2,y2,color=P['line'],lw=.3,dash=False,arrow=False):
        self.svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{lw}"'+(' stroke-dasharray="1.2 1"' if dash else '')+'/>')
        c=self.pdf;c.setStrokeColor(HexColor(color));c.setLineWidth(lw*MM);c.setDash([1.2*MM,MM] if dash else [])
        c.line(x1*MM,(self.h-y1)*MM,x2*MM,(self.h-y2)*MM);c.setDash([])
        if arrow:
            a=math.atan2(y2-y1,x2-x1);l=1.8;s=.8
            self.poly([(x2,y2),(x2-l*math.cos(a)+s*math.sin(a),y2-l*math.sin(a)-s*math.cos(a)),(x2-l*math.cos(a)-s*math.sin(a),y2-l*math.sin(a)+s*math.cos(a))],color,None)
    def poly(self,points,fill,stroke=None,lw=.3):
        self.svg.append(f'<polygon points="'+ ' '.join(f'{x},{y}' for x,y in points)+f'" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{lw}"/>')
        c=self.pdf;p=c.beginPath();p.moveTo(points[0][0]*MM,(self.h-points[0][1])*MM)
        for x,y in points[1:]:p.lineTo(x*MM,(self.h-y)*MM)
        p.close()
        if fill:c.setFillColor(HexColor(fill))
        if stroke:c.setStrokeColor(HexColor(stroke))
        c.setLineWidth(lw*MM);c.drawPath(p,stroke=bool(stroke),fill=bool(fill))
    def circle(self,x,y,r,fill,stroke=None,lw=.3):
        self.svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{lw}"/>')
        c=self.pdf
        if fill:c.setFillColor(HexColor(fill))
        if stroke:c.setStrokeColor(HexColor(stroke))
        c.setLineWidth(lw*MM);c.circle(x*MM,(self.h-y)*MM,r*MM,stroke=bool(stroke),fill=bool(fill))
    def text(self,x,y,s,size=10,color=P['ink'],bold=False,align='left',id=None):
        # Coordinates specify baseline; SVG text remains independently editable.
        face='Bold' if bold else 'Main';width=pdfmetrics.stringWidth(s,face,size)/MM
        lo=x-(width/2 if align=='center' else width if align=='right' else 0)
        self.texts.append({'text':s,'x':x,'y':y,'size_pt':size,'left':lo,'right':lo+width,'top':y-size/MM,'bottom':y,'id':id or f't{len(self.texts)}'})
        if lo<-.1 or lo+width>160.1 or y>self.h or y-size/MM<-.1:raise ValueError(f'Out of bounds: {s} ({lo}, {lo+width})')
        # Check actual font coverage, including ASCII/Greek/mathematical signs.
        cmap=pdfmetrics.getFont(face).face.charToGlyph
        if any(ord(ch) not in cmap for ch in s): raise ValueError(f'Font coverage: {s}')
        anchor={'left':'start','center':'middle','right':'end'}[align]
        self.svg.append(f'<text id="{self.texts[-1]["id"]}" x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="{size/MM}" font-weight="{"bold" if bold else "normal"}" text-anchor="{anchor}" fill="{color}">{html.escape(s)}</text>')
        c=self.pdf;c.setFont(face,size);c.setFillColor(HexColor(color))
        c.drawString(lo*MM,(self.h-y)*MM,s)
    def diamond(self,x,y,r,fill,stroke,lw=.4):self.poly([(x,y-r),(x+r,y),(x,y+r),(x-r,y)],fill,stroke,lw)
    def save(self,pdftoppm):
        self.svg.append('</svg>');(self.out/(self.name+'.svg')).write_text('\n'.join(self.svg),encoding='utf-8')
        self.pdf.showPage();self.pdf.save()
        subprocess.run([str(pdftoppm),'-singlefile','-r','300','-png',str(self.out/(self.name+'.pdf')),str(self.out/self.name)],check=True,capture_output=True)
        im=Image.open(self.out/(self.name+'.png')).convert('RGB')
        im.convert('L').convert('RGB').save(self.out/(self.name+'_gray.png'))
        a=np.array(im)/255.;lin=np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
        # Machado et al. 2009, full-severity deuteranomaly transform; simulation only.
        matrix=np.array([[.367322,.860646,-.227968],[.280085,.672501,.047413],[-.011820,.042940,.968881]])
        sim=np.clip(lin@matrix.T,0,1);srgb=np.where(sim<=.0031308,12.92*sim,1.055*sim**(1/2.4)-.055)
        Image.fromarray(np.uint8(np.clip(srgb*255,0,255))).save(self.out/(self.name+'_deuteranopia.png'))
        pg=PdfReader(self.out/(self.name+'.pdf')).pages[0]
        audit={'pdf_mm':[round(float(pg.mediabox.width)/MM,4),round(float(pg.mediabox.height)/MM,4)],'png_px':im.size,'min_font_pt':min(t['size_pt'] for t in self.texts),'text_count':len(self.texts),'text_bounds_checked':True,'font_coverage_checked':True,'pdf_text_searchable':bool(pg.extract_text().strip()),'items':self.texts}
        (self.out/(self.name+'_technical.json')).write_text(json.dumps(audit,indent=2),encoding='utf-8')

def mechanism(args,out):
    f=Figure('figure1_owner_guard',104,out,args.font,args.bold_font)
    f.text(2,6,'a   One face, one owner, one snapshot event',10.5,bold=True)
    f.text(158,6,'DEMO SCHEMATIC',8.5,color=P['muted'],align='right')
    # Two cells are a representative boundary detail, not a 2-cell group.
    f.text(18,16,'Group A',10,bold=True,align='center');f.text(50,16,'Group B',10,bold=True,align='center')
    f.box(5,20,29,22,P['reuse_fill'],P['reuse'],.4)
    f.box(34,20,29,22,P['light'],P['muted'],.4)
    f.line(34,18,34,44,P['ink'],.55,dash=True)
    f.text(19.5,27,'Cell i',10,align='center');f.text(48.5,27,'Cell j',10,align='center')
    f.circle(19.5,33,.9,P['ink']);f.circle(48.5,33,.9,P['ink'])
    f.line(20.5,33,47.5,33,P['ink'],.6,arrow=True)
    f.text(34,39,'f : i < j',9.5,align='center')
    f.line(19.5,43,19.5,57,P['reuse'],.35,dash=True)
    f.line(48.5,43,48.5,57,P['reuse'],.35,dash=True)
    f.text(34,50,'Owner A stores together',10,bold=True,align='center')
    f.box(5,55,58,15,P['reuse_fill'],P['reuse'],.5,r=1.3)
    for x in (24.3,43.6):f.line(x,55,x,70,P['reuse'],.3)
    f.text(14.6,64,'G cached',9.5,align='center');f.text(33.9,64,'T i at r',9.5,align='center');f.text(53.3,64,'T j at r',9.5,align='center')
    f.text(34,76,'Same refresh event r',10,align='center')
    f.line(69,16,69,80,P['line'],.3)
    f.text(76,16,'b   Guard before flux',10.5,bold=True)
    f.box(77,22,80,15,P['test_fill'],P['test'],.4,r=1.4)
    f.text(117,31,'b(D) = exp(βD) − 1',11,align='center')
    f.line(117,37,117,41,P['test'],.4)
    f.line(94,41,141,41,P['test'],.4)
    f.line(94,41,94,49,P['reuse'],.45,arrow=True);f.line(141,41,141,49,P['refresh'],.45,arrow=True)
    f.text(88,46,'≤ η',10,color=P['reuse'],align='right');f.text(147,46,'> η',10,color=P['refresh'])
    f.box(77,50,34,18,P['reuse_fill'],P['reuse'],.4,r=1.3)
    f.box(123,50,34,18,P['refresh_fill'],P['refresh'],.4,r=1.3)
    f.text(94,57,'Reuse',11,bold=True,align='center');f.text(94,64,'stored pair',9.5,align='center')
    f.text(140,57,'Refresh',11,bold=True,align='center');f.text(140,64,'whole owner',9.5,align='center')
    f.line(94,69,94,75,P['reuse'],.4);f.line(140,69,140,75,P['refresh'],.4)
    f.line(94,75,140,75,P['ink'],.35);f.line(117,75,117,81,P['ink'],.4,arrow=True)
    f.box(3,85,154,15,P['light'],None,r=1)
    if args.revision=='first':
        f.text(80,91,'All decisions finish → check row sums → one flux per face',10,align='center')
        f.text(80,97,'Same q enters its two cells with opposite signs',10,align='center')
    else:
        f.text(9,91,'All guards finish',10,bold=True)
        f.line(40,89.8,46,89.8,P['ink'],.4,arrow=True)
        f.text(50,91,'Row sums',10,bold=True)
        f.line(72,89.8,78,89.8,P['ink'],.4,arrow=True)
        f.text(82,91,'One flux q',10,bold=True)
        f.line(103,89.8,109,89.8,P['ink'],.4,arrow=True)
        f.text(113,91,'−q at i / +q at j',10,bold=True)
        f.text(80,97,'Same cached coefficient and endpoint snapshots belong to owner A.',9,align='center',color=P['muted'])
    f.save(args.pdftoppm)

def results(args,out,rows):
    f=Figure('figure2_cost_and_qualification',120,out,args.font,args.bold_font)
    cases=list(dict.fromkeys(r['case'] for r in rows));by={(r['case'],r['method']):r for r in rows}
    labels={'plate_slow':'Slow plate','boundary_ramp':'Boundary ramp','moving_source':'Moving source','switching_load':'Switching load','small_mesh':'Small mesh','static_conduction':'Constant G'}
    f.text(2,6,'a   Faster only when cost and accuracy agree',10.5,bold=True)
    f.text(158,6,'DEMO ACCOUNTING',8.5,color=P['muted'],align='right')
    # Method shape is independent of qualification and survives grayscale.
    f.circle(5,12,1.3,P['reuse']);f.text(8,13,'G',9)
    f.diamond(20,12,1.4,P['p4'],P['p4']);f.text(23,13,'P4',9)
    f.diamond(40,12,1.4,P['white'],P['fail']);f.line(38.8,13.2,41.2,10.8,P['fail'],.35)
    f.text(44,13,'Fails 0.010 K limit',9)
    f.text(116,13,'Final error (K)',9,bold=True)
    f.text(133,18,'P4',9,color=P['p4'],align='center');f.text(151,18,'G',9,color=P['reuse'],align='center')
    x0,x1=43,119
    def x(v):return x0+(v+25)/60*(x1-x0)
    for t in (-20,0,20,30):
        f.line(x(t),20,x(t),66,P['line'],.25,dash=(t==0));f.text(x(t),72,f'{t:+d}' if t else 'V = 0',9,align='center')
    deriv=[]
    for k,case in enumerate(cases):
        y=23+7.9*k;f.text(2,y+1,labels[case],9.5,bold=True)
        v=float(by[case,'V']['total_ms'])
        for meth,dy in [('P4',-1.25),('G',1.25)]:
            r=by[case,meth];delta=(float(r['total_ms'])/v-1)*100;ok=r['accuracy_pass']=='TRUE'
            col=P['reuse'] if meth=='G' else P['p4'];yy=y+dy
            f.line(x(0),yy,x(delta),yy,col,.42)
            if meth=='G':f.circle(x(delta),yy,1.2,col if ok else P['white'],col,.38)
            else:f.diamond(x(delta),yy,1.45,col if ok else P['white'],col,.38)
            if not ok:f.line(x(delta)-1.3,yy+1.3,x(delta)+1.3,yy-1.3,P['fail'],.4)
            err=float(r['max_abs_error_K']);f.text(133 if meth=='P4' else 151,y+1,f'{err:.3f}',9,color=P['ink'] if ok else P['fail'],align='center',bold=not ok)
            deriv.append({'case':case,'method':meth,'source_total_ms':float(r['total_ms']),'reference_V_ms':v,'time_change_pct':delta,'accuracy_pass':ok,'error_K':err})
    f.text(80,78,'Total time change from V (%)',9.5,align='center')
    f.text(2,88,'b   Slow plate: 90% fewer face evaluations, 11.4% less total time',10.5,bold=True)
    # Honest linear stacked cost scale; starts at zero, all three methods shown.
    bx0,bx1=20,126;scale=(bx1-bx0)/420
    for n,meth in enumerate(('V','P4','G')):
        r=by['plate_slow',meth];y=92+n*6.1;f.text(12,y+3.3,meth,9.5,bold=True,align='right');start=bx0
        for key,col in [('transport_ms',P['transport']),('coefficient_ms',P['refresh']),('guard_ms',P['test'])]:
            w=float(r[key])*scale
            if w:f.box(start,y,w,4.3,col,None)
            start+=w
        f.text(start+2,y+3.3,r['total_ms']+' ms',9.5)
    for xx,t,col in [(20,'Transport',P['transport']),(62,'Coefficients',P['refresh']),(111,'Group test',P['test'])]:
        f.box(xx,114,3,3,col,None);f.text(xx+5,116.8,t,9)
    f.save(args.pdftoppm)
    return deriv

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--font',type=Path,required=True);p.add_argument('--bold-font',type=Path,required=True);p.add_argument('--pdftoppm',type=Path,required=True);p.add_argument('--revision',choices=['first','final'],default='first');args=p.parse_args()
    if args.out.exists():p.error('Refusing to overwrite existing output directory: '+str(args.out))
    for path in (args.input,args.font,args.bold_font,args.pdftoppm):
        if not path.exists():p.error('Required dependency missing: '+str(path))
    rows=list(csv.DictReader((args.input/'results_runtime.csv').open(encoding='utf-8-sig')))
    sweep=list(csv.DictReader((args.input/'results_guard_sweep.csv').open(encoding='utf-8-sig')))
    assert len(rows)==18 and len(sweep)==6
    for r in rows+sweep:
        assert r['provenance']=='DEMO_STIPULATED'
        assert math.isclose(sum(float(r[k]) for k in ['guard_ms','coefficient_ms','transport_ms']),float(r['total_ms']),rel_tol=1e-12)
        assert (float(r['max_abs_error_K'])<=float(r['accuracy_limit_K']))==(r['accuracy_pass']=='TRUE')
    dup=next(r for r in sweep if float(r['eta'])==.003)
    assert dup==next(r for r in rows if r['case']=='moving_source' and r['method']=='G')
    args.out.mkdir(parents=True)
    mechanism(args,args.out);deriv=results(args,args.out,rows)
    (args.out/'derived_metrics.json').write_text(json.dumps({'time_change_formula':'(method_ms / V_ms - 1) * 100','runtime_rows_read':18,'sweep_rows_read':6,'duplicate_sweep_row':'eta=0.003 equals moving_source G; not counted independently','derived':deriv},indent=2),encoding='utf-8')
    manifest={'revision':args.revision,'evidence':'DEMO_STIPULATED; no solver execution, physical experiment or novelty evidence','inputs':{p.name:sha(p) for p in sorted(args.input.iterdir()) if p.is_file()},'builder_sha256':sha(__file__),'font_sha256':sha(args.font),'bold_font_sha256':sha(args.bold_font),'exports':{p.name:sha(p) for p in sorted(args.out.iterdir()) if p.is_file()},'technical_status':'PASS','scientific_review_status':'REVIEW_REQUIRED','visual_review_status':'REVIEW_REQUIRED','author_acceptance':'PENDING','overall_status':'REVIEW_REQUIRED'}
    (args.out/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'out':str(args.out),'figures':2,'input_rows':[len(rows),len(sweep)],'min_font_pt':8.5}))

if __name__=='__main__':main()
