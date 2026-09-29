#!/usr/bin/env python3
"""Explicit orthographic geometry and visibility repair of the sealed trial.

Keep this file beside drawing_backend.py. Dependencies: reportlab, numpy,
Pillow, pypdf, Arial font files and Poppler pdftoppm, passed as arguments.
The output directory must not exist. No old artifact is rewritten.
"""
from __future__ import annotations
import argparse, hashlib, json, math, subprocess, sys
from pathlib import Path
import numpy as np
from pypdf import PdfReader
from PIL import Image
from drawing_backend import Figure, polygon, ellipse_path, export_qa, MM, W, H, sha

RADII=(48.0,45.4,36.4)
A0,A1=151.0,35.0
WIDTH=14.0
BETA=15.0
VIEW=np.array([.65,.65*math.tan(math.radians(BETA)),1.0]);VIEW/=np.linalg.norm(VIEW)
RIGHT=np.array([VIEW[2],0.,-VIEW[0]]);RIGHT/=np.linalg.norm(RIGHT)
UP=np.cross(VIEW,RIGHT)
ORIGIN=np.array([62.,77.])
LIGHT=np.array([.25,.65,1.]);LIGHT/=np.linalg.norm(LIGHT)
EPS=1e-7

def xyz(r,a,z):
    a=math.radians(a);return np.array([r*math.cos(a),r*math.sin(a),z])

def project(p):
    p=np.asarray(p);return np.array([ORIGIN[0]+np.dot(p,RIGHT),ORIGIN[1]-np.dot(p,UP)])

def depth(p):return float(np.dot(p,VIEW))

def poly(name,points,normal,role,color,entity='strip'):
    return dict(name=name,p=np.asarray(points,dtype=float),n=np.asarray(normal,dtype=float),role=role,color=color,entity=entity)

def shade(hex_color,factor):
    vals=[int(hex_color[i:i+2],16) for i in [1,3,5]]
    return '#'+''.join(f'{min(255,max(0,round(v*factor))):02x}' for v in vals)

