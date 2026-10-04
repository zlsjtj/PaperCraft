"""Rebuild authored full-text edits against the retained complete DEMO."""
from pathlib import Path
import argparse,subprocess,sys

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--paper-skill',type=Path,default=Path(__file__).resolve().parents[2])
    a=p.parse_args()
    example=Path(__file__).resolve().parent
    source=example.parent/'complete-fixture/final-delivery/clean.docx'
    subprocess.run([sys.executable,'-X','utf8','-B',str(a.paper_skill/'scripts/apply_authored_edits.py'),'--source',str(source),'--edits',str(example/'edits.json'),'--skill',str(a.paper_skill),'--out',str(a.out)],check=True)

if __name__=='__main__':main()
