"""Small synthetic record: shorter phrasing introduces an unsupported claim."""
from pathlib import Path
import argparse,hashlib,json
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    versions={'baseline':'In the three supplied traces, fewer nodes were evaluated in two cases; wall-clock time was not measured.','candidate':'The method is faster.'}
    arts=[]
    for name,s in versions.items():
        f=a.out/(name+'.txt');f.write_text(s,encoding='utf8');arts.append({'id':name,'path':f.name,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
    evidence=[{'artifact':n,'locator':'whole sentence'} for n in versions]
    row={'id':'R1','requested_effect':'Read the result with less effort without changing its meaning','baseline_observation':'Explicit cases and measurement boundary','candidate_observation':'Shorter, but invents a runtime conclusion','assessment':'mixed','evidence':evidence,'dimensions':[{'name':'word burden','assessment':'improved','baseline_observation':'Longer statement','candidate_observation':'One short statement','evidence':evidence},{'name':'scientific meaning','assessment':'regressed','baseline_observation':'Only node-count evidence','candidate_observation':'Unmeasured runtime implied','evidence':evidence}],'remaining':['A future revision may shorten the original without claiming speed.'],'tradeoff':'Concision does not justify changing the measured quantity','decision':{'action':'rollback','reason':'The shorter candidate changes the scientific claim','chosen_artifact':'baseline','rollback_to':'baseline'}}
    (a.out/'record.json').write_text(json.dumps({'schema_version':2,'reviewer':'Constructed explanatory example, not a reader study','artifacts':arts,'requirements':[row]},ensure_ascii=False,indent=2),encoding='utf8')
if __name__=='__main__':main()