def scene():
    # The analytical grazing angle is explicitly in the tessellation, so no
    # patch straddles a visibility transition.
    tangent=BETA+90.0
    angles=sorted(set(np.linspace(A1,A0,241).tolist()+[tangent]))
    faces=[];edges=[];intervals=[]
    ro,rm,ri=RADII;z0,z1=-WIDTH/2,WIDTH/2
    for material,hi,lo,color in [('outer',ro,rm,'#b47840'),('support',rm,ri,'#477f8b')]:
        for i,(a,b) in enumerate(zip(angles[:-1],angles[1:])):
            faces.append(poly(f'front-{material}-{i}',[xyz(hi,a,z1),xyz(hi,b,z1),xyz(lo,b,z1),xyz(lo,a,z1)],[0,0,1],material,color))
            faces.append(poly(f'back-{material}-{i}',[xyz(hi,a,z0),xyz(lo,a,z0),xyz(lo,b,z0),xyz(hi,b,z0)],[0,0,-1],material,color))
    for side,r,sign,color in [('outer-surface',ro,1,'#d8ab6b'),('inner-surface',ri,-1,'#386c76')]:
        for i,(a,b) in enumerate(zip(angles[:-1],angles[1:])):
            mid=math.radians((a+b)/2);normal=np.array([sign*math.cos(mid),sign*math.sin(mid),0])
            col=shade(color,.92+.10*max(0,float(np.dot(normal,LIGHT))))
            faces.append(poly(f'{side}-{i}',[xyz(r,a,z0),xyz(r,b,z0),xyz(r,b,z1),xyz(r,a,z1)],normal,side,col))
    for end,a,sign in [('free',A1,1),('clamped',A0,-1)]:
        rad=math.radians(a);normal=sign*np.array([math.sin(rad),-math.cos(rad),0])
        for material,hi,lo,color in [('outer',ro,rm,'#dfb372'),('support',rm,ri,'#aacbd0')]:
            faces.append(poly(f'{end}-end-{material}',[xyz(hi,a,z1),xyz(hi,a,z0),xyz(lo,a,z0),xyz(lo,a,z1)],normal,f'end-{material}',color))
    # True three-dimensional opaque clamp, intersecting the first portion of
    # the strip. Clamp and strip enter the SAME visibility ordering.
    ar=math.radians(A0);n=np.array([math.cos(ar),math.sin(ar),0]);t=np.array([math.sin(ar),-math.cos(ar),0]);zz=np.array([0,0,1.])
    cp=xyz((ro+ri)/2,A0,0)
    basis=[n,t,zz];half=[8.,9.,WIDTH/2+.8]
    def cq(u,v,z):return cp+u*n+v*t+z*zz
    for axis in range(3):
        other=[j for j in range(3) if j!=axis]
        for sign in [-1,1]:
            points=[]
            for p,q in [(-1,-1),(1,-1),(1,1),(-1,1)]:
                vals=[0.,0.,0.];vals[axis]=sign*half[axis];vals[other[0]]=p*half[other[0]];vals[other[1]]=q*half[other[1]]
                points.append(cq(*vals))
            normal=sign*basis[axis]
            color=shade('#8d9aa2',.88+.18*max(0,float(np.dot(normal,LIGHT))))
            faces.append(poly(f'clamp-{axis}-{sign}',points,normal,'clamp',color,'clamp'))
    # Physical edges only: material interface, exposed perimeter and the box
    # edges. Mesh seams never receive a dark stroke.
    for z in [z0,z1]:
        for r,tag,color in [(ro,'outer','#89592e'),(rm,'interface','#6d634c'),(ri,'inner','#315d65')]:
            for a,b in zip(angles[:-1],angles[1:]):
                edges.append((f'edge-{tag}',xyz(r,a,z),xyz(r,b,z),color))
    for a in [A0,A1,tangent]:
        for r,tag,color in [(ro,'outer','#89592e'),(rm,'interface','#6d634c'),(ri,'inner','#315d65')]:
            # The interface at the analytical tangent is INTERNAL; do not
            # invent a seam there. Outer/inner grazing edges are silhouettes.
            if a==tangent and r==rm:continue
            edges.append((f'long-{tag}',xyz(r,a,z0),xyz(r,a,z1),color))
    for a in [A0,A1]:
        for z in [z0,z1]:edges.append(('end-radial',xyz(ro,a,z),xyz(ri,a,z),'#465d61'))
    for axis in range(3):
        other=[j for j in range(3) if j!=axis]
        for p in [-1,1]:
            for q in [-1,1]:
                vals=[0.,0.,0.];vals[other[0]]=p*half[other[0]];vals[other[1]]=q*half[other[1]]
                vals[axis]=-half[axis];pa=cq(*vals);vals[axis]=half[axis];pb=cq(*vals)
                edges.append(('clamp-edge',pa,pb,'#626e75'))
    anchor_clamp=cq(-5,-9,half[2])
    visible=[f for f in faces if float(np.dot(f['n'],VIEW))>EPS]
    return faces,visible,edges,anchor_clamp,angles

def plane(points):
    for i in range(1,len(points)-1):
        n=np.cross(points[i]-points[0],points[i+1]-points[0]);l=np.linalg.norm(n)
        if l>EPS:
            n/=l;return n,float(np.dot(n,points[0]))
    raise ValueError('Degenerate polygon')

def split(f,n,d):
    pts=f['p'];dist=pts@n-d
    if np.all(np.abs(dist)<=EPS):return 'coplanar',f,None
    if np.all(dist>=-EPS):return 'front',f,None
    if np.all(dist<=EPS):return 'back',f,None
    front=[];back=[]
    for i,a in enumerate(pts):
        j=(i+1)%len(pts);b=pts[j];da,db=dist[i],dist[j]
        if da>=-EPS:front.append(a)
        if da<=EPS:back.append(a)
        if (da>EPS and db<-EPS) or (da<-EPS and db>EPS):
            p=a+(b-a)*da/(da-db);front.append(p);back.append(p)
    fa=dict(f,p=np.asarray(front),name=f['name']+'-F');fb=dict(f,p=np.asarray(back),name=f['name']+'-B')
    return 'split',fa,fb

