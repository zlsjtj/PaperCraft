"""重建已写好的修改，不调用模型。"""
from pathlib import Path
import argparse, subprocess, sys
p=argparse.ArgumentParser();p.add_argument('--skill',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
r=Path(__file__).resolve().parent
subprocess.run([sys.executable,str(a.skill/'scripts/apply_authored_edits.py'),'--source',str(r/'input/rough.docx'),'--edits',str(r/'authored-edits.json'),'--skill',str(a.skill),'--out',str(a.out)],check=True)
