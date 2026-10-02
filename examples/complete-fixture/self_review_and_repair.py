"""One explicitly recorded self-review after the retained first complete draft."""
from pathlib import Path
import argparse,copy,hashlib,json
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def main():
 p=argparse.ArgumentParser();p.add_argument('--first',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 e=json.loads((a.first/'authored-edits.json').read_text(encoding='utf-8'));changes=[]
 for r in e['edits']:
  old=r['after']
  if r['paragraph_id']=='P0004':
   r['after']=r['after'].replace('with all six hose/base leak checks passing. Maximum absolute differences from matched reference readings change from 0.11–0.14 to 0.12–0.14 kPa.', 'with both assemblies passing all three leak checks. Maximum absolute differences from matched reference readings increase by 0.01 kPa in two conditions and remain unchanged in the third.')
  if r['paragraph_id']=='P0008':
   r['after']=r['after'].replace('In the hose baseline, each reference side instead connects to the same reference source through its own hose. The base assembly preserves the sensor range and software difference calculation. Its practical change is to replace all three reference hose segments with one removable component while the sample modules remain in their original positions.', 'The hose baseline connects each reference side to the same source through its own hose. Replacing these hoses with the base leaves the sensor range and software difference calculation unchanged.')
  if r['paragraph_id']=='P0017':
   r['after']=r['after'].replace('The base changes how the common reference is assembled, not what pressure principle is available. The hose baseline already provides the common reference and remains a functional comparator in all three synthetic conditions. The base trades three individual hose connections for a single interface whose alignment and sealing must work together.', 'The paired conditions make replacement an interface-level tradeoff. The hose baseline already passes every leak check; the base must retain that qualification while reducing setup time. It exchanges three individual hose connections for a single interface whose alignment and sealing must work together.')
  if old!=r['after']:changes.append({'paragraph':r['paragraph_id'],'first':old,'final':r['after'],'reason':'Make the actual pressure-difference cost visible early and remove repeated operation descriptions while preserving the baseline and qualification condition.'})
 save(a.out/'authored-edits.json',e)
 s=json.loads((a.first/'figure_spec.json').read_text(encoding='utf-8'));s['figure_id']='pressure_base_DEMO_final'
 for v in s['items']:
  if v['id']=='gasket-label':v.update(x=28,align='left')
  if v['id']=='gasket-leader':v['points']=[[90,442],[90,311],[105,311]]
 save(a.out/'figure_spec.json',s)
 for n in ['caption.txt','alt_text.txt','derived-data.json','entry-candidates.md']:(a.out/n).write_bytes((a.first/n).read_bytes())
 save(a.out/'self-review.json',{'reviewer':'same generating model; self-review, not independent or human acceptance','first_complete_document':'../first-complete-v1/clean.docx','first_complete_figure':'../first-figure/figure.png','prose_changes':changes,'figure_change':{'first':'Gasket leader runs across the central reference-volume label.','final':'Leader and label are routed down the outer left margin; no information removed.','reason':'Actual PNG inspection detected a crossing missed by the engine geometry PASS.'},'selection':{'selected':'Assembled section; direct adjacency and one continuous reference cavity are simultaneously visible.','rejected':'Exploded alternative breaks visible diaphragm-reference adjacency and leaves pin leaders detached after translation.','retained_tradeoff':'The section shows one gasket as several cut segments; the caption explains that convention. The hose baseline is explained in prose, not a second diagram.'},'evidence_recheck':['All nine CSV records retained in native table','Two failed pin-free leak checks and NA pressure results retained','No inference of pressure equivalence from near values','No physical, sampled-statistical, manufacturing or novelty claim','60-second exclusion applies equally to hose and base; transient behavior remains unknown'],'scope':'candidate-only fresh transfer; not an old/plain controlled comparison or proof of general Nature quality'})
if __name__=='__main__':main()