class BSP:
    """Split polygons against planes; orthographic far-to-near traversal.

    Unlike sorting centroids, plane splitting remains valid where surfaces
    intersect (notably at the clamp). Mesh geometry is piecewise planar.
    """
    def __init__(self,f):
        self.n,self.d=plane(f['p']);self.same=[f];self.front=None;self.back=None
    def insert(self,f):
        mode,a,b=split(f,self.n,self.d)
        if mode=='coplanar':self.same.append(a);return
        if mode in ['front','split']:
            if self.front:self.front.insert(a)
            else:self.front=BSP(a)
        if mode in ['back','split']:
            item=b if mode=='split' else a
            if self.back:self.back.insert(item)
            else:self.back=BSP(item)
    def traverse(self):
        far,near=(self.back,self.front) if np.dot(self.n,VIEW)>=0 else (self.front,self.back)
        if far:yield from far.traverse()
        yield from self.same
        if near:yield from near.traverse()

def triangles(faces):
    result=[]
    for f in faces:
        p=f['p']
        for j in range(1,len(p)-1):result.append(np.array([p[0],p[j],p[j+1]]))
    return np.asarray(result)

class RayVisibility:
    def __init__(self,all_faces):
        tri=triangles(all_faces)
        self.xy=np.stack([ORIGIN[0]+tri@RIGHT,ORIGIN[1]-tri@UP],axis=-1)
        self.z=tri@VIEW
        a,b,c=self.xy[:,0],self.xy[:,1],self.xy[:,2]
        self.den=(b[:,1]-c[:,1])*(a[:,0]-c[:,0])+(c[:,0]-b[:,0])*(a[:,1]-c[:,1])
        self.ok=np.abs(self.den)>1e-10
    def front_depth(self,xy,painter_order=False):
        a,b,c=self.xy[:,0],self.xy[:,1],self.xy[:,2]
        x,y=xy
        den=np.where(self.ok,self.den,1.)
        u=((b[:,1]-c[:,1])*(x-c[:,0])+(c[:,0]-b[:,0])*(y-c[:,1]))/den
        v=((c[:,1]-a[:,1])*(x-c[:,0])+(a[:,0]-c[:,0])*(y-c[:,1]))/den
        w=1-u-v
        inside=self.ok&(u>=-1e-8)&(v>=-1e-8)&(w>=-1e-8)
        ds=u*self.z[:,0]+v*self.z[:,1]+w*self.z[:,2]
        if not np.any(inside):return -float('inf')
        return float(ds[np.flatnonzero(inside)[-1]]) if painter_order else float(np.max(ds[inside]))
    def visible(self,p,tol=.004):return depth(p)>=self.front_depth(project(p))-tol

def painter_sample_check(ordered,all_faces):
    """Independent ray depth vs last painted face at reproducible sample points."""
    all_ray=RayVisibility(all_faces);paint_ray=RayVisibility(ordered);bad=[];checked=0
    rng=np.random.default_rng(20260929)
    for face in ordered:
        pts=face['p']
        for _ in range(2):
            w=rng.uniform(.2,1,len(pts));w/=sum(w);sample=w@pts;xy=project(sample)
            expected=all_ray.front_depth(xy)
            last=paint_ray.front_depth(xy,painter_order=True)
            checked+=1
            if last is None or abs(last-expected)>.01:bad.append({'xy':xy.tolist(),'front':expected,'painted':last})
    return {'sample_count':checked,'mismatches':len(bad),'examples':bad[:8],
            'scope':'Independent maximum ray-depth at samples vs final BSP painter; not exhaustive pixel proof.'}

