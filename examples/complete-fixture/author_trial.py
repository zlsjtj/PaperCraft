"""Authored transfer artefacts. Rebuilds use explicit input and tool directories."""
from pathlib import Path
import argparse,csv,hashlib,json,subprocess,sys

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,obj): p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')

CAPTION = ('Fig. 1. DEMO sectional schematic of the removable reference base, not to scale. '
 'Three isolated sample chambers face one connected reference volume across three sensor diaphragms. '
 'The diaphragm boundaries remain closed. Two locating pins align the base; the orange segments are sections '
 'through one gasket around the three reference ports. The sample modules stay in position during replacement. '
 'Housing dimensions and the pin and gasket geometry are illustrative; pressure must be released before opening.')

TEXT = {
'P0001':'An aligned reference base for a three-channel pressure fixture',
'P0004':('Restoring three separate reference hoses can complicate replacement work in a modular pressure fixture. '
 'This DEMO study replaces those hoses with one removable reference base while keeping the three sample modules in position. '
 'The base exposes all three sensor reference sides to one connected volume; diaphragms preserve sample isolation. '
 'Two locating pins and one gasket register and seal the common interface. In three fixed synthetic paired conditions, '
 'the base reduces setup time from 8.0–8.6 to 3.0–3.3 min, with all six hose/base leak checks passing. '
 'Maximum absolute differences from matched reference readings change from 0.11–0.14 to 0.12–0.14 kPa. '
 'Removing the pins shortens attempts further but produces two failed leak checks in three attempts. '
 'The comparison therefore links replacement time to sealing qualification, without establishing physical performance or reliability.'),
'P0006':('A three-channel pressure fixture can already compare each sample with a common reference by connecting three sensor reference ports to the same source through separate hoses. '
 'The remaining assembly question is how to restore those reference connections while leaving the sample modules in place. '
 'Here, a single removable base replaces the three hose segments. This changes the replacement interface, while retaining the common reference, sensors, diaphragms and differential calculation.\n\n'
 'The interface must both locate the base and seal its three reference ports. The design couples two locating pins with a single gasket, so its shorter setup time must be read alongside leakage outcomes. '
 'The synthetic comparison below asks whether the complete assembly saves time in each paired condition and what is lost when the pins are omitted. '
 'It makes no claim of a new sensing principle or priority over published apparatus.'),
'P0008':('Figure 1 shows three mutually isolated sample chambers, S1–S3, above a common reference base. '
 'Each sensor compares the pressure in its own sample chamber with the pressure on the opposite side of its diaphragm. '
 'The base contains one connected reference volume extending beneath all three sensors; the sample chambers communicate neither with one another nor with that volume. '
 'The diaphragms provide the physical separation, not a route for flow.\n\n'
 'In the hose baseline, each reference side instead connects to the same reference source through its own hose. '
 'The base assembly preserves the sensor range and software difference calculation. Its practical change is to replace all three reference hose segments with one removable component while the sample modules remain in their original positions.'),
'P0009':('The upper surface of the base carries three sealing seats. Two locating pins register the base with those interfaces, and one gasket surrounds all three reference ports. '
 'Pressure must be released before the fixture is opened. A control omits the pins but can still be assembled, allowing the records to distinguish a quick attempt from an assembly that passes its leak check. '
 'A failed attempt retains its setup time and has no pressure result. An alternative with three disconnected reference boxes was neither manufactured nor tested and contributes no result.'),
'P0010':('The pressure quantity is the maximum absolute difference from the matched reference reading over the retained window. '
 'The first 60 s after each pressure change are excluded using the same time window for the hose and base assemblies. '
 'C1–C3 are fixed paired synthetic conditions, not random samples. Table 1 reports every assembly attempt, including failures; '
 'NA denotes a missing pressure result after a failed leak check, not zero. The records permit direct comparisons of these conditions, not population significance tests.'),
'P0012':CAPTION,
'P0014':('For C1, C2 and C3, respectively, setup time falls from 8.4 to 3.1, 8.0 to 3.0, and 8.6 to 3.3 min when the three hoses are replaced by the aligned base (Table 1). '
 'The absolute reductions are 5.3, 5.0 and 5.3 min, equivalent to 63.1%, 62.5% and 61.6% of each matched hose time. '
 'Both assemblies pass all three leak checks. Their maximum absolute pressure differences are 0.12 versus 0.13 kPa in C1, '
 '0.11 versus 0.12 kPa in C2, and 0.14 versus 0.14 kPa in C3. Thus the shorter setup is accompanied by a 0.01 kPa increase in two conditions and no change in the third; it is not a demonstrated accuracy improvement.\n\n'
 'The pin-free attempts take 2.7, 2.6 and 2.8 min. C1 and C2 fail the leak check and have no pressure value; only C3 passes, with a maximum absolute difference of 0.15 kPa. '
 'The two failed attempts cannot be counted as additional usable time savings. The complete base comparison changes the reference packaging as a whole, so these records do not isolate the separate time contributions of the pins, gasket or hose removal.'),
'P0015':'Table 1. Complete DEMO records for the fixed paired conditions. Setup time is in minutes and maximum absolute difference is in kPa. NA follows a failed leak check.',
'P0017':('The base changes how the common reference is assembled, not what pressure principle is available. The hose baseline already provides the common reference and remains a functional comparator in all three synthetic conditions. '
 'The base trades three individual hose connections for a single interface whose alignment and sealing must work together. '
 'Its recorded benefit is therefore the shorter setup of the complete, leak-passing assembly; the pin-free failures prevent treating the fastest attempt as the best usable configuration.\n\n'
 'These records identify a design tradeoff to test, rather than validate a device. They do not establish pressure equivalence, resolution, response time, lifetime, fatigue or manufacturing reliability. '
 'Long-term leakage, repeated insertion and behavior during the discarded stabilization interval remain unknown. '
 'No physical fixture has been built or experimentally validated, and no literature comparison establishes novelty. '
 'Within the stated DEMO conditions, the aligned removable base offers a coherent replacement operation, with its time advantage contingent on passing the leak check.')
}

