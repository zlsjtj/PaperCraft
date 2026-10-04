"""Rebuild the frozen DEMO revision. Explicit dependencies; never overwrite an output."""
from pathlib import Path
import argparse, csv, hashlib, json, subprocess, sys, time, shutil, zipfile, copy, os
sys.dont_write_bytecode=True
os.environ['PYTHONDONTWRITEBYTECODE']='1'
from datetime import datetime, timezone
from lxml import etree as ET
from docx import Document
from docx.shared import Mm, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2) if not isinstance(v,str) else v,encoding='utf-8')

CAPTION='Figure 1. Three uses of the same single-axis compression pad on a pitch-sloped coupon. E fixes the horizontal pad before approach; F allows pitch rotation during seating and the ramp; L settles under 10 N, then locks during the acknowledged preload hold without lifting. Filled and open lock markers denote clamp state, not clamp construction. The side views repeat one fixture; the circular pin is viewed along its axis. The arc denotes permitted pitch rotation, not a measured angle. Slopes and the E-mode gap are exaggerated. The roll slope is outside the permitted motion. Poses are schematic, not contact-pressure maps.'

DRAFT={
'P0002':'When to lock a pivoting compression pad',
'P0004':'''A pivoting pad can settle onto a sloping coupon, but leaving it free during compression may permit lateral drift. This constructed teaching study compares three operating sequences on one existing fixture: lock before approach (E), remain free (F), or seat under preload and then lock (L). For a 1 degree pitch slope, L gives a 2.3% coefficient of variation (CV) of endpoint force across reseatings and 19 micrometres drift, compared with 2.1% and 125 micrometres for F; seating takes 32 rather than 17 seconds. Early locking gives less drift but 7.2% force CV. Flat coupons show no repeatability benefit from L, and a slope across the available axis remains uncompensated. The records illustrate a conditional tradeoff in lock timing, without establishing material accuracy or a new joint design.''',
'P0006':'''A flat compression pad and a sloping coupon need not first meet across their full faces. Allowing the pad to pitch offers an existing way to accommodate a slope in one direction. Yet the freedom useful during seating remains available during the subsequent displacement ramp unless the operator closes the angular clamp. The practical question is whether that freedom should be retained throughout loading or used only to establish the seated pose.''',
'P0007':'''We examine the timing of one existing friction clamp, keeping the frame, sensors, calibration, pad surface and analysis unchanged. The comparison separates a pitch slope that the pin can follow from a roll slope that it cannot. Flat coupons test whether the additional action is useful when alignment is already simple. Figure 1 makes the lock states and contact poses explicit. This is an operating-sequence comparison using constructed records [1,2]; it does not introduce a new pivot, controller or feedback algorithm.''',
'P0009':'''Mode E starts with the upper pad horizontal and locked before approach to 10 N. Mode F approaches with the clamp open and leaves it open during the ramp. Mode L approaches freely to 10 N, holds that preload, and closes the clamp without lifting the pad. A preload-hold acknowledgement is required before locking; its absence aborts the run. All supplied records contain the acknowledgement. Holding contact makes the locking action act on the seated pose rather than requiring a second approach. Displacement is zeroed after the prescribed approach or lock sequence, followed by the same 0.20 mm increment. The clamp is released only after unloading.''',
'P0010':'''The crosshead carries a transverse pivot pin, perpendicular to the side-view plane. The rigid pad can pitch about that pin but cannot roll about another axis; its flat face presses the coupon against a fixed lower platen. The coupon tops are planar: flat, tilted 1 degree in pitch, or tilted 1 degree in roll. The 10 N preload and 0.20 mm increment are inherited teaching settings, not optimized values.''',
'P0013':'''Drift is the median magnitude of lateral pad displacement during the ramp. Seating time is the median interval from starting the approach to starting the ramp, including the hold and lock in L; it excludes unloading and specimen preparation. Full test duration was not measured. Mode order was not randomized, and raw force samples, pad-angle traces, lock-force measurements and pressure maps are unavailable. No automated correction was made.''',
'P0017':'''On the pitch slope, E, F and L have force CVs of 7.2%, 2.1% and 2.3%, respectively. F already supplies the low-variation comparison that E lacks; L is therefore better understood as retaining that approximate level while restraining drift. Drift is 12, 125 and 19 micrometres, and seating takes 18, 17 and 32 seconds. L trades 15 additional seconds relative to F for 106 micrometres less median drift, rather than improving every metric. The small CV difference between F and L cannot be interpreted as equivalence or significance without uncertainty estimates.\n\nThe other conditions determine how far this choice can be extended. On flat tops, all CVs lie between 1.3% and 1.4%; L takes 31 seconds versus 18 for E, with drift of 16 versus 14 micrometres. Early locking is already adequate on these recorded metrics. Across the pivot direction, the roll condition remains at 6.8–7.0% CV in all modes. L reduces drift relative to F but does not repair that high variation. The single permitted rotation therefore limits the use of preload seating, even when a low drift value is obtained.''',
'P0019':CAPTION,
'P0021':'''The constructed records support using the available pitch freedom for seating and then closing the clamp when the reduction in ramp drift justifies extra operator time. They do not support a universal preference for L: flat tops offer no repeatability gain, and roll slopes remain outside the joint's capability. Repeated mountings measure consistency of endpoint force, not unbiased force, modulus or pressure uniformity. With one coupon per condition and no physical experiments, this demonstration establishes an interpretable comparison and its limits, not validated fixture performance.'''
}

