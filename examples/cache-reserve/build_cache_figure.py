"""Publication diagram of specified allowances, not elapsed time or measurements."""
from pathlib import Path
import argparse,subprocess,json,hashlib
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from PIL import Image,ImageOps
W,H=160*72/25.4,63*72/25.4
def build(out,font,bold,poppler):
    out.mkdir(parents=True,exist_ok=False);pdfmetrics.registerFont(TTFont('F',str(font)));pdfmetrics.registerFont(TTFont('FB',str(bold)))
    c=canvas.Canvas(str(out/'figure.pdf'),pagesize=(W,H),invariant=1);parts=[];labels=[]
    def rect(x,y,w,h,fill):
        c.setFillColor(HexColor(fill));c.rect(x,H-y-h,w,h,fill=1,stroke=0);parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"/>')
    def text(t,x,y,size=10,b=False):
        c.setFillColor(HexColor('#263B48'));c.setFont('FB' if b else 'F',size);c.drawString(x,H-y,t);parts.append(f'<text x="{x}" y="{y}" font-family="Arial" font-size="{size}" font-weight="{700 if b else 400}" fill="#263B48">{escape(t)}</text>');labels.append(t)
    text('Same scan ceiling, different allocation',12,19,11,True)
    text('Cap64',12,61,10,True);rect(102,42,336,27,'#D7E8EF');text('Up to 64 foreground examinations',160,59)
    text('Reserve',12,106,10,True);rect(102,87,252,27,'#D7E8EF');rect(354,87,84,27,'#F1D9A4')
    text('Up to 48 foreground',164,104);text('Up to 16',365,104)
    text('Maintenance after every request',289,134,9)
    text('Soft free-space target: 4, 8 or 16 MiB',102,164,10)
    c.showPage();c.save();(out/'figure.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="160mm" height="63mm" viewBox="0 0 {W} {H}"><title>Specified reference-examination allowances</title><desc>Both policies cap examinations at 64. Reserve allocates separate caps of 48 and 16, with no budget borrowing. Bars represent allowances, not measured work or duration.</desc>'+''.join(parts)+'</svg>',encoding='utf-8')
    subprocess.run([str(poppler),'-png','-singlefile','-r','180',str(out/'figure.pdf'),str(out/'figure')],check=True,capture_output=True)
    ImageOps.grayscale(Image.open(out/'figure.png')).save(out/'grayscale.png')
    (out/'record.json').write_text(json.dumps({'source':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'width_mm':160,'height_mm':63,'labels':labels,'meaning':'specified allowances, not measured time','data':[64,48,16],'svg':'all-vector'},indent=2),encoding='utf-8')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--font',type=Path,required=True);p.add_argument('--bold-font',type=Path,required=True);p.add_argument('--pdftoppm',type=Path,required=True);a=p.parse_args();build(a.out,a.font,a.bold_font,a.pdftoppm)
