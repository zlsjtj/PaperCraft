"""Small renderer checks: visible occluder, input-order invariance, bad camera.
These tests say nothing about whether a figure is aesthetically successful.
"""
import unittest
import numpy as np
from mesh_surface import render

class SurfaceTest(unittest.TestCase):
    def faces(self):
        return [dict(p=np.array([[-1.,-1,z],[1,-1,z],[1,1,z],[-1,1,z]]),n=np.array([0.,0,1]),role=role,color=color) for z,role,color in [(0,'far','#004455'),(1,'near','#d9ab65')]]
    def test_occluder_and_input_order(self):
        args=([1,0,0],[0,1,0],[0,0,1])
        a,m,_,_,r=render(self.faces(),*args,px_per_unit=20)
        b,n,_,_,s=render(list(reversed(self.faces())),*args,px_per_unit=20)
        self.assertEqual(a.tobytes(),b.tobytes())
        self.assertEqual(m.tobytes(),n.tobytes())
        self.assertEqual(set(v['role_id'] for v in r['visibility_samples']),{r['roles']['near']})
        self.assertTrue(all(abs(v['depth']-1)<1e-10 for v in r['visibility_samples']))
    def test_camera_rejected(self):
        with self.assertRaises(ValueError):render(self.faces(),[2,0,0],[0,1,0],[0,0,1])
    def test_light_rejected(self):
        with self.assertRaises(ValueError):render(self.faces(),[1,0,0],[0,1,0],[0,0,1],light=(0,0,0))

if __name__=='__main__':unittest.main()