def scene(inputs, alternative=False):
    s={'schema_version':1,'figure_id':'pressure_base_DEMO_'+('alternative' if alternative else 'first'),
    'mode':'new_schematic','demo':True,'evidence_status':'DEMO_SYNTHETIC_NOT_PHYSICAL',
    'scientific_message':'Three isolated samples face one connected reference space through closed diaphragms; the reference connection is packaged as an aligned removable base.',
    'source_refs':[{'path':n,'resolver':'original input directory supplied with --input','sha256':sha(inputs/n)} for n in ['source.docx','implementation.md','results.csv','README.md']],
    'forbidden_implications':['No flow crosses a diaphragm.','No sample-to-sample or sample-to-reference communication.','No measured geometry, deflection, flow direction, new sensing principle or real-device validation.'],
    'entities':[{'id':k,'semantic_role':role,'description':desc} for k,role,desc in [('base','housing','One removable reference base'),('reference','reference','One connected reference volume'),('gasket','seal','One gasket around three reference ports')]+[(f'S{i}','sample',f'Isolated sample chamber S{i}') for i in range(1,4)]+[(f'sensor{i}','housing',f'Sensor {i}') for i in range(1,4)]+[(f'diaphragm{i}','membrane',f'Closed separating diaphragm {i}') for i in range(1,4)]+[(f'pin{i}','pin',f'Locating pin {i}') for i in range(1,3)]],
    'relations':[], 'exact_labels':['S1','S2','S3','One connected reference volume','DEMO'],
    'locked_values':{'samples':3,'sensors':3,'diaphragms':3,'connected_reference_volumes':1,'locating_pins':2,'gaskets':1,'sample_modules_move_on_replacement':False,'drawing_scale':'schematic only','depressurize_before_opening':True},
    'count_constraints':[], 'reference_palette':'blue_gold_coral',
    'role_map':{'sample':{'base':'#76A8C4'},'reference':{'base':'#5AA59F'},'housing':{'base':'#A7B4BB'},'membrane':{'base':'#334957'},'seal':{'base':'#CB813D'},'pin':{'base':'#778794'}},
    'layout':{'archetype':'section_through_three_sample_modules','reading_order':'isolated samples, closed diaphragms, one continuous reference cavity, mounting interface'},
    'depth':{'mode':'D0','affects_quantitative_encoding':False},
    'edit_scope':{'allowed':['replace placeholder with scientific schematic'],'protected':['three sample chambers in one row','one reference base below','all source topology and DEMO boundaries']},
    'publication':{'target_journal':None,'eligibility':'unverified'},
    'output':{'width_mm':160,'placement_width_mm':160,'view_width':960,'view_height':510,'font_profile':'Arial 10.4 pt labels; 9.45 pt supplementary'},
    'items':[], 'caption':CAPTION,
    'alt_text':'DEMO sectional diagram. Three separate sample spaces S1, S2 and S3 each terminate at a closed diaphragm. Below all three is a single connected green reference cavity inside a removable base. Two exterior pins align the base; sections through one orange gasket flank the three reference ports. No arrows cross any diaphragm.'}
    a=s['items']
    def add(id,t,**kw): a.append({'id':id,'type':t,**kw})
    def rect(id,x,y,w,h,fill,stroke=None,**kw): add(id,'rect',x=x,y=y,w=w,h=h,fill=fill,stroke=stroke or 'none',stroke_width=2,**kw)
    def txt(id,text,x,y,size=22,align='left',**kw): add(id,'text',text=text,x=x,y=y,size=size,align=align,fill='#243A45',background=kw.pop('background','#FFFFFF'),**kw)
    def line(id,pts,**kw): add(id,'line',points=pts,fill='none',stroke='#627680',stroke_width=1.8,**kw)
    rect('canvas',0,0,960,510,'#FFFFFF')
    txt('title','Isolated samples above a removable reference base',28,38,24)
    txt('demo','DEMO',931,38,20,'right')
    txt('sample-heading','Sample chambers',480,97,22,'center')
    # One common housing and continuous internal reference cavity; solid border remains.
    rect('base-body',95,315,770,105,'#E6EBED','#738791',entity='base',logical_id='base',object_part='primary')
    commands=[['M',115,345],['L',195,345],['L',195,239],['L',305,239],['L',305,345],['L',425,345],['L',425,239],['L',535,239],['L',535,345],['L',655,345],['L',655,239],['L',765,239],['L',765,345],['L',845,345],['L',845,400],['L',115,400],['Z']]
    # sensor bodies behind the reference necks
    for i,c in enumerate([250,480,710],1):
        rect(f'sensor-{i}',c-78,209,156,106,'#E6EBED','#738791',entity=f'sensor{i}',logical_id=f'sensor{i}',object_part='primary')
    add('reference-cavity','path',commands=commands,fill='#D6EFEB',stroke='#39837C',stroke_width=2,entity='reference',logical_id='reference',object_part='primary')
    for i,c in enumerate([250,480,710],1):
        rect(f'chamber-{i}',c-65,127,130,108,'#D9EAF5','#5683A0',entity=f'S{i}',logical_id=f'S{i}',object_part='primary')
        txt(f'sample-{i}',f'S{i}',c,175,25,'center',entity=f'S{i}',background='#D9EAF5')
        rect(f'diaphragm-{i}',c-65,232,130,7,'#334957',entity=f'diaphragm{i}',logical_id=f'diaphragm{i}',object_part='primary')
    # The single gasket is intersected by the three ports in this section.
    gasket=[]
    for l,r in [(105,195),(305,425),(535,655),(765,855)]:
        gasket += [['M',l,307],['L',r,307],['L',r,315],['L',l,315],['Z']]
    add('gasket-section','path',commands=gasket,fill='#CB813D',stroke='none',entity='gasket',logical_id='gasket',object_part='primary')
    for i,x in enumerate([125,825],1):
        rect(f'pin-{i}',x,282,10,54,'#778794','#465C68',entity=f'pin{i}',logical_id=f'pin{i}',object_part='primary')
    txt('ref-label','One connected reference volume',480,380,24,'center',entity='reference',background='#D6EFEB')
    txt('pin-left','Pin',106,270,20,'center',entity='pin1')
    line('pin-left-leader',[[109,275],[130,287]])
    txt('pin-right','Pin',853,270,20,'center',entity='pin2')
    line('pin-right-leader',[[850,275],[830,287]])
    txt('sensor-label','Sensors',28,211,20)
    line('sensor-leader',[[108,214],[158,214],[174,221]])
    txt('diaphragm-label','Diaphragms',931,210,20,'right')
    line('diaphragm-leader',[[860,218],[817,218],[775,235]])
    txt('gasket-label','One gasket',250,463,22,'center')
    line('gasket-leader',[[250,442],[340,430],[350,312]])
    txt('base-label','Removable base',710,463,22,'center')
    line('base-leader',[[710,442],[710,421]])
    txt('section-note','Sectional schematic · not to scale',480,498,20,'center')
    for name,prefix,ids in [('samples','chamber-',[f'S{i}' for i in range(1,4)]),('sensors','sensor-',[f'sensor{i}' for i in range(1,4)]),('diaphragms','diaphragm-',[f'diaphragm{i}' for i in range(1,4)]),('pins','pin-',[f'pin{i}' for i in range(1,3)])]:
        # Entity scope excludes labels/leaders bearing similar IDs.
        s['count_constraints'].append({'name':name,'expected':len(ids),'scope':{'id_prefix':prefix},'expected_logical_ids':ids})
    # Labels with matching prefixes are explicitly annotations, excluded via changing IDs.
    for v in a:
        if v['type'] in ['text','line'] and any(v['id'].startswith(p) for p in ['sensor-','diaphragm-','pin-']): v['id']='annotation-'+v['id']
    for name,item,logical in [('reference volumes','reference-cavity','reference'),('gaskets','gasket-section','gasket'),('base','base-body','base')]:
        s['count_constraints'].append({'name':name,'expected':1,'scope':{'id_prefix':item},'expected_logical_ids':[logical]})
    for i in range(1,4):
        s['relations'] += [{'id':f'separation-{i}','from':f'S{i}','to':'reference','kind':'inhibition','meaning':f'diaphragm{i} physically separates the sample from the reference; represented by a closed boundary, without flow arrows'}, {'id':f'reference-{i}','from':'reference','to':f'sensor{i}','kind':'reference','meaning':'Sensor reference side directly faces the same connected cavity; represented by continuous space, without directional arrows'}]
    if alternative:
        # A genuinely distinct complete topology-first candidate: sample/modules in an upper band,
        # sealed measurement relation retained but the base is an exploded replaceable object.
        # Not selected: explosion breaks visible direct adjacency at the diaphragm.
        for v in a:
            if v['id'] in ['base-body','gasket-section','pin-1','pin-2','ref-label']:
                if 'y' in v:v['y']+=27
                if 'commands' in v:
                    for c in v['commands']:
                        for n in range(2,len(c),2):c[n]+=27
            if v['id']=='reference-cavity':
                # Three lowered reference-port sections remain continuous with the base.
                for c in v['commands']:
                    for n in range(2,len(c),2):c[n]+=27
            if v['id'] in ['gasket-label','gasket-leader','base-label','base-leader','section-note']:
                v['fill']='none';v['stroke']='none';v['text']='' if v['type']=='text' else v.get('text','')
        s['caption']='Alternative DEMO exploded schematic. Upper and lower components are separated for assembly interpretation; this is not the operating state. '+CAPTION
        s['layout']['archetype']='exploded_section'
        s['items']=[v for v in a if v['id'] not in ['gasket-label','gasket-leader','base-label','base-leader','section-note']]
        txt('exploded-note','Exploded view for replacement · depressurize first',480,495,20,'center')
    return s

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    a.out.mkdir(parents=True,exist_ok=False)
    from docx import Document
    paras=Document(a.input/'source.docx').paragraphs
    edits=[]
    for pid,after in TEXT.items():
        before=paras[int(pid[1:])-1].text
        edits.append({'paragraph_id':pid,'operation':'replace_paragraph','before':before,'after':after,'reason':'Organize the assembly change, matched evidence and limitations into a connected argument.','source':['source.docx','implementation.md','results.csv']})
    save(a.out/'authored-edits.json',{'source_sha256':sha(a.input/'source.docx'),'edits':edits})
    save(a.out/'figure_spec.json',scene(a.input))
    save(a.out/'alternative-spec.json',scene(a.input,True))
    rows=list(csv.DictReader((a.input/'results.csv').open(encoding='utf-8')))
    calc=[]
    for c in ['C1','C2','C3']:
        b=next(r for r in rows if r['condition']==c and r['assembly']=='three hoses');n=next(r for r in rows if r['condition']==c and r['assembly']=='reference base')
        x,y=float(b['setup_min']),float(n['setup_min'])
        calc.append({'condition':c,'hose_min':x,'base_min':y,'absolute_reduction_min':round(x-y,8),'relative_reduction_pct':100*(x-y)/x,'denominator':'matched hose setup time','synthetic':True})
    save(a.out/'derived-data.json',{'source_sha256':sha(a.input/'results.csv'),'rows':calc,'inference':'direct arithmetic only; no statistics or real-device performance'})
    (a.out/'entry-candidates.md').write_text('''# Authored entry candidates, before full draft selection\n\n## Selected: replacement operation\nAn aligned reference base for a three-channel pressure fixture\n\nA three-channel pressure fixture can already compare each sample with a common reference by connecting three sensor reference ports to the same source through separate hoses. The remaining assembly question is how to restore those reference connections while leaving the sample modules in place. Here, a single removable base replaces the three hose segments.\n\n## Alternative: fastest attempt versus usable assembly\nWhen shorter setup fails the seal: a synthetic pressure-fixture comparison\n\nRemoving locating pins makes a pressure-fixture assembly quicker to attempt, but two of three synthetic attempts fail their leak checks. A useful replacement procedure must therefore keep sealing qualification beside setup time. We examine one aligned reference base that replaces three separate reference hoses while retaining the same sensors and isolated samples.\n\n## Choice\nThe operation-led entry establishes the actual physical change before asking the reader to interpret failed controls. The failure-led alternative makes qualification salient but delays the fixture's identity and risks making a small synthetic control seem like the primary research result. The selected route spends one extra sentence acknowledging the common-reference baseline.\n''',encoding='utf-8')
    (a.out/'caption.txt').write_text(CAPTION,encoding='utf-8')
    (a.out/'alt_text.txt').write_text(scene(a.input)['alt_text'],encoding='utf-8')
    (a.out/'source-prose.txt').write_text('\n\n'.join(p.text for p in paras),encoding='utf-8')

if __name__=='__main__':main()