ROUTES='''# Two continuous argument routes, authored before file assembly

## Route A — operation first (selected)
A freely pivoting pad can settle onto a slope, but the same angular freedom remains available during the ramp. The practical choice is when to close the existing clamp. E locks the horizontal pad before approach; F leaves the clamp open; L first seats at 10 N and closes it during an acknowledged hold, without lifting. This sequence uses an existing joint rather than supplying a new alignment mechanism. On a pitch slope, F already gives 2.1% force CV against 7.2% for E. L's 2.3% therefore does not demonstrate a new repeatability capability; its useful distinction is 19 rather than 125 micrometres drift, at 32 rather than 17 seconds seating. Flat and cross-axis conditions delimit that tradeoff.

## Route B — decision from paired costs
None of the three sequences is best on every metric. On a pitch slope, choosing L instead of F buys 106 micrometres less median drift for 15 additional seconds, while their CVs remain close without evidence of equivalence. Choosing L instead of E instead sacrifices some drift and time for a much lower CV. To understand these choices, trace the clamp: E fixes the horizontal pad before contact, F remains open throughout, and L closes only after the pad settles under 10 N. The flat case gives no repeatability reason to pay for this extra step, and the roll slope defeats the single-axis alignment capability in every mode.

## Selection
Route A brings the reader to the physical timing decision before requiring a three-way numeric comparison. Route B's paired F/L cost is retained in the results. The cost is a longer method explanation; the full table still carries all nine rows. Neither route is a prior-art novelty claim. These are alternative argument sketches, not multiple completed outputs selected by repeated sampling.
'''