def draw(fig):
    all_faces,visible,edges,clamp_anchor,angles=scene()
    tree=BSP(visible[0])
    for f in visible[1:]:tree.insert(f)
    ordered=list(tree.traverse())
    # The full near annulus is coplanar. Its same-material mesh patches form
    # contiguous groups in the BSP order, so merge each group into one fill
    # without moving it past any other surface. This removes rendering seams
    # while retaining the exact polygon boundary used by the visibility test.
    merge_groups={}
    for material in ['outer','support']:
        ids=[i for i,f in enumerate(ordered) if f['name'].startswith('front-'+material+'-')]
        assert ids==list(range(ids[0],ids[-1]+1)), 'Cannot merge noncontiguous painter group'
        merge_groups[material]=ids
    merged=set()
    for i,f in enumerate(ordered):
        material=next((m for m in merge_groups if i in merge_groups[m]),None)
        if material:
            if material in merged:continue
            hi,lo=(RADII[0],RADII[1]) if material=='outer' else (RADII[1],RADII[2])
            verts=[xyz(hi,a,WIDTH/2) for a in angles]+[xyz(lo,a,WIDTH/2) for a in reversed(angles)]
            fig.path('merged-front-'+material,polygon([project(p).tolist() for p in verts]),fill=f['color'],entity='strip',role=material)
            merged.add(material);continue
        pts=[project(p).tolist() for p in f['p']]
        # Thin same-colour seam stroke suppresses antialiasing cracks, not a
        # drawn structural seam. It is 0.03 mm, below one 300-dpi pixel.
        fig.path(f'surface-{i:04d}-{f["name"]}',polygon(pts),fill=f['color'],stroke=f['color'],sw=.03,entity=f['entity'],role=f['role'])
    ray=RayVisibility(all_faces);edge_stats={'segments':0,'visible':0,'hidden':0}
    for i,(tag,a,b,col) in enumerate(edges):
        count=max(1,math.ceil(np.linalg.norm(project(b)-project(a))/.16))
        for k in range(count):
            p=a+(b-a)*k/count;q=a+(b-a)*(k+1)/count;m=(p+q)/2
            edge_stats['segments']+=1
            if ray.visible(m):
                fig.path(f'visible-edge-{i}-{k}',[('M',*project(p)),('L',*project(q))],stroke=col,sw=.18,entity='clamp' if tag=='clamp-edge' else 'strip',role='visible-physical-edge')
                edge_stats['visible']+=1
            else:edge_stats['hidden']+=1
    # A pure scale + translation of the SAME orthographic terminal face.
    ro,rm,ri=RADII
    def terminal(hi,lo):return [xyz(hi,A1,WIDTH/2),xyz(hi,A1,-WIDTH/2),xyz(lo,A1,-WIDTH/2),xyz(lo,A1,WIDTH/2)]
    end=np.asarray([project(p) for p in terminal(ro,ri)]);center=np.mean(end,axis=0)
    target=np.array([135.,51.]);scale=1.85
    for tag,hi,lo,color,stroke in [('support',rm,ri,'#aacbd0','#315d65'),('outer',ro,rm,'#dfb372','#89592e')]:
        pts=[(target+scale*(project(p)-center)).tolist() for p in terminal(hi,lo)]
        fig.path(f'detail-{tag}-same-free-end',polygon(pts),fill=color,stroke=stroke,sw=.22,entity='strip',role=f'detail-{tag}')
    detail=target+scale*(end-center);left=detail[np.argmin(detail[:,0])]
    fig.path('detail-selection',ellipse_path(*center,12.5,9.),stroke='#8b969c',sw=.16,role='detail-selection',dash=[1.15,1.2])
    fig.path('detail-identity-link',[('M',center[0]+12.5,center[1]),('L',left[0]-.8,left[1])],stroke='#8b969c',sw=.16,role='same-object-detail',dash=[1.15,1.2])
    outer=project(xyz(ro,70.,0.))
    fig.path('leader-outer',[('M',73.,24.),('L',*outer)],stroke='#59666e',sw=.18,role='label-leader')
    fig.text('label-outer-layer','Outer layer',73.,21.6)
    support=project(xyz((rm+ri)/2,90.,WIDTH/2))
    fig.path('leader-support',[('M',support[0],57.7),('L',*support)],stroke='#59666e',sw=.18,role='label-leader')
    fig.text('label-support-layer','Support layer',support[0],63.0)
    cp=project(clamp_anchor)
    fig.path('leader-clamp',[('M',cp[0],70.9),('L',*cp)],stroke='#59666e',sw=.18,role='label-leader')
    fig.text('label-clamp','Clamp',cp[0],76.0)
    fig.text('label-detail','Same free end',135,26.0,10.5)
    fig.text('label-detail-enlarged','(enlarged)',135,31.0,9,fill='#59666e')
    fig.text('label-scale','Not to scale',155,81.0,8.5,anchor='end',fill='#59666e')
    checks=painter_sample_check(ordered,all_faces)
    return {
        'camera_toward_viewer':VIEW.tolist(),'screen_right':RIGHT.tolist(),'screen_up':UP.tolist(),
        'orthogonality_matrix':np.array([RIGHT,UP,VIEW]).dot(np.array([RIGHT,UP,VIEW]).T).tolist(),
        'radii':list(RADII),'arc_degrees':[A1,A0],'width_design_units':WIDTH,'not_measured':True,
        'visible_outer_interval_degrees':[A1,BETA+90],'visible_inner_interval_degrees':[BETA+90,A0],
        'visible_end_planes_degrees':[A1],'front_z':WIDTH/2,'culled_back_z':-WIDTH/2,
        'all_surface_patches':len(all_faces),'front_facing_patches':len(visible),'bsp_painted_fragments':len(ordered),
        'render_only_coplanar_merge':{m:{'first_index':ids[0],'last_index':ids[-1],'patches':len(ids)} for m,ids in merge_groups.items()},
        'edge_visibility':edge_stats,'painter_ray_check':checks,'detail_scale':scale,'detail_translation_mm':(target-scale*center).tolist(),
        'main_free_end_center_mm':center.tolist(),'detail_center_mm':target.tolist(),
        'maximum_arc_chord_sagitta_mm':RADII[0]*(1-math.cos(math.radians(max(np.diff(angles)))/2)),
        'normal_culling':'n dot camera_toward_viewer > 0; curved intervals split at 105 degrees',
        'occlusion':'BSP polygon splitting and far-to-near traversal; physical-edge rays intersect all surfaces including the opaque clamp',
        'depth_note':'Explicit three-dimensional geometry projected orthographically into editable vector polygons; not experimental geometry.'}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',required=True,type=Path);ap.add_argument('--font',required=True,type=Path)
    ap.add_argument('--bold-font',required=True,type=Path);ap.add_argument('--pdftoppm',required=True,type=Path)
    args=ap.parse_args()
    if args.out.exists():ap.error(f'Refusing overwrite: {args.out}')
    for p in [args.font,args.bold_font,args.pdftoppm]:
        if not p.is_file():ap.error(f'Missing {p}')
    args.out.mkdir(parents=True)
    fig=Figure(args.out,args.font,args.bold_font);record=draw(fig);fig.finish()
    command=[str(args.pdftoppm),'-png','-r','300','-singlefile',str(args.out/'figure.pdf'),str(args.out/'figure')]
    result=subprocess.run(command,capture_output=True,text=True)
    if result.returncode:raise RuntimeError(result.stderr)
    export_qa(args.out)
    runs=[]
    def visitor(text,cm,tm,font,size):
        if text.strip():runs.append({'text':text.strip(),'size_pt':size})
    reader=PdfReader(args.out/'figure.pdf');reader.pages[0].extract_text(visitor_text=visitor)
    record.update({'command':sys.argv,'render_command':command,'render_exit':result.returncode,
        'actual_pdf_text':runs,'minimum_font_pt':min(v['size_pt'] for v in runs),
        'pdf_mm':[float(reader.pages[0].mediabox.width)/MM,float(reader.pages[0].mediabox.height)/MM],
        'png_px':list(Image.open(args.out/'figure.png').size),
        'source_hashes':{p.name:sha(p) for p in [Path(__file__),Path(__file__).with_name('drawing_backend.py')]},
        'artifacts':{p.name:sha(p) for p in args.out.iterdir() if p.is_file()},
        'stage':'POST_TRIAL_DEVELOPMENT_REPAIR; not independent first-pass validation',
        'visual_review':'REVIEW_REQUIRED','author_acceptance':'NOT_RUN'})
    (args.out/'geometry-and-checks.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'out':str(args.out),'visibility_check':record.get('raster_ray_check',record.get('painter_ray_check')),'minimum_font_pt':record['minimum_font_pt']}))

if __name__=='__main__':main()
