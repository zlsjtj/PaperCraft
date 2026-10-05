"""用确切交付页面制作网页预览；这是成稿导览，不是生成过程录像。"""
from pathlib import Path
import argparse, subprocess
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader

def main():
    p=argparse.ArgumentParser();p.add_argument('--pages',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--font',type=Path,required=True);p.add_argument('--bold-font',type=Path,required=True);p.add_argument('--pdftoppm',type=Path,required=True);a=p.parse_args()
    if a.out.exists():p.error('输出目录必须不存在')
    a.out.mkdir(parents=True);pdfmetrics.registerFont(TTFont('zh',str(a.font),subfontIndex=0));pdfmetrics.registerFont(TTFont('zhb',str(a.bold_font),subfontIndex=0))
    w,h=1200,650;c=canvas.Canvas(str(a.out/'overview.pdf'),pagesize=(w,h),invariant=1)
    c.setFillColor(HexColor('#F3F5F5'));c.rect(0,0,w,h,fill=1,stroke=0)
    def text(t,x,y,size=24,bold=False,color='#20323B'):
        c.setFont('zhb' if bold else 'zh',size);c.setFillColor(HexColor(color));c.drawString(x,h-y,t)
    text('同一份材料，连起问题、设计与证据',40,56,36,True)
    text('PaperCraft × FigureCraft  /  公开教学构造案例',41,94,20,color='#5C6A70')
    for i,label in enumerate(['问题与机制','必要操作与完整数据','收益、代价与边界'],1):
        x=40+(i-1)*394
        text(f'0{i}',x,144,22,True,color='#A44C37');text(label,x+43,144,23,True)
        img=ImageReader(str(a.pages/f'page-{i}.png'));iw,ih=img.getSize();pw=320;ph=pw*ih/iw
        c.setFillColor(HexColor('#DDE3E5'));c.rect(x+6,h-170-ph-6,pw,ph,fill=1,stroke=0)
        c.drawImage(img,x,h-170-ph,width=pw,height=ph)
    c.save();subprocess.run([str(a.pdftoppm),'-r','110','-png','-singlefile',str(a.out/'overview.pdf'),str(a.out/'overview')],check=True,capture_output=True)
if __name__=='__main__':main()