def figure_spec(inp,stage='first'):
    items=[]
    def add(id,type,**kw):items.append(dict(id=id,type=type,**kw))
    def txt(id,x,y,text,size=23,**kw):add(id,'text',x=x,y=y,text=text,size=size,fill='#233746',**kw)
    def poly(id,points,fill,entity=None,stroke='#3F5665',sw=2):add(id,'polygon',points=points,fill=fill,stroke=stroke,stroke_width=sw,**({'entity':entity} if entity else {}))
    def line(id,p,stroke='#607681',sw=2):add(id,'line',points=p,stroke=stroke,stroke_width=sw)
    def lock(id,x,y,closed):
        add(id+'-body','rect',x=x-10,y=y,w=20,h=16,radius=2,fill='#233746' if closed else '#FFFFFF',stroke='#233746',stroke_width=2,entity='clamp')
        add(id+'-loop','path',commands=[['M',x-7,y],['L',x-7,y-6],['C',x-7,y-17,x+7,y-17,x+7,y-6],['L',x+7,y if closed else y-8]],fill='none',stroke='#233746',stroke_width=2,entity='clamp')
    add('canvas','rect',x=0,y=0,w=1000,h=625,fill='#FFFFFF')
    for n,(c,mode,heading) in enumerate([(167,'E','Lock before approach'),(500,'F','Remain free'),(833,'L','Seat then lock')]):
        txt(mode+'-mode',c,34,mode,27,align='center')
        txt(mode+'-heading',c,64,heading,23,align='center')
        # Fixed lower platen and planar coupon share a contact boundary.
        add(mode+'-platen','rect',x=c-116,y=278,w=232,h=31,fill='#CBD3D7',stroke='#607681',stroke_width=2,entity='platen')
        poly(mode+'-coupon',[[c-95,243],[c+95,219],[c+95,278],[c-95,278]],'#E7C37B','coupon')
        cy=207 if mode=='E' else 219
        # Crosshead and pin, no unprovided clamp internals.
        add(mode+'-crosshead','rect',x=c-39,y=96,w=78,h=31,fill='#DCE3E7',stroke='#607681',stroke_width=2,entity='crosshead')
        add(mode+'-stem','rect',x=c-11,y=127,w=22,h=cy-127,fill='#DCE3E7',stroke='#607681',stroke_width=2,entity='crosshead')
        if mode=='E':points=[[c-95,195],[c+95,195],[c+95,219],[c-95,219]]
        else:points=[[c-95,219],[c+95,195],[c+95,219],[c-95,243]]
        poly(mode+'-pad',points,'#A3CDCD','pad')
        add(mode+'-pin','circle',x=c,y=cy,r=11,fill='#FFFFFF',stroke='#233746',stroke_width=2,entity='pin')
        add(mode+'-pin-axis','circle',x=c,y=cy,r=3,fill='#233746',entity='pin')
        lock(mode+'-lock',c+53,151,mode!='F')
        line(mode+'-lock-leader',[[c+43,162],[c+20,cy-10]])
        # Downward arrow means imposed vertical loading, never lateral sliding.
        line(mode+'-load',[[c,76],[c,89]],'#233746',2.5)
        poly(mode+'-load-tip',[[c,94],[c-5,85],[c+5,85]],'#233746',stroke='#233746',sw=1)
        txt(mode+'-ramp-state',c,346,'Fixed for ramp' if mode!='F' else 'Free during ramp',23,align='center')
    # Labels point to unique material objects in E, apart from lock state markers.
    txt('pad-label',35,166,'Pad',21)
    line('pad-leader',[[76,170],[90,195]])
    txt('coupon-label',167,263,'Coupon',20,align='center',background='#E7C37B')
    txt('platen-label',167,300,'Fixed lower platen',21,align='center',background='#CBD3D7')
    txt('pin-label',25,126,'Pivot pin',20)
    line('pin-leader',[[111,132],[158,200]])
    txt('clamp-label',967,125,'Clamp',20,align='right')
    line('clamp-leader',[[930,131],[900,151]])
    # One arc about F's existing pivot: available pitch, not a second axis or angle trace.
    add('F-pitch-arc','path',commands=[['M',446,188],['C',452,174,463,164,479,161]],fill='none',stroke='#233746',stroke_width=2.5,entity='pad',relation='pin_motion')
    poly('F-pitch-tip',[[479,161],[468,158],[470,168]],'#233746',entity='pad',stroke='#233746',sw=1)
    txt('F-pitch-label',411,153,'Pitch',20)
    # Timing strip is a literal operating sequence, not an extra fixture.
    add('sequence-bg','rect',x=26,y=417,w=948,h=99,radius=10,fill='#EEF4F4')
    txt('sequence-title',44,444,'L sequence',22)
    seq=[(210,'Seat freely','10 N'),(431,'Hold preload','acknowledge'),(650,'Close clamp','do not lift'),(864,'Zero, ramp','0.20 mm')]
    for i,(x,a,b) in enumerate(seq):
        txt('seq-a'+str(i),x,465,a,23,align='center');txt('seq-b'+str(i),x,494,b,20,align='center')
        if i<3:
            line('seq-line'+str(i),[[x+86,461],[x+114,461]],'#607681',2)
            poly('seq-tip'+str(i),[[x+122,461],[x+113,456],[x+113,466]],'#607681',stroke='#607681',sw=1)
    txt('axis-boundary',500,567,'DEMO  |  One pitch axis  |  Roll slope: not corrected',20,align='center')
    entities=[dict(id=k,semantic_role=k,description=v) for k,v in [('pad','one rigid rectangular upper contact pad'),('pin','one transverse single-axis pivot pin'),('clamp','existing friction clamp shown only by a lock marker'),('coupon','one representative pitch-sloped coupon'),('platen','fixed lower platen'),('crosshead','crosshead carrying the pivot')]]
    return dict(schema_version=1,figure_id='lock_timing_demo',mode='new_schematic',demo=True,scientific_message='L uses pitch freedom to seat before locking the same pad for the ramp; roll remains outside that freedom.',evidence_status='CONSTRUCTED_DEMO_NOT_PHYSICAL_TEST',source_refs=[{'file':x,'sha256':sha(inp/x)} for x in ['task.md','implementation.md','results.csv','rough.docx']],forbidden_implications=['No second rotation axis','No pressure map','No measured geometry','No horizontal actuation','No automatic correction','No independent material specimens'],entities=entities,relations=[dict(id='pad_coupon_contact',**{'from':'pad','to':'coupon'},kind='dependency',meaning='The lower pad face presses the coupon; contact pose is illustrative'),dict(id='pin_motion',**{'from':'pin','to':'pad'},kind='motion',meaning='The pad can pitch about this pin when open')],exact_labels=['Lock before approach','Remain free','Seat then lock','Roll slope: not corrected','10 N','0.20 mm'],locked_values={'preload_N':10,'ramp_mm':0.20,'pitch_deg':1,'roll_deg':1,'modes':['E','F','L'],'repeated_views_of_one_fixture':3,'axes':1,'results_csv_sha256':sha(inp/'results.csv')},count_constraints=[],reference_palette='blue_gold_coral',role_map={'pad':{'base':'#A3CDCD'},'coupon':{'base':'#E7C37B'},'support':{'base':'#CBD3D7'}},layout={'archetype':'aligned side views plus L timing strip','reading_order':'E F L then timing and one-axis limit'},depth={'mode':'D0','affects_quantitative_encoding':False},edit_scope={'allowed':['new schematic'],'protected':['one-axis topology','all table values']},output={'width_mm':160,'view_width':1000,'view_height':625,'placement_width_mm':160,'font_profile':'Arial_10pt_main_9pt_auxiliary'},publication={'target_journal':None,'eligibility':'unverified'},items=items,caption=CAPTION,alt_text='Three side views of the same compression fixture show a rigid pad, circular transverse pin, coupon and fixed platen. E is locked horizontal before approach with an illustrative edge contact. An arc beside F denotes pitch about the existing pin. F and L lie parallel to the pitch slope, but only F remains free in the ramp. L seats at 10 N, holds and acknowledges preload, locks without lifting, then zeros and ramps 0.20 mm. A roll slope cannot be corrected.',object_mapping={'approach':'pad lower face to coupon top; same pin and clamp in all three views','lock':'symbol attached by leader to pivot; construction deliberately unspecified','scope':'representative pitch condition; full nine-row table in paper'},data_source='inputs/results.csv',data_sha256=sha(inp/'results.csv'))

