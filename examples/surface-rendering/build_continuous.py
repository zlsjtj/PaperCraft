"""Existing exact strip geometry; continuous surfaces and same-object local segment."""
from pathlib import Path
import base64,hashlib,io,json,sys
import numpy as np
from reportlab.lib.utils import ImageReader
import geometry_scene as scene
from mesh_surface import render

def insert(fig,im,x,y,w,h,ident):
    b=io.BytesIO();im.save(b,format='PNG');data=b.getvalue()
    fig.svg.append(f'<image id="{ident}" x="{x}" y="{y}" width="{w}" height="{h}" href="data:image/png;base64,{base64.b64encode(data).decode()}" data-entity="strip" data-editability="source-rebuildable-surface"/>')
    fig.c.drawImage(ImageReader(im),x*scene.MM,(scene.H-y-h)*scene.MM,width=w*scene.MM,height=h*scene.MM,mask='auto')

original=scene.draw
def draw(fig):
    faces,_,_,_,_=scene.scene()
    for f in faces:
        role=f['role']
        if role in ['outer-surface','inner-surface']:
            nn=f['p'].copy();nn[:,2]=0;nn/=np.linalg.norm(nn,axis=1)[:,None]
            f['vertex_normals']=nn*(-1 if role=='inner-surface' else 1)
            f['base_color']='#d8ab6b' if role=='outer-surface' else '#386c76'
        elif role=='clamp':f['base_color']='#8d9aa2'
    im,mask,lo,hi,record=render(faces,scene.RIGHT,scene.UP,scene.VIEW)
    im.save(fig.out/'strip-surface.png');mask.save(fig.out/'strip-materials.png')
    insert(fig,im,*(scene.ORIGIN+lo),*(hi-lo),'main-geometry')
    # Keep the original exact repeated terminal face. The tested segment inset
    # gave more volume but implied a newly cut specimen in independent review.
    ray=scene.RayVisibility(faces)
    errors=[abs(ray.front_depth(scene.ORIGIN+np.array(s['xy']))-s['depth']) for s in record['visibility_samples']]
    raster_check={'samples':len(errors),'max_depth_error':max(errors,default=0),'mismatches':sum(e>1e-6 for e in errors),'scope':'Actual supersampled z-buffer versus independent face-ray query at 400 fixed occupied pixels; not exhaustive.'}
    assert raster_check['mismatches']==0,raster_check
    oldpath=fig.path
    def path(ident,commands,*args,**kwargs):
        if ident.startswith(('surface-','merged-front-')):return
        if ident.startswith('visible-edge-'):
            # Keep scientific boundaries as vector strokes, lighter than labels.
            kwargs['sw']=.12
        return oldpath(ident,commands,*args,**kwargs)
    fig.path=path
    result=original(fig)
    result['reference_bsp_ray_check']=result.pop('painter_ray_check')
    result['surface_backend']=record;result['raster_ray_check']=raster_check
    result['detail_kind']='Original vector terminal face repeated at 1.85x; no additional segment'
    result['occlusion']='Main surfaces: per-pixel maximum depth; vector edge visibility: face-ray queries. BSP metadata describes the retained reference renderer only.'
    result['depth_note']='Same explicit geometry and camera as baseline; continuous vertex normals for curved surface shading. Illustrative geometry, not experimental.'
    result['editability']='Hybrid: editable vector labels/relationships/edges and source-rebuildable material raster layers. Not all-vector.'
    return result

scene.draw=draw
if __name__=='__main__':
    scene.main()
    out=Path(sys.argv[sys.argv.index('--out')+1]);p=out/'geometry-and-checks.json'
    d=json.loads(p.read_text(encoding='utf8'))
    d['source_hashes']={n:hashlib.sha256((Path(__file__).parent/n).read_bytes()).hexdigest() for n in ['build_continuous.py','mesh_surface.py','geometry_scene.py','drawing_backend.py']}
    p.write_text(json.dumps(d,indent=2),encoding='utf8')
