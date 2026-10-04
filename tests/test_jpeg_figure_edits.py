"""Same-codec JPEG source recovery must not rewrite any Word XML or image bytes."""
from pathlib import Path
import io,json,sys,tempfile,unittest,zipfile
from docx import Document
from docx.shared import Mm
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import apply_figure_edits as F

def jpeg(size,color,orientation=None):
    im=Image.new('RGB',size,color);buf=io.BytesIO();kwargs={}
    if orientation is not None:
        ex=Image.Exif();ex[274]=orientation;kwargs['exif']=ex
    im.save(buf,format='JPEG',**kwargs);return buf.getvalue()

class JpegReplacement(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.p=Path(self.tmp.name)
        self.original=jpeg((200,100),'red');self.better=jpeg((400,200),'blue')
        d=Document();d.add_paragraph('Retain all source objects.').add_run('x').italic=True
        d.add_picture(io.BytesIO(self.original),width=Mm(90));d.save(self.p/'input.docx')
        with zipfile.ZipFile(self.p/'input.docx') as z:self.parts={n:z.read(n) for n in z.namelist()}
        self.part=next(n for n in self.parts if n.startswith('word/media/'))
        self.spec={'source_sha256':F.sha((self.p/'input.docx').read_bytes()),'replacements':[{'drawing_index':1,'representations':[{'kind':'primary','part':self.part,'old_media_sha256':F.sha(self.original),'source_asset':'better.jpg','source_asset_sha256':F.sha(self.better)}]}]}
    def tearDown(self):self.tmp.cleanup()
    def run_apply(self,payload=None,name='better.jpg'):
        payload=self.better if payload is None else payload
        rep=self.spec['replacements'][0]['representations'][0];rep['source_asset']=name;rep['source_asset_sha256']=F.sha(payload)
        (self.p/name).write_bytes(payload);(self.p/'manifest.json').write_text(json.dumps(self.spec),'utf8')
        return F.apply(self.p/'input.docx',self.p/'manifest.json',self.p/'out.docx',self.p/'receipt.json')
    def test_jpg_to_jpeg_alias_preserves_payload_and_all_other_parts(self):
        r=self.run_apply()
        self.assertEqual(r['technical_status'],'PASS');self.assertEqual(r['overall_status'],'REVIEW_REQUIRED')
        with zipfile.ZipFile(self.p/'out.docx') as z:
            self.assertEqual(z.read(self.part),self.better)
            for n,b in self.parts.items():
                if n!=self.part:self.assertEqual(z.read(n),b,n)
    def test_same_extension(self):self.run_apply(name='better.jpeg')
    def test_exif_rotation_refused_without_output(self):
        with self.assertRaisesRegex(ValueError,'EXIF orientation'):self.run_apply(jpeg((400,200),'blue',6))
        self.assertFalse((self.p/'out.docx').exists())
    def test_png_disguised_as_jpeg_refused(self):
        b=io.BytesIO();Image.new('RGB',(400,200)).save(b,format='PNG')
        with self.assertRaisesRegex(ValueError,'single-frame JPEG'):self.run_apply(b.getvalue())
    def test_wrong_aspect_refused(self):
        with self.assertRaisesRegex(ValueError,'aspect ratio'):self.run_apply(jpeg((400,300),'blue'))
    def test_wrong_content_type_refused(self):
        with zipfile.ZipFile(self.p/'input.docx','w') as z:
            for n,b in self.parts.items():z.writestr(n,b.replace(b'image/jpeg',b'image/png') if n=='[Content_Types].xml' else b)
        self.spec['source_sha256']=F.sha((self.p/'input.docx').read_bytes())
        with self.assertRaisesRegex(ValueError,'content type'):self.run_apply()
    def test_old_hash_mismatch_refused(self):
        self.spec['replacements'][0]['representations'][0]['old_media_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'Old media SHA'):self.run_apply()
    def test_same_pixels_old_bytes_not_silent_success(self):
        with self.assertRaisesRegex(ValueError,'old media bytes'):self.run_apply(self.original)

if __name__=='__main__':unittest.main()