def main():
    a=argparse.ArgumentParser();a.add_argument('--input',type=Path,required=True);a.add_argument('--out',type=Path,required=True);a.add_argument('--papercraft',type=Path,required=True);a.add_argument('--figurecraft',type=Path,required=True);a.add_argument('--font',type=Path,required=True);a.add_argument('--pdftoppm',type=Path,required=True);a.add_argument('--stage',choices=['after-review'],default='after-review');a.add_argument('--resume-incomplete',action='store_true');args=a.parse_args()
    if args.out.exists() and not args.resume_incomplete:raise ValueError('Output must be new')
    if (args.out/'build-summary.json').exists():raise ValueError('Completed outputs are immutable')
    args.out.mkdir(parents=True,exist_ok=True)
    start=time.time();commands=json.loads((args.out/'commands.json').read_text()) if args.resume_incomplete else []
    def run(cmd):
        # Resume only the interrupted assembly; never redraw or reauthor completed stages.
        if args.resume_incomplete and '--out' in cmd and Path(cmd[cmd.index('--out')+1]).exists():return
        t=time.time();r=subprocess.run([str(x) for x in cmd],capture_output=True,text=True,encoding='utf-8',errors='replace')
        commands.append({'utc':datetime.fromtimestamp(t,timezone.utc).isoformat(),'command':[str(x) for x in cmd],'elapsed_s':round(time.time()-t,3),'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
        write(args.out/'commands.json',commands)
        if r.returncode and str(cmd[1]).endswith('audit_preservation.py'):
            report=json.loads(Path(cmd[cmd.index('--out')+1]).read_text(encoding='utf-8'))
            failed=[k for k,v in report['checks'].items() if v['status']=='FAIL']
            if failed==['drawings'] and report['counts']['source']['drawings']==0 and report['counts']['candidate']['drawings']==1:
                write(args.out/(Path(cmd[3]).stem+'-authorized-drawing-delta.json'),{'audit_status':'FAIL retained unchanged','authorized_difference':'Original text placeholder becomes exactly one drawing with PNG and SVG alternatives','other_protected_checks':'PASS','disposition':'Expected authorized insertion; not an unqualified preservation PASS'})
                return
        if r.returncode:raise RuntimeError(r.stdout+'\n'+r.stderr)
    inp=args.out/'inputs';inp.mkdir(exist_ok=True)
    for f in ['task.md','rough.docx','implementation.md','results.csv']:shutil.copy2(args.input/f,inp/f)
    write(args.out/'argument-routes.md',ROUTES)
    spec=figure_spec(inp,args.stage)
    write(args.out/'figure_spec.json',spec)
    write(args.out/'caption.txt',CAPTION);write(args.out/'alt_text.txt',spec['alt_text'])
    run([sys.executable,args.figurecraft/'scripts/render_figure.py',args.out/'figure_spec.json','--out',args.out/'figure','--font',args.font,'--pdftoppm',args.pdftoppm,'--qa-views','--placement-width-mm','160'])
    run([sys.executable,args.papercraft/'scripts/review_docx.py','inspect',inp/'rough.docx','--out',args.out/'inspect.json'])
    inventory=json.loads((args.out/'inspect.json').read_text(encoding='utf-8'));lookup={p['id']:p for p in inventory['paragraphs']}
    edits=[]
    for pid,text in DRAFT.items():edits.append(dict(paragraph_id=pid,operation='replace_paragraph',before=lookup[pid]['text'],after=text,reason='Connect the clamp timing to the matched tradeoff and its directional boundary.',source=['implementation.md','results.csv']))
    # Edit ordinary neighbors only; preserve mathematical object and italic variable runs.
    edits.extend([
        dict(paragraph_id='P0011',operation='replace_span',before=' across the eight reseatings: ',after=' of endpoint force after the 0.20 mm ramp across eight reseatings: ',reason='Specify force sample endpoint next to the native equation.',source=['implementation.md metric definition']),
        dict(paragraph_id='P0012',operation='replace_span',before='Each condition uses eight remove-and-reseat cycles of one coupon, not eight independent specimens. ',after='Each row summarizes eight remove-and-reseat cycles of one coupon in that condition, not eight independent specimens. Geometry and synthetic inputs are identical across modes. ',reason='State the replication unit without altering the historical yellow run.',source=['implementation.md sampling']),
        dict(paragraph_id='P0015',operation='replace_span',before='. E mode has small drift in every condition. F has low variation for pitch but more drift. L uses more seating time. The roll condition remains variable.',after='. The pitch condition tests whether locking after seating can retain low force variation while limiting ramp drift. Flat and roll conditions test whether that choice is broadly useful.',reason='Keep native REF field and introduce the three-way comparison.',source=['results.csv']),
    ])
    plan={'source_sha256':sha(inp/'rough.docx'),'edits':edits};write(args.out/'authored-edits.json',plan)
    run([sys.executable,args.papercraft/'scripts/apply_authored_edits.py','--source',inp/'rough.docx','--edits',args.out/'authored-edits.json','--skill',args.papercraft,'--out',args.out/'text-stage'])
    from PIL import Image
    Image.new('RGB',(1600,1000),'white').save(args.out/'blank-binding.png')
    blank_svg=b'<svg xmlns="http://www.w3.org/2000/svg" width="160mm" height="100mm" viewBox="0 0 1600 1000"><rect width="1600" height="1000" fill="white"/></svg>'
    # No drawing exists in the input. Insert the first drawing through the format-aware path,
    # then run the skill's media replacement for synchronized PNG and SVG representations.
    for label in ['clean','review']:
        if args.resume_incomplete and (args.out/f'{label}.docx').exists():continue
        source=args.out/'text-stage'/f'{label}.docx'; doc=Document(source)
        placeholder=next(p for p in doc.paragraphs if p.text=='[Figure 1 placeholder]')
        original_placeholder_xml=ET.tostring(placeholder._p).decode()
        for r in placeholder.runs:
            for t in r._r.findall(qn('w:t')):t.text=''
        pic=placeholder.add_run().add_picture(str(args.out/'blank-binding.png'),width=Mm(160),height=Mm(100))
        placeholder.paragraph_format.keep_with_next=True
        placeholder.paragraph_format.space_before=Pt(5);placeholder.paragraph_format.space_after=Pt(4)
        pic._inline.docPr.set('descr',spec['alt_text'])
        # Move complete figure and caption nodes to the end of Method, before Results.
        caption=next(p for p in doc.paragraphs if p.text==CAPTION)
        method_end=next(p for p in doc.paragraphs if p.text==DRAFT['P0013'])
        method_end._p.addnext(placeholder._p);placeholder._p.addnext(caption._p)
        caption.paragraph_format.keep_with_next=False;caption.paragraph_format.space_after=Pt(9)
        for r in caption.runs:r.font.size=Pt(9)
        # Existing source styles are retained, with page geometry wide enough for 160 mm.
        for sec in doc.sections:
            sec.page_width=Mm(210);sec.page_height=Mm(297);sec.left_margin=Mm(25);sec.right_margin=Mm(25);sec.top_margin=Mm(20);sec.bottom_margin=Mm(20)
        normal=doc.styles['Normal'];normal.font.name='Arial';normal.font.size=Pt(10.5)
        normal.paragraph_format.line_spacing=1.05;normal.paragraph_format.space_after=Pt(6)
        for p in doc.paragraphs:
            if p.style.name.startswith('Heading'):
                p.paragraph_format.keep_with_next=True
                p.style.font.color.rgb=RGBColor(0,0,0)
            if p.text==DRAFT['P0013'] or p.text==DRAFT['P0017'].split('\n\n')[0]:
                p.paragraph_format.keep_together=True
        title=next(p for p in doc.paragraphs if p.text==DRAFT['P0002']);title.style='Title';title.paragraph_format.keep_with_next=True
        title.style.font.name='Arial';title.style.font.size=Pt(20);title.style.font.color.rgb=RGBColor(0,0,0)
        table_caption=next(p for p in doc.paragraphs if p.text.startswith('Table 1.'));table_caption.paragraph_format.keep_with_next=True
        bound=args.out/f'{label}-bound.docx';doc.save(bound)
        # Add SVG alternate to the newly created drawing; preserve every other ZIP part.
        with zipfile.ZipFile(bound) as z:parts={n:z.read(n) for n in z.namelist()}
        wroot=ET.fromstring(parts['word/document.xml']);rr=ET.fromstring(parts['word/_rels/document.xml.rels']);ct=ET.fromstring(parts['[Content_Types].xml'])
        ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
        blip=wroot.find('.//a:blip',ns);extlist=ET.SubElement(blip,'{'+ns['a']+'}extLst');ext=ET.SubElement(extlist,'{'+ns['a']+'}ext',uri='{96DAC541-7B7A-43D3-8B79-37D633B846F1}')
        ET.SubElement(ext,'{http://schemas.microsoft.com/office/drawing/2016/SVG/main}svgBlip',{'{'+ns['r']+'}embed':'rIdTrialSVG'})
        ET.SubElement(rr,'{http://schemas.openxmlformats.org/package/2006/relationships}Relationship',Id='rIdTrialSVG',Type=ns['r']+'/image',Target='media/trial.svg')
        ET.SubElement(ct,'{http://schemas.openxmlformats.org/package/2006/content-types}Default',Extension='svg',ContentType='image/svg+xml')
        parts['word/document.xml']=ET.tostring(wroot,xml_declaration=True,encoding='UTF-8',standalone=True);parts['word/_rels/document.xml.rels']=ET.tostring(rr,xml_declaration=True,encoding='UTF-8',standalone=True);parts['[Content_Types].xml']=ET.tostring(ct,xml_declaration=True,encoding='UTF-8',standalone=True);parts['word/media/trial.svg']=blank_svg
        with zipfile.ZipFile(bound,'w',zipfile.ZIP_DEFLATED) as z:
            for n,b in parts.items():z.writestr(n,b)
        sys.path.insert(0,str(args.papercraft/'scripts'));import audit_figure_integration as afi
        inv=afi.inspect(bound)
        write(args.out/f'{label}-figure-inventory.json',inv)
        # Actual names are obtained from DrawingML / relationships, not presumed filenames.
        drawing=inv['drawings'][0]
        reps=[]
        for rep in drawing['representations']:
            asset=args.out/'figure'/('figure.svg' if rep['kind']=='svg' else 'figure.png')
            reps.append(dict(kind=rep['kind'],part=rep['part'],old_media_sha256=rep['sha256'],source_asset=asset.relative_to(args.out).as_posix(),source_asset_sha256=sha(asset)))
        manifest={'source_sha256':sha(bound),'replacements':[{'drawing_index':1,'representations':reps}]};write(args.out/f'{label}-images.json',manifest)
        run([sys.executable,args.papercraft/'scripts/apply_figure_edits.py',bound,args.out/f'{label}-images.json',args.out/f'{label}.docx','--receipt',args.out/f'{label}-images-receipt.json'])
        run([sys.executable,args.papercraft/'scripts/audit_preservation.py',inp/'rough.docx',args.out/f'{label}.docx','--out',args.out/f'{label}-preservation.json'])
        write(args.out/f'{label}-format-receipt.json',{'original_placeholder_xml':original_placeholder_xml,'new_drawing_mm':[160,100],'movement':'Complete figure paragraph and caption moved after final Method paragraph and before Results','table':'Untouched XML; nine rows retained','protected_content':'Preservation audit plus content checks','visual_review':'NOT_RUN_BY_CHILD_PARENT_RENDER_REQUIRED'})
    write(args.out/'build-summary.json',{'stage':args.stage,'start_utc':datetime.fromtimestamp(start,timezone.utc).isoformat(),'finish_utc':datetime.now(timezone.utc).isoformat(),'build_elapsed_s':round(time.time()-start,3),'hashes':{p.name:sha(p) for p in args.out.glob('*.docx')},'source_script_sha256':sha(__file__),'word_render':'Delegated to parent; not run by this child','generated_with':'PaperCraft apply_authored_edits + format-aware insertion + apply_figure_edits; FigureCraft render_figure','independent_review':False,'human_approval':False})
    print(args.out)

if __name__=='__main__':main()
